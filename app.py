import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(
    page_title="ỨNG DỤNG TRA CỨU THỜI TIẾT THỜI GIAN THỰC",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CSS: Styling for title, layout, button, etc.
# =========================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
    html, body, [class*="css"]  {
      font-family: 'Roboto', sans-serif;
    }

    /* Page background gradient */
    .stApp {
        background: linear-gradient(135deg, #0f4c81 0%, #146c9a 40%, #1aa7b8 100%);
        color: #fff;
    }

    /* Title styling */
    .neon-title {
        font-weight: 900;
        font-size: 48px;
        text-transform: uppercase;
        letter-spacing: 1px;
        display: block;
        padding: 8px 16px;
        -webkit-text-stroke: 0.6px rgba(0,0,0,0.12);
        animation: neonGlow 6s linear infinite;
        text-align: center;
        margin-top: 30px;
        color: #ffffff;
    }

    .neon-title-left {
        font-size: 32px;
        text-align: center;
    }

    /* Neon glowing effect */
    @keyframes neonGlow {
      0% { text-shadow: 0 0 6px #fff, 0 0 12px #ff4d4d, 0 0 20px #ff7b00; color:#fff; }
      25% { text-shadow: 0 0 6px #fff, 0 0 12px #ffd24d, 0 0 20px #fff44d; color:#fff; }
      50% { text-shadow: 0 0 6px #fff, 0 0 12px #2aff2a, 0 0 20px #00ff7f; color:#fff; }
      75% { text-shadow: 0 0 6px #fff, 0 0 12px #4dd2ff, 0 0 20px #4d7bff; color:#fff; }
      100% { text-shadow: 0 0 6px #fff, 0 0 12px #ff4d4d, 0 0 20px #ff7b00; color:#fff; }
    }

    /* Fixed topbar (copyright) */
    .fixed-topbar {
      position: fixed;
      bottom: 0;
      left: 0;
      width: 100%;
      background: rgba(255,255,255,0.9);
      color: #003366;
      font-weight: 700;
      font-size: 15px;
      text-align: center;
      padding: 8px 0;
      box-shadow: 0 2px 8px rgba(0,0,0,0.12);
      z-index: 9999;
    }

    /* Container for content and sidebar */
    .main-content {
      margin-top: 120px;
      padding-left: 16px;
      padding-right: 16px;
    }

    /* Sidebar layout */
    .sidebar {
        background: #2a3c55;
        padding: 16px;
        color: white;
        border-radius: 8px;
    }

    .panel {
        background: rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
    }

    /* Button styling */
    div.stButton > button {
        background-color: #007BFF;
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: 700;
        padding: 0.45rem 0.9rem;
        transition: transform 0.15s ease, background-color 0.15s ease;
        box-shadow: 0 6px 12px rgba(0,0,0,0.12);
    }
    div.stButton > button:hover {
        background-color: #00BFFF;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 18px rgba(0,0,0,0.18);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Title Section
# =========================
st.markdown('<div class="neon-title">ỨNG DỤNG TRA CỨU</div>', unsafe_allow_html=True)
st.markdown('<div class="neon-title-left">Thông số Thời tiết Theo thời gian thực</div>', unsafe_allow_html=True)

# =========================
# Main content wrapper
# =========================
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# =========================
# Sidebar configuration section
# =========================
with st.sidebar:
    st.header("Cấu hình")
    selected_place = st.selectbox("Chọn tỉnh/thành", options=["An Giang", "Bắc Ninh", "Cà Mau", "Đắk Lắk", "Đồng Nai"])
    st.write("Chọn thông số hiển thị:")
    params_default = ["Nhiệt độ (°C)", "Độ ẩm (%)", "Lượng mưa (mm)", "Tốc độ gió (m/s)", "Chỉ số UV"]
    selected_params = st.multiselect("Thông số", options=params_default, default=params_default[:4])

    allow_csv = st.checkbox("Cho phép xuất CSV (cột không dấu)", value=True)

# =========================
# Results Section
# =========================
st.markdown('### Kết quả tra cứu')
st.markdown(f"**Địa phương:** {selected_place}")
st.write(f"Vị trí: {selected_place} — Tìm kiếm dữ liệu từ Open-Meteo")

# =========================
# Chatbot Section
# =========================
st.markdown('### Chatbot Hỏi đáp Thời tiết & Khí hậu')
user_input = st.text_input("Nhập câu hỏi của bạn về thời tiết hoặc khí hậu...")
if user_input:
    st.write(f"Chatbot trả lời: {user_input}")

# =========================
# Footer Section (Fixed bottom)
# =========================
st.markdown(
    """
    <div class="fixed-topbar">
    © 2025 Trường THPT Lê Quý Đôn – Long Bình Tân | Web app thu thập dữ liệu thời gian thực
    </div>
    """,
    unsafe_allow_html=True
)

# End of main content wrapper
st.markdown('</div>', unsafe_allow_html=True)
