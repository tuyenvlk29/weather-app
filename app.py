# ===========================
# 2️⃣ Khung cấu hình (ô checkbox chữ trắng rõ ràng, dễ đọc)
# ===========================

# CSS tùy chỉnh màu chữ cho checkbox
st.markdown("""
<style>
/* Đổi màu chữ ô checkbox thành trắng cho dễ đọc trên nền xanh */
div[data-testid="stCheckbox"] label p {
    color: white !important;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# Bắt đầu khung cấu hình
st.markdown('<div class="frame config-frame">', unsafe_allow_html=True)

# Tiêu đề phụ cho phần cấu hình
st.subheader("⚙️ Cấu hình")

# Danh sách chọn tỉnh/thành
selected_place = st.selectbox(
    "Chọn tỉnh/thành:",
    options=list(PROVINCES_34.keys())
)

# Chọn thông số hiển thị
st.markdown("Chọn thông số hiển thị:")
params_default = [
    "Nhiệt độ (°C)",
    "Độ ẩm (%)",
    "Lượng mưa (mm)",
    "Tốc độ gió (m/s)",
    "Chỉ số UV"
]
selected_params = st.multiselect(
    "Thông số",
    options=params_default,
    default=params_default[:4]
)

# Ô checkbox hiển thị rõ, chữ trắng sáng
allow_csv = st.checkbox("Cho phép xuất CSV (cột không dấu)", value=True)

# Kết thúc khung cấu hình
st.markdown('</div>', unsafe_allow_html=True)
