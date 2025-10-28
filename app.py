# app.py
# ỨNG DỤNG TRA CỨU THÔNG SỐ THỜI TIẾT THỜI GIAN THỰC (Phiên bản 4)
# - 6 khung màu tông xanh
# - Logo nhúng base64 (app độc lập)
# - Open-Meteo (real-time)
# - Chatbot AI (Hugging Face public endpoint)
# Yêu cầu: Python 3.10+, pip install streamlit requests pandas plotly

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px
import base64
from io import BytesIO

st.set_page_config(
    page_title="ỨNG DỤNG TRA CỨU THÔNG SỐ THỜI TIẾT THỜI GIAN THỰC",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Logo (base64 embedded)
# -----------------------------
logo_b64 = (
" We9W9hX+PGKADAM0Lwll8yaahzwO8jnqbqxh7w+KvOR90BFTmtRLrAX5b3DiyBgP...EEAAAQQQQAABBBBAAAEEEEAAAQQQQCBkgf8PTKvEnxCDVecAAAAASUVORK5CYII="
)
# (NOTE: the long base64 string above is embedded. If you need to replace logo, replace this variable with a new base64 string.)

# decode and prepare logo image (if valid)
logo_img = None
try:
    logo_bytes = base64.b64decode(logo_b64)
    logo_img = BytesIO(logo_bytes)
except Exception:
    logo_img = None

# =========================
# CSS: layout, 6 panels, neon title, topbar, API status, buttons
# =========================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap');
    html, body, [class*="css"]  {
      font-family: 'Roboto', sans-serif;
    }
    .stApp { background: linear-gradient(135deg, #0f4c81 0%, #146c9a 40%, #1aa7b8 100%); color: #fff; }

    /* Neon title + logo row */
    .top-row { display:flex; align-items:center; gap:16px; justify-content:center; margin-top:12px; }
    .logo-img { height:60px; width:auto; border-radius:8px; box-shadow: 0 6px 14px rgba(0,0,0,0.3); }
    .neon-title {
        font-weight: 900;
        font-size: 30px;
        text-transform: uppercase;
        letter-spacing: 1px;
        -webkit-text-stroke: 0.6px rgba(0,0,0,0.12);
        animation: neonGlow 6s linear infinite;
        color: #fff;
    }
    @keyframes neonGlow {
      0% { text-shadow: 0 0 6px #fff, 0 0 12px #ff4d4d, 0 0 20px #ff7b00; color:#fff; }
      25% { text-shadow: 0 0 6px #fff, 0 0 12px #ffd24d, 0 0 20px #fff44d; color:#fff; }
      50% { text-shadow: 0 0 6px #fff, 0 0 12px #2aff2a, 0 0 20px #00ff7f; color:#fff; }
      75% { text-shadow: 0 0 6px #fff, 0 0 12px #4dd2ff, 0 0 20px #4d7bff; color:#fff; }
      100% { text-shadow: 0 0 6px #fff, 0 0 12px #ff4d4d, 0 0 20px #ff7b00; color:#fff; }
    }

    /* Fixed topbar (copyright) below title */
    .fixed-topbar {
      position: fixed;
      top: 92px;
      left: 0;
      width: 100%;
      background: rgba(255,255,255,0.95);
      color: #003366;
      font-weight: 700;
      font-size: 15px;
      text-align: center;
      padding: 8px 0;
      box-shadow: 0 2px 8px rgba(0,0,0,0.12);
      z-index: 9999;
    }

    /* main content area margin to avoid overlap */
    .main-content { margin-top: 150px; padding: 12px 24px 80px 24px; }

    /* Panels (6 blocks) */
    .panel {
      border-radius: 12px;
      padding: 14px;
      box-shadow: 0 6px 14px rgba(0,0,0,0.12);
      margin-bottom: 16px;
    }
    .panel-1 { background: linear-gradient(90deg,#003B73,#0b4f8a); } /* title block */
    .panel-2 { background: linear-gradient(90deg,#004E89,#066c8f); } /* config */
    .panel-3 { background: linear-gradient(90deg,#005F73,#087f7a); } /* results */
    .panel-4 { background: linear-gradient(90deg,#017A8A,#018e92); } /* info */
    .panel-5 { background: linear-gradient(90deg,#01949A,#01a7a7); } /* guide */
    .panel-6 { background: linear-gradient(90deg,#028B8C,#02a59f); } /* chatbot */

    .panel h3 { margin-top:0; color: #fff; }
    .panel p { color: #f0f7f7; }

    /* Button style (global) */
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

    /* api status top-right */
    .api-status {
        position: fixed;
        top: 12px;
        right: 18px;
        background: rgba(255,255,255,0.08);
        color: #eaffea;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.12);
        z-index: 9999;
        font-weight: 700;
    }
    .api-dot { display:inline-block; width:12px; height:12px; border-radius:50%; margin-right:8px; vertical-align:middle; }

    /* small responsive tweaks */
    @media (max-width: 900px) {
      .top-row { flex-direction: column; }
      .logo-img { height:48px; }
      .fixed-topbar { top: 140px; }
      .main-content { margin-top: 190px; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Top row: logo + neon title
# -----------------------------
col_left, col_center, col_right = st.columns([1,6,1])
with col_center:
    # left: logo
    st.markdown('<div class="top-row">', unsafe_allow_html=True)
    if logo_img:
        st.image(logo_img, width=140, use_column_width=False)
    st.markdown('<div style="flex:1"><span class="neon-title">Ứng dụng tra cứu thông số Thời tiết thời gian thực</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# fixed topbar (copyright)
st.markdown(
    """
    <div class="fixed-topbar">
    © 2025 Trường THPT Lê Quý Đôn – Long Bình Tân | Web app thu thập dữ liệu thời gian thực
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Main content wrapper
# -----------------------------
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# -----------------------------
# Data: 34 tỉnh/thành (có dấu)
# -----------------------------
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

# -----------------------------
# Sidebar: configuration (displayed inside a panel)
# -----------------------------
with st.container():
    st.markdown('<div class="panel panel-2">', unsafe_allow_html=True)
    st.markdown("## Cấu hình", unsafe_allow_html=True)
    # Controls
    selected_place = st.selectbox("Chọn tỉnh/thành", options=list(PROVINCES_34.keys()))
    st.write("Chọn thông số muốn xem:")
    params_default = ["Nhiệt độ (°C)", "Độ ẩm (%)", "Lượng mưa (mm)", "Tốc độ gió (m/s)", "Chỉ số UV"]
    selected_params = st.multiselect("Thông số", options=params_default, default=params_default[:4])
    st.write("---")
    allow_csv = st.checkbox("Cho phép xuất CSV (cột không dấu)", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Test API connectivity (Open-Meteo)
# -----------------------------
def test_api_connectivity():
    try:
        lat, lon = PROVINCES_34["TP. Hà Nội"]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m&timezone=Asia/Ho_Chi_Minh"
        r = requests.get(url, timeout=8)
        return r.status_code == 200
    except Exception:
        return False

api_ok = test_api_connectivity()

# Show fixed status top-right
status_text = "Đã kết nối thành công với API thời tiết của trung tâm khí tượng thủy văn Meteo" if api_ok else "Không thể kết nối tới API Open-Meteo"
status_dot_color = "#4CAF50" if api_ok else "#B71C1C"
status_html = f"""
<div class="api-status">
    <span class="api-dot" style="background: {status_dot_color}"></span>
    {status_text}
</div>
"""
st.markdown(status_html, unsafe_allow_html=True)

# -----------------------------
# Helper: fetch real-time hourly data from Open-Meteo
# -----------------------------
def fetch_open_meteo_hourly(lat, lon, hours=24):
    tz = "Asia/Ho_Chi_Minh"
    params = "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,uv_index"
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly={params}&forecast_hours={hours}&timezone={tz}"
    )
    r = requests.get(url, timeout=12)
    r.raise_for_status()
    js = r.json()
    hourly = js.get("hourly", {})
    df = pd.DataFrame({
        "thoi_gian": hourly.get("time", []),
        "Nhiệt độ (°C)": hourly.get("temperature_2m", []),
        "Độ ẩm (%)": hourly.get("relative_humidity_2m", []),
        "Lượng mưa (mm)": hourly.get("precipitation", []),
        "Tốc độ gió (m/s)": hourly.get("wind_speed_10m", []),
        "Chỉ số UV": hourly.get("uv_index", [])
    })
    if not df.empty:
        df["thoi_gian"] = pd.to_datetime(df["thoi_gian"])
    return df

# -----------------------------
# Results panel (main)
# -----------------------------
with st.container():
    st.markdown('<div class="panel panel-3">', unsafe_allow_html=True)
    st.markdown("## Kết quả tra cứu", unsafe_allow_html=True)
    st.write(f"**Địa phương:** {selected_place}")
    lat, lon = PROVINCES_34[selected_place]
    st.write(f"Vĩ độ: {lat:.4f} — Kinh độ: {lon:.4f}")
    if api_ok:
        st.markdown("**Nguồn dữ liệu:** Open-Meteo (API đã kết nối thành công) ✅")
    else:
        st.markdown("**Nguồn dữ liệu:** Open-Meteo (chưa kết nối) ❌")
    st.write("---")
    fetch_btn = st.button("🔄 Lấy dữ liệu thời gian thực")
    if fetch_btn:
        with st.spinner("Đang gọi API Open-Meteo để lấy dữ liệu..."):
            try:
                df_hour = fetch_open_meteo_hourly(lat, lon, hours=24)
                if df_hour.empty:
                    st.error("API trả về dữ liệu rỗng.")
                else:
                    show_cols = ["thoi_gian"]
                    for p in params_default:
                        if p in selected_params or not selected_params:
                            if p in df_hour.columns:
                                show_cols.append(p)
                    display_df = df_hour[show_cols].rename(columns={"thoi_gian": "Thời gian"})
                    st.dataframe(display_df, use_container_width=True)

                    # Plot temperature & humidity
                    if "Nhiệt độ (°C)" in df_hour.columns and ("Nhiệt độ (°C)" in selected_params or not selected_params):
                        fig_t = px.line(df_hour, x="thoi_gian", y="Nhiệt độ (°C)", title=f"{selected_place} — Nhiệt độ (24h)", labels={"thoi_gian":"Thời gian","Nhiệt độ (°C)":"Nhiệt độ (°C)"})
                        st.plotly_chart(fig_t, use_container_width=True)
                    if "Độ ẩm (%)" in df_hour.columns and ("Độ ẩm (%)" in selected_params or not selected_params):
                        fig_h = px.line(df_hour, x="thoi_gian", y="Độ ẩm (%)", title=f"{selected_place} — Độ ẩm (24h)", labels={"thoi_gian":"Thời gian","Độ ẩm (%)":"Độ ẩm (%)"})
                        st.plotly_chart(fig_h, use_container_width=True)

                    # Export CSV with non-diacritic column names
                    if allow_csv:
                        export_df = df_hour.copy()
                        rename_map = {
                            "Nhiệt độ (°C)": "nhiet_do",
                            "Độ ẩm (%)": "do_am",
                            "Lượng mưa (mm)": "luong_mua",
                            "Tốc độ gió (m/s)": "toc_do_gio",
                            "Chỉ số UV": "uv_index",
                            "thoi_gian": "thoi_gian"
                        }
                        rename_existing = {k: v for k, v in rename_map.items() if k in export_df.columns}
                        export_df = export_df.rename(columns=rename_existing)
                        export_df["dia_phuong"] = selected_place
                        cols = ["dia_phuong", "thoi_gian"] + [c for c in export_df.columns if c not in ["dia_phuong", "thoi_gian"]]
                        export_df = export_df[cols]
                        csv_bytes = export_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8")
                        st.download_button("💾 Xuất CSV (cột không dấu)", data=csv_bytes, file_name=f"thoitiet_{selected_place.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")
                        st.download_button("💾 Xuất JSON (gốc)", data=export_df.to_json(orient="records", force_ascii=False), file_name=f"thoitiet_{selected_place.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.json", mime="application/json")
            except requests.HTTPError as he:
                st.error(f"Lỗi HTTP khi gọi API: {he}")
            except Exception as e:
                st.error(f"Lỗi khi lấy dữ liệu: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Info and Guide panels
# -----------------------------
with st.container():
    st.markdown('<div class="panel panel-4">', unsafe_allow_html=True)
    st.markdown("### Thông tin nhanh", unsafe_allow_html=True)
    if api_ok:
        st.markdown("- Nguồn dữ liệu: **Open-Meteo (API đã kết nối thành công)** ✅")
    else:
        st.markdown("- Nguồn dữ liệu: **Open-Meteo** (chưa kết nối)")
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="panel panel-5">', unsafe_allow_html=True)
    st.markdown("### Hướng dẫn sử dụng ngắn gọn", unsafe_allow_html=True)
    st.markdown("1. Chọn địa phương → 2. Bấm **Lấy dữ liệu** → 3. Xem bảng/biểu đồ → 4. Xuất CSV nếu cần.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Chatbot AI panel (Hugging Face)
# -----------------------------
HF_MODEL_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct"
# Note: public endpoints may have rate limits; no API key is provided here.

def query_hf_model(prompt: str, max_tokens: int = 256):
    try:
        headers = {"Content-Type": "application/json"}
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens}}
        resp = requests.post(HF_MODEL_URL, json=payload, headers=headers, timeout=30)
        # Response may be JSON with 'generated_text' or text directly
        if resp.status_code == 200:
            try:
                j = resp.json()
                # if list of generated outputs
                if isinstance(j, dict) and "generated_text" in j:
                    return j["generated_text"]
                if isinstance(j, list) and len(j) > 0:
                    # some HF models return list with 'generated_text'
                    if isinstance(j[0], dict) and "generated_text" in j[0]:
                        return j[0]["generated_text"]
                # fallback to raw text
                return resp.text
            except ValueError:
                return resp.text
        else:
            return f"(Chatbot không khả dụng: HTTP {resp.status_code})"
    except Exception as e:
        return f"(Lỗi khi gọi Chatbot: {e})"

# Chat UI state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.container():
    st.markdown('<div class="panel panel-6">', unsafe_allow_html=True)
    st.markdown("### Chatbot AI – Hỏi đáp về Thời tiết & Khí hậu", unsafe_allow_html=True)
    st.markdown("Hãy nhập câu hỏi về thời tiết, khí hậu, hiện tượng thiên nhiên. Chatbot trả lời bằng tiếng Việt.", unsafe_allow_html=True)
    user_input = st.text_input("Nhập câu hỏi của bạn...", key="chat_input")
    if st.button("💬 Gửi câu hỏi"):
        if user_input and user_input.strip():
            # append user message
            st.session_state.chat_history.append(("Học sinh", user_input.strip()))
            # query HF
            with st.spinner("Chatbot đang suy nghĩ..."):
                answer = query_hf_model(user_input.strip(), max_tokens=256)
            st.session_state.chat_history.append(("Chatbot", answer))
            # clear input (workaround)
            st.experimental_set_query_params()
    # show history
    for speaker, text in st.session_state.chat_history:
        if speaker == "Học sinh":
            st.markdown(f"<div style='background:#e6f7ff;padding:8px;border-radius:8px;margin:6px 0;color:#003366'><strong>👨‍🎓 {speaker}:</strong> {text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#f7fff7;padding:8px;border-radius:8px;margin:6px 0;color:#003366'><strong>🤖 {speaker}:</strong> {text}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# End main-content wrapper
# -----------------------------
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Final notes
# -----------------------------
st.markdown("<div style='position:fixed;bottom:8px;right:12px;color:#ffffff;opacity:0.8;font-size:12px'>Ứng dụng do THPT Lê Quý Đôn – Long Bình Tân phát triển</div>", unsafe_allow_html=True)
