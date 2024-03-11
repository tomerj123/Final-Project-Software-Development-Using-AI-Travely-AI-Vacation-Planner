import json
from fastapi import FastAPI, HTTPException, Query
from haversine import haversine, Unit
from fastapi.encoders import jsonable_encoder
from playwright.async_api import async_playwright
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import httpx
import requests
import logging
import sqlite3

load_dotenv()

# Configure the logging system
logging.basicConfig(filename='data.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# generate photo for the trip html page
def generate_photo_for_html(destination):
    response = client.images.generate(
        model="dall-e-3",
        prompt="I'm planning a trip to " + destination + ". Can you help me to create a photo for the trip?",
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    return image_url

#use all the data we gathered so far to create a detailed plan for the trip using openai API
def get_trip_suggestions(client, prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt + ". this is all the data that i have gathered so far about the trip im planning. "
                                    "please help me to create a detailed plan for the trip based on this data. write "
                                    "brief list of the flights and show to me what is the best flight based on the data i "
                                    "provided. then do the same for the hotels i provided. Then write a"
                                    "detailed plan for each day and consider the budget i have left after "
                                    "the flight and hotel. use the attractions i provided from tripadvisor and the nearby places in the hotel info to create a detailed plan for each "
                                    "day, and for each attraction add the website i provided. use all the budget and "
                                    "tell me recommendations for events and activities i"
                                    "can do in the destination and also include shopping and dining. use the data in the how to arrange the activities to know which activities are close to each other and can be done in the same day. "
                                    "i also want to mention that i will put this plan in my html page here: <div "
                                    "class=trip-plan>{trip_plan_html}</div> so please make the format of the plan in "
                                    "a way that will look good in the html page. (i.e if you want to make some text bold then use <b> tag and not **bold**)."
            }
        ],
        model="gpt-4-0125-preview",
        # model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content


async def get_flights_info(departure_id: str, arrival_id: str, outbound_date: str, return_date: str):
    serpapi_params = {
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "currency": "USD",
        "hl": "en",
        "api_key": os.environ.get("SERPAPI_API_KEY")
    }

    async with httpx.AsyncClient() as client:
        response = await client.get("https://serpapi.com/search?engine=google_flights", params=serpapi_params)

        if response.status_code == 200:
            return response.json()["best_flights"]
        else:
            print(f"Error: {response.text}")  # Print error message for debugging
            raise HTTPException(status_code=response.status_code,
                                detail=f"Failed to fetch flight data from SerpApi: {response.text}")


async def get_hotel_info(destination, check_in_date, check_out_date):
    serpapi_params = {
        "q": "central hotels in " + destination,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "currency": "USD",
        "api_key": os.environ.get("SERPAPI_API_KEY")
    }

    async with httpx.AsyncClient() as client:
        response = await client.get("https://serpapi.com/search?engine=google_hotels", params=serpapi_params)

        if response.status_code == 200:
            return response.json()["properties"]
        else:
            print(f"Error: {response.text}")  # Print error message for debugging
            raise HTTPException(status_code=response.status_code,
                                detail=f"Failed to fetch hotel data from SerpApi: {response.text}")


def extract_hotel_data(hotels_data):
    # Initialize a list to hold the extracted data
    extracted_data = []

    # Iterate through each hotel in the data
    for hotel in hotels_data:
        # Extract required information
        hotel_info = {
            "Name": hotel.get("name", "N/A"),
            "Link": hotel.get("link", "N/A"),
            "Check-in Time": hotel.get("check_in_time", "N/A"),
            "Check-out Time": hotel.get("check_out_time", "N/A"),
            "Rate Per Night (Lowest)": hotel.get("rate_per_night", {}).get("lowest", "N/A"),
            "Total Rate (Lowest)": hotel.get("total_rate", {}).get("lowest", "N/A"),
            "Nearby Places": [place.get("name", "N/A") for place in hotel.get("nearby_places", [])]
        }

        # Add the extracted info to the list
        extracted_data.append(hotel_info)

    # Return the list of extracted data
    return extracted_data


def format_hotels_for_prompt(hotels_data):
    # Initialize an empty string to hold the formatted hotel information
    hotels_string = ""

    # Iterate through each hotel in the data
    for hotel in hotels_data:
        # Format the hotel information and add it to the hotels_string
        hotel_info = f"Name: {hotel['Name']}, Link: {hotel['Link']}, Check-in Time: {hotel['Check-in Time']}, Check-out Time: {hotel['Check-out Time']}, Rate Per Night (Lowest): {hotel['Rate Per Night (Lowest)']}, Total Rate (Lowest): {hotel['Total Rate (Lowest)']}, Nearby Places: {', '.join(hotel['Nearby Places'])}\n"
        hotels_string += hotel_info

    return hotels_string


async def get_top_hotels(client, hotels_data):
    # Use the extract_hotel_data function to extract hotel information
    extracted_data = extract_hotel_data(hotels_data)

    # Format the extracted hotel data for the prompt
    prompt_text = format_hotels_for_prompt(extracted_data)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "This is the hotels list I have gathered so far. Write me a list of the top hotels and the info on each hotel you got.\n" + prompt_text
            }
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content

"""
async def get_activities_info(destination):
    key = os.environ.get("TRIPADVISOR_API_KEY")
    url = f"https://api.content.tripadvisor.com/api/v1/location/search?key={key}&searchQuery={destination}&category=attractions&language=en"
    url2 = f"https://api.content.tripadvisor.com/api/v1/location/search?key={key}&searchQuery={destination}&category=restaurants&language=en"
    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers)
    response2 = requests.get(url2, headers=headers)
    return response.text + "\n" + response2.text"""

async def get_activities_info(destination):
    key = os.environ.get("TRIPADVISOR_API_KEY")
    headers = {"accept": "application/json"}
    combined_data = []
    location_ids = []

    # URLs for attractions and restaurants
    urls = [
        f"https://api.content.tripadvisor.com/api/v1/location/search?key={key}&searchQuery={destination}&category=attractions&language=en",
        f"https://api.content.tripadvisor.com/api/v1/location/search?key={key}&searchQuery={destination}&category=restaurants&language=en"
    ]

    async with httpx.AsyncClient() as client:
        for url in urls:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json().get("data", [])
                combined_data.extend(data)
                location_ids.extend([item["location_id"] for item in data])

    return combined_data, location_ids


async def get_location_details(location_id):
    key = os.environ.get("TRIPADVISOR_API_KEY")
    url = f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/details?language=en&currency=USD&key={key}"
    headers = {"accept": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            details = response.json()
            return dict(location_id=details["location_id"], name=details["name"],
                        location=(float(details.get("latitude", 0)), float(details.get("longitude", 0))),
                        website=details.get("website", "N/A"))
        else:
            print(f"Error fetching details for location ID {location_id}: {response.text}")


class TripDescription(BaseModel):
    origin: str
    origin_iata: str
    destination: str
    destination_iata: str
    budget: int
    start_date: str
    end_date: str


# Connect to your SQLite database
conn = sqlite3.connect('IATA_Codes.db')


def get_iata_code(city_name):
    cursor = conn.cursor()
    # Updated query to match the specified format
    cursor.execute("SELECT IATA_code FROM IATA_Codes WHERE LOWER(Municipality) = LOWER(?)", (city_name,))
    result = cursor.fetchall()
    return result if result else None


async def generate_genral_activities(client, distances, days):
    formatted_distances = json.dumps(distances, indent=2)  # Convert the dictionary to a JSON string for readability
    content = (
        "I have this list of activities and the distances in km between each activity. Write a new "
        "list that is divided into {days} days. And in each day, write to me which attractions and "
        "restaurants to go to. I need you to also take into account the distances so we won't have too "
        "long trips. Also, don't repeat attractions on separate days. Don't assume any activity as a "
        "starting point. Just give the plan and also try to combine restaurants and attractions. If "
        "there is a bit of travel that's also ok; we don't need the closest attractions each "
        "day.\n{distances}"
    ).format(days=days, distances=formatted_distances)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content


from datetime import datetime
dateformat = "%Y-%m-%d"
async def gather_data(trip: TripDescription):
    # Convert trip origin and destination names to IATA codes
    if not trip.origin_iata:
        trip.origin_iata = get_iata_code(trip.origin)
    if not trip.destination_iata:
        trip.destination_iata = get_iata_code(trip.destination)
    if not trip.origin_iata or not trip.destination_iata:
        # Handle cases where IATA codes are not found
        raise HTTPException(status_code=404, detail="IATA code for city not found")

    # Use IATA codes for flight and hotel information fetching
    flights_info = await get_flights_info(trip.origin_iata, trip.destination_iata, trip.start_date, trip.end_date)
    # print(flights_info)
    hotels_info = await get_hotel_info(trip.destination, trip.start_date, trip.end_date)
    top_hotels = await get_top_hotels(client, hotels_info)
    activities_info, activities_location_ids = await get_activities_info(trip.destination)
    activities_details = []
    for location_id in activities_location_ids:
        activity_details = await get_location_details(location_id)
        if activity_details:
            activities_details.append(activity_details)

    distances = await calculate_distances(activities_details)
    start_date = datetime.strptime(trip.start_date, dateformat)
    end_date = datetime.strptime(trip.end_date, dateformat)
    num_days = (end_date - start_date).days

    location_based_activities = await generate_genral_activities(client, distances, str(num_days))


    # print(activities_info)

    data = f"""
    Destination: {trip.destination}
    Budget: {trip.budget}
    Dates: From {trip.start_date} to {trip.end_date}
    Flights Info: {flights_info}
    Accommodation Info: {top_hotels}
    how to arrange the activities: {location_based_activities}
    Activities Info: {activities_info}
    activities websites: {activities_details}
    """
    return data.strip()


def get_iata_codes_and_airports(city_name):
    cursor = conn.cursor()
    query = "SELECT aiport_name, IATA_code FROM IATA_Codes WHERE LOWER(Municipality) = LOWER(?)"
    cursor.execute(query, (city_name,))
    results = cursor.fetchall()
    return [{"Name": name, "IATA code": code} for name, code in results]


async def calculate_distances(activities):
    distances = {}
    for i in range(len(activities)):
        for j in range(i + 1, len(activities)):
            try:
                # Ensure locations are tuples of floats
                loc1 = activities[i]['location']
                loc2 = activities[j]['location']
                distance = haversine(loc1, loc2)
                # Create a readable key for the distance
                key = f"{activities[i]['name']} to {activities[j]['name']}"
                distances[key] = distance
            except Exception as e:
                print(f"Error calculating distance between {activities[i]['name']} and {activities[j]['name']}: {e}")
    return distances


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


app = FastAPI()

@app.get("/test-activities/")
async def test_activities(destination: str = Query(..., title="Destination", description="The destination to fetch activities for")):
    try:
        activities_info, ids = await get_activities_info(destination)
        activities_details = []
        for location_id in ids:
            detail = await get_location_details(location_id)
            if detail:  # Ensure detail is not None and has 'name' and 'location'
                # Append the detail dict as-is, assuming it has 'name' and 'location'
                activities_details.append(detail)
        distances = await calculate_distances(activities_details)
        return distances
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")

@app.get("/test-flights/")
async def test_get_flights_info(departure_id: str = Query(..., title="Departure IATA Code"),
                                arrival_id: str = Query(..., title="Arrival IATA Code"),
                                outbound_date: str = Query(..., title="Outbound Date"),
                                return_date: str = Query(..., title="Return Date")):
    try:
        best_flights = await get_flights_info(departure_id, arrival_id, outbound_date, return_date)
        return {"best_flights": best_flights}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
@app.get("/select-airport/")
async def select_airport(city_name: str = Query(..., title="City Name", description="Type the name of the city to get the IATA codes for the airpots")):
    airports = get_iata_codes_and_airports(city_name)
    if not airports:
        raise HTTPException(status_code=404, detail="No airports found for the given city")
    elif len(airports) == 1:
        # If there's only one airport, return its IATA code
        return {"city_name": city_name, "iata_code": airports[0][1]}
    else:
        # Return a list of airports for the user to choose from
        return {"city_name": city_name, "airports": airports}


@app.post("/plan-trip/", response_class=HTMLResponse)
async def get_trip_plan(trip: TripDescription):
    data = await gather_data(trip)
    # Configure the logging system
    logging.info(data)
    trip_plan = get_trip_suggestions(client, data)  # convert the trip plan to string
    trip_plan_html = trip_plan.replace("\n", "<br>")
    # data = data.replace("\n", "<br>")

    # Insert trip_plan string into the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trip Plan</title>
        <!-- Bootstrap CSS -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <!-- Font Awesome Icons -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
        <style>
            body {{
                padding-top: 20px;
                background-color: #f0f2f5; /* Light grey background */
            }}
            .header {{
                display: flex;
                align-items: center;
                padding: 10px 0;
            }}
            .header img {{
                width: 500px; /* Adjust based on your image size */
                height: auto;
                margin-left: 600px;
            }}
            .container {{
                max-width: 800px;
                margin: auto;
                background-color: #fff; /* White background for the content */
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* Adding some shadow for depth */
                padding: 20px;
                border-radius: 8px; /* Slightly rounded corners */
            }}
            .icon {{
                padding-right: 5px;
                color: #007bff; /* Bootstrap primary color */
            }}
            .trip-details .card {{
                margin-bottom: 20px;
                border-left: 4px solid #007bff; /* Add a colored border to the left */
            }}
            .card-body {{
                color: #495057; /* Darker text for better readability */
            }}
            .jumbotron {{
                background-color: #007bff; /* Bootstrap primary color */
                color: #fff; /* White text color */
                border-radius: 8px; /* Slightly rounded corners */
                padding: 30px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
    <div class="header">
        <img src="{generate_photo_for_html(trip.destination)}" alt="Photo">
    </div>
    
    <div class="container">
    
        <div class="trip-details">
        
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Destination</h5>
                    <p class="card-text">{trip.destination}</p>
                </div>
            </div>
    
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Budget</h5>
                    <p class="card-text">{trip.budget}</p>
                </div>
            </div>
    
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Start Date</h5>
                    <p class="card-text">{trip.start_date}</p>
                </div>
            </div>
    
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">End Date</h5>
                    <p class="card-text">{trip.end_date}</p>
                </div>
            </div>
        </div>
    
        <div class="jumbotron text-center">
            <h1 class="display-4"><i class="fas fa-map-marked-alt icon"></i>Your Trip Plan</h1>
            <p class="lead">Here's a detailed plan for your upcoming adventure.</p>
            <div class="trip-plan">{trip_plan_html}</div> <!-- Display the trip plan string here -->
        </div>
    
    </div>
    <div class="container">
    <div class="trip-details">
                <div class="card">
                <div class="card-body">
                    <h5 class="card-title"></h5>
                </div>
            </div>
    </div>
    </div>
    
    </body>
    </html>
    """

    file_path = '/Users/tomerjuster/Desktop/Final Project Software Development Using AI/trip_plan.html'  # Specify the path where you want to save the HTML file

    with open(file_path, 'w') as file:
        file.write(html_content)

    return HTMLResponse(content=html_content)
