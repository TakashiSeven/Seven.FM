"""
Weather Dashboard UI module
Provides a GUI for displaying weather information using tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
from weather_api import WeatherAPI


class WeatherDashboard:
    """Main weather dashboard UI class."""
    
    def __init__(self, root):
        """
        Initialize the weather dashboard.
        
        Args:
            root: tkinter root window
        """
        self.root = root
        self.root.title("Weather Dashboard")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.weather_api = WeatherAPI()
        self.current_location = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Weather Dashboard", 
                               font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="City:").grid(row=0, column=0, padx=5)
        self.city_entry = ttk.Entry(search_frame, width=30)
        self.city_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        self.city_entry.bind("<Return>", lambda e: self.search_weather())
        
        self.search_button = ttk.Button(search_frame, text="Search", 
                                       command=self.search_weather)
        self.search_button.grid(row=0, column=2, padx=5)
        
        # Separator
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Current weather frame
        current_frame = ttk.LabelFrame(main_frame, text="Current Weather", padding="10")
        current_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        current_frame.columnconfigure(1, weight=1)
        
        # Location display
        self.location_label = ttk.Label(current_frame, text="No location selected", 
                                       font=("Arial", 14, "bold"))
        self.location_label.grid(row=0, column=0, columnspan=2, pady=5)
        
        # Weather details
        self.temp_label = ttk.Label(current_frame, text="Temperature: --°C", 
                                   font=("Arial", 12))
        self.temp_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        
        self.feels_like_label = ttk.Label(current_frame, text="Feels Like: --°C", 
                                         font=("Arial", 12))
        self.feels_like_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=3)
        
        self.humidity_label = ttk.Label(current_frame, text="Humidity: --%", 
                                       font=("Arial", 12))
        self.humidity_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        
        self.wind_label = ttk.Label(current_frame, text="Wind Speed: -- km/h", 
                                   font=("Arial", 12))
        self.wind_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=3)
        
        self.weather_desc_label = ttk.Label(current_frame, text="Condition: --", 
                                           font=("Arial", 12))
        self.weather_desc_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, 
                                    padx=5, pady=3)
        
        self.precipitation_label = ttk.Label(current_frame, text="Precipitation: -- mm", 
                                            font=("Arial", 12))
        self.precipitation_label.grid(row=4, column=0, sticky=tk.W, padx=5, pady=3)
        
        self.updated_label = ttk.Label(current_frame, text="Last updated: --", 
                                      font=("Arial", 10, "italic"))
        self.updated_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, 
                               padx=5, pady=5)
        
        # Forecast frame
        forecast_frame = ttk.LabelFrame(main_frame, text="7-Day Forecast", padding="10")
        forecast_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                           pady=10)
        forecast_frame.columnconfigure(0, weight=1)
        forecast_frame.rowconfigure(0, weight=1)
        
        # Forecast canvas with scrollbar
        canvas = tk.Canvas(forecast_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(forecast_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)
        
        self.forecast_container = scrollable_frame
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Loading indicator
        self.loading_label = ttk.Label(main_frame, text="", font=("Arial", 10))
        self.loading_label.grid(row=5, column=0, columnspan=3, pady=5)
    
    def search_weather(self):
        """Search for weather data for the entered city."""
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name")
            return
        
        self.search_button.config(state="disabled")
        self.loading_label.config(text="Loading weather data...")
        
        # Run search in separate thread to avoid freezing UI
        thread = threading.Thread(target=self._fetch_weather, args=(city,))
        thread.daemon = True
        thread.start()
    
    def _fetch_weather(self, city):
        """Fetch weather data in a background thread."""
        try:
            weather_data = self.weather_api.get_weather_by_city(city)
            
            if not weather_data:
                self.root.after(0, lambda: messagebox.showerror("Error", 
                                f"Could not find weather data for {city}"))
                self.root.after(0, lambda: self.search_button.config(state="normal"))
                return
            
            # Get forecast data
            coords = weather_data.get("coordinates", {})
            forecast_data = self.weather_api.get_forecast(
                coords.get("latitude"), 
                coords.get("longitude")
            )
            
            # Update UI in main thread
            self.root.after(0, self._update_ui, weather_data, forecast_data)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", 
                            f"An error occurred: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.search_button.config(state="normal"))
            self.root.after(0, lambda: self.loading_label.config(text=""))
    
    def _update_ui(self, weather_data, forecast_data):
        """Update UI with fetched weather data."""
        current = weather_data.get("current", {})
        
        # Update location
        city = weather_data.get("city", "Unknown")
        self.location_label.config(text=city)
        
        # Update current weather
        temp = current.get("temperature_2m", "N/A")
        self.temp_label.config(text=f"Temperature: {temp}°C")
        
        feels_like = current.get("apparent_temperature", "N/A")
        self.feels_like_label.config(text=f"Feels Like: {feels_like}°C")
        
        humidity = current.get("relative_humidity_2m", "N/A")
        self.humidity_label.config(text=f"Humidity: {humidity}%")
        
        wind = current.get("wind_speed_10m", "N/A")
        self.wind_label.config(text=f"Wind Speed: {wind} km/h")
        
        weather_code = current.get("weather_code", 0)
        weather_desc = self.weather_api.interpret_weather_code(weather_code)
        self.weather_desc_label.config(text=f"Condition: {weather_desc}")
        
        precipitation = current.get("precipitation", 0)
        self.precipitation_label.config(text=f"Precipitation: {precipitation} mm")
        
        # Update timestamp
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_label.config(text=f"Last updated: {now}")
        
        # Update forecast
        self._update_forecast(forecast_data)
    
    def _update_forecast(self, forecast_data):
        """Update the forecast display."""
        # Clear previous forecast
        for widget in self.forecast_container.winfo_children():
            widget.destroy()
        
        if not forecast_data:
            return
        
        daily = forecast_data.get("daily", {})
        dates = daily.get("time", [])
        temps_max = daily.get("temperature_2m_max", [])
        temps_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        codes = daily.get("weather_code", [])
        
        for i in range(min(7, len(dates))):
            day_frame = ttk.LabelFrame(self.forecast_container, 
                                      text=dates[i], padding="5")
            day_frame.pack(side=tk.LEFT, padx=5, fill=tk.BOTH)
            
            ttk.Label(day_frame, text=f"High: {temps_max[i]}°C", 
                     font=("Arial", 10)).pack()
            ttk.Label(day_frame, text=f"Low: {temps_min[i]}°C", 
                     font=("Arial", 10)).pack()
            ttk.Label(day_frame, text=f"Precip: {precip[i]} mm", 
                     font=("Arial", 10)).pack()
            
            weather_desc = self.weather_api.interpret_weather_code(codes[i])
            ttk.Label(day_frame, text=weather_desc, font=("Arial", 9, "italic")).pack()
    
    def on_closing(self):
        """Handle window closing."""
        self.weather_api.close()
        self.root.destroy()


def main():
    """Main entry point for the weather dashboard application."""
    root = tk.Tk()
    dashboard = WeatherDashboard(root)
    root.protocol("WM_DELETE_WINDOW", dashboard.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
