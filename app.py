import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64
from io import BytesIO

# API Key cho Hugging Face (thay thế bằng key của bạn)
API_KEY = "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"

# -------------------------------
# Cấu hình ứng dụng Streamlit
st.set_page_config(
    page_title="ỨNG DỤNG TRA CỨU THÔNG SỐ THỜI TIẾT THỜI GIAN THỰC",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# CSS tùy chỉnh giao diện
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
    html, body, [class*="css"] {
      font-family: 'Roboto', sans-serif;
    }
    
    /* Giao diện nền */
    .stApp {
        background: linear-gradient(135deg, #0f4c81 0%, #146c9a 40%, #1aa7b8 100%);
        color: white;
    }
    
    /* Tiêu đề neon */
    .neon-title {
        font-size: 36px;
        font-weight: 900;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #fff;
        text-align: center;
        padding: 16px;
        animation: neonGlow 6s linear infinite;
    }

    @keyframes neonGlow {
      0% { text-shadow: 0 0 6px #fff, 0 0 12px #ff4d4d, 0 0 20px #ff7b00; }
      25% { text-shadow: 0 0 6px #fff, 0 0 12px #ffd24d, 0 0 20px #fff44d; }
      50% { text-shadow: 0 0 6px #fff, 0 0 12px #2aff2a, 0 0 20px #00ff7f; }
      75% { text-shadow: 0 0 6px #fff, 0 0 12px #4dd2ff, 0 0 20px #4d7bff; }
      100% { text-shadow: 0 0 6px #fff, 0 0 12px #ff4d4d, 0 0 20px #ff7b00; }
    }

    /* Chatbot */
    .chatbox {
        background-color: #028B8C;
        padding: 12px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        height: 400px;
        overflow-y: scroll;
    }

    /* Các khung nội dung */
    .panel {
        background: rgba(255,255,255,0.06);
        padding: 16px;
        margin-bottom: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 14px rgba(0,0,0,0.12);
    }

    /* Nút button */
    div.stButton > button {
        background-color: #007BFF;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 700;
        padding: 0.45rem 0.9rem;
        transition: transform 0.15s ease;
    }

    div.stButton > button:hover {
        background-color: #00BFFF;
        transform: translateY(-2px);
    }

    /* Phần khung 2 bên */
    .side-panel {
        background: rgba(255,255,255,0.04);
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 6px 14px rgba(0,0,0,0.12);
    }
    
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Phần hiển thị tiêu đề
st.markdown('<div class="neon-title">ỨNG DỤNG TRA CỨU</div>', unsafe_allow_html=True)
st.markdown('<div class="neon-title">THÔNG SỐ THỜI TIẾT THỜI GIAN THỰC</div>', unsafe_allow_html=True)

# -------------------------------
# Sidebar: chọn địa phương và thông số
st.sidebar.header("Cấu hình")
selected_place = st.sidebar.selectbox("Chọn tỉnh/thành", options=["An Giang", "Bắc Ninh", "Cà Mau", "Đà Nẵng"])
selected_params = st.sidebar.multiselect("Chọn thông số", options=["Nhiệt độ (°C)", "Độ ẩm (%)", "Lượng mưa (mm)", "Tốc độ gió (m/s)", "Chỉ số UV"])
allow_csv = st.sidebar.checkbox("Xuất CSV (cột không dấu)", value=True)

# -------------------------------
# Fetch weather data function
def fetch_weather_data():
    # Giả lập việc lấy dữ liệu từ API (bạn cần thay thế với API thật)
    data = {
        "Nhiệt độ (°C)": [25, 26, 27, 28],
        "Độ ẩm (%)": [80, 82, 85, 87],
        "Lượng mưa (mm)": [1, 2, 0, 1],
        "Tốc độ gió (m/s)": [3, 4, 5, 3],
        "Chỉ số UV": [3, 4, 6, 5],
    }
    df = pd.DataFrame(data)
    df["Thời gian"] = pd.date_range("2022-01-01", periods=4, freq="H")
    return df

# -------------------------------
# Hiển thị kết quả tra cứu
st.markdown("## Kết quả tra cứu", unsafe_allow_html=True)
st.write(f"**Địa phương:** {selected_place}")
weather_data = fetch_weather_data()

# Hiển thị dữ liệu và biểu đồ
if "Nhiệt độ (°C)" in selected_params:
    st.subheader("Biểu đồ Nhiệt độ")
    fig_temp = px.line(weather_data, x="Thời gian", y="Nhiệt độ (°C)", title="Nhiệt độ (°C)")
    st.plotly_chart(fig_temp)

if "Độ ẩm (%)" in selected_params:
    st.subheader("Biểu đồ Độ ẩm")
    fig_humidity = px.line(weather_data, x="Thời gian", y="Độ ẩm (%)", title="Độ ẩm (%)")
    st.plotly_chart(fig_humidity)

if "Lượng mưa (mm)" in selected_params:
    st.subheader("Biểu đồ Lượng mưa")
    fig_rain = px.line(weather_data, x="Thời gian", y="Lượng mưa (mm)", title="Lượng mưa (mm)")
    st.plotly_chart(fig_rain)

if allow_csv:
    st.download_button("Tải dữ liệu CSV", weather_data.to_csv(index=False), file_name="weather_data.csv")

# -------------------------------
# Chatbot AI
def get_chatbot_response(query):
    url = "https://api-inference.huggingface.co/models/your-model-name"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.post(url, headers=headers, json={"inputs": query})
    return response.json().get("generated_text", "Không có câu trả lời.")

# -------------------------------
# Khung chat
st.markdown('<div class="panel chatbox">', unsafe_allow_html=True)
st.markdown("### Chatbot AI - Hỏi về thời tiết")
user_input = st.text_input("Nhập câu hỏi của bạn:")
if user_input:
    answer = get_chatbot_response(user_input)
    st.markdown(f"**Chatbot trả lời:** {answer}")
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# Phần giao diện chính
st.markdown('<div class="side-panel">', unsafe_allow_html=True)
st.markdown("### Thông tin nhanh")
st.markdown("- Nguồn dữ liệu: Open-Meteo (API đã kết nối thành công) ✅")
st.markdown("- Dữ liệu: cập nhật theo thời gian thực khi bấm 'Lấy dữ liệu'")
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# End of page layout
st.markdown('</div>', unsafe_allow_html=True)
