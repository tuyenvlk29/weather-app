# app.py
# ỨNG DỤNG TRA CỨU THÔNG SỐ THỜI TIẾT THỜI GIAN THỰC
# Kết nối Open-Meteo (https://open-meteo.com/)
# Yêu cầu: Python 3.10+, thư viện: streamlit, requests, pandas, plotly

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(
    page_title="ỨNG DỤNG TRA CỨU THÔNG SỐ THỜI TIẾT THỜI GIAN THỰC",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CSS: neon title, fixed status, footer
# =========================
st.markdown(
    """
    <style>
    /* Gradient background */
    .stApp {
        background: linear-gradient(135deg, #0f4c81 0%, #1aa7b8 50%, #90e0ef 100%);
        color: #fff;
    }

    /* Neon animated title */
    .neon-title {
        font-weight: 900;
        font-size: 34px;
        text-transform: uppercase;
        letter-spacing: 1px;
        display: inline-block;
        padding: 8px 16px;
        -webkit-text-stroke: 0.6px rgba(0,0,0,0.15);
        animation: neonGlow 6s linear infinite;
        text-align: center;
    }

    @keyframes neonGlow {
      0% {
        text-shadow: 0 0 6px #fff, 0 0 12px #ff4d4d, 0 0 20px #ff4d4d, 0 0 30px #ff7b00;
        color: #fff;
      }
      25% {
        text-shadow: 0 0 6px #fff, 0 0 12px #ffd24d, 0 0 20px #ffd24d, 0 0 30px #fff44d;
        color: #fff;
      }
      50% {
        text-shadow: 0 0 6px #fff, 0 0 12px #7bff7b, 0 0 20px #2aff2a, 0 0 30px #00ff7f;
        color: #fff;
      }
      75% {
        text-shadow: 0 0 6px #fff, 0 0 12px #4dd2ff, 0 0 20px #4dd2ff, 0 0 30px #4d7bff;
        color: #fff;
      }
      100% {
        text-shadow: 0 0 6px #fff, 0 0 12px #ff4d4d, 0 0 20px #ff4d4d, 0 0 30px #ff7b00;
        color: #fff;
      }
    }

    /* Fixed top-right status */
    .api-status {
        position: fixed;
        top: 12px;
        right: 18px;
        background: rgba(255,255,255,0.08);
        color: #eaffea;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        z-index: 9999;
        font-weight: 600;
    }
    .api-dot {
        display:inline-block;
        width:12px;
        height:12px;
        border-radius:50%;
        margin-right:8px;
        vertical-align:middle;
    }

    /* Footer fixed */
    .fixed-footer {
      position: fixed;
      left: 0;
      bottom: 0;
      width: 100%;
      text-align: center;
      background-color: rgba(255,255,255,0.06);
      color: #fff;
      padding: 8px 0;
      font-size: 14px;
      border-top: 1px solid rgba(255,255,255,0.08);
      z-index: 9998;
    }

    /* Content spacing to avoid overlap with footer */
    .streamlit-expanderHeader {
        color: #fff;
    }
    .stApp > header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True
)

# =========================
# Header
# =========================
st.markdown('<div style="text-align:center"><span class="neon-title">Ứng dụng tra cứu thông số Thời tiết thời gian thực</span></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# =========================
# 34 provinces (names no-diacritics)
# =========================
PROVINCES_34 = {
    "An Giang": (10.5230, 105.1259),
    "Bac Ninh": (21.1867, 106.0833),
    "Ca Mau": (9.1763, 105.1524),
    "Dak Lak": (12.6667, 108.0500),
    "Dong Nai": (10.9453, 106.8246),
    "Dong Thap": (10.4938, 105.6885),
    "Gia Lai": (13.9833, 108.0000),
    "Hung Yen": (20.6597, 106.0704),
    "Khanh Hoa": (12.2388, 109.1967),
    "Lao Cai": (22.4833, 103.9667),
    "Lam Dong": (11.9404, 108.4583),
    "Ninh Binh": (20.2510, 105.9743),
    "Phu Tho": (21.3579, 103.8333),
    "Quang Ngai": (15.1217, 108.8011),
    "Quang Tri": (16.7445, 107.1839),
    "Tay Ninh": (11.3333, 106.1667),
    "Thai Nguyen": (21.6000, 105.8500),
    "Tuyen Quang": (21.8167, 105.2333),
    "Vinh Long": (10.2430, 105.9750),
    "TP Can Tho": (10.0452, 105.7469),
    "TP Da Nang": (16.0544, 108.2022),
    "TP Hai Phong": (20.8449, 106.6881),
    "TP Ho Chi Minh": (10.8231, 106.6297),
    "Cao Bang": (22.6667, 106.2500),
    "Dien Bien": (21.3856, 103.0239),
    "Ha Tinh": (18.3432, 105.9057),
    "Lai Chau": (22.3833, 103.9333),
    "Lang Son": (21.8468, 106.7585),
    "Nghe An": (19.2676, 104.9997),
    "Quang Ninh": (21.0138, 107.9572),
    "Thanh Hoa": (19.8067, 105.7768),
    "Son La": (21.3256, 103.9149),
    "TP Ha Noi": (21.0285, 105.8542),
    "TP Hue": (16.4637, 107.5909)
}

# =========================
# Sidebar controls
# =========================
st.sidebar.header("Cấu hình")
st.sidebar.markdown("Chọn tỉnh/thanh từ danh sách (34 địa phương).")

selected_place = st.sidebar.selectbox("Chọn tỉnh/thanh", options=list(PROVINCES_34.keys()))
st.sidebar.markdown("---")
st.sidebar.markdown("Chọn thông số hiển thị")
params_default = ["Nhiệt độ (°C)", "Độ ẩm (%)", "Lượng mưa (mm)", "Tốc độ gió (m/s)", "Chỉ số UV"]
selected_params = st.sidebar.multiselect("Thông số", options=params_default, default=params_default[:4])
st.sidebar.markdown("---")
st.sidebar.markdown("Xuất dữ liệu")
allow_csv = st.sidebar.checkbox("Cho phép xuất CSV (cột không dấu)", value=True)

# =========================
# Test API connectivity (light request)
# =========================
def test_api_connectivity():
    # call Open-Meteo for a small query (Hanoi) to verify
    try:
        lat, lon = PROVINCES_34["TP Ha Noi"]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m&timezone=Asia/Ho_Chi_Minh"
        r = requests.get(url, timeout=8)
        return r.status_code == 200
    except Exception:
        return False

api_ok = test_api_connectivity()

# Show fixed status top-right
status_html = f"""
<div class="api-status">
    <span class="api-dot" style="background: {'#4CAF50' if api_ok else '#B71C1C'}"></span>
    {'Đã kết nối thành công với API thời tiết của trung tâm khí tượng thủy văn Meteo' if api_ok else 'Không thể kết nối đến API Open-Meteo (kiểm tra kết nối)'}
</div>
"""
st.markdown(status_html, unsafe_allow_html=True)

# =========================
# Helper: fetch real-time hourly data from Open-Meteo
# =========================
def fetch_open_meteo_hourly(lat, lon, hours=24):
    tz = "Asia/Ho_Chi_Minh"
    # request uv_index if possible
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
    # ensure correct time format
    if not df.empty:
        df["thoi_gian"] = pd.to_datetime(df["thoi_gian"])
    return df

# =========================
# Main interactive area
# =========================
st.markdown("### Kết quả tra cứu")
col1, col2 = st.columns([2, 1])

with col1:
    st.write(f"**Địa phương:** {selected_place}")
    lat, lon = PROVINCES_34[selected_place]
    st.write(f"Vĩ độ: {lat:.4f} — Kinh độ: {lon:.4f}")
    if not api_ok:
        st.warning("Hiện tại ứng dụng chưa kết nối được tới API Open-Meteo. Vui lòng kiểm tra kết nối internet.")
    fetch_btn = st.button("🔄 Lấy dữ liệu thời gian thực")

    if fetch_btn:
        with st.spinner("Đang gọi API Open-Meteo để lấy dữ liệu..."):
            try:
                df_hour = fetch_open_meteo_hourly(lat, lon, hours=24)
                if df_hour.empty:
                    st.error("API trả về dữ liệu rỗng.")
                else:
                    # Show basic table (subset)
                    display_cols = ["thoi_gian"] + [c for c in ["Nhiệt độ (°C)", "Độ ẩm (%)", "Lượng mưa (mm)", "Tốc độ gió (m/s)", "Chỉ số UV"] if c in selected_params or c in selected_params]
                    # if selected_params is empty, show default cols
                    if not selected_params:
                        display_cols = ["thoi_gian", "Nhiệt độ (°C)", "Độ ẩm (%)"]
                    st.dataframe(df_hour[display_cols].rename(columns={"thoi_gian": "Thời gian"}), use_container_width=True)

                    # Plot temperature
                    if "Nhiệt độ (°C)" in df_hour.columns and ("Nhiệt độ (°C)" in selected_params or not selected_params):
                        fig_t = px.line(df_hour, x="thoi_gian", y="Nhiệt độ (°C)", title=f"{selected_place} — Nhiệt độ (24h)", labels={"thoi_gian": "Thời gian", "Nhiệt độ (°C)": "Nhiệt độ (°C)"})
                        st.plotly_chart(fig_t, use_container_width=True)

                    # Plot humidity
                    if "Độ ẩm (%)" in df_hour.columns and ("Độ ẩm (%)" in selected_params or not selected_params):
                        fig_h = px.line(df_hour, x="thoi_gian", y="Độ ẩm (%)", title=f"{selected_place} — Độ ẩm (24h)", labels={"thoi_gian": "Thời gian", "Độ ẩm (%)": "Độ ẩm (%)"})
                        st.plotly_chart(fig_h, use_container_width=True)

                    # Export CSV / JSON
                    if allow_csv:
                        # Map to non-diacritic column names for export
                        export_df = df_hour.copy()
                        # Rename columns to required export names
                        rename_map = {
                            "Nhiệt độ (°C)": "nhiet_do",
                            "Độ ẩm (%)": "do_am",
                            "Lượng mưa (mm)": "luong_mua",
                            "Tốc độ gió (m/s)": "toc_do_gio",
                            "Chỉ số UV": "uv_index",
                            "thoi_gian": "thoi_gian"
                        }
                        # Apply rename (only existing columns)
                        rename_existing = {k: v for k, v in rename_map.items() if k in export_df.columns}
                        export_df = export_df.rename(columns=rename_existing)
                        # Add location column
                        export_df["dia_phuong"] = selected_place
                        # Reorder columns to put dia_phuong, thoi_gian first
                        cols = ["dia_phuong", "thoi_gian"] + [c for c in export_df.columns if c not in ["dia_phuong", "thoi_gian"]]
                        export_df = export_df[cols]
                        csv_bytes = export_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8")
                        st.download_button("💾 Xuất CSV (cột không dấu)", data=csv_bytes, file_name=f"weather_{selected_place.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")
                        # JSON export (kept original names)
                        st.download_button("💾 Xuất JSON (gốc)", data=export_df.to_json(orient="records", force_ascii=False), file_name=f"weather_{selected_place.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.json", mime="application/json")
            except requests.HTTPError as he:
                st.error(f"Lỗi HTTP khi gọi API: {he}")
            except Exception as e:
                st.error(f"Lỗi khi lấy dữ liệu: {e}")

with col2:
    st.markdown("### Thông tin nhanh")
    st.markdown("- Nguồn dữ liệu: **Open-Meteo (API mở)**")
    st.markdown("- Dữ liệu: cập nhật theo thời gian thực khi bấm 'Lấy dữ liệu'")
    st.markdown("- Lưu ý: API miễn phí có giới hạn quota; nếu cần chạy xuất toàn bộ nhiều địa phương, hãy cấu hình tần suất hợp lý.")
    st.markdown("---")
    st.markdown("### Hướng dẫn sử dụng ngắn gọn")
    st.markdown("1. Chọn địa phương ở sidebar → bấm **Lấy dữ liệu**.  \n2. Xem biểu đồ/ bảng.  \n3. Bấm **Xuất CSV** để lưu dữ liệu (cột không dấu phù hợp Excel).")

# =========================
# Footer
# =========================
st.markdown(
    """
    <div class="fixed-footer">
    © 2025 Trường THPT Lê Quý Đôn – Long Bình Tân | Web app thu thập dữ liệu thời gian thực
    </div>
    """, unsafe_allow_html=True
)
