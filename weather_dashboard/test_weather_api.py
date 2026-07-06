"""
Unit tests for the Weather Dashboard application
Tests the weather API module and core functionality
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from weather_dashboard.weather_api import WeatherAPI


class TestWeatherAPI(unittest.TestCase):
    """Test cases for WeatherAPI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = WeatherAPI()
    
    def tearDown(self):
        """Clean up after tests."""
        self.api.close()
    
    @patch('weather_dashboard.weather_api.requests.Session.get')
    def test_get_coordinates_success(self, mock_get):
        """Test successful coordinate retrieval for a city."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "name": "New York"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        coords = self.api.get_coordinates("New York")
        
        self.assertIsNotNone(coords)
        self.assertEqual(coords[0], 40.7128)
        self.assertEqual(coords[1], -74.0060)
    
    @patch('weather_dashboard.weather_api.requests.Session.get')
    def test_get_coordinates_not_found(self, mock_get):
        """Test coordinate retrieval when city is not found."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response
        
        coords = self.api.get_coordinates("NonexistentCity12345")
        
        self.assertIsNone(coords)
    
    @patch('weather_dashboard.weather_api.requests.Session.get')
    def test_get_current_weather_success(self, mock_get):
        """Test successful current weather retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 22.5,
                "relative_humidity_2m": 65,
                "apparent_temperature": 21.0,
                "precipitation": 0.0,
                "weather_code": 0,
                "wind_speed_10m": 10.5,
                "wind_direction_10m": 270
            }
        }
        mock_get.return_value = mock_response
        
        weather = self.api.get_current_weather(40.7128, -74.0060)
        
        self.assertIsNotNone(weather)
        self.assertEqual(weather["current"]["temperature_2m"], 22.5)
        self.assertEqual(weather["current"]["weather_code"], 0)
    
    @patch('weather_dashboard.weather_api.requests.Session.get')
    def test_get_forecast_success(self, mock_get):
        """Test successful forecast retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "daily": {
                "time": ["2026-07-06", "2026-07-07", "2026-07-08"],
                "temperature_2m_max": [25.0, 26.0, 24.0],
                "temperature_2m_min": [18.0, 19.0, 17.0],
                "precipitation_sum": [0.0, 2.5, 0.0],
                "weather_code": [0, 61, 0]
            }
        }
        mock_get.return_value = mock_response
        
        forecast = self.api.get_forecast(40.7128, -74.0060, days=3)
        
        self.assertIsNotNone(forecast)
        self.assertEqual(len(forecast["daily"]["time"]), 3)
        self.assertEqual(forecast["daily"]["temperature_2m_max"][0], 25.0)
    
    @patch('weather_dashboard.weather_api.requests.Session.get')
    def test_get_forecast_clamps_days(self, mock_get):
        """Test that forecast days parameter is clamped between 1 and 16."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"daily": {}}
        mock_get.return_value = mock_response
        
        # Test with days > 16
        self.api.get_forecast(40.7128, -74.0060, days=100)
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]['params']['forecast_days'], 16)
        
        # Test with days < 1
        self.api.get_forecast(40.7128, -74.0060, days=-5)
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]['params']['forecast_days'], 1)
    
    def test_interpret_weather_code_clear_sky(self):
        """Test weather code interpretation for clear sky."""
        description = self.api.interpret_weather_code(0)
        self.assertEqual(description, "Clear sky")
    
    def test_interpret_weather_code_rain(self):
        """Test weather code interpretation for rain."""
        description = self.api.interpret_weather_code(61)
        self.assertEqual(description, "Slight rain")
    
    def test_interpret_weather_code_snow(self):
        """Test weather code interpretation for snow."""
        description = self.api.interpret_weather_code(71)
        self.assertEqual(description, "Slight snow")
    
    def test_interpret_weather_code_thunderstorm(self):
        """Test weather code interpretation for thunderstorm."""
        description = self.api.interpret_weather_code(95)
        self.assertEqual(description, "Thunderstorm")
    
    def test_interpret_weather_code_unknown(self):
        """Test weather code interpretation for unknown code."""
        description = self.api.interpret_weather_code(999)
        self.assertEqual(description, "Unknown")
    
    @patch('weather_dashboard.weather_api.requests.Session.get')
    def test_get_weather_by_city_success(self, mock_get):
        """Test complete weather retrieval by city name."""
        # First call for geocoding
        geocoding_response = MagicMock()
        geocoding_response.json.return_value = {
            "results": [{"latitude": 40.7128, "longitude": -74.0060}]
        }
        
        # Second call for weather
        weather_response = MagicMock()
        weather_response.json.return_value = {
            "current": {"temperature_2m": 22.5}
        }
        
        mock_get.side_effect = [geocoding_response, weather_response]
        
        weather = self.api.get_weather_by_city("New York")
        
        self.assertIsNotNone(weather)
        self.assertEqual(weather["city"], "New York")
        self.assertEqual(weather["coordinates"]["latitude"], 40.7128)
    
    @patch('weather_dashboard.weather_api.requests.Session.get')
    def test_get_weather_by_city_not_found(self, mock_get):
        """Test weather retrieval when city is not found."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response
        
        weather = self.api.get_weather_by_city("NonexistentCity12345")
        
        self.assertIsNone(weather)


class TestWeatherCodeInterpretation(unittest.TestCase):
    """Test cases for WMO weather code interpretation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = WeatherAPI()
    
    def test_all_clear_codes(self):
        """Test clear sky weather codes."""
        clear_codes = [0, 1, 2, 3]
        for code in clear_codes:
            result = self.api.interpret_weather_code(code)
            self.assertNotEqual(result, "Unknown")
    
    def test_all_precipitation_codes(self):
        """Test precipitation weather codes."""
        precip_codes = [51, 53, 55, 61, 63, 65, 80, 81, 82]
        for code in precip_codes:
            result = self.api.interpret_weather_code(code)
            self.assertIn("rain", result.lower())
    
    def test_all_snow_codes(self):
        """Test snow weather codes."""
        snow_codes = [71, 73, 75, 77, 85, 86]
        for code in snow_codes:
            result = self.api.interpret_weather_code(code)
            self.assertIn("snow", result.lower())


class TestAPIErrorHandling(unittest.TestCase):
    """Test error handling in WeatherAPI."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = WeatherAPI()
    
    @patch('weather_dashboard.weather_api.requests.Session.get')
    def test_get_coordinates_network_error(self, mock_get):
        """Test handling of network errors during geocoding."""
        mock_get.side_effect = Exception("Network error")
        
        coords = self.api.get_coordinates("New York")
        
        self.assertIsNone(coords)
    
    @patch('weather_dashboard.weather_api.requests.Session.get')
    def test_get_current_weather_network_error(self, mock_get):
        """Test handling of network errors during weather fetch."""
        mock_get.side_effect = Exception("Network error")
        
        weather = self.api.get_current_weather(40.7128, -74.0060)
        
        self.assertIsNone(weather)
    
    @patch('weather_dashboard.weather_api.requests.Session.get')
    def test_get_forecast_network_error(self, mock_get):
        """Test handling of network errors during forecast fetch."""
        mock_get.side_effect = Exception("Network error")
        
        forecast = self.api.get_forecast(40.7128, -74.0060)
        
        self.assertIsNone(forecast)


if __name__ == "__main__":
    unittest.main()
