import json
import tempfile
import webbrowser
from haversine import haversine
from openai import OpenAI
import os
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import logging
from logging.handlers import RotatingFileHandler
import sqlite3
import re
from datetime import datetime

from starlette.responses import RedirectResponse

dateformat = "%Y-%m-%d"

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG

# Create a rotating file handler
log_handler = RotatingFileHandler(
    '../data.log', maxBytes=10 * 1024 * 1024, backupCount=5
)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add the handler to the logger
logger.addHandler(log_handler)

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


### functions that uses openai API: ###
# generate photo for the trip html page
async def generate_photo_for_html(destination):
    response = client.images.generate(
        model="dall-e-3",
        prompt="I'm planning a trip to " + destination + ". Can you help me to create a photo for the trip?",
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    return image_url


# use all the data we gathered so far to create a detailed plan for the trip using openai API
async def get_trip_suggestions(client, prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt + "I'm planning a trip and need a detailed plan based on this information. Please "
                                    "create a comprehensive trip plan that includes in this order:"
                                    "1. The best flight option considering price and timing."
                                    "2. Top 3 hotel recommendations based on the data."
                                    "3. show now the budget that was left after the flight and hotel. take into consideration the number of people in the trip"
                                    "4. A day-by-day itinerary that: (in the first day take into account the arrival time of the flight in the planning)"
                                    "- Allocates activities and attractions based on their proximity (using the data)."
                                    "- Suggests dining options near each activity or attraction."
                                    "- Utilizes the budget effectively, considering the cost of flights and accommodation."
                                    "- Incorporates free time for shopping and exploration."
                                    "- Include addresses and websites of attractions"
                                    "4. Ensure all recommendations are presented in a way that will be visually appealing on a webpage, using HTML formatting where appropriate (e.g., <b> for bold)."
                                    "5. do not write me any instructions on how to put the trip plan in the html, just provide the plan like i instructed."

                                    "ensure it is well-organized and includes all relevant details."
            }
        ],
        model="gpt-4-0125-preview",
        temperature=0.5,
        # model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content


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


### functions that uses serpAPI: ###
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
            return response.json()
        else:
            print(f"Error: {response.text}")  # Print error message for debugging
            raise HTTPException(status_code=response.status_code,
                                detail=f"Failed to fetch flight data from SerpApi: {response.text}")


async def get_hotel_info(destination, check_in_date, check_out_date, people_num):
    serpapi_params = {
        "q": "central hotels in " + destination,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "currency": "USD",
        "adults": people_num,
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


### functions that uses tripadvisor API: ###
async def get_activities_info(destination):
    key = os.environ.get("TRIPADVISOR_API_KEY")
    headers = {"accept": "application/json"}
    combined_data = []
    location_ids = []

    # URLs for attractions and restaurants
    urls = [
        f"https://api.content.tripadvisor.com/api/v1/location/search?key={key}&searchQuery={destination}&category=attractions&language=en",
        f"https://api.content.tripadvisor.com/api/v1/location/search?key={key}&searchQuery=restaurants%20in%20{destination}&category=restaurants&language=en"
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


### functions that extract data from our database: ###

def get_iata_code(city_name):
    conn = sqlite3.connect('./IATA_Codes.db')
    cursor = conn.cursor()
    # Updated query to match the specified format
    cursor.execute("SELECT IATA_code FROM IATA_Codes WHERE LOWER(Municipality) = LOWER(?)", (city_name,))
    result = cursor.fetchall()
    return result if result else None


def get_iata_codes_and_airports(city_name):
    conn = sqlite3.connect('./IATA_Codes.db')
    cursor = conn.cursor()
    query = "SELECT aiport_name, IATA_code FROM IATA_Codes WHERE LOWER(Municipality) = LOWER(?)"
    cursor.execute(query, (city_name,))
    results = cursor.fetchall()
    return [{"Name": name, "IATA code": code} for name, code in results]


### functions that format the data text or for the html page: ###
def format_trip_plan(plan_text):
    # Replace ### with <h3> tags
    plan_text = re.sub(r'###\s*(.*?)\s*\n', r'<h3>\1</h3><br>', plan_text)

    # Replace ** with <strong> tags
    plan_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong><br>', plan_text)

    # Updated URL pattern to exclude closing parenthesis and existing <a> tags
    url_pattern = r'(?<!href=")(http[s]?://[^\s\)]+)(?!"[>])'
    plan_text = re.sub(url_pattern, r'<a href="\1" style="color:black;">\1</a>', plan_text)

    # Correcting double <a> tags if present
    double_a_tag_pattern = r'<a href=\'<a href="([^"]+)" style="color:black;">[^<]+</a>\' style="color:black;">[^<]+</a>'
    plan_text = re.sub(double_a_tag_pattern, r'<a href="\1" style="color:black;">\1</a>', plan_text)

    plan_text = plan_text.replace("```html", "")

    return plan_text


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


# convert the hotel data to a string that can be used in the prompt
def format_hotels_for_prompt(hotels_data):
    # Initialize an empty string to hold the formatted hotel information
    hotels_string = ""

    # Iterate through each hotel in the data
    for hotel in hotels_data:
        # Format the hotel information and add it to the hotels_string
        hotel_info = f"Name: {hotel['Name']}, Link: {hotel['Link']}, Check-in Time: {hotel['Check-in Time']}, Check-out Time: {hotel['Check-out Time']}, Rate Per Night (Lowest): {hotel['Rate Per Night (Lowest)']}, Total Rate (Lowest): {hotel['Total Rate (Lowest)']}, Nearby Places: {', '.join(hotel['Nearby Places'])}\n"
        hotels_string += hotel_info

    return hotels_string


class TripDescription(BaseModel):
    origin: str
    origin_iata: str
    destination: str
    destination_iata: str
    budget: int
    start_date: str
    end_date: str
    num_of_people: int


### main functions that gather all the data to create the trip plan: ###
async def gather_data(trip: TripDescription):
    try:
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
        hotels_info = await get_hotel_info(trip.destination, trip.start_date, trip.end_date, trip.num_of_people)
        top_hotels = await get_top_hotels(client, hotels_info)
        activities_info, activities_location_ids = await get_activities_info(trip.destination)

        activities_details = []
        for location_id in activities_location_ids:
            activity_details = await get_location_details(location_id)
            if activity_details:
                activities_details.append(activity_details)

        distances = await calculate_distances(activities_details)
        start_date = datetime.strptime(trip.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(trip.end_date, "%Y-%m-%d")
        num_days = (end_date - start_date).days

        location_based_activities = await generate_genral_activities(client, distances, str(num_days))

        data = f"""
        Destination: {trip.destination}
        Budget: {trip.budget}
        Dates: From {trip.start_date} to {trip.end_date}
        Number of people: {trip.num_of_people}
        Flights Info: {flights_info}
        Accommodation Info: {top_hotels}
        How to arrange the activities: {location_based_activities}
        Activities Info: {activities_info}
        Activities websites: {activities_details}
        """
        return data.strip()

    except Exception as e:
        # Log the exception or handle it as needed
        print(f"Error gathering trip data: {e}")
        # You might want to raise an HTTPException to send a specific error response to the client
        raise HTTPException(status_code=500, detail="An error occurred while gathering trip data.")


async def calculate_distances(activities):
    distances = []
    for i in range(len(activities)):
        for j in range(i + 1, len(activities)):
            try:
                # Ensure locations are tuples of floats
                loc1 = activities[i]['location']
                loc2 = activities[j]['location']
                distance = haversine(loc1, loc2)
                # Create a readable key for the distance
                key = f"{activities[i]['name']} to {activities[j]['name']}"
                distances.append((key, distance))
            except Exception as e:
                print(f"Error calculating distance between {activities[i]['name']} and {activities[j]['name']}: {e}")
    # Sort distances by the second item in each tuple (the distance)
    distances.sort(key=lambda x: x[1])
    return distances


### fastAPI: ###
app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000",
    "http://localhost:8000"
    "http://0.0.0.0:80"
    "http://backend:8000"
    "backend:8000"
    "tomerandsionefinalproject.eastus.azurecontainer.io"
    "postman"
    # app domain on azure
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specify the frontend origin here, or use "*" for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# You might also want to redirect the root URL to the frontend
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/search-for-your-preferred-airports/")
async def select_airports(
        origin_city: str = Query(..., title="Origin City",
                                 description="Type the name of the origin city to get the IATA codes for the airports"),
        destination_city: str = Query(..., title="Destination City",
                                      description="Type the name of the destination city to get the IATA codes for the airports")):
    # Get airports for the origin city
    origin_airports = get_iata_codes_and_airports(origin_city)
    if not origin_airports:
        raise HTTPException(status_code=404, detail=f"No airports found for the origin city: {origin_city}")

    # Get airports for the destination city
    destination_airports = get_iata_codes_and_airports(destination_city)
    if not destination_airports:
        raise HTTPException(status_code=404, detail=f"No airports found for the destination city: {destination_city}")

    # Prepare the response
    response = {
        "origin_city": {
            "city_name": origin_city,
            "airports": origin_airports
        },
        "destination_city": {
            "city_name": destination_city,
            "airports": destination_airports
        }
    }

    return response

@app.get("/CI-check")
async def check():
    return {"message": "CI Working"}


@app.post("/plan-trip/", response_class=HTMLResponse)
async def get_trip_plan(trip: TripDescription):
    # print(trip.model_dump())
    data = await gather_data(trip)
    trip_plan = await get_trip_suggestions(client, data)  # convert the trip plan to string
    trip_plan = format_trip_plan(trip_plan)
    trip_plan_html = trip_plan.replace("\n", "<br>")
    logging.info(f"Trip plan for {trip.destination} was created successfully")

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
            .trip-details-main {{
                display: flex; /* This makes it a Flex container */
                flex-direction: row; /* This aligns children in a row */
                flex-wrap: wrap; /* This allows items to wrap to the next line if there's not enough space */
                justify-content: space-around; /* This distributes space around the items */
                align-items: stretch; /* This stretches the items to fill the container height */
                gap: 20px; /* This adds some space between the items */
                margin-bottom: 20px; /* Add a colored border to the left */
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
            a {{
                color: black;
            }}
    </style>
    </head>
    <body>
    <div class="header">
        <img src="{await generate_photo_for_html(trip.destination)}" alt="Photo">
    </div>
    
    <div class="container">
    
        <div class="trip-details-main">
        
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
            <h1 class="display-4"></i>Your Trip Plan</h1>
            <p class="lead">Here's a detailed plan for your upcoming adventure.</p>
            <div class="trip-plan">{trip_plan_html}</div> <!-- Display the trip plan string here -->
        </div>
    
    </div>
    <div class="container">
    <div class="trip-details">
                <div class="card">
                <div class="card-body">
                    <h5 class="card-title"> if you liked the plan, click ctrl+s to save the plan to your device</h5>
                </div>
            </div>
    </div>
    </div>
    
    </body>
    </html>
    """
    logging.info(html_content)
    # Generate a temporary file to store the HTML content
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as file:
        file.write(html_content.encode('utf-8'))
        file_path = file.name

    # Open the temporary HTML file in the default browser
    webbrowser.open('file://' + file_path)

    return HTMLResponse(content=html_content)
