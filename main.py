from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from flights import run
import httpx
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import tempfile
import asyncio
import requests
import logging

load_dotenv()

# Configure the logging system
logging.basicConfig(filename='data.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


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
                                    "day. use all the budget and tell me recommendations for events and activities i "
                                    "can do in the destination and also include shopping and dining."
                                    "i also want to mention that i will put this plan in my html page here: <div "
                                    "class=trip-plan>{trip_plan_html}</div> so please make the format of the plan in "
                                    "a way that will look good in the html page. (i.e if you want to make some text bold then use <b> tag and not **bold**)."
            }
        ],
        model="gpt-4-0125-preview",
        temperature=0.3,
        # model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content


async def get_flights_info(origin, destination, departure_date, return_date, max_price):
    loop = asyncio.get_running_loop()
    google_flights_results = await loop.run_in_executor(None, run, origin, destination, departure_date, return_date)
    return google_flights_results


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


def get_top_hotels(client, hotels_data):
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


async def get_activities_info(destination):
    key = os.environ.get("TRIPADVISOR_API_KEY")
    url = f"https://api.content.tripadvisor.com/api/v1/location/search?key={key}&searchQuery={destination}&category=attractions&language=en"
    url2 = f"https://api.content.tripadvisor.com/api/v1/location/search?key={key}&searchQuery={destination}&category=restaurants&language=en"
    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers)
    response2 = requests.get(url2, headers=headers)
    return response.text + "\n" + response2.text


async def get_event_tickets(destination, start_date, end_date):
    seatgeek_params = {
        "venue.city": destination,
        "datetime_utc.gte": start_date,
        "datetime_utc.lte": end_date,
        "client_id": os.environ.get("SEATGEEK_CLIENT_ID")
    }

    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.seatgeek.com/2/events", params=seatgeek_params)

        if response.status_code == 200:
            return response.json()["events"]
        else:
            print(f"Error: {response.text}")  # Print error message for debugging
            raise HTTPException(status_code=response.status_code,
                                detail=f"Failed to fetch event data from SeatGeek: {response.text}")


class TripDescription(BaseModel):
    origin: str
    destination: str
    budget: int
    start_date: str
    end_date: str


async def gather_data(trip: TripDescription):
    flights_info = await get_flights_info(trip.origin, trip.destination, trip.start_date, trip.end_date, trip.budget)
    # print(flights_info)
    hotels_info = await get_hotel_info(trip.destination, trip.start_date, trip.end_date)
    top_hotels = get_top_hotels(client, hotels_info)
    activities_info = await get_activities_info(trip.destination)
    print(activities_info)

    data = f"""
    Destination: {trip.destination}
    Budget: {trip.budget}
    Dates: From {trip.start_date} to {trip.end_date}
    Flights Info: {flights_info}
    Accommodation Info: {top_hotels}
    Activities Info: {activities_info}
    """
    return data.strip()


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/plan-trip/", response_class=HTMLResponse)
async def get_trip_plan(trip: TripDescription):
    html_content = "<h1>An error occurred while generating the trip plan</h1>"

    try:
        data = await gather_data(trip)
        # #return data
        logging.info(data)
        trip_plan =  get_trip_suggestions(client, data)  # This returns the trip plan as a string
        trip_plan_html = trip_plan.replace("\n", "<br>")

        # Insert trip_plan string into the HTML content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w+") as tmp_file:
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
                    <h5 class="card-title">full trip data can be found in the log file</h5>
                </div>
            </div>
    </div>
    </div>
    
    </body>
    </html>
    """
                    tmp_file.write(html_content)
                    tmp_file_path = tmp_file.name

        with open(tmp_file_path, "r") as tmp_file:
            html_content = tmp_file.read()

        os.remove(tmp_file_path)
    except Exception as e:
        print(f"An error occurred in get_trip_plan: {e}")
        return HTMLResponse(content=html_content, status_code=500)
    finally:
        return HTMLResponse(content=html_content, status_code=200)


 
