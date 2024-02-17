from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
from hotel_provider import HotelProvider

load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("ORGANIZATION")
)
app = FastAPI()
hotel_provider = HotelProvider()

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


def flight(origin, destination, start_date, end_date):
    # call the Amadeus flight api
    URL = "https://test.api.amadeus.com/v1/shopping/flight-destination"
    AMADEUS = os.environ.get("AMADEUS_API_KEY")
    HEADERS = {
        "Authorization": "Bearer " + AMADEUS,
        "Content-Type": "application/json"
    }
    PARAMS = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": start_date,
        "returnDate": end_date,
        "adults": 1
    }
    response = requests.get(url=URL, headers=HEADERS, params=PARAMS)
    data = response.json()
    return data


# accsess the data from the user and asks all our apis for data. then returns a string with all the data
def gather_data(trip):
    origin = trip.origin
    destination = trip.destination
    budget = trip.budget
    duration = trip.duration
    start_date = trip.start_date
    end_date = trip.end_date
    flight_data = flight(origin, destination, start_date, end_date)
    data = f"origin: {origin}, destination: {destination}, budget: {budget}, duration: {duration}, start_date: {start_date}, end_date: {end_date}, flight_data: {flight_data}"
    return data





@app.get("/")
def read_root():
    return {"Hello": "World"}


class TripDescription(BaseModel):
    origin: str
    destination: str
    budget: int
    duration: int
    start_date: str
    end_date: str


@app.post("/plan-trip/")
async def get_trip_plan(trip: TripDescription):
    data = gather_data(trip)
    print(data)
    trip_plan = get_trip_suggestions(client, data)
    return {"Trip Plan": trip_plan}


@app.get("/search-hotels-region-id/{country}")
async def search_hotels_region_id(country: str):  # Removed 'self' parameter
    response = await hotel_provider.search_hotels_region_id(country)
    return response