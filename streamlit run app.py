import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. Page Config (Poori screen use karne ke liye)
st.set_page_config(layout="wide")
st.title("🏭 Factory Maintenance & Electrical Load Analyzer")
st.write("Welcome Chief Engineer! Live data, breakdown log aur energy consumption yahan dekhein.")

# 2. Data Load Pipeline (With Power Calculations)
@st.cache_data
def load_data():
    df = pd.read_excel('factory_maintenance.xlsx', sheet_name='Sheet1')
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Three-Phase Power Formula: (√3 * V * I * PF) / 1000  [Standard PF = 0.85]
    df['Power_kW'] = (1.732 * df['Voltage'] * df['Current_Amps'] * 0.85) / 1000
    # Readings har 2 ghante par hain, toh Hours = 2
    df['Energy_kWh'] = df['Power_kW'] * 2
    df['Hour'] = df['Date'].dt.hour
    return df

df = load_data()

# 3. SIDEBAR: Settings & Filters
st.sidebar.header("⚙️ Dashboard Settings")

# Machine Selection Filter
machine_list = ['All'] + list(df['Machine_ID'].unique())
selected_machine = st.sidebar.selectbox("Select Machine ID", machine_list)

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Load Thresholds")
# Target load threshold change karne ke liye slider
capacity_threshold = st.sidebar.slider("Panel Capacity Limit (kW)", min_value=10.0, max_value=50.0, value=35.0, step=1.0)
electricity_rate = st.sidebar.number_input("Rate (₹ / kWh)", min_value=1.0, value=8.0, step=0.5)

# Data filtering based on machine selection
if selected_machine != 'All':
    filtered_df = df[df['Machine_ID'] == selected_machine]
else:
    filtered_df = df

# 4. MAIN SCREEN: KPI Metrics Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="📊 Total Logs", value=len(filtered_df))
with col2:
    st.metric(label="🛑 Total Downtime", value=f"{int(filtered_df['Downtime_Mins'].sum())} Mins")
with col3:
    # Celsius Bug Fix check karein (.1f}°C)
    st.metric(label="🌡️ Avg Temperature", value=f"{filtered_df['Temperature_C'].mean():.1f}°C")
with col4:
    total_bill = filtered_df['Energy_kWh'].sum() * electricity_rate
    st.metric(label="💰 Est. Bill (Selected)", value=f"₹{total_bill:,.0f}")

st.markdown("---")

# 5. CHARTS ROW 1: Temperature & Load Curve
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader(f"📈 Temperature Trend: {selected_machine}")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(filtered_df['Date'].head(50), filtered_df['Temperature_C'].head(50), color='orange', marker='o')
    ax.axhline(y=80, color='red', linestyle='--', label='Danger Alert (80°C)')
    ax.set_ylabel("Temperature (°C)")
    plt.xticks(rotation=30)
    ax.legend()
    st.pyplot(fig)

with chart_col2:
    st.subheader("🕒 24-Hour Average Load Curve")
    hourly_load = filtered_df.groupby('Hour')['Power_kW'].mean()
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    hourly_load.plot(kind='line', marker='s', color='blue', linewidth=2, ax=ax2)
    ax2.axhline(y=capacity_threshold, color='red', linestyle='--', label=f'Limit ({capacity_threshold} kW)')
    ax2.set_ylabel("Power Demand (kW)")
    ax2.set_xlabel("Hour of Day (0-23)")
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend()
    st.pyplot(fig2)

st.markdown("---")

# 6. ROW 2: Failure Analysis & Overload Log Table
data_col1, data_col2 = st.columns([1, 2])

with data_col1:
    st.subheader("⚠️ Failure Breakup")
    failure_counts = filtered_df['Failure_Type'].value_counts()
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    failure_counts.plot(kind='bar', color='darkred', ax=ax3)
    plt.xticks(rotation=45)
    st.pyplot(fig3)

with data_col2:
    st.subheader("📋 Detected Overload Log Data")
    overload_data = filtered_df[filtered_df['Power_kW'] > capacity_threshold][['Date', 'Machine_ID', 'Voltage', 'Current_Amps', 'Power_kW']]
    if not overload_data.empty:
        st.dataframe(overload_data.sort_values(by='Power_kW', ascending=False), use_container_width=True)
    else:
        st.success("Mubarak ho! Is machine/limit par koi overload event nahi mila.")