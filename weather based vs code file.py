import matplotlib.pyplot as plt
import numpy as np

# Simulated 5-day weather forecast (rainfall in mm/day)
forecast_rainfall = [0.0, 2.0, 0.0, 5.0, 0.0]  # Replace with real API later

# PID Controller Class
class PIDController:
    def __init__(self, Kp, Ki, Kd, setpoint):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.integral = 0
        self.previous_error = 0

    def compute(self, current_value):
        error = self.setpoint - current_value
        self.integral += error
        derivative = error - self.previous_error
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        self.previous_error = error
        return max(0, output)  # No negative watering

# Simulate soil moisture using forecast and PID
def simulate_soil_moisture(forecast_rainfall, initial_moisture=30.0, target_moisture=50.0):
    pid = PIDController(Kp=0.8, Ki=0.05, Kd=0.1, setpoint=target_moisture)
    moisture_levels = [initial_moisture]
    watering_schedule = []

    for day in range(5):
        current_moisture = moisture_levels[-1]
        rainfall = forecast_rainfall[day]
        watering = pid.compute(current_moisture)
        watering_schedule.append(round(watering, 2))

        # Simulate new soil moisture with 15% natural loss
        new_moisture = current_moisture * 0.85 + rainfall + watering
        moisture_levels.append(min(new_moisture, 100.0))  # Max 100%

    return moisture_levels, watering_schedule

# Plotting function
def plot_moisture(moisture_levels):
    days = list(range(len(moisture_levels)))
    plt.figure(figsize=(10, 5))
    plt.plot(days, moisture_levels, marker='o', linestyle='-', color='green', label='Soil Moisture (%)')
    plt.axhline(y=50, color='blue', linestyle='--', label='Target Moisture')
    plt.title("Soil Moisture Simulation Over 5 Days")
    plt.xlabel("Day")
    plt.ylabel("Soil Moisture (%)")
    plt.xticks(days)
    plt.ylim(0, 100)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# Main function
if __name__ == "__main__":
    moisture, watering = simulate_soil_moisture(forecast_rainfall)
    print("Forecast Rainfall (mm):", forecast_rainfall)
    print("Watering Schedule (units):", watering)
    print("Soil Moisture (%):", [round(m, 2) for m in moisture])
    plot_moisture(moisture)
