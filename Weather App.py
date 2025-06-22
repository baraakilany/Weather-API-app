#Baraa Alkilany
#Github: baraakilany
import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette


class WeatherApp(QWidget):
    """
    A PyQt5 desktop application for fetching and displaying weather
    information using the OpenWeatherMap API, with a distinct digital aesthetic.
    """
    def __init__(self):
        super().__init__()
        # API key
        # in a production app, I'd load this securely from an environment variable).
        self.api_key = "75e3f3ca59e8d2761c35aa6e43fc9432"

        self.city_label = QLabel("Enter City Name:", self)
        self.city_input = QLineEdit(self)
        self.find_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)

        # Temperature buttons
        self.celsius_button = QPushButton("°C", self)
        self.fahrenheit_button = QPushButton("°F", self)
        self.is_celsius = True # Default unit

        # Stores the most recent weather data for unit conversion without re-fetching
        self._current_weather_data = None

        self.initUI()

    def initUI(self):
        """
        UI initialization, setting up layouts,
        widgets, and styling.
        """
        self.setWindowTitle("Weather Forecast")
        self.setMinimumSize(480, 680)

        # Main vertical layout for overall structure
        vbox = QVBoxLayout()
        vbox.setSpacing(25) #spacing for a cleaner look

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_label.setObjectName("city_label")
        vbox.addWidget(self.city_label)

        # Horizontal layout to center the city input field
        city_input_layout = QHBoxLayout()
        city_input_layout.addStretch(1)
        city_input_layout.addWidget(self.city_input)
        city_input_layout.addStretch(1)
        vbox.addLayout(city_input_layout)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.city_input.setPlaceholderText("e.g., London, Paris, Tokyo")
        self.city_input.setObjectName("city_input")


        # Horizontal layout for centered unit toggle buttons
        unit_toggle_layout = QHBoxLayout()
        unit_toggle_layout.addStretch(1)
        unit_toggle_layout.addWidget(self.celsius_button)
        unit_toggle_layout.addWidget(self.fahrenheit_button)
        unit_toggle_layout.addStretch(1)
        vbox.addLayout(unit_toggle_layout)

        # Horizontal layout to center the "Get Weather" button
        find_weather_button_layout = QHBoxLayout()
        find_weather_button_layout.addStretch(1)
        find_weather_button_layout.addWidget(self.find_weather_button)
        find_weather_button_layout.addStretch(1)
        vbox.addLayout(find_weather_button_layout)
        self.find_weather_button.setObjectName("find_weather_button")

        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setObjectName("emoji_label")

        # setting emoji font for consistent cross-platform rendering
        emoji_font = QFont()
        emoji_font.setFamily("Segoe UI Emoji")
        if emoji_font.family() != "Segoe UI Emoji":
            emoji_font.setFamily("Apple Color Emoji")
        if emoji_font.family() not in ["Segoe UI Emoji", "Apple Color Emoji"]:
            emoji_font.setFamily("Noto Color Emoji")
        emoji_font.setPointSize(90) # Slightly larger emoji
        self.emoji_label.setFont(emoji_font)
        vbox.addWidget(self.emoji_label)

        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.temperature_label.setWordWrap(True) # Allows temperature details to wrap if too long
        self.temperature_label.setObjectName("temperature_label")
        vbox.addWidget(self.temperature_label)

        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setObjectName("description_label")
        vbox.addWidget(self.description_label)


        vbox.addStretch(1)

        self.setLayout(vbox)

        # Connecting user to app
        self.find_weather_button.clicked.connect(self.get_weather)
        self.city_input.returnPressed.connect(self.get_weather) # Enable search on Enter key press
        self.celsius_button.clicked.connect(lambda: self.set_unit(True))
        self.fahrenheit_button.clicked.connect(lambda: self.set_unit(False))

        self.update_unit_button_style() # Set initial styling for unit buttons
        self.setStyleSheet(self.get_stylesheet())

    def get_stylesheet(self):
        return """
            QWidget {
                background-color: #1A1A2E;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                color: #E0E0E0;
            }

            QLabel#city_label {
                font-size: 38px;
                font-style: normal;
                font-weight: bold;
                color: #00FFFF;
                margin-bottom: 20px;
                text-shadow: 0 0 8px rgba(0, 255, 255, 0.5);
            }

            QLineEdit#city_input {
                font-size: 30px;
                padding: 15px 25px;
                border: 2px solid #00FFFF;
                border-radius: 8px;
                background-color: #0F0F1A;
                color: #00FF00;
                max-width: 480px;
                box-shadow: 0px 0px 15px rgba(0, 255, 255, 0.3);
                selection-background-color: #008080;
                selection-color: white;
            }
            QLineEdit#city_input:focus {
                border: 2px solid #00FFFF;
                outline: none;
                box-shadow: 0px 0px 20px rgba(0, 255, 255, 0.7);
            }

            QPushButton {
                font-size: 28px;
                font-weight: bold;
                padding: 16px 35px;
                border-radius: 10px;
                border: 2px solid #00FFFF;
                color: #00FFFF;
                background-color: #1A1A2E;
                min-width: 220px;
                max-width: 320px;
                box-shadow: 0px 0px 10px rgba(0, 255, 255, 0.4);
                transition: background-color 0.2s ease, transform 0.2s ease, color 0.2s ease;
            }
            QPushButton:hover {
                background-color: #00FFFF;
                color: #1A1A2E;
                transform: translateY(-3px);
                box-shadow: 0px 0px 20px rgba(0, 255, 255, 0.8);
            }
            QPushButton:pressed {
                background-color: #00BFFF;
                transform: translateY(0px);
                box-shadow: 0px 0px 5px rgba(0, 255, 255, 0.5);
            }
            QPushButton:disabled {
                background-color: #33334F;
                color: #777788;
                border: 2px solid #55556F;
                box-shadow: none;
            }

            QPushButton#celsius_button, QPushButton#fahrenheit_button {
                font-size: 20px;
                font-weight: normal;
                padding: 12px 20px;
                border-radius: 8px;
                border: 2px solid #00FFFF;
                background-color: #1A1A2E;
                color: #00FFFF;
                min-width: 75px;
                max-width: 95px;
                margin: 0 8px;
                box-shadow: none;
            }
            QPushButton#celsius_button.active, QPushButton#fahrenheit_button.active {
                background-color: #00FF00;
                color: #1A1A2E;
                font-weight: bold;
                box-shadow: 0px 0px 10px rgba(0, 255, 0, 0.6);
                border: 2px solid #00FF00;
            }
            QPushButton#celsius_button:hover:!active, QPushButton#fahrenheit_button:hover:!active {
                background-color: #004040;
                transform: translateY(-1px);
            }
            QPushButton#celsius_button.active:hover, QPushButton#fahrenheit_button.active:hover {
                background-color: #00CC00;
                transform: translateY(-1px);
            }

            QLabel#emoji_label {
                font-size: 120px;
                margin-top: 30px;
                margin-bottom: 15px;
                text-shadow: 0 0 15px rgba(255, 255, 0, 0.7);
            }

            QLabel#temperature_label {
                font-size: 34px;
                font-weight: bold;
                color: #F0F0F0;
                margin-top: 15px;
                margin-bottom: 15px;
                line-height: 1.5;
                text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);
            }

            QLabel#description_label {
                font-size: 36px;
                font-weight: bold;
                color: #00FFFF;
                margin-top: 20px;
                margin-bottom: 30px;
                text-shadow: 0 0 10px rgba(0, 255, 255, 0.6);
            }
        """

    def update_unit_button_style(self):
        self.celsius_button.setProperty("class", "active" if self.is_celsius else "")
        self.fahrenheit_button.setProperty("class", "active" if not self.is_celsius else "")
        self.setStyleSheet(self.get_stylesheet()) # Reapply to trigger style update

    def set_unit(self, is_celsius):
        if self.is_celsius != is_celsius:
            self.is_celsius = is_celsius
            self.update_unit_button_style()
            if self._current_weather_data:
                self.display_weather(self._current_weather_data)

    def get_weather(self):
        """
        Includes visual loading feedback and robust error handling for API and network issues.
        """
        city = self.city_input.text().strip()

        if not city:
            self.display_error("Input Required", "Please enter a city name.")
            return

        # Show loading state in UI
        self.temperature_label.setText("Loading weather data...")
        self.temperature_label.setStyleSheet("font-size: 34px; color: #E0E0E0; font-weight: bold; text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);") # Digital style for loading
        self.emoji_label.setText("⏳")
        self.description_label.setText("Fetching data...")
        QApplication.processEvents() # Force UI update for immediate feedback

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}"

        try:
            response = requests.get(url, timeout=10) # Added a timeout
            response.raise_for_status() # Raises HTTPError for 4xx/5xx responses
            data = response.json()

            if data["cod"] == 200:
                self._current_weather_data = data
                self.display_weather(data)
            else:
                self.display_error("Weather Data Error", f"Could not retrieve weather for '{city}'. Please check the city name.")

        except requests.exceptions.HTTPError as http_err:
            status_code = http_err.response.status_code
            match status_code:
                case 400: self.display_error("Bad Request", "Please check the city name entered. It might be misspelled or invalid.")
                case 401: self.display_error("Unauthorized", "API Key Invalid. Please verify the API key in the code.")
                case 403: self.display_error("Forbidden", "Access Denied by the weather service.")
                case 404: self.display_error("City Not Found", f"City '{city}' not found. Please try a different city.")
                case 500: self.display_error("Server Error", "The weather service is experiencing an internal server error. Please try again later.")
                case 502: self.display_error("Bad Gateway", "Invalid response received from the server.")
                case 503: self.display_error("Service Unavailable", "The weather service is currently down for maintenance.")
                case 504: self.display_error("Gateway Timeout", "The weather server took too long to respond.")
                case _: self.display_error("HTTP Error", f"An unexpected HTTP error occurred: {status_code} - {http_err.response.reason}")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error", "Unable to connect to the internet. Please check your network connection.")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error", "The request to the weather service timed out. Please try again.")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Redirect Error", "Too many redirects. This might indicate an issue with the API endpoint.")
        except requests.exceptions.RequestException as req_error:
            self.display_error("Request Error", f"An unexpected error occurred during the request: {req_error}")
        except Exception as e:
            self.display_error("Application Error", f"An unexpected error occurred: {e}")

    def display_error(self, title, message):
        """
        Presenting the error messages
        """
        self.temperature_label.setText("")
        self.emoji_label.setText("⚠️")
        self.description_label.setText(message)
        self.temperature_label.setStyleSheet("font-size: 34px; color: #FF6347; font-weight: bold; text-shadow: 0 0 8px rgba(255, 99, 71, 0.5);") # Error color

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_() # Blocks execution until closed

    def display_weather(self, data):
        self.temperature_label.setStyleSheet("font-size: 34px; color: #F0F0F0; font-weight: bold; text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);")

        temperature_k = data["main"]["temp"]
        feels_like_k = data["main"]["feels_like"]
        min_temp_k = data["main"]["temp_min"]
        max_temp_k = data["main"]["temp_max"]
        humidity = data["main"]["humidity"]
        weather_id = data["weather"][0]["id"]
        weather_description = ' '.join(word.capitalize() for word in data["weather"][0]["description"].split())

        temp_display_lines = []

        if self.is_celsius:
            temp_display_lines.append(f"Current: {(temperature_k - 273.15):.0f}°C")
            temp_display_lines.append(f"Feels Like: {(feels_like_k - 273.15):.0f}°C")
            temp_display_lines.append(f"Lowest Today: {(min_temp_k - 273.15):.0f}°C")
            temp_display_lines.append(f"Highest Today: {(max_temp_k - 273.15):.0f}°C")
        else: # Fahrenheit conversion
            temp_display_lines.append(f"Current: {((temperature_k - 273.15) * 9/5 + 32):.0f}°F")
            temp_display_lines.append(f"Feels Like: {((feels_like_k - 273.15) * 9/5 + 32):.0f}°F")
            temp_display_lines.append(f"Lowest Today: {((min_temp_k - 273.15) * 9/5 + 32):.0f}°F")
            temp_display_lines.append(f"Highest Today: {((max_temp_k - 273.15) * 9/5 + 32):.0f}°F")

        temp_display_lines.append(f"Humidity: {humidity}%")

        self.temperature_label.setText("\n".join(temp_display_lines))
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description_label.setText(weather_description)

    @staticmethod
    def get_weather_emoji(weather_id):
        """
        Maping OpenWeatherMap's numeric weather IDs to a corresponding emoji
        """
        if 200 <= weather_id <= 232: return "⛈️" # Thunderstorm
        elif 300 <= weather_id <= 321: return "🌦️" # Drizzle
        elif 500 <= weather_id <= 531: return "🌧️"
        elif 600 <= weather_id <= 622: return "❄️"
        elif 701 <= weather_id <= 741: return "🌫️" # fog
        elif weather_id == 762: return "🌋" # Volcanic ash
        elif weather_id == 771: return "💨" # Squall
        elif weather_id == 781: return "🌪️" # Tornado
        elif weather_id == 800: return "☀️"
        elif 801 <= weather_id <= 804: return "☁️"
        else: return "❓" # Unknown weather condition

if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
