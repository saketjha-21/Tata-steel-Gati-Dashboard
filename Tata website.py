# Tata website.py - Project GATI - Final Presentation Dashboard (Dark Theme Optimized)
import os
import time
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pydeck as pdk
from openpyxl import load_workbook
from datetime import datetime

# =====================================================================================
# 0. PAGE CONFIGURATION & STYLING
# =====================================================================================
st.set_page_config(
    page_title="Project GATI - Advanced Control Tower",
    page_icon="🚛",
    layout="wide",
)

# Centralized styling optimized for Streamlit's NATIVE DARK THEME.
st.markdown("""
    <style>
        .stMetric { border: 1px solid #444; border-radius: 10px; padding: 12px; text-align: center; }
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #1E2128; border-radius: 6px 6px 0px 0px; padding: 10px; }
        .stTabs [aria-selected="true"] { background-color: #0E1117; border-bottom: 3px solid #0487D9; }
        .stButton>button { width: 100%; }
        .small-font { font-size: 14px; color: #aaa; }
    </style>""", unsafe_allow_html=True)

# Central color palette for consistency
PALETTE = {
    "green": "#00A6A6", "orange": "#F29F05", "red": "#D94A4A",
    "blue": "#0487D9", "grey": "#2d3136"
}


# =====================================================================================
# 1. UTILITY FUNCTIONS
# =====================================================================================
def format_inr_cr(x):
    return f"₹{x:,.1f} Cr" if isinstance(x, (int, float)) else str(x)


def safe_float(x, default=0.0):
    return float(x) if x is not None else default


@st.cache_data
def read_named_ranges_from_excel(path):
    if not path or not os.path.exists(path): return {}
    try:
        wb = load_workbook(path, data_only=True)
        named_ranges = {}
        for name in wb.defined_names.definedName:
            for sheetname, coord in name.destinations:
                named_ranges[name.name] = wb[sheetname][coord.replace('$', '')].value
                break
        return named_ranges
    except Exception:
        return {}


# =====================================================================================
# 2. GATI DATA & LOGIC MODEL (The "Brain")
# =====================================================================================
class GATIModel:
    def __init__(self, seed=42, excel_named=None):
        np.random.seed(seed)
        self.excel_named = excel_named or {}
        self.truck_df = self._generate_truck_data()
        self.savings_df, self.base_assumptions = self._generate_financial_data()
        self.payback_df = self._calculate_payback(self.savings_df["Conservative (Cr)"].sum())

    def _generate_truck_data(self, num_trucks=150):
        routes = {
            "Jamshedpur -> Mumbai": {"start": (22.8046, 86.2029), "end": (19.0760, 72.8777)},
            "Jamshedpur -> Delhi": {"start": (22.8046, 86.2029), "end": (28.7041, 77.1025)},
            "Kalinganagar -> Hyderabad": {"start": (20.9729, 85.9329), "end": (17.3850, 78.4867)},
        }
        data = []
        for i in range(num_trucks):
            route_name, coords = list(routes.items())[i % len(routes)]
            progress = np.random.rand()
            lat = coords["start"][0] + (coords["end"][0] - coords["start"][0]) * progress
            lon = coords["start"][1] + (coords["end"][1] - coords["start"][1]) * progress
            status = np.random.choice(["On-Time", "At-Risk", "Delayed"], p=[0.7, 0.2, 0.1])
            data.append({
                "truck_id": f"TS-{(i + 1):04d}", "lat": lat, "lon": lon, "status": status, "route": route_name,
                "speed_kmh": int(np.random.randint(40, 80) if status != "Delayed" else np.random.randint(5, 30)),
                "eta_delay_min": int(np.random.randint(60, 240) if status == "Delayed" else (
                    np.random.randint(10, 30) if status == "At-Risk" else 0)),
                "issue": np.random.choice(
                    ["Heavy Traffic", "Maintenance Alert", "Harsh Braking"]) if status != "On-Time" else "No Issues",
                "driver_name": f"Driver {101 + i}", "last_seen": f"{np.random.randint(1, 5)} min ago"
            })
        return pd.DataFrame(data)

    def _generate_financial_data(self):
        savings_df = pd.DataFrame({
            "Savings Lever": ["Pillar 1 - Digital Yard (TAT)", "Pillar 2 - Network (Backhaul)",
                              "Pillar 2 - Network (Fuel)", "Multimodal Shift (Pilot)", "Pillar 3 - Driver (Direct)"],
            "Conservative (Cr)": [84.0, 208.0, 78.0, 50.0, 0.0],
            "Base (Cr)": [134.4, 208.0, 78.0, 75.0, 20.0],
            "Upside (Cr)": [147.0, 312.0, 98.0, 100.0, 50.0]
        })
        base_assumptions = {
            "tat_reduction_hrs": safe_float(self.excel_named.get("TAT_Saved_Base", 3.2)),
            "empty_mile_reduction_pct": safe_float(self.excel_named.get("Empty_Waste_Capture_Base", 57.0)),
            "fuel_efficiency_gain_pct": safe_float(self.excel_named.get("Fuel_Gain_Base_Pct", 8.0)),
            "annual_trips": int(safe_float(self.excel_named.get("Annual_Trips", 420000))),
            "hourly_cost": int(safe_float(self.excel_named.get("Hourly_Cost", 1000))),
            "empty_return_waste_cr": safe_float(self.excel_named.get("Empty_Return_Waste_Cr", 364)),
            "annual_fuel_spend_cr": safe_float(self.excel_named.get("Annual_Fuel_Spend_Cr", 980))
        }
        return savings_df, base_assumptions

    def _calculate_payback(self, conservative_savings_total):
        df = pd.DataFrame({"Year": [0, 1, 2, 3]})
        df["Annual Savings (Cr)"] = [0, conservative_savings_total * 0.3, conservative_savings_total * 0.6,
                                     conservative_savings_total * 0.9]
        df["Net Cash Flow (Cr)"] = df["Annual Savings (Cr)"] + [0, -8.0, -9.0, -9.0]
        df.loc[0, "Net Cash Flow (Cr)"] = -2.25
        df.loc[1, "Net Cash Flow (Cr)"] -= (10.0 - 2.25)
        df.loc[2, "Net Cash Flow (Cr)"] -= (13.5 - 10.0)
        df["Cumulative Cash Flow (Cr)"] = df["Net Cash Flow (Cr)"].cumsum()
        return df

    def update_live_data(self):
        deltas = np.random.uniform(-0.02, 0.02, size=(len(self.truck_df), 2))
        self.truck_df[['lat', 'lon']] += deltas
        idx = np.random.choice(self.truck_df.index, size=3, replace=False)
        self.truck_df.loc[idx, "status"] = np.random.choice(["On-Time", "At-Risk", "Delayed"], size=3,
                                                            p=[0.5, 0.3, 0.2])

    def calculate_what_if_savings(self, tat_saved, empty_capture_pct, fuel_gain_pct):
        tat_s = (self.base_assumptions['annual_trips'] * tat_saved * self.base_assumptions['hourly_cost']) / 1_00_00_000
        backhaul_s = self.base_assumptions['empty_return_waste_cr'] * (empty_capture_pct / 100)
        fuel_s = self.base_assumptions['annual_fuel_spend_cr'] * (fuel_gain_pct / 100)
        return tat_s, backhaul_s, fuel_s


# =====================================================================================
# 3. INITIALIZATION & SESSION STATE
# =====================================================================================
excel_path = next((p for p in ["./Project_GATI_Financial_Model_v5.xlsx", "Project_GATI_Financial_Model_v5.xlsx"] if
                   os.path.exists(p)), None)
if 'model' not in st.session_state:
    excel_data = read_named_ranges_from_excel(excel_path)
    st.session_state.model = GATIModel(excel_named=excel_data)
model = st.session_state.model

# =====================================================================================
# 4. SIDEBAR CONTROLS
# =====================================================================================
with st.sidebar:
    st.image("https://logodownload.org/wp-content/uploads/2014/09/tata-steel-logo-0.png",
             use_column_width=True)  # White logo for dark theme
    st.title("Controls & Scenarios")

    st.subheader("Live Simulation")
    live_mode = st.toggle("Activate Live Mode", value=False, help="Simulates real-time data updates.")
    st.divider()

    st.subheader("Financial Scenario")
    scenario_options = ["Base", "Conservative", "Upside"]
    selected_scenario = st.selectbox("Select a Scenario", options=scenario_options, index=0)

    with st.expander("View/Edit Scenario Assumptions"):
        assumptions = model.base_assumptions
        st.markdown(f"""
        - **Annual Trips:** `{assumptions['annual_trips']:,}`
        - **Hourly Truck Cost:** `₹{assumptions['hourly_cost']:,}`
        - **Annual Empty Return Waste:** `{format_inr_cr(assumptions['empty_return_waste_cr'])}`
        - **Annual Fuel Spend:** `{format_inr_cr(assumptions['annual_fuel_spend_cr'])}`
        """)
    st.divider()

    if excel_path:
        with open(excel_path, "rb") as f:
            st.download_button("⬇️ Download Full Financial Model", f, file_name=os.path.basename(excel_path))
    else:
        st.info("Place `Project_GATI_Financial_Model_v5.xlsx` in this folder to enable download.")

# =====================================================================================
# 5. MAIN DASHBOARD LAYOUT
# =====================================================================================
st.title("🚛 Project GATI: Advanced Logistics Control Tower")

tabs = st.tabs([
    "📈 **Control Tower Overview**", "💰 **Financial Modeler & ROI**",
    "🏭 **Pillar 1: Digital Yard**", "🌐 **Pillar 2: Intelligent Network**",
    "👷 **Pillar 3: Empowered Driver**"
])

# --- TAB 1: CONTROL TOWER OVERVIEW ---
with tabs[0]:
    if live_mode:
        model.update_live_data()
        st.toast(f"Live data refreshed at {datetime.now().strftime('%H:%M:%S')}", icon="🛰️")

    map_col, details_col = st.columns([2.5, 1.5])
    with map_col:
        st.subheader("Live Fleet Map")
        COLOR_MAP = {"On-Time": [0, 166, 166, 180], "At-Risk": [242, 159, 5, 180], "Delayed": [217, 74, 74, 180]}
        data_copy = model.truck_df.copy()
        data_copy['color'] = data_copy['status'].map(COLOR_MAP)
        view_state = pdk.ViewState(latitude=22.8, longitude=82.5, zoom=4.2, pitch=45)
        layer = pdk.Layer(
            "ScatterplotLayer", data=data_copy, get_position='[lon, lat]', get_fill_color='color',
            get_radius=8000, pickable=True, auto_highlight=True
        )
        tooltip = {"html": "<b>Truck ID:</b> {truck_id}<br/><b>Status:</b> {status}<br/><b>Route:</b> {route}"}
        # DARK theme for map base layer
        deck = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip, map_style="dark")
        st.pydeck_chart(deck, use_container_width=True)

    with details_col:
        st.subheader("Operational Drill-Down")
        at_risk_trucks = model.truck_df[model.truck_df['status'] != "On-Time"]
        selected_truck_id = st.selectbox("Select At-Risk/Delayed Truck", options=at_risk_trucks['truck_id'],
                                         index=0 if not at_risk_trucks.empty else None, placeholder="No at-risk trucks")

        if selected_truck_id:
            truck_info = at_risk_trucks.loc[at_risk_trucks['truck_id'] == selected_truck_id].iloc[0]
            st.warning(f"**Details for {truck_info['truck_id']}** (Status: {truck_info['status']})")
            c1, c2 = st.columns(2)
            c1.metric("Current Speed", f"{truck_info['speed_kmh']} km/h")
            c2.metric("ETA Delay", f"{truck_info['eta_delay_min']} mins")
            st.markdown(f"""<p class="small-font">
                <b>Route:</b> {truck_info['route']}<br>
                <b>Driver:</b> {truck_info['driver_name']}<br>
                <b>Alert:</b> {truck_info['issue']}<br>
                <b>Last Update:</b> {truck_info['last_seen']}
            </p>""", unsafe_allow_html=True)
            if st.button("Propose Corrective Action", key=f"action_{truck_info['truck_id']}"):
                st.success(
                    f"Action plan initiated for {truck_info['truck_id']}: Driver contacted, alternate route suggested.")

# --- TAB 2: FINANCIAL MODELER & ROI ---
with tabs[1]:
    st.header("Interactive Financial Modeler")
    st.info("Adjust the sliders to model performance outcomes and see the impact on annual savings.")

    c1, c2, c3 = st.columns(3)
    tat_saved = c1.slider("Avg. TAT Reduction (Hours)", 0.0, 5.0, model.base_assumptions['tat_reduction_hrs'], 0.1,
                          help="Base case: 3.2 hrs")
    empty_capture = c2.slider("Empty Mile Waste Captured (%)", 0, 100,
                              int(model.base_assumptions['empty_mile_reduction_pct']), 1, help="Base case: 57%")
    fuel_gain = c3.slider("Fuel Efficiency Gain (%)", 0, 15, int(model.base_assumptions['fuel_efficiency_gain_pct']), 1,
                          help="Base case: 8%")

    tat_s, backhaul_s, fuel_s = model.calculate_what_if_savings(tat_saved, empty_capture, fuel_gain)
    total_s = tat_s + backhaul_s + fuel_s

    st.metric(f"**Total Projected Annual Savings**", format_inr_cr(total_s),
              f"{format_inr_cr(total_s - model.savings_df['Base (Cr)'].sum())} vs. Base Case")

    st.subheader("Project Payback Period (Conservative Basis)")
    fig_pay = go.Figure()
    fig_pay.add_trace(go.Bar(x=model.payback_df['Year'], y=model.payback_df['Net Cash Flow (Cr)'], name='Net Cash Flow',
                             marker_color=[PALETTE['red'] if v < 0 else PALETTE['green'] for v in
                                           model.payback_df['Net Cash Flow (Cr)']]))
    fig_pay.add_trace(go.Scatter(x=model.payback_df['Year'], y=model.payback_df['Cumulative Cash Flow (Cr)'],
                                 name='Cumulative Cash Flow', mode='lines+markers',
                                 line=dict(color=PALETTE['blue'], width=3)))
    fig_pay.add_hline(y=0)
    fig_pay.update_layout(title_text="Project Cash Flow & Payback", template="plotly_dark")  # Dark theme for chart
    st.plotly_chart(fig_pay, use_container_width=True)

# --- TABS 3, 4, 5: THE PILLARS ---
with tabs[2]:
    st.header("Pillar 1: The Digital Yard")
    st.metric("Base Case Savings (Pillar 1)", format_inr_cr(model.savings_df.loc[0, "Base (Cr)"]))
    with st.expander("How GATI Achieves This"):
        st.markdown(
            "- **Smart Gates:** ANPR/RFID cuts gate processing from minutes to < 60 seconds.\n- **AI-Powered YMS:** A 'Digital Twin' of the yard performs dynamic dock assignments.\n- **Pre-Arrival Slot Booking:** Eliminates idle waiting by allowing carriers to book appointments.")
    tat_trend = pd.DataFrame(
        {"Date": pd.date_range(end=datetime.today(), periods=30), "Before GATI": np.random.normal(10.5, 0.8, 30),
         "After GATI": np.random.normal(7.0, 0.3, 30)})
    fig = go.Figure([go.Scatter(x=tat_trend['Date'], y=tat_trend['Before GATI'], name='Before',
                                line=dict(dash='dash', color='firebrick')),
                     go.Scatter(x=tat_trend['Date'], y=tat_trend['After GATI'], name='After',
                                line=dict(color=PALETTE['blue']))])
    fig.update_layout(title="Jamshedpur Pilot: TAT Trend (Hours)", template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

with tabs[3]:
    st.header("Pillar 2: The Intelligent Network")
    p2_savings = model.savings_df.loc[model.savings_df['Savings Lever'].str.contains("Pillar 2"), "Base (Cr)"].sum()
    st.metric("Base Case Savings (Pillar 2)", format_inr_cr(p2_savings))
    with st.expander("How GATI Achieves This"):
        st.markdown(
            "- **NDFE Integration:** Connects return trips with available loads from major shippers, attacking the 70% empty mile problem.\n- **Dynamic AI Routing:** Analyzes real-time traffic, weather, and fuel prices to find the most efficient route.")
    labels, before, after = ['Fuel', 'Vehicle/Driver', 'Empty Returns', 'Tolls & Other'], [35, 30, 13, 22], [32, 30, 4,
                                                                                                             21]
    c1, c2 = st.columns(2)
    fig1 = go.Figure(data=[go.Pie(labels=labels, values=before, hole=.4, title="Cost Structure: Before GATI")])
    fig2 = go.Figure(data=[go.Pie(labels=labels, values=after, hole=.4, title="Cost Structure: After GATI")])
    fig1.update_layout(template='plotly_dark')
    fig2.update_layout(template='plotly_dark')
    c1.plotly_chart(fig1, use_container_width=True)
    c2.plotly_chart(fig2, use_container_width=True)

with tabs[4]:
    st.header("Pillar 3: The Empowered Driver")
    p3_savings = model.savings_df.loc[model.savings_df['Savings Lever'].str.contains("Pillar 3"), "Base (Cr)"].sum()
    st.metric("Base Case Value (Pillar 3)", format_inr_cr(p3_savings))
    with st.expander("How GATI Achieves This"):
        st.markdown(
            "- **Driver Mobile App:** Provides navigation, e-POD for faster payments, and a transparent earnings dashboard.\n- **Telematics-Driven Incentives:** Safety, fuel efficiency, and on-time performance are measured objectively and linked to bonuses.\n- **AI-Optimized Rostering:** Balances network cost with driver 'Time at Home' to reduce attrition.")
    drv = pd.DataFrame(
        {"Driver ID": [f"DRV{100 + i}" for i in range(25)], "Safety Score": np.random.randint(80, 100, 25),
         "On-Time %": np.random.randint(90, 101, 25)}).sort_values("Safety Score", ascending=False)
    st.dataframe(drv.head(10), use_container_width=True)

# --- Live Mode Rerun Logic ---
if live_mode:
    time.sleep(3)
    st.rerun()