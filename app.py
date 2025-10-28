# app.py
# Streamlit app: Ứng dụng thu thập dữ liệu thời tiết thời gian thực cho 34 tỉnh/thành (theo yêu cầu Thầy)
# API template (do Thầy cung cấp):
# https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,relative_humidity_2m,precipitation

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time
import json

st.set_page_config(page_title="Thời tiết thời gian thực - THPT Lê Quý Đôn", layout="wide")

# ---------- CSS footer cố định ----------
st.markdown("""
<style>
.fixed-footer {
  position: fixed;
  left: 0;
  bottom: 0;
  width: 100%;
  text-align: center;
  background-color: rgba(230,240,255,0.95);
  color: #000;
  padding: 8px 0;
  font-size: 14px;
  border-top: 1px solid #d0d7e6;
  z-index: 9999;
}
.stApp { margin-bottom: 70px; }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.title("🌦 Ứng dụng Thời tiết Thời gian thực — THPT Lê Quý Đôn")
st.markdown("Ứng dụng dùng API Open-Meteo (theo mẫu do Thầy cung cấp) — lấy Nhiệt độ, Tốc độ gió, Độ ẩm, Lượng mưa.")

# ---------- Load default 34 tỉnh/thành ----------
try:
    df_places = pd.read_csv("/mnt/data/34_tinh_thanh.csv")
except Exception:
    # fallback embedded list if file not found
    data = [
        ("An Giang", 10.3692, 105.4389),
        ("Bắc Ninh", 21.1867, 106.0833),
        ("Cà Mau", 9.1741, 105.1520),
        ("Đắk Lắk", 12.6667, 108.0500),
        ("Đồng Nai", 10.9468, 106.8240),
        ("Đồng Tháp", 10.5326, 105.6740),
        ("Gia Lai", 13.9833, 108.0000),
        ("Hưng Yên", 20.6597, 106.0704),
        ("Khánh Hòa", 12.2388, 109.1967),
        ("Lào Cai", 22.4833, 103.9667),
        ("Lâm Đồng", 11.9404, 108.4583),
        ("Ninh Bình", 20.2510, 105.9743),
        ("Phú Thọ", 21.3579, 103.8333),
        ("Quảng Ngãi", 15.1217, 108.8011),
        ("Quảng Trị", 16.7445, 107.1839),
        ("Tây Ninh", 11.3333, 106.1667),
        ("Thái Nguyên", 21.5926, 105.8432),
        ("Tuyên Quang", 21.8236, 105.2190),
        ("Vĩnh Long", 10.2442, 105.9716),
        ("Cần Thơ", 10.0452, 105.7469),
        ("Đà Nẵng", 16.0544, 108.2022),
        ("Hải Phòng", 20.8449, 106.6881),
        ("TP. Hồ Chí Minh", 10.8231, 106.6297),
        ("Cao Bằng", 22.6667, 106.2500),
        ("Điện Biên", 21.3856, 103.0239),
        ("Hà Tĩnh", 18.3432, 105.9057),
        ("Lai Châu", 22.3833, 103.9333),
        ("Lạng Sơn", 21.8468, 106.7585),
        ("Nghệ An", 19.2676, 105.9789),
        ("Quảng Ninh", 21.0138, 107.9572),
        ("Thanh Hóa", 19.8050, 105.3421),
        ("Sơn La", 21.3256, 103.9149),
        ("Hà Nội", 21.0285, 105.8542),
        ("Huế", 16.4637, 107.5909)
    ]
    df_places = pd.DataFrame(data, columns=["name", "lat", "lon"])

st.sidebar.header("Cấu hình")
uploaded = st.sidebar.file_uploader("Upload file danh sách (CSV: name,lat,lon) — tuỳ chọn", type=["csv"])
if uploaded:
    try:
        df_uploaded = pd.read_csv(uploaded)
        df_places = df_uploaded[["name","lat","lon"]]
        st.sidebar.success(f"Đã load {len(df_places)} địa phương từ file upload.")
    except Exception as e:
        st.sidebar.error(f"Lỗi đọc file upload: {e}")

# ---------- Sidebar controls ----------
st.sidebar.markdown("---")
st.sidebar.markdown("Chọn tỉnh/thành (một hoặc nhiều):")
choices = list(df_places["name"].astype(str))
selected = st.sidebar.multiselect("Chọn (multi) — hoặc chọn 1 ở main:", choices, default=[choices[0]])

st.sidebar.markdown("---")
st.sidebar.markdown("Tuỳ chọn xuất dữ liệu:")
export_csv = st.sidebar.checkbox("Cho phép xuất CSV", value=True)
export_json = st.sidebar.checkbox("Cho phép xuất JSON", value=True)

# ---------- Main selection ----------
st.subheader("Chọn 1 tỉnh/thành (tùy chọn):")
sel_single = st.selectbox("Hoặc chọn 1:", ["-- Không chọn --"] + choices)

# Merge selections
places = selected.copy()
if sel_single and sel_single != "-- Không chọn --" and sel_single not in places:
    places.append(sel_single)

if not places:
    st.info("Vui lòng chọn ít nhất một tỉnh/thành (từ sidebar hoặc ô chọn).")

# ---------- Helper: call API per coordinate ----------
API_TEMPLATE = "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,relative_humidity_2m,precipitation"

def call_open_meteo_current(lat, lon, timeout=10):
    url = API_TEMPLATE.format(lat=lat, lon=lon)
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# ---------- Fetch button ----------
if st.button("🌍 Lấy dữ liệu hiện tại"):
    results = []
    progress = st.progress(0)
    n = len(places)
    for i, pname in enumerate(places):
        row = df_places[df_places["name"].astype(str) == pname].iloc[0]
        lat, lon = row["lat"], row["lon"]
        st.info(f"Lấy dữ liệu: {pname} — vĩ độ={lat}, kinh độ={lon}")
        js = call_open_meteo_current(lat, lon)
        if "error" in js:
            st.error(f"Lỗi API cho {pname}: {js['error']}")
            continue
        current = js.get("current_weather") or js.get("current") or js.get("current_weather", {})
        # The API template returns 'current_weather' for some fields; else the JSON may include 'current'
        # However our explicit query uses 'current=' params; Open-Meteo sometimes places them under 'current_weather' or 'current'
        # We'll try several locations
        # First check top-level 'current_weather' keys
        temp = None; wind = None; hum = None; precip = None
        # Preferred locations for values:
        # 1) js.get("current_weather") contains temperature and windspeed (but not always humidity/precip)
        if "current_weather" in js:
            cw = js["current_weather"]
            temp = cw.get("temperature") or cw.get("temperature_2m")
            wind = cw.get("windspeed") or cw.get("wind_speed_10m")
        # 2) js.get("current") may contain explicit fields
        if "current" in js:
            c = js["current"]
            temp = temp if temp is not None else c.get("temperature_2m") or c.get("temperature")
            wind = wind if wind is not None else c.get("wind_speed_10m") or c.get("wind_speed")
            hum = c.get("relative_humidity_2m") or c.get("humidity")
            precip = c.get("precipitation") or c.get("precip")
        # 3) js.get('hourly') with 'time' equal to now (fallback)
        if temp is None or wind is None:
            hourly = js.get("hourly", {})
            times = hourly.get("time", [])
            if times:
                # find last index
                idx = len(times)-1
                try:
                    temp = temp or hourly.get("temperature_2m", [None]*len(times))[idx]
                    hum = hum or hourly.get("relative_humidity_2m", [None]*len(times))[idx]
                    precip = precip or hourly.get("precipitation", [None]*len(times))[idx]
                    wind = wind or hourly.get("wind_speed_10m", [None]*len(times))[idx]
                except Exception:
                    pass
        # Compose result
        rec = {
            "Địa phương": pname,
            "lat": lat,
            "lon": lon,
            "Thời gian lấy": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Nhiệt độ (°C)": temp,
            "Tốc độ gió (m/s)": wind,
            "Độ ẩm (%)": hum,
            "Lượng mưa (mm)": precip,
            "API_called": API_TEMPLATE.format(lat=lat, lon=lon)
        }
        results.append(rec)
        progress.progress(int((i+1)/n*100))
        time.sleep(0.2)  # avoid hammering the API

    if results:
        df_res = pd.DataFrame(results)
        st.subheader("Kết quả hiện tại")
        st.dataframe(df_res, use_container_width=True)
        # Export options
        if export_csv:
            st.download_button("💾 Tải CSV", df_res.to_csv(index=False).encode("utf-8-sig"),
                               file_name=f"weather_now_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                               mime="text/csv")
        if export_json:
            st.download_button("💾 Tải JSON", df_res.to_json(orient="records", force_ascii=False).encode("utf-8"),
                               file_name=f"weather_now_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                               mime="application/json")
        st.success("Hoàn tất thu thập dữ liệu hiện tại.")
    else:
        st.warning("Không có dữ liệu hợp lệ thu thập được. Vui lòng kiểm tra kết nối mạng hoặc danh sách tỉnh/thành.")

# ---------- Footer ----------
st.markdown("""
<div class="fixed-footer">
© 2025 Trường THPT Lê Quý Đôn – Long Bình Tân | Web app thu thập dữ liệu thời gian thực
</div>
""", unsafe_allow_html=True)
