# app.py
# ỨNG DỤNG TRA CỨU THÔNG SỐ THỜI TIẾT THỜI GIAN THỰC
# Phiên bản ổn định (kèm CSS checkbox chữ trắng)

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="ỨNG DỤNG TRA CỨU THỜI TIẾT THỜI GIAN THỰC", layout="wide")

# ===========================
# CSS chung (gộp, tránh nhiều st.markdown gây lỗi)
# ===========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
html, body, [class*="css"]  {
  font-family: 'Roboto', sans-serif;
}

/* Tổng thể nền */
.stApp {
    background: linear-gradient(135deg, #002b5b 0%, #004e89 50%, #017a8a 100%);
    color: #fff;
}

/* Hiệu ứng neon tiêu đề */
.neon-title {
  font-weight: 900;
  font-size: 34px;
  text-transform: uppercase;
  letter-spacing: 1px;
  text-align: center;
  margin-top: 10px;
  animation: neonGlow 5s linear infinite;
}
@keyframes neonGlow {
  0% { text-shadow: 0 0 8px #00eaff, 0 0 20px #00cfff, 0 0 30px #00bfff; }
  50% { text-shadow: 0 0 10px #0ff, 0 0 25px #00ffea, 0 0 35px #4dffff; }
  100% { text-shadow: 0 0 8px #00eaff, 0 0 20px #00cfff, 0 0 30px #00bfff; }
}

/* Thanh bản quyền cố định phía dưới */
.fixed-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: rgba(255,255,255,0.95);
  color: #003366;
  font-weight: 700;
  font-size: 15px;
  text-align: center;
  padding: 8px 0;
  box-shadow: 0 -2px 6px rgba(0,0,0,0.15);
  z-index: 9999;
}

/* Khung chung */
.frame {
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 18px;
  box-shadow: 0 0 12px rgba(0,0,0,0.15);
  border: 2px solid rgba(255,255,255,0.25);
  transition: all 0.3s ease;
}
.frame:hover {
  transform: scale(1.01);
  box-shadow: 0 0 18px rgba(255,255,255,0.25);
}

/* Màu nền riêng từng khung */
.title-frame {background-color: #003B73;}
.config-frame {background-color: #004E89;}
.result-frame {background-color: #005F73;}
.info-frame {background-color: #017A8A;}
.guide-frame {background-color: #01949A;}

/* Nút bấm */
div.stButton > button {
  background-color: #00aaff;
  color: white !important;
  font-weight: 700;
  border: none;
  border-radius: 8px;
  padding: 0.45rem 0.9rem;
  transition: 0.3s;
  box-shadow: 0 6px 12px rgba(0,0,0,0.12);
}
div.stButton > button:hover {
  background-color: #00d4ff;
  transform: translateY(-2px);
  box-shadow: 0 10px 18px rgba(0,0,0,0.25);
}

/* Checkbox: chữ màu trắng, đậm */
div[data-testid="stCheckbox"] label p {
    color: white !important;
    font-weight: 700;
}

/* Selectbox / multiselect label trắng */
div[data-testid="stSelectbox"] label p, div[data-testid="stMultiselect"] label p {
    color: white !important;
    font-weight: 600;
}

/* Dataframe header (chuẩn) */
.css-1d391kg .stDataFrameContainer table thead tr th {
    color: #003B73 !important;
}

/* Đảm bảo download button vẫn hiển thị tốt */
.download-btn > button {
    background-color: #0066CC;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ===========================
# Tiêu đề + Thông tin nhanh lên sau tiêu đề
# ===========================
st.markdown('<div class="title-frame"><div class="neon-title">ỨNG DỤNG TRA CỨU THÔNG SỐ THỜI TIẾT THỜI GIAN THỰC</div></div>', unsafe_allow_html=True)

# Thông tin nhanh (đặt dưới tiêu đề)
st.markdown("""
<div class="frame info-frame">
<h4>📡 Thông tin nhanh</h4>
✅ Nguồn dữ liệu: Open-Meteo (API đã kết nối thành công)<br>
📍 Khu vực: Đồng Nai<br>
🌐 Vĩ độ – Kinh độ: 10.9453, 106.8246<br>
⏰ Cập nhật: Thời gian thực khi bấm “Lấy dữ liệu”
</div>
""", unsafe_allow_html=True)

# ===========================
# Danh sách tỉnh/thành (34 có dấu)
# ===========================
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

# ===========================
# 2️⃣ Khung cấu hình
# ===========================
st.markdown('<div class="frame config-frame">', unsafe_allow_html=True)
st.subheader("⚙️ Cấu hình")

# Chọn tỉnh/thành
selected_place = st.selectbox("Chọn tỉnh/thành:", options=list(PROVINCES_34.keys()))

# Chọn thông số hiển thị
st.markdown("Chọn thông số hiển thị:")
params_default = [
    "Nhiệt độ (°C)",
    "Độ ẩm (%)",
    "Lượng mưa (mm)",
    "Tốc độ gió (m/s)",
    "Chỉ số UV"
]
selected_params = st.multiselect("Thông số", options=params_default, default=params_default[:4])

# Ô checkbox chữ trắng
allow_csv = st.checkbox("Cho phép xuất CSV (cột không dấu)", value=True)

st.markdown('</div>', unsafe_allow_html=True)

# ===========================
# 3️⃣ Khung kết quả tra cứu
# ===========================
st.markdown('<div class="frame result-frame">', unsafe_allow_html=True)
st.subheader("🌦️ Kết quả tra cứu")

def fetch_data(lat, lon):
    tz = "Asia/Ho_Chi_Minh"
    params = "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,uv_index"
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={params}&timezone={tz}"
    r = requests.get(url, timeout=12)
    r.raise_for_status()
    js = r.json()
    hourly = js.get("hourly", {})
    df = pd.DataFrame({
        "Thời gian": hourly.get("time", []),
        "Nhiệt độ (°C)": hourly.get("temperature_2m", []),
        "Độ ẩm (%)": hourly.get("relative_humidity_2m", []),
        "Lượng mưa (mm)": hourly.get("precipitation", []),
        "Tốc độ gió (m/s)": hourly.get("wind_speed_10m", []),
        "Chỉ số UV": hourly.get("uv_index", [])
    })
    if not df.empty:
        df["Thời gian"] = pd.to_datetime(df["Thời gian"])
    return df

lat, lon = PROVINCES_34[selected_place]
if st.button("🔄 Lấy dữ liệu thời gian thực"):
    with st.spinner("Đang truy xuất dữ liệu thời gian thực..."):
        try:
            df = fetch_data(lat, lon)
            if df.empty:
                st.error("API trả về dữ liệu rỗng.")
            else:
                st.success(f"✅ Nguồn dữ liệu: Open-Meteo (API đã kết nối thành công) | {selected_place}")
                show_cols = ["Thời gian"] + [p for p in selected_params if p in df.columns]
                st.dataframe(df[show_cols], use_container_width=True)

                # Biểu đồ
                if "Nhiệt độ (°C)" in selected_params and "Nhiệt độ (°C)" in df.columns:
                    st.plotly_chart(px.line(df, x="Thời gian", y="Nhiệt độ (°C)", title="Biểu đồ Nhiệt độ"), use_container_width=True)
                if "Độ ẩm (%)" in selected_params and "Độ ẩm (%)" in df.columns:
                    st.plotly_chart(px.line(df, x="Thời gian", y="Độ ẩm (%)", title="Biểu đồ Độ ẩm"), use_container_width=True)

                # Xuất CSV (không dấu tên cột)
                if allow_csv:
                    export = df.rename(columns={
                        "Thời gian": "thoi_gian",
                        "Nhiệt độ (°C)": "nhiet_do",
                        "Độ ẩm (%)": "do_am",
                        "Lượng mưa (mm)": "luong_mua",
                        "Tốc độ gió (m/s)": "toc_do_gio",
                        "Chỉ số UV": "uv_index"
                    })
                    export["dia_phuong"] = selected_place
                    csv = export.to_csv(index=False, encoding="utf-8-sig")
                    st.download_button("💾 Xuất CSV (cột không dấu)", data=csv, file_name=f"thoitiet_{selected_place.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")
        except requests.HTTPError as he:
            st.error(f"Lỗi HTTP khi gọi API: {he}")
        except Exception as e:
            st.error(f"Lỗi khi lấy dữ liệu: {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ===========================
# 5️⃣ Khung hướng dẫn sử dụng
# ===========================
st.markdown('<div class="frame guide-frame">', unsafe_allow_html=True)
st.subheader("🎓 Hướng dẫn sử dụng ngắn gọn")
st.markdown("""
1️⃣ **Chọn địa phương** từ danh sách (Cấu hình).  
2️⃣ **Nhấn “Lấy dữ liệu thời gian thực”** để xem bảng và biểu đồ.  
3️⃣ **Xuất CSV** để lưu dữ liệu học tập, các cột đã chuyển không dấu.  
📘 Ứng dụng này giúp học sinh **rèn luyện tư duy dữ liệu – đọc hiểu biểu đồ – vận dụng CNTT trong học tập STEM.**
""")
st.markdown('</div>', unsafe_allow_html=True)

# ===========================
# Footer bản quyền – cố định dưới trang
# ===========================
st.markdown("""
<div class="fixed-footer">
© 2025 Trường THPT Lê Quý Đôn – Long Bình Tân | Web app thu thập dữ liệu thời gian thực
</div>
""", unsafe_allow_html=True)
