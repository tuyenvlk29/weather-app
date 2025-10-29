# app.py — Phiên bản giao diện hoàn thiện (Tiêu đề neon hai dòng + khung rõ ràng + footer dưới cùng)
# Cần: pip install streamlit pandas requests plotly

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="ỨNG DỤNG TRA CỨU THỜI TIẾT THỜI GIAN THỰC",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CSS tổng thể =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
html, body, [class*="css"]  {
  font-family: 'Roboto', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0f4c81, #146c9a, #1aa7b8);
    color: white;
}

/* Tiêu đề neon 2 dòng */
.neon-title {
    text-align: center;
    margin-top: 15px;
    font-weight: 900;
    font-size: 34px;
    text-transform: uppercase;
    letter-spacing: 1px;
    line-height: 1.3em;
    color: #fff;
    text-shadow:
      0 0 5px #fff,
      0 0 10px #4fc3dc,
      0 0 20px #4fc3dc,
      0 0 40px #6a5acd,
      0 0 80px #6a5acd;
    animation: flicker 3s infinite alternate;
}
@keyframes flicker {
  0% { opacity:1; text-shadow:0 0 6px #fff,0 0 12px #4fc3dc;}
  50%{opacity:0.85;text-shadow:0 0 6px #fff,0 0 12px #6a5acd;}
  100%{opacity:1;text-shadow:0 0 8px #fff,0 0 16px #00ffff;}
}

/* Khung nội dung */
.panel {
    background: rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 16px;
    margin-top: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    border: 1px solid rgba(255,255,255,0.2);
}
.panel h3 {
    color: #fff;
    text-align: left;
    font-weight: 700;
    border-bottom: 1px solid rgba(255,255,255,0.2);
    padding-bottom: 5px;
    margin-bottom: 10px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.1);
}
.stButton > button {
    background-color: #007BFF;
    color: #fff !important;
    border-radius: 8px;
    font-weight: 600;
    transition: 0.3s;
}
.stButton > button:hover {
    background-color: #00BFFF;
    transform: scale(1.05);
}

/* Footer taskbar */
.footer {
  position: fixed;
  left: 0;
  bottom: 0;
  width: 100%;
  background: rgba(0, 51, 102, 0.95);
  color: white;
  text-align: center;
  padding: 8px 0;
  font-size: 15px;
  font-weight: 600;
  z-index: 9999;
}
</style>
""", unsafe_allow_html=True)

# ===== Tiêu đề =====
st.markdown("""
<div class="neon-title">
  ỨNG DỤNG TRA CỨU THÔNG SỐ<br>THỜI TIẾT THỜI GIAN THỰC
</div>
""", unsafe_allow_html=True)

# ===== Sidebar cấu hình =====
st.sidebar.header("🧭 Cấu hình")
st.sidebar.markdown("Chọn tỉnh/thành để tra cứu dữ liệu thời tiết:")

PROVINCES = {
    "Hà Nội": (21.0285, 105.8542),
    "TP. Hồ Chí Minh": (10.8231, 106.6297),
    "Đà Nẵng": (16.0544, 108.2022),
    "Cần Thơ": (10.0452, 105.7469),
    "Khánh Hòa": (12.2388, 109.1967),
    "Đắk Lắk": (12.6667, 108.0500),
    "Lâm Đồng": (11.9404, 108.4583),
    "Bắc Ninh": (21.1867, 106.0833)
}
selected_place = st.sidebar.selectbox("Chọn địa phương", list(PROVINCES.keys()))

params = ["Nhiệt độ (°C)", "Độ ẩm (%)", "Lượng mưa (mm)", "Tốc độ gió (m/s)", "Chỉ số UV"]
selected_params = st.sidebar.multiselect("Chọn thông số hiển thị", options=params, default=params[:3])

allow_csv = st.sidebar.checkbox("Cho phép xuất dữ liệu CSV", value=True)

# ===== Hàm lấy dữ liệu từ Open-Meteo =====
def fetch_weather(lat, lon):
    tz = "Asia/Ho_Chi_Minh"
    p = "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,uv_index"
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={p}&timezone={tz}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json().get("hourly", {})
    df = pd.DataFrame({
        "Thời gian": data.get("time", []),
        "Nhiệt độ (°C)": data.get("temperature_2m", []),
        "Độ ẩm (%)": data.get("relative_humidity_2m", []),
        "Lượng mưa (mm)": data.get("precipitation", []),
        "Tốc độ gió (m/s)": data.get("wind_speed_10m", []),
        "Chỉ số UV": data.get("uv_index", [])
    })
    if not df.empty:
        df["Thời gian"] = pd.to_datetime(df["Thời gian"])
    return df

# ===== Hiển thị chính =====
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### 🌦️ Kết quả tra cứu")
    lat, lon = PROVINCES[selected_place]
    st.write(f"**Địa phương:** {selected_place}")
    st.write(f"Vĩ độ: {lat:.4f}, Kinh độ: {lon:.4f}")
    fetch_btn = st.button("🔄 Lấy dữ liệu thời gian thực")

    if fetch_btn:
        try:
            df = fetch_weather(lat, lon)
            if df.empty:
                st.warning("Không có dữ liệu.")
            else:
                show_cols = ["Thời gian"] + [p for p in selected_params if p in df.columns]
                st.dataframe(df[show_cols], use_container_width=True)
                # Vẽ biểu đồ
                for p in selected_params:
                    if p in df.columns:
                        fig = px.line(df, x="Thời gian", y=p, title=f"{p} tại {selected_place}")
                        st.plotly_chart(fig, use_container_width=True)
                if allow_csv:
                    csv = df.to_csv(index=False).encode("utf-8-sig")
                    st.download_button("💾 Xuất dữ liệu CSV", csv, file_name=f"{selected_place}_weather.csv")
        except Exception as e:
            st.error(f"Lỗi khi lấy dữ liệu: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### 🧾 Thông tin nhanh")
    st.markdown("- Nguồn dữ liệu: **Open-Meteo (API đã kết nối thành công)** ✅")
    st.markdown("- Cập nhật thời gian thực theo tọa độ địa phương.")
    st.markdown("- Dữ liệu gồm: Nhiệt độ, Độ ẩm, Lượng mưa, Tốc độ gió, Chỉ số UV.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### 📘 Hướng dẫn sử dụng")
    st.markdown("""
    1. Chọn **địa phương** cần tra cứu ở thanh bên trái.  
    2. Bấm **"Lấy dữ liệu thời gian thực"** để xem thông tin.  
    3. Xem bảng, biểu đồ, hoặc **xuất file CSV** để lưu.  
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# ===== Footer (Taskbar bản quyền) =====
st.markdown("""
<div class="footer">
© 2025 Trường THPT Lê Quý Đôn – Long Bình Tân | Web app thu thập dữ liệu thời gian thực
</div>
""", unsafe_allow_html=True)
