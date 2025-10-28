import streamlit as st
import requests
import pandas as pd

st.title("🌤 Ứng dụng Mô phỏng Dữ liệu Thời tiết – Open-Meteo")

latitude = st.number_input("Nhập vĩ độ (latitude)", value=52.52, format="%.2f")
longitude = st.number_input("Nhập kinh độ (longitude)", value=13.41, format="%.2f")

if st.button("Lấy dữ liệu"):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&current=temperature_2m,wind_speed_10m"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    response = requests.get(url)
    data = response.json()

    current_data = {
        'Current Time': [data['current']['time']],
        'Temperature_2m (°C)': [data['current']['temperature_2m']],
        'Wind_Speed_10m (m/s)': [data['current']['wind_speed_10m']]
    }
    df_current = pd.DataFrame(current_data)

    hourly_data = {
        'Hourly Time': data['hourly']['time'],
        'Temperature_2m (°C)': data['hourly']['temperature_2m'],
        'Relative_Humidity_2m (%)': data['hourly']['relative_humidity_2m'],
        'Wind_Speed_10m (m/s)': data['hourly']['wind_speed_10m']
    }
    df_hourly = pd.DataFrame(hourly_data)

    st.subheader("📍 Dữ liệu hiện tại")
    st.dataframe(df_current)

    st.subheader("🕒 Dữ liệu theo giờ")
    st.dataframe(df_hourly)

    csv = df_hourly.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Tải dữ liệu theo giờ (.CSV)", data=csv, file_name='hourly_weather.csv')

    st.success("✅ Hoàn tất! Dữ liệu đã được lấy thành công.")
