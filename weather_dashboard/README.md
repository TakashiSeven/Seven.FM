# Weather Dashboard

A simple weather dashboard application that fetches real-time weather data from the Open-Meteo public API.

## Features

- **Real-time Weather Data**: Displays current weather conditions including temperature, humidity, wind speed, and precipitation
- **Location Search**: Search weather for any city worldwide using geocoding
- **7-Day Forecast**: View a 7-day weather forecast with high/low temperatures and precipitation
- **Weather Interpretation**: Converts WMO weather codes to human-readable descriptions
- **No API Key Required**: Uses the free Open-Meteo API with no authentication needed
- **Responsive UI**: Built with Python's tkinter for a cross-platform GUI

## Requirements

- Python 3.7+
- requests library

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## Usage

1. Launch the application by running `python main.py`
2. Enter a city name in the search box
3. Press "Search" or hit Enter
4. View current weather conditions and the 7-day forecast

## API Used

This dashboard uses the **Open-Meteo API** (https://open-meteo.com/):
- Free weather data API
- No authentication required
- Provides current weather and forecast data
- Includes geocoding for city name lookup

## Architecture

- **weather_api.py**: Core API client for fetching weather data
- **ui.py**: Tkinter-based GUI for the dashboard
- **main.py**: Entry point for the application

## Features Details

### Weather Data Displayed

**Current Weather:**
- Temperature (°C)
- Feels Like temperature
- Humidity (%)
- Wind speed (km/h)
- Weather condition description
- Precipitation (mm)

**Forecast:**
- Daily high/low temperatures
- Daily precipitation
- Weather condition for each day

## Future Enhancements

- [ ] Temperature unit toggle (Celsius/Fahrenheit)
- [ ] Weather alerts and warnings
- [ ] Favorite locations saved to file
- [ ] Weather maps visualization
- [ ] Historical weather data
- [ ] Multiple weather provider support
- [ ] Dark mode theme
- [ ] System tray integration

## License

MIT License
