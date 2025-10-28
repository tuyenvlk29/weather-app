import streamlit as st
import pandas as pd
import requests

# -------------------------------
# Cấu hình trang
# -------------------------------
st.set_page_config(page_title="Mô phỏng Dữ liệu Thời tiết Việt Nam", page_icon="🌦", layout="centered")

st.title("🌦 Mô phỏng Dữ liệu Thời tiết Việt Nam – Thời gian thực")
st.markdown("### Ứng dụng thu thập, mô phỏng và xuất dữ liệu khí tượng phục vụ học tập STEM")

# -------------------------------
# Danh sách tỉnh/thành phố Việt Nam
# -------------------------------
cities = {
    "Hà Nội": (21.0285, 105.8542),
    "Hải Phòng": (20.8648, 106.6835),
    "Đà Nẵng": (16.0678, 108.2208),
    "Huế": (16.4637, 107.5909),
    "TP. Hồ Chí Minh": (10.7769, 106.7009),
    "Cần Thơ": (10.0452, 105.7469),
    "Nha Trang": (12.2388, 109.1967),
    "Đà Lạt": (11.9404, 108.4583),
    "Pleiku": (13.9833, 108.0000),
    "Vinh": (18.6736, 105.6924)
}

# -------------------------------
# Giao diện chọn tỉnh/thành phố
# -------------------------------
selected_city = st.selectbox("🏙️ Chọn tỉnh/thành phố:", list(cities.keys()))
latitude, longitude = cities[selected_city]

# -------------------------------
# Các loại dữ liệu cần lấy
# -------------------------------
st.markdown("#### Chọn loại dữ liệu muốn hiển thị và tải xuống:")
data_options = ["Nhiệt độ (°C)", "Lượng mưa (mm)", "Độ ẩm (%)", "Tốc độ gió (m/s)"]
selected_data = st.multiselect("🧭 Chọn thông số:", data_options, default=data_options)

# -------------------------------
# Gọi API thời tiết mở Open-Meteo
# -------------------------------
if st.button("🌍 Lấy dữ liệu thời tiết"):
    st.info(f"Đang tải dữ liệu thời tiết tại **{selected_city}** ...")

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
        f"&forecast_days=1&timezone=Asia/Bangkok"
    )

    try:
        response = requests.get(url)
        data = response.json()

        hourly = data["hourly"]
        df = pd.DataFrame({
            "Thời gian": hourly["time"],
            "Nhiệt độ (°C)": hourly["temperature_2m"],
            "Độ ẩm (%)": hourly["relative_humidity_2m"],
            "Lượng mưa (mm)": hourly["precipitation"],
            "Tốc độ gió (m/s)": hourly["wind_speed_10m"]
        })

        # Lọc theo thông số được chọn
        columns_to_show = ["Thời gian"] + [col for col in df.columns if any(x in col for x in selected_data)]
        df_filtered = df[columns_to_show]

        # -------------------------------
        # Hiển thị bảng dữ liệu
        # -------------------------------
        st.subheader(f"📊 Dữ liệu khí tượng tại {selected_city}")
        st.dataframe(df_filtered, use_container_width=True)

        # -------------------------------
        # Hiển thị biểu đồ nếu có chọn
        # -------------------------------
        for param in selected_data:
            col_name = [c for c in df.columns if param in c][0]
            st.line_chart(df, x="Thời gian", y=col_name, height=250)

        # -------------------------------
        # Tùy chọn tải file CSV
        # -------------------------------
        csv = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="💾 Tải dữ liệu (.CSV)",
            data=csv,
            file_name=f"{selected_city}_weather_data.csv",
            mime="text/csv"
        )

        st.success("✅ Dữ liệu đã được tải và hiển thị thành công!")

    except Exception as e:
        st.error(f"❌ Lỗi khi tải dữ liệu: {e}")

# -------------------------------
# Chân trang cố định
# -------------------------------
st.markdown(
    """
    <hr style="margin-top:50px; margin-bottom:10px;">
    <div style="text-align:center; color:gray; font-size:14px;">
    © 2025 Trường THPT Lê Quý Đôn – Long Bình Tân | Web app thu thập dữ liệu thời gian thực
    </div>
    """,
    unsafe_allow_html=True
)
