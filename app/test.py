import unittest
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
        self.assertEqual(result, [('PHT',), ('PRX',), ('LBG',), ('CDG',), ('ORY',)])

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


    async def test_get_flights_info_success(self):
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"flights": ["Flight1", "Flight2"]}
        
        with patch('httpx.AsyncClient.get', new=mock_response):
            flights_info = await get_flights_info("JFK", "LAX", "2024-01-01", "2024-01-05")
            self.assertEqual(flights_info, {"flights": ["Flight1", "Flight2"]})

    async def test_generate_photo_for_html(self):
        mock_response = AsyncMock()
        mock_response.data = [{"url": "http://example.com/photo.jpg"}]
        with patch('client.images.generate', return_value=mock_response):
            image_url = await generate_photo_for_html("Paris")
            self.assertEqual(image_url, "http://example.com/photo.jpg")

    async def test_get_trip_suggestions(self):
        mock_response = AsyncMock()
        mock_response.choices[0].message.content = "Trip plan content"
        with patch('client.chat.completions.create', return_value=mock_response):
            trip_suggestions = await get_trip_suggestions(AsyncMock(), "Sample prompt")
            self.assertEqual(trip_suggestions, "Trip plan content")

    async def test_get_top_hotels(self):
        mock_response = AsyncMock()
        mock_response.choices[0].message.content = "Top hotels content"
        with patch('client.chat.completions.create', return_value=mock_response):
            top_hotels = await get_top_hotels(AsyncMock(), [{"name": "Hotel1"}])
            self.assertEqual(top_hotels, "Top hotels content")

    async def test_generate_general_activities(self):
        mock_response = AsyncMock()
        mock_response.choices[0].message.content = "General activities content"
        with patch('client.chat.completions.create', return_value=mock_response):
            activities = await generate_genral_activities(AsyncMock(), {"A to B": 10}, 2)
            self.assertEqual(activities, "General activities content")

if __name__ == "__main__":
    unittest.main()
