# app.py — Phiên bản 4.2
# Ứng dụng tra cứu thời tiết + Chatbot AI (Mixtral) + chế độ dự phòng offline
# Yêu cầu: pip install streamlit pandas requests plotly

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# ===== Cấu hình trang =====
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
.neon-title {
    text-align: center;
    margin-top: 15px;
    font-weight: 900;
    font-size: 36px;
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
.panel {
    background: rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 18px;
    margin-top: 18px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.25);
}
.panel h3 {
    color: #fff;
    font-weight: 700;
    border-bottom: 1px solid rgba(255,255,255,0.3);
    padding-bottom: 5px;
    margin-bottom: 10px;
}
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.1);
}
.stButton > button {
    background-color: #ffffff;
    color: #002B5B !important;
    border-radius: 8px;
    font-weight: 700;
    border: 2px solid #002B5B;
    transition: 0.3s;
}
.stButton > button:hover {
    background-color: #00BFFF;
    color: white !important;
    border: 2px solid #ffffff;
    transform: scale(1.05);
}
.footer {
  position: fixed;
  left: 0;
  bottom: 0;
  width: 100%;
  background: rgba(0, 43, 91, 0.98);
  color: white;
  text-align: center;
  padding: 8px 0;
  font-size: 15px;
  font-weight: 600;
  z-index: 9999;
}
.chatbox {
    background-color: rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 15px;
    max-height: 400px;
    overflow-y: auto;
}
.chat-input textarea {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ===== Tiêu đề =====
st.markdown("""
<div class="neon-title">
  ỨNG DỤNG TRA CỨU THÔNG SỐ<br>THỜI TIẾT THỜI GIAN THỰC
</div>
""", unsafe_allow_html=True)

# ===== 34 tỉnh/thành =====
PROVINCES_34 = {
    "An Giang": (10.5230, 105.1259),
    "Bắc Ninh": (21.1867, 106.0833),
    "Cà Mau": (9.1763, 105.1524),
    "Đắk Lắk": (12.6667, 108.0500),
    "Đồng Nai": (10.9453, 106.8246),
    "Đồng Tháp": (10.4938, 105.6885),
    "Gia Lai": (13.9833, 108.0000),
    "Hưng Yên": (20.6597, 106.0704),
    "Khánh Hòa": (12.2388, 109.1967),
    "Lào Cai": (22.4833, 103.9667),
    "Lâm Đồng": (11.9404, 108.4583),
    "Ninh Bình": (20.2510, 105.9743),
    "Phú Thọ": (21.3579, 103.8333),
    "Quảng Ngãi": (15.1217, 108.8011),
    "Quảng Trị": (16.7445, 107.1839),
    "Tây Ninh": (11.3333, 106.1667),
    "Thái Nguyên": (21.6000, 105.8500),
    "Tuyên Quang": (21.8167, 105.2333),
    "Vĩnh Long": (10.2430, 105.9750),
    "TP. Cần Thơ": (10.0452, 105.7469),
    "TP. Đà Nẵng": (16.0544, 108.2022),
    "TP. Hải Phòng": (20.8449, 106.6881),
    "TP. Hồ Chí Minh": (10.8231, 106.6297),
    "Cao Bằng": (22.6667, 106.2500),
    "Điện Biên": (21.3856, 103.0239),
    "Hà Tĩnh": (18.3432, 105.9057),
    "Lai Châu": (22.3833, 103.9333),
    "Lạng Sơn": (21.8468, 106.7585),
    "Nghệ An": (19.2676, 104.9997),
    "Quảng Ninh": (21.0138, 107.9572),
    "Thanh Hóa": (19.8067, 105.7768),
    "Sơn La": (21.3256, 103.9149),
    "TP. Hà Nội": (21.0285, 105.8542),
    "TP. Huế": (16.4637, 107.5909)
}

# ===== Sidebar =====
st.sidebar.header("🧭 Cấu hình")
selected_place = st.sidebar.selectbox("Chọn tỉnh/thành:", list(PROVINCES_34.keys()))
params = ["🌡️ Nhiệt độ (°C)", "💧 Độ ẩm (%)", "🌧️ Lượng mưa (mm)", "💨 Tốc độ gió (m/s)", "☀️ Chỉ số UV"]
selected_params = st.sidebar.multiselect("Chọn thông số hiển thị:", options=params, default=params[:3])
allow_csv = st.sidebar.checkbox("💾 Cho phép xuất dữ liệu CSV", value=True)

# ===== Hàm lấy dữ liệu từ API thời tiết =====
def fetch_weather(lat, lon):
    tz = "Asia/Ho_Chi_Minh"
    p = "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,uv_index"
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={p}&timezone={tz}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json().get("hourly", {})
    df = pd.DataFrame({
        "Thời gian": data.get("time", []),
        "🌡️ Nhiệt độ (°C)": data.get("temperature_2m", []),
        "💧 Độ ẩm (%)": data.get("relative_humidity_2m", []),
        "🌧️ Lượng mưa (mm)": data.get("precipitation", []),
        "💨 Tốc độ gió (m/s)": data.get("wind_speed_10m", []),
        "☀️ Chỉ số UV": data.get("uv_index", [])
    })
    if not df.empty:
        df["Thời gian"] = pd.to_datetime(df["Thời gian"])
    return df
# ===== PHẦN 2: Chatbot AI + chế độ dự phòng offline =====

# API Hugging Face (Mixtral-8x7B-Instruct)
API_KEY = "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"  # 🔑 Dán token Hugging Face của Thầy vào đây

# --- Hàm Chatbot AI ---
def ask_chatbot(user_question: str):
    """
    Trả lời câu hỏi từ học sinh.
    Ưu tiên gọi API Mixtral (Hugging Face).
    Nếu không có mạng hoặc lỗi quota → trả lời từ bộ dữ liệu dự phòng.
    """

    # === GỌI API THẬT TẠI ĐÂY ===
    # Nếu muốn kích hoạt Chatbot online, bỏ dấu # ở các dòng dưới và nhập API_KEY thật
    try:
          response = requests.post(
              "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct",
              headers={"Authorization": f"Bearer {API_KEY}"},
              json={"inputs": f"Trả lời bằng tiếng Việt, ngắn gọn, dễ hiểu: {user_question}"}
          )
          if response.status_code == 200:
              data = response.json()
              if isinstance(data, list) and "generated_text" in data[0]:
                  return data[0]["generated_text"]

        # Giả sử API bị lỗi, chuyển sang dự phòng:
        raise Exception("API not active in demo mode")

    except Exception:
        # Nếu API lỗi, tìm trong cơ sở dữ liệu dự phòng
        return find_offline_answer(user_question)


# ===== Dữ liệu dự phòng (FAQ offline) =====
FAQ_DATA = [
    {"q": "nhiệt độ là gì", "a": "Nhiệt độ cho biết mức độ nóng hay lạnh của một vật hoặc môi trường. Đơn vị thường dùng là °C."},
    {"q": "vì sao trời mưa", "a": "Trời mưa khi hơi nước trong khí quyển ngưng tụ thành giọt nước đủ nặng để rơi xuống."},
    {"q": "chỉ số uv là gì", "a": "Chỉ số UV thể hiện cường độ tia cực tím từ Mặt Trời. Chỉ số càng cao càng dễ gây hại da."},
    {"q": "vì sao có gió", "a": "Gió hình thành do sự chênh lệch áp suất giữa các vùng khí quyển, không khí di chuyển từ nơi áp cao sang áp thấp."},
    {"q": "độ ẩm là gì", "a": "Độ ẩm cho biết lượng hơi nước có trong không khí. Khi độ ẩm cao, không khí ẩm ướt và dễ gây cảm giác oi bức."},
    {"q": "vì sao có bão", "a": "Bão hình thành khi vùng áp thấp trên đại dương hút không khí ẩm, tạo thành xoáy mạnh quanh tâm."},
    {"q": "tốc độ gió bao nhiêu là mạnh", "a": "Khi gió trên 10 m/s (36 km/h) đã được xem là gió mạnh, có thể làm đổ cây nhỏ hoặc gây nguy hiểm."},
    {"q": "nhiệt độ trung bình việt nam", "a": "Việt Nam có nhiệt độ trung bình năm khoảng 25–27°C, tùy vùng miền."},
    {"q": "vì sao buổi sáng có sương mù", "a": "Sương mù xuất hiện khi hơi nước gần mặt đất ngưng tụ do không khí lạnh vào ban đêm."},
    {"q": "khí hậu nhiệt đới là gì", "a": "Khí hậu nhiệt đới có đặc điểm nóng ẩm, mưa nhiều, nhiệt độ trung bình cao quanh năm."},
]

# === Gợi ý thêm 90 câu hỏi khác (Thầy có thể mở rộng) ===
for i in range(11, 101):
    FAQ_DATA.append({
        "q": f"câu hỏi phổ biến {i}",
        "a": f"Đây là câu trả lời dự phòng mẫu cho câu hỏi phổ biến số {i}. Thầy có thể thay thế nội dung này bằng thông tin thực tế."
    })


def find_offline_answer(user_question: str) -> str:
    """
    Tìm câu trả lời dự phòng trong danh sách FAQ_DATA theo từ khóa.
    """
    uq = user_question.lower()
    for item in FAQ_DATA:
        if any(keyword in uq for keyword in item["q"].split()):
            return item["a"]
    return "Xin lỗi, tôi chưa có câu trả lời cho câu hỏi này. Em có thể hỏi lại theo cách khác nhé."


# ===== Giao diện khung Chatbot =====
st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown("### 🤖 Chatbot AI – Hỏi đáp về Thời tiết & Khí hậu")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Ô nhập câu hỏi
user_input = st.text_input("💬 Nhập câu hỏi của em (ví dụ: 'Vì sao trời nóng hơn vào mùa hè?')")

if st.button("🚀 Gửi câu hỏi"):
    if user_input.strip():
        answer = ask_chatbot(user_input)
        st.session_state.chat_history.append(("Học sinh", user_input))
        st.session_state.chat_history.append(("Chatbot", answer))

# Hiển thị hội thoại
chat_box = st.container()
with chat_box:
    st.markdown('<div class="chatbox">', unsafe_allow_html=True)
    for role, text in st.session_state.chat_history:
        if role == "Học sinh":
            st.markdown(f"🧑‍🎓 **{role}:** {text}")
        else:
            st.markdown(f"🤖 **{role}:** {text}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ===== Footer =====
st.markdown("""
<div class="footer">
© 2025 Trường THPT Lê Quý Đôn – Long Bình Tân | Web app thu thập dữ liệu thời gian thực
</div>
""", unsafe_allow_html=True)
