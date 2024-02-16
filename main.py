import asyncio

from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from flights import run
from playwright.sync_api import sync_playwright

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
    print(flights_info)
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


@app.post("/plan-trip/")
async def get_trip_plan(trip: TripDescription):
    data = await gather_data(trip)
    #print(data)
    #trip_plan = get_trip_suggestions(client, data)
    return {"Trip Plan": data}
