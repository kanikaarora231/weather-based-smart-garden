import requests
import numpy as np
import matplotlib.pyplot as plt
import time

# Constants
SOIL_MOISTURE_THRESHOLD = 30  # Threshold for watering (in percentage)
WATERING_AMOUNT = 20           # Amount of water to add (in percentage)
DAYS = 5                       # Number of days to simulate

# Function to fetch weather data
def fetch_weather_data(api_key, location):
    url = f"http://api.open-meteo.com/v1/forecast?latitude={location[0]}&longitude={location[1]}&daily=precipitation_sum&timezone=auto"
    response = requests.get(url)
    data = response.json()
    return data['daily']['precipitation_sum']

# PID Controller for soil moisture
class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.prev_error = 0
        self.integral = 0

    def compute(self, setpoint, measured_value):
        error = setpoint - measured_value
        self.integral += error
        derivative = error - self.prev_error
        self.prev_error = error
        return self.Kp * error + self.Ki * self.integral + self.Kd * derivative

# Simulate soil moisture over time
def simulate_garden(api_key, location):
    precipitation = fetch_weather_data(api_key, location)
    soil_moisture = 50  # Initial soil moisture percentage
    moisture_history = []

    pid = PIDController(Kp=1.0, Ki=0.1, Kd=0.05)

    for day in range(DAYS):
        # Update soil moisture based on precipitation
        soil_moisture += precipitation[day] - WATERING_AMOUNT if soil_moisture > SOIL_MOISTURE_THRESHOLD else 0
        moisture_history.append(soil_moisture)

        # Check if watering is needed
        if soil_moisture < SOIL_MOISTURE_THRESHOLD:
            watering = pid.compute(SOIL_MOISTURE_THRESHOLD, soil_moisture)
            soil_moisture += watering
            print(f"Day {day + 1}: Watering needed. Added {watering:.2f}% water.")

        # Simulate evaporation (decrease moisture)
        soil_moisture -= 5  # Simulate daily evaporation
        soil_moisture = max(0, soil_moisture)  # Ensure moisture doesn't go below 0

    return moisture_history

# Plotting the soil moisture curve
def plot_soil_moisture(moisture_history):
    plt.plot(moisture_history, marker='o')
    plt.title('Soil Moisture Over Time')
    plt.xlabel('Days')
    plt.ylabel('Soil Moisture (%)')
    plt.ylim(0, 100)
    plt.grid()
    plt.show()

# Main function
if __name__ == "__main__":
    API_KEY = 'your_api_key_here'  # Replace with your Open-Meteo API key
    LOCATION = (35.6895, 139.6917)  # Example: Tokyo, Japan (latitude, longitude)

    moisture_history = simulate_garden(API_KEY, LOCATION)
    plot_soil_moisture(moisture_history)
