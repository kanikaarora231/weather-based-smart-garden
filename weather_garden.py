import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLabel, QTabWidget, QHBoxLayout, QLineEdit, QPushButton
)
from PyQt5.QtGui import QPixmap, QFont, QPalette, QBrush
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime

# --------------- Weather Data Fetcher ---------------
def get_coordinates(city_name):
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "results" in data and data["results"]:
                lat = data["results"][0]["latitude"]
                lon = data["results"][0]["longitude"]
                return lat, lon
    except Exception as e:
        print("Geocoding error:", e)
    return None, None

def get_weather_data(lat=28.61, lon=77.20):  # Default: Delhi
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# --------------- Chart Canvas Class -----------------
class ChartCanvas(FigureCanvas):
    def __init__(self, chart_type, weather_data=None):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        super().__init__(self.fig)
        self.chart_type = chart_type
        self.weather_data = weather_data
        self.draw_chart()

    def draw_chart(self):
        ax = self.fig.add_subplot(111)
        ax.clear()

        if not self.weather_data:
            ax.text(0.5, 0.5, "No weather data available", ha='center', va='center')
            self.draw()
            return

        days = [datetime.strptime(d, '%Y-%m-%d').strftime('%a') for d in self.weather_data['daily']['time']]
        temp_max = self.weather_data['daily']['temperature_2m_max']
        temp_min = self.weather_data['daily']['temperature_2m_min']
        rainfall = self.weather_data['daily']['precipitation_sum']

        if self.chart_type == 'line':
            ax.plot(days, temp_max, marker='o', color='red', label='Max Temp')
            ax.plot(days, temp_min, marker='o', color='blue', label='Min Temp')
            ax.set_title("Max and Min Temperature Over Days")
            ax.set_ylabel("Temperature (°C)")
            ax.legend()

        elif self.chart_type == 'bar':
            ax.bar(days, rainfall, color='skyblue')
            ax.set_title("Rainfall Forecast")
            ax.set_ylabel("Rainfall (mm)")

        elif self.chart_type == 'area':
            ax.fill_between(days, temp_max, color='lightcoral', alpha=0.6)
            ax.set_title("Area Chart - Max Temperature")
            ax.set_ylabel("Temp (°C)")

        elif self.chart_type == 'pie':
            sunny = sum(1 for t in temp_max if t > 30)
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

        self.draw()

# --------------- Main App Window ---------------------
class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌱 Smart Garden Weather Simulator")
        self.setGeometry(100, 100, 950, 720)

        self.weather_data = get_weather_data()
        self.initUI()

    def initUI(self):
        self.main_widget = QWidget()
        self.layout = QVBoxLayout()

        # Header with Title and City Input
        header_layout = QHBoxLayout()
        self.title = QLabel("🌤 Weather-Based Smart Garden")
        self.title.setFont(QFont("Arial", 22, QFont.Bold))
        self.title.setAlignment(Qt.AlignLeft)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter city name (e.g. Delhi)")
        self.city_input.setFixedWidth(200)

        load_button = QPushButton("Load Weather")
        load_button.clicked.connect(self.update_city_weather)

        header_layout.addWidget(self.title)
        header_layout.addStretch()
        header_layout.addWidget(self.city_input)
        header_layout.addWidget(load_button)

        self.layout.addLayout(header_layout)

        # Weather Icon
        weather_icon = QLabel()
        icon_path = "sun.png"
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio)
            weather_icon.setPixmap(pixmap)
        else:
            weather_icon.setText("🌞")
        self.layout.addWidget(weather_icon)

        # Tabs for Charts
        self.tabs = QTabWidget()
        self.load_charts(self.weather_data)
        self.layout.addWidget(self.tabs)

        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

    def load_charts(self, weather_data):
        self.tabs.clear()
        self.tabs.addTab(ChartCanvas('line', weather_data), "Temperature Line")
        self.tabs.addTab(ChartCanvas('bar', weather_data), "Rainfall Bar")
        self.tabs.addTab(ChartCanvas('area', weather_data), "Area Temp")
        self.tabs.addTab(ChartCanvas('pie', weather_data), "Pie Weather")

    def update_city_weather(self):
        city = self.city_input.text()
        if city:
            lat, lon = get_coordinates(city)
            if lat and lon:
                new_data = get_weather_data(lat, lon)
                if new_data:
                    self.weather_data = new_data
                    self.load_charts(new_data)
                else:
                    self.title.setText(f"⚠️ Weather data not found for {city}")
            else:
                self.title.setText(f"⚠️ Couldn't locate city: {city}")
        else:
            self.title.setText("🌤 Weather-Based Smart Garden")

# --------------- Run the Application -----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())
