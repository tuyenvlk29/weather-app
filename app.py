# app.py
# ỨNG DỤNG TRA CỨU THÔNG SỐ THỜI TIẾT THỜI GIAN THỰC (Phiên bản 4)
# Yêu cầu: Python 3.10+, pip install streamlit requests pandas plotly

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px
import random

st.set_page_config(
    page_title="ỨNG DỤNG TRA CỨU THỜI TIẾT THỜI GIAN THỰC",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CSS: neon title, fixed topbar (bản quyền), api status, buttons
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

    /* Fixed topbar (copyright) */
    .fixed-topbar {
      position: fixed;
      top: 64px; /* leave space for neon title */
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

    /* Make main content not overlap topbar */
    .main-content {
      margin-top: 120px;
      padding-left: 16px;
      padding-right: 16px;
    }

    /* Neon animated title */
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

    @keyframes neonGlow {
      0% { text-shadow: 0 0 6px #fff, 0 0 12px #ff4d4d, 0 0 20px #ff7b00; color:#fff; }
      25% { text-shadow: 0 0 6px #fff, 0 0 12px #ffd24d, 0 0 20px #fff44d; color:#fff; }
      50% { text-shadow: 0 0 6px #fff, 0 0 12px #2aff2a, 0 0 20px #00ff7f; color:#fff; }
      75% { text-shadow: 0 0 6px #fff, 0 0 12px #4dd2ff, 0 0 20px #4d7bff; color:#fff; }
      100% { text-shadow: 0 0 6px #fff, 0 0 12px #ff4d4d, 0 0 20px #ff7b00; color:#fff; }
    }

    /* API status top-right */
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
    .api-dot {
        display:inline-block;
        width:12px;
        height:12px;
        border-radius:50%;
        margin-right:8px;
        vertical-align:middle;
    }

    /* Style for Streamlit buttons (global) */
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

    /* Card like panels */
    .panel {
        background: rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 12px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Neon title + topbar (copyright)
# =========================
st.markdown('<div style="text-align:center"><span class="neon-title">Ứng dụng tra cứu thông số Thời tiết thời gian thực</span></div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="fixed-topbar">
    © 2025 Trường THPT Lê Quý Đôn – Long Bình Tân | Web app thu thập dữ liệu thời gian thực
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# Main content wrapper
# =========================
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# =========================
# Danh sách 34 tỉnh/thành có dấu
# =========================
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

# =========================
# Sidebar controls
# =========================
st.sidebar.header("Cấu hình")
st.sidebar.markdown("Chọn tỉnh/thành từ danh sách 34 địa phương.")
selected_place = st.sidebar.selectbox("Chọn tỉnh/thành", options=list(PROVINCES_34.keys()))
st.sidebar.markdown("---")
st.sidebar.markdown("Chọn thông số hiển thị")
params_default = ["Nhiệt độ (°C)", "Độ ẩm (%)", "Lượng mưa (mm)", "Tốc độ gió (m/s)", "Chỉ số UV"]
selected_params = st.sidebar.multiselect("Thông số", options=params_default, default=params_default[:4])
st.sidebar.markdown("---")
st.sidebar.markdown("Xuất dữ liệu")
allow_csv = st.sidebar.checkbox("Cho phép xuất CSV (cột không dấu)", value=True)

# =========================
# Test API connectivity (Open-Meteo)
# =========================
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

# =========================
# Helper: fetch real-time hourly data from Open-Meteo
# =========================
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

# =========================
# Main interactive area
# =========================
st.markdown("### Kết quả tra cứu", unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"**Địa phương:** {selected_place}")
    lat, lon = PROVINCES_34[selected_place]
    st.markdown(f"Vĩ độ: {lat:.4f} — Kinh độ: {lon:.4f}")
    # Source info (API connected message)
    if api_ok:
        st.markdown("**Nguồn dữ liệu:** Open-Meteo (API đã kết nối thành công) ✅")
    else:
        st.markdown("**Nguồn dữ liệu:** Open-Meteo (chưa kết nối) ❌")
    st.markdown("---")
    fetch_btn = st.button("🔄 Lấy dữ liệu thời gian thực")

    if fetch_btn:
        with st.spinner("Đang gọi API Open-Meteo để lấy dữ liệu..."):
            try:
                df_hour = fetch_open_meteo_hourly(lat, lon, hours=24)
                if df_hour.empty:
                    st.error("API trả về dữ liệu rỗng.")
                else:
                    # Select columns to show
                    show_cols = ["thoi_gian"]
                    mapping_display = {
                        "Nhiệt độ (°C)": "Nhiệt độ (°C)",
                        "Độ ẩm (%)": "Độ ẩm (%)",
                        "Lượng mưa (mm)": "Lượng mưa (mm)",
                        "Tốc độ gió (m/s)": "Tốc độ gió (m/s)",
                        "Chỉ số UV": "Chỉ số UV"
                    }
                    for p in params_default:
                        if p in selected_params or not selected_params:
                            if p in df_hour.columns:
                                show_cols.append(p)
                    # Show table (rename thoi_gian to Thời gian for display)
                    display_df = df_hour[show_cols].rename(columns={"thoi_gian": "Thời gian"})
                    st.dataframe(display_df, use_container_width=True)

                    # Plot temperature & humidity if present
                    if "Nhiệt độ (°C)" in df_hour.columns and ("Nhiệt độ (°C)" in selected_params or not selected_params):
                        fig_t = px.line(df_hour, x="thoi_gian", y="Nhiệt độ (°C)", title=f"{selected_place} — Nhiệt độ (24h)", labels={"thoi_gian": "Thời gian", "Nhiệt độ (°C)": "Nhiệt độ (°C)"})
                        st.plotly_chart(fig_t, use_container_width=True)
                    if "Độ ẩm (%)" in df_hour.columns and ("Độ ẩm (%)" in selected_params or not selected_params):
                        fig_h = px.line(df_hour, x="thoi_gian", y="Độ ẩm (%)", title=f"{selected_place} — Độ ẩm (24h)", labels={"thoi_gian": "Thời gian", "Độ ẩm (%)": "Độ ẩm (%)"})
                        st.plotly_chart(fig_h, use_container_width=True)

                    # Export CSV / JSON with non-diacritic column names
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

with col2:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("### Thông tin nhanh")
    if api_ok:
        st.markdown("- Nguồn dữ liệu: **Open-Meteo (API đã kết nối thành công)** ✅")
    else:
        st.markdown("- Nguồn dữ liệu: **Open-Meteo** (chưa kết nối)")
    st.markdown("- Dữ liệu: cập nhật theo thời gian thực khi bấm 'Lấy dữ liệu'")
    st.markdown("---")
    st.markdown("### Hướng dẫn sử dụng ngắn gọn")
    st.markdown("1. Chọn địa phương ở thanh bên → bấm **Lấy dữ liệu**.  \n2.
