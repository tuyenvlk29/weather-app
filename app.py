import requests
import pandas as pd

# API endpoint và thông số cho vị trí
url = "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"

# Gửi yêu cầu GET đến API
response = requests.get(url)
data = response.json()

# Lấy dữ liệu hiện tại
current_data = {
    'Current Time': data['current']['time'],
    'Temperature_2m (°C)': data['current']['temperature_2m'],
    'Wind_Speed_10m (m/s)': data['current']['wind_speed_10m']
}

# Lấy dữ liệu theo giờ
hourly_data = {
    'Hourly Time': data['hourly']['time'],
    'Temperature_2m (°C)': data['hourly']['temperature_2m'],
    'Relative_Humidity_2m (%)': data['hourly']['relative_humidity_2m'],
    'Wind_Speed_10m (m/s)': data['hourly']['wind_speed_10m']
}

# Chuyển dữ liệu vào DataFrame
df_current = pd.DataFrame([current_data])
df_hourly = pd.DataFrame(hourly_data)

# Lưu dữ liệu vào file CSV
df_current.to_csv('current_weather.csv', index=False)
df_hourly.to_csv('hourly_weather.csv', index=False)

print("Weather data saved to current_weather.csv and hourly_weather.csv")
