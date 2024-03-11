import unittest
import httpx
from unittest.mock import MagicMock, patch
from unittest.mock import AsyncMock
import sqlite3
import re

from main import (
    calculate_distances,
    get_location_details,
    get_iata_code,
    get_iata_codes_and_airports,
    format_trip_plan,
    extract_hotel_data,
    format_hotels_for_prompt,
)


class TestFunctions(unittest.IsolatedAsyncioTestCase):
    async def test_calculate_distances(self):
        activities = [
            {"name": "A", "location": (0, 0)},
            {"name": "B", "location": (1, 1)},
            {"name": "C", "location": (2, 2)},
        ]
        result = await calculate_distances(activities)
        self.assertEqual(len(result), 3)

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

    def test_get_iata_code(self):
        conn = sqlite3.connect("IATA_Codes.db")
        result = get_iata_code("Paris")
        self.assertEqual(result[0][0], "CDG")  # Assuming CDG is the IATA code for Paris

    def test_get_iata_codes_and_airports(self):
        conn = sqlite3.connect("IATA_Codes.db")
        result = get_iata_codes_and_airports("Tel Aviv")
        self.assertEqual(result[0]["IATA code"], "TLV")  # Assuming TLV is the IATA code for Tel Aviv

    def test_format_trip_plan(self):
        plan_text = "### Header **Bold Text** [link](http://example.com)"
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
        self.assertIn("Hotel A", formatted_text)


if __name__ == "__main__":
    unittest.main()
