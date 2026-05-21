@st.cache_data
def load_data():
    df = pd.read_excel('factory_maintenance.xlsx', sheet_name='Sheet1')
    
    # 👇 YEH LINE JODHNI HAI (Purane naam : Naye naam)
    df['Machine_ID'] = df['Machine_ID'].replace({
        'CNC_Machine_09': 'Spinning Machine 01',
        'Compressor_01': 'Main Air Compressor',
        'HVAC_Unit_2': 'Humidification Plant 2'
    })
    
    df['Date'] = pd.to_datetime(df['Date'])
    df['Power_kW'] = (1.732 * df['Voltage'] * df['Current_Amps'] * 0.85) / 1000
    df['Energy_kWh'] = df['Power_kW'] * 2
    df['Hour'] = df['Date'].dt.hour
    return df
