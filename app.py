import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Smart Irrigation", layout="wide")

# ---------- UI STYLE ----------
st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    text-align: center;
}
.title {
    font-size: 32px;
    font-weight: bold;
}
.subtitle {
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class="card">
    <div class="title">Good Morning, Sahil 👋</div>
    <div class="subtitle">Smart Irrigation System</div>
</div>
""", unsafe_allow_html=True)

st.write("")

# ---------- FILE UPLOAD ----------
file = st.file_uploader("Upload your CSV file", type="csv")

if file:
    # Fix encoding issue
    df = pd.read_csv(file, encoding='latin1')

    # Clean column names
    df.columns = df.columns.str.strip()

    # Show columns (optional debug)
    st.write("Detected Columns:", df.columns)

    # Auto-detect columns
    time_col = df.columns[0]
    soil_col = df.columns[1]
    temp_col = df.columns[2]
    hum_col = df.columns[3]

    # ---------- CARDS ----------
    col1, col2, col3 = st.columns(3)

    soil = df[soil_col].iloc[-1]
    temp = df[temp_col].iloc[-1]
    hum = df[hum_col].iloc[-1]

    col1.markdown(f"<div class='card'>🌱 Soil Moisture<br><h2>{soil}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'>🌡 Temperature<br><h2>{temp}°C</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'>💧 Humidity<br><h2>{hum}%</h2></div>", unsafe_allow_html=True)

    st.write("")

    # ---------- GRAPH ----------
    st.markdown("### 📈 Sensor Trends")
    st.line_chart(df.set_index(time_col)[[soil_col, temp_col, hum_col]])

    st.write("")

    # ---------- PUMP STATUS ----------
    if len(df.columns) >= 5:
        pump_col = df.columns[4]
        st.markdown("### 🚰 Pump Status")
        st.dataframe(df[[time_col, pump_col]], use_container_width=True)

else:
    st.info("Upload your CSV file to start")
