# ... (keep all previous import statements)
import numpy as np  # Add this import at the top if not present

# Add a new chart type: 'soil' in ChartCanvas class
class ChartCanvas(FigureCanvas):
    def __init__(self, chart_type, weather_data=None, icon_path=None):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        super().__init__(self.fig)
        self.chart_type = chart_type
        self.weather_data = weather_data
        self.icon_path = icon_path
        self.draw_chart()

    def draw_chart(self):
        ax = self.fig.add_subplot(111)
        ax.clear()

        if not self.weather_data:
            ax.text(0.5, 0.5, "No weather data available", ha='center', va='center')
            self.draw()
            return

        days = [datetime.strptime(d, '%Y-%m-%d').strftime('%a') for d in self.weather_data['daily']['time']]
        temperature = self.weather_data['daily']['temperature_2m_max']
        rainfall = self.weather_data['daily']['precipitation_sum']

        if self.chart_type == 'line':
            ax.plot(days, temperature, marker='o', color='green', label="Temperature")
            diffs = np.diff(temperature)
            signs = ['↑' if diff > 0 else '↓' if diff < 0 else '-' for diff in diffs]
            for i, sign in enumerate(signs):
                ax.text(i+0.5, (temperature[i]+temperature[i+1])/2, sign, fontsize=12, ha='center')
            ax.set_title("Temperature Rise/Fall")
            ax.set_ylabel("Temp (°C)")
            ax.legend()

        elif self.chart_type == 'bar':
            ax.bar(days, rainfall, color='skyblue')
            ax.set_title("Rainfall Forecast")
            ax.set_ylabel("Rainfall (mm)")

        elif self.chart_type == 'area':
            ax.fill_between(days, temperature, color='lightcoral', alpha=0.6)
            ax.set_title("Area Chart - Temperature")
            ax.set_ylabel("Temp (°C)")

        elif self.chart_type == 'pie':
            sunny = sum(1 for t in temperature if t > 30)
            rainy = sum(1 for r in rainfall if r > 5)
            cloudy = max(5 - sunny - rainy, 0)
            values = [sunny, cloudy, rainy]
            values = [v if v >= 0 else 0 for v in values]

            if sum(values) == 0:
                ax.text(0.5, 0.5, "No weather data to plot pie chart", ha='center', va='center')
            else:
                ax.pie(values, labels=['Sunny', 'Cloudy', 'Rainy'],
                       autopct='%1.1f%%', colors=['orange', 'gray', 'blue'])
                ax.set_title("Weather Distribution")

        elif self.chart_type == 'soil':
            # Simulated soil moisture using cumulative rainfall
            soil_moisture = np.cumsum(rainfall)
            ax.plot(days, soil_moisture, marker='s', color='brown')
            ax.set_title("Simulated Soil Moisture")
            ax.set_ylabel("Soil Moisture Index")

        # Show weather image in charts (except pie)
        if self.icon_path and os.path.exists(self.icon_path) and self.chart_type != 'pie':
            try:
                image = mpimg.imread(self.icon_path)
                ax.imshow(image, aspect='auto', extent=[5.5, 6.5, max(ax.get_ylim())*0.8, max(ax.get_ylim())], alpha=0.3)
            except Exception as e:
                print("Image overlay error:", e)

        self.draw()
