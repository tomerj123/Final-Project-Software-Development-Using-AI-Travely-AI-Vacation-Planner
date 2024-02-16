import asyncio
import webbrowser

from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from flights import run
from playwright.sync_api import sync_playwright
from fastapi.responses import HTMLResponse


load_dotenv()


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def get_trip_suggestions(client, prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt + ". this is all the data that i have gathered so far about the trip im planning. "
                                    "please help me to create a detailed plan for the trip based on this data.",
            }
        ],
        model="gpt-3.5-turbo"
    )
    return chat_completion.choices[0].message.content


async def get_flights_info(origin, destination, departure_date, return_date, max_price):
    async with async_playwright() as playwright:
        google_flights_results = await run(playwright, origin, destination, departure_date, return_date)

    return google_flights_results


def get_accommodation_info(destination, start_date, end_date):
    # Placeholder for an accommodation API call
    # Replace with actual API integration
    return f"Accommodations in {destination} arranged from {start_date} to {end_date}."

def get_activities_info(destination, start_date, end_date):
    # Placeholder for an activities information API call
    # Replace with actual API integration
    return f"Activities in {destination} planned from {start_date} to {end_date}."


class TripDescription(BaseModel):
    origin: str
    destination: str
    budget: int
    start_date: str
    end_date: str


async def gather_data(trip: TripDescription):
    flights_info = await get_flights_info(trip.origin, trip.destination, trip.start_date, trip.end_date, trip.budget)
    #print(flights_info)
    accommodation_info = get_accommodation_info(trip.destination, trip.start_date, trip.end_date)
    activities_info = get_activities_info(trip.destination, trip.start_date, trip.end_date)

    data = f"""
    Destination: {trip.destination}
    Budget: {trip.budget}
    Dates: From {trip.start_date} to {trip.end_date}
    Flights Info: {flights_info}
    Accommodation Info: {accommodation_info}
    Activities Info: {activities_info}
    """
    return data.strip()


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/plan-trip/", response_class=HTMLResponse)
async def get_trip_plan(trip: TripDescription):
    data = await gather_data(trip)
    trip_plan = get_trip_suggestions(client, data)  # This returns the trip plan as a string
    trip_plan_html = trip_plan.replace("\n", "<br>")

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
            body {{ padding-top: 20px; }}
            .container {{ max-width: 800px; }}
            .icon {{ padding-right: 5px; }}
        </style>
    </head>
    <body>
            <div class="card">
            <div class="card-body">
                <h5 class="card-title">Destination</h5>
                <p class="card-text">{trip.destination}</p>

                <h5 class="card-title">Budget</h5>
                <p class="card-text">{trip.budget}</p>
                
                <h5 class="card-title>Start Date</h5>
                <p class="card-text">{trip.start_date}</p>
                
                <h5 class="card-title>End Date</h5>
                <p class="card-text">{trip.end_date}</p>
                
            </div>
            </div>
    
    <div class="container">
        <div class="jumbotron text-center">
            <h1 class="display-4"><i class="fas fa-map-marked-alt icon"></i>Your Trip Plan</h1>
            <p class="lead">Here's a detailed plan for your upcoming adventure.</p>
            <div class="trip-plan">{trip_plan_html}</div>  <!-- Display the trip plan string here -->
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
