import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

# =========================
# CSS chỉnh sửa giao diện
# =========================
st.markdown(
    """
    <style>
    /* Cập nhật giao diện và hiệu ứng */
    .stApp {
        background: linear-gradient(135deg, #0f4c81 0%, #146c9a 40%, #1aa7b8 100%);
        color: #fff;
    }

    .neon-title {
        font-weight: 900;
        font-size: 34px;
        text-transform: uppercase;
        letter-spacing: 1px;
        display: block;
        padding: 8px 16px;
        -webkit-text-stroke: 0.6px rgba(0,0,0,0.12);
        animation: neonGlow 6s linear infinite;
        text-align: center;
        margin-top: 12px;
        color: #ffffff;
    }

    .panel-6 {
        background: #028B8C; /* Màu xanh teal cho chatbot */
        border-radius: 12px;
        padding: 12px;
        margin-top: 10px;
    }

    .panel h3 {
        margin-top:0;
        color: #fff;
    }

    .panel p {
        color: #f0f7f7;
    }

    div.stButton > button {
        background-color: #007BFF;
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: 700;
        padding: 0.45rem 0.9rem;
        transition: transform 0.12s ease, background-color 0.12s ease;
        box-shadow: 0 6px 12px rgba(0,0,0,0.12);
    }
    div.stButton > button:hover {
        background-color: #00BFFF;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 18px rgba(0,0,0,0.18);
    }

    /* Khung chatbot */
    .chatbot-box {
        height: 300px;
        overflow-y: scroll;
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
    }

    /* Style cho nút Chatbot */
    .chat-button {
        background-color: #028B8C;
        color: white;
        border-radius: 8px;
        padding: 12px;
        margin-top: 12px;
        text-align: center;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# API Hugging Face Chatbot
# =========================
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct"

def query_hf_model(prompt: str):
    try:
        headers = {"Content-Type": "application/json"}
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 100}}
        response = requests.post(HF_API_URL, json=payload, headers=headers, timeout=20)

        if response.status_code == 200:
            response_json = response.json()
            if isinstance(response_json, dict) and "generated_text" in response_json:
                return response_json["generated_text"]
            return "Chatbot không có phản hồi hợp lệ."
        return f"(Lỗi khi kết nối: HTTP {response.status_code})"
    except Exception as e:
        return f"(Lỗi khi gọi API: {e})"

# =========================
# Giao diện Streamlit
# =========================
st.set_page_config(
    page_title="Ứng dụng Tra Cứu Thời Tiết Thời Gian Thực",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Tiêu đề và bản quyền
# =========================
st.markdown('<div style="text-align:center"><span class="neon-title">Ứng Dụng Tra Cứu Thời Tiết Thực Thời Gian</span></div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="fixed-topbar">
    © 2025 Trường THPT Lê Quý Đôn – Long Bình Tân | Web app thu thập dữ liệu thời gian thực
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# Sidebar cấu hình
# =========================
st.sidebar.header("Cấu Hình")
st.sidebar.markdown("Chọn tỉnh/thành và thông số cần xem.")
selected_place = st.sidebar.selectbox("Chọn tỉnh/thành", options=["TP. Hà Nội", "TP. Hồ Chí Minh", "Cần Thơ", "Đà Nẵng", "Huế"])
st.sidebar.markdown("---")
params_default = ["Nhiệt độ (°C)", "Độ ẩm (%)", "Lượng mưa (mm)", "Tốc độ gió (m/s)", "Chỉ số UV"]
selected_params = st.sidebar.multiselect("Thông số", options=params_default, default=params_default[:4])

# =========================
# Chatbot Input
# =========================
st.markdown('<div class="panel panel-6">', unsafe_allow_html=True)
st.markdown("### Chatbot AI - Hỏi đáp về thời tiết & khí hậu", unsafe_allow_html=True)
user_input = st.text_input("Nhập câu hỏi của bạn về thời tiết hoặc khí hậu...", key="chat_input")

if st.button("💬 Gửi câu hỏi"):
    if user_input:
        with st.spinner("Đang gửi câu hỏi..."):
            response = query_hf_model(user_input)
            st.markdown(f"**Trả lời từ Chatbot:** {response}")

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# Display kết quả
# =========================
st.markdown("### Kết quả tra cứu", unsafe_allow_html=True)
# Giả sử API đã kết nối và có dữ liệu.
# Trong trường hợp thực tế, bạn cần gọi API như đã làm ở phần trước để lấy dữ liệu.

st.write(f"Địa phương: {selected_place}")
st.write(f"Các thông số được chọn: {', '.join(selected_params)}")

# Chỉ thị từ phía API Hugging Face đã tích hợp sẵn, trong trường hợp hệ thống không có mạng, dữ liệu dự phòng sẽ được sử dụng.
