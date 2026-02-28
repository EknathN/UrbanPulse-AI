import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# AUTO REFRESH EVERY 2 SECONDS
# -----------------------------
st_autorefresh(interval=2000, key="datarefresh")

st.set_page_config(page_title="UrbanPulse AI", layout="wide")

st.title("🏙️ UrbanPulse AI - Smart City Intelligence Dashboard")
st.markdown("---")

# -----------------------------
# FILE READER FUNCTION
# -----------------------------
def read_file(filename):
    try:
        with open(filename, "r") as f:
            return f.read().strip()
    except:
        return "0"

# -----------------------------
# READ LIVE DATA
# -----------------------------
vehicle_count = int(read_file("vehicle_count.txt"))
helmet_status = read_file("helmet_status.txt")
litter_status = read_file("litter_status.txt")

helmet_detected = helmet_status == "1"
litter_detected = litter_status == "1"

# -----------------------------
# SIGNAL LOGIC
# -----------------------------
if vehicle_count > 20:
    green_time = 70
    traffic_status = "🔴 High Traffic"
elif vehicle_count > 10:
    green_time = 50
    traffic_status = "🟡 Medium Traffic"
else:
    green_time = 30
    traffic_status = "🟢 Smooth Traffic"

# -----------------------------
# ENVIRONMENT CALCULATIONS
# -----------------------------
fuel_saved = green_time * 0.05
co2_reduced = fuel_saved * 2.3

# -----------------------------
# TOP STATUS CARDS
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🚗 Vehicle Count", vehicle_count)
    st.write(traffic_status)

with col2:
    st.metric("🚦 Green Signal Time (sec)", green_time)

with col3:
    if helmet_detected:
        st.error("🪖 Helmet Violation Detected")
    else:
        st.success("🪖 Helmet Status: OK")

with col4:
    if litter_detected:
        st.error("🗑️ Littering Detected")
    else:
        st.success("🗑️ Area Clean")

st.markdown("---")

# -----------------------------
# ENVIRONMENT SECTION
# -----------------------------
st.subheader("🌱 Environmental Impact")

col5, col6 = st.columns(2)

with col5:
    st.metric("Fuel Saved (Liters)", f"{fuel_saved:.2f}")

with col6:
    st.metric("CO₂ Reduced (kg)", f"{co2_reduced:.2f}")

st.markdown("---")

# -----------------------------
# ALERT PANEL
# -----------------------------
st.subheader("🚨 Smart Alerts")

if helmet_detected or litter_detected:
    st.warning("⚠️ Active Violations Detected in Monitoring Zone")
else:
    st.success("✅ No Active Violations")

st.markdown("---")

# -----------------------------
# LIVE TRAFFIC GRAPH
# -----------------------------
st.subheader("📊 Live Traffic Snapshot")

data = pd.DataFrame({
    "Time": [datetime.now()],
    "Vehicle Count": [vehicle_count]
})

st.line_chart(data.set_index("Time"))

st.markdown("---")
st.caption("UrbanPulse AI | Real-Time Smart City Monitoring System")