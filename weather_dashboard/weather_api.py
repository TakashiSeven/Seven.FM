"""
Weather API module for fetching weather data from Open-Meteo API
Open-Meteo is a free weather API that doesn't require authentication
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional, Tuple


class WeatherAPI:
    """
    A class to interact with the Open-Meteo weather API.
    Provides methods to fetch current weather and forecast data.
    """
    
    BASE_URL = "https://api.open-meteo.com/v1"
    
    def __init__(self):
        """Initialize the WeatherAPI client."""
        self.session = requests.Session()
    
    def get_coordinates(self, city: str, country: Optional[str] = None) -> Optional[Tuple[float, float]]:
        """
        Get latitude and longitude for a city using Geocoding API.
        
        Args:
            city: City name
            country: Optional country name for disambiguation
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            geocoding_url = f"{self.BASE_URL}/geocoding"
            params = {
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            }
            
            if country:
                params["country"] = country
            
            response = self.session.get(geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("results"):
                result = data["results"][0]
                return (result["latitude"], result["longitude"])
            
            return None
        except Exception as e:
            print(f"Error getting coordinates: {e}")
            return None
    
    def get_current_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Fetch current weather data for given coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with weather data or None if request fails
        """
        try:
            weather_url = f"{self.BASE_URL}/current"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
                "timezone": "auto"
            }
            
            response = self.session.get(weather_url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error fetching current weather: {e}")
            return None
    
    def get_forecast(self, latitude: float, longitude: float, days: int = 7) -> Optional[Dict]:
        """
        Fetch weather forecast data for given coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            days: Number of days to forecast (1-16)
            
        Returns:
            Dictionary with forecast data or None if request fails
        """
        try:
            days = min(max(days, 1), 16)  # Clamp between 1 and 16
            
            forecast_url = f"{self.BASE_URL}/forecast"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
                "timezone": "auto",
                "forecast_days": days
            }
            
            response = self.session.get(forecast_url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return None
    
    def get_weather_by_city(self, city: str, country: Optional[str] = None) -> Optional[Dict]:
        """
        Get complete weather information for a city.
        
        Args:
            city: City name
            country: Optional country name
            
        Returns:
            Dictionary with current weather and location info or None if request fails
        """
        coordinates = self.get_coordinates(city, country)
        if not coordinates:
            return None
        
        latitude, longitude = coordinates
        current_weather = self.get_current_weather(latitude, longitude)
        
        if current_weather:
            current_weather["city"] = city
            current_weather["coordinates"] = {"latitude": latitude, "longitude": longitude}
            return current_weather
        
        return None
    
    def interpret_weather_code(self, code: int) -> str:
        """
        Interpret WMO Weather Code to human-readable description.
        
        Args:
            code: WMO weather code
            
        Returns:
            String description of the weather
        """
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        
        return weather_codes.get(code, "Unknown")
    
    def close(self):
        """Close the session."""
        self.session.close()
