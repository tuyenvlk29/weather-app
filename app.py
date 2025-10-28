import requests
from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# API của Open-Meteo hoặc bạn có thể thay thế bằng API khác
def get_weather_data(city_name):
    # Thay đổi latitude và longitude theo tỉnh thành
    location_map = {
        "Hà Nội": {"latitude": 21.0285, "longitude": 105.8542},
        "Hồ Chí Minh": {"latitude": 10.8231, "longitude": 106.6297},
        "Đà Nẵng": {"latitude": 16.0471, "longitude": 108.2068},
        # Bạn có thể thêm các tỉnh thành khác vào đây
    }

    location = location_map.get(city_name)

    if location:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={location['latitude']}&longitude={location['longitude']}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
        response = requests.get(url)
        data = response.json()
        return data
    else:
        return None

@app.route("/", methods=["GET", "POST"])
def home():
    cities = ["Hà Nội", "Hồ Chí Minh", "Đà Nẵng"]  # Thêm các tỉnh thành khác nếu cần
    weather_data = None

    if request.method == "POST":
        city = request.form["city"]
        weather_data = get_weather_data(city)

        if weather_data:
            # Xử lý dữ liệu để hiển thị
            current_weather = weather_data["current"]
            hourly_weather = weather_data["hourly"]

            # Chuyển dữ liệu vào DataFrame
            df_hourly = pd.DataFrame({
                "Time": hourly_weather["time"],
                "Temperature (°C)": hourly_weather["temperature_2m"],
                "Humidity (%)": hourly_weather["relative_humidity_2m"],
                "Wind Speed (m/s)": hourly_weather["wind_speed_10m"]
            })

            # Lưu vào file CSV (tuỳ chọn)
            df_hourly.to_csv(f"{city}_weather.csv", index=False)

            return render_template("index.html", cities=cities, weather_data=current_weather, df_hourly=df_hourly)

    return render_template("index.html", cities=cities, weather_data=weather_data, df_hourly=None)

if __name__ == "__main__":
    app.run(debug=True)
