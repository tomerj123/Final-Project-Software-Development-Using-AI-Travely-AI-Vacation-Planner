import unittest
from fastapi import HTTPException
import httpx
from unittest.mock import MagicMock, patch
from unittest.mock import AsyncMock
import sqlite3
from main import (
    calculate_distances,
    extract_hotel_data,
    format_hotels_for_prompt,
    format_trip_plan,
    get_activities_info,
    get_flights_info,
    get_hotel_info,
    get_iata_codes_and_airports,
    get_location_details,
    get_trip_suggestions,
    generate_photo_for_html,
    get_top_hotels,
    generate_genral_activities,
)




class TestFunctions(unittest.IsolatedAsyncioTestCase):
    async def test_calculate_distances_between_locations(self):
        activities = [
            {"name": "A", "location": (0, 0)},
            {"name": "B", "location": (1, 1)},
            {"name": "C", "location": (2, 2)},
        ]
        result = await calculate_distances(activities)
        self.assertEqual(result, {'A to B': 157.2495984740402, 'A to C': 314.47523947196964, 'B to C': 157.22564920708905}
)

    async def test_get_location_details(self):
        with patch("httpx.AsyncClient") as MockClient:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "location_id": "1",
                "name": "Test Location",
                "latitude": "0",
                "longitude": "0",
                "website": "example.com",
            }
            MockClient.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            details = await get_location_details("1")
            self.assertEqual(details["name"], "Test Location")
            self.assertEqual(details["website"], "example.com")

    def test_get_iata_code(self):
        conn = sqlite3.connect("./IATA_Codes.db")
        result = get_iata_codes_and_airports("Paris")
        expected_result = [
            {'IATA code': 'PHT', 'Name': 'Henry County Airport'},
            {'IATA code': 'PRX', 'Name': 'Cox Field'},
            {'IATA code': 'LBG', 'Name': 'Paris-Le Bourget Airport'},
            {'IATA code': 'CDG', 'Name': 'Charles de Gaulle International Airport'},
            {'IATA code': 'ORY', 'Name': 'Paris-Orly Airport'}
        ]
        self.assertEqual(result, expected_result)


    def test_get_iata_codes_and_airports(self):
        conn = sqlite3.connect("./IATA_Codes.db")
        result = get_iata_codes_and_airports("Tel Aviv")
        self.assertEqual(result, [{'Name': 'Ben Gurion International Airport', 'IATA code': 'TLV'}, {'Name': 'Sde Dov Airport', 'IATA code': 'SDV'}])

    def test_format_trip_plan(self):
        plan_text = "### Header \n **Bold Text** [link](http://example.com)"
        formatted_text = format_trip_plan(plan_text)
        self.assertIn("<h3>Header</h3>", formatted_text)
        self.assertIn("<strong>Bold Text</strong>", formatted_text)
        self.assertIn('<a href="http://example.com"', formatted_text)

    def test_extract_hotel_data(self):
        hotels_data = [
            {
                "name": "Hotel A",
                "link": "example.com",
                "check_in_time": "12:00 PM",
                "check_out_time": "10:00 AM",
                "rate_per_night": {"lowest": "$100"},
                "total_rate": {"lowest": "$500"},
                "nearby_places": [{"name": "Park"}, {"name": "Restaurant"}],
            }
        ]
        extracted_data = extract_hotel_data(hotels_data)
        self.assertEqual(extracted_data[0]["Name"], "Hotel A")

    def test_format_hotels_for_prompt(self):
        hotels_data = [
            {
                "Name": "Hotel A",
                "Link": "example.com",
                "Check-in Time": "12:00 PM",
                "Check-out Time": "10:00 AM",
                "Rate Per Night (Lowest)": "$100",
                "Total Rate (Lowest)": "$500",
                "Nearby Places": ["Park", "Restaurant"],
            }
        ]
        formatted_text = format_hotels_for_prompt(hotels_data)
        print(formatted_text)
        self.assertIn("Hotel A", formatted_text)

    async def test_get_hotel_info_success(self):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"properties": ["Hotel1", "Hotel2"]}

        # Patch the httpx.AsyncClient.get method to return the mock response
        with patch.object(httpx.AsyncClient, 'get', return_value=mock_response):
            properties = await get_hotel_info("New York", "2024-04-01", "2024-04-10", "2")
            assert properties == ["Hotel1", "Hotel2"], "Should return a list of properties"

    async def test_get_activities_info_success(self):
        # Mock successful responses for both URLs
        mock_response_attractions = MagicMock()
        mock_response_attractions.status_code = 200
        mock_response_attractions.json.return_value = {"data": [{"location_id": "1", "name": "Attraction1"}]}

        mock_response_restaurants = MagicMock()
        mock_response_restaurants.status_code = 200
        mock_response_restaurants.json.return_value = {"data": [{"location_id": "2", "name": "Restaurant1"}]}

        # Patch the httpx.AsyncClient.get method to return the mock responses in sequence
        with patch.object(httpx.AsyncClient, 'get', side_effect=[mock_response_attractions, mock_response_restaurants]):
            combined_data, location_ids = await get_activities_info("Paris")
            assert combined_data == [{"location_id": "1", "name": "Attraction1"}, {"location_id": "2", "name": "Restaurant1"}], "Should return combined data"
            assert location_ids == ["1", "2"], "Should return a list of location_ids"

    async def test_get_flights_info_failure(self):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not Found"}
        mock_response.text = "Not Found"

        with patch.object(httpx.AsyncClient, 'get', return_value=mock_response):
            with self.assertRaises(HTTPException) as context:
                await get_flights_info("ABC", "DEF", "2024-01-01", "2024-01-15")
            self.assertEqual(context.exception.status_code, 404)






 

  

if __name__ == "__main__":
    unittest.main()
