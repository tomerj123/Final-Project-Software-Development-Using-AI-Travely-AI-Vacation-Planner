import os
from dotenv import load_dotenv
import httpx  # Make sure to install this package

load_dotenv()

class HotelProvider:
    def __init__(self):
        self.url = "https://hotels-com-provider.p.rapidapi.com/v2/hotels/"
        self.headers = {
            "X-RapidAPI-Key": os.environ.get("HOTEL_API_KEY"),
            "X-RapidAPI-Host": "hotels-com-provider.p.rapidapi.com"
        }

    async def search_hotels(self, querystring):
        url = self.url + 'search'
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=querystring)
                response.raise_for_status()  # Raises an exception for 4XX/5XX responses
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            # Return a meaningful error message or response here
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
            # Return a meaningful error message or response here

    async def search_hotels_region_id(self, country: str):
        url = self.url + 'regions'
        querystring = {"query": country, "locale": "en_GB", "domain": "AE"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=querystring)
                response.raise_for_status()  # Raises an exception for 4XX/5XX responses
                return response.json()['data'][0]['gaiaId']
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            # Return a meaningful error message or response here
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
            # Return a meaningful error message or response here
