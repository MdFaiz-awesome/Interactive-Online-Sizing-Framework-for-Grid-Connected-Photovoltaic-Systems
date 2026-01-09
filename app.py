import streamlit as st
import math
import time
import base64

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="PV Sizing Tool",
    page_icon="🔆",
    layout="wide"
)

# =====================================================
# SESSION STATE
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "welcome"

for key in ["total_modules", "total_power", "total_energy"]:
    if key not in st.session_state:
        st.session_state[key] = None


def go(page):
    st.session_state.page = page
    st.rerun()


# =====================================================
# BACKGROUND IMAGE
# =====================================================
def apply_background():
    try:
        with open("bg.png", "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except:
        pass


# =====================================================
# UI HELPERS
# =====================================================
def section_box(title, subtitle="", color="#4A90E2"):
    st.markdown(
        f"""
        <div style="
            padding:18px;
            background:#f9fafc;
            border-left:6px solid {color};
            border-radius:10px;
            margin-bottom:20px;">
            <h3>{title}</h3>
            <p style="margin-bottom:0;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# PAGE 1: WELCOME
# =====================================================
if st.session_state.page == "welcome":

    apply_background()

    st.markdown(
        """
        <div style="
        text-align:center;
        padding:45px;
        background:rgba(255,255,255,0.9);
        border-radius:14px;">
            <h1>Interactive Online Sizing Framework</h1>
            <h3>for Grid-Connected Photovoltaic Systems</h3>
            <p style="font-size:18px;">
                Professional engineering tool for large-scale PV system design
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Start PV Sizing Tool", use_container_width=True):
        with st.spinner("Initializing system..."):
            time.sleep(1.2)
        go("part_a")


# =====================================================
# PAGE 2: PART A
# =====================================================
elif st.session_state.page == "part_a":

    st.title("📘 Part A: PV Module & Layout Sizing")
    st.markdown("---")

    # ---------------- Step 1 ----------------
    section_box(
        "Step 1: PV Module Parameters",
        "Define electrical and physical characteristics of the PV module."
    )

    col1, col2 = st.columns(2)

    with col1:
        panel_length = st.number_input("Panel Length (m)", value=2.382)
        panel_width = st.number_input("Panel Width (m)", value=1.134)
        rated_power = st.number_input("Rated Power (W)", value=605)

    with col2:
        T_coef = st.number_input("Temperature Coefficient (%/°C)", value=-0.28)
        T_mod = st.number_input("Module Temperature (°C)", value=55)
        T_ref = st.number_input("Reference Temperature (°C)", value=25)
        f_mm = st.number_input("Mismatch Factor", value=0.97)
        f_deg = st.number_input("Degradation Factor", value=0.975)
        psh = st.number_input("Peak Sun Hours (h/day)", value=4.0)

    panel_area = panel_length * panel_width
    f_temp = 1 + (T_coef / 100) * (T_mod - T_ref)

    power_density = (rated_power * f_mm * f_temp * f_deg) / panel_area
    energy_density = (psh * 365 * rated_power *
                      f_mm * f_temp * f_deg) / panel_area / 1000

    st.markdown("#### 📊 Module Performance Results")
    colA, colB = st.columns(2)
    colA.metric("Power Density (W/m²)", f"{power_density:.2f}")
    colB.metric("Energy Density (kWh/m²/year)", f"{energy_density:.2f}")

    # ---------------- Step 2 ----------------
    st.markdown("---")
    section_box(
        "Step 2: Site Layout Constraint",
        "Determine maximum installable PV modules based on site dimensions."
    )

    site_width = st.number_input("Site Width (m)", value=45.74)
    site_length = st.number_input("Site Length (m)", value=115.88)
    gap = st.number_input("Inter-module Gap (m)", value=0.01)

    N_land = math.floor(site_width / (panel_width + gap)) * \
             math.floor(site_length / (panel_length + gap))
    N_port = math.floor(site_width / (panel_length + gap)) * \
             math.floor(site_length / (panel_width + gap))

    if N_land >= N_port:
        best_orientation = "Landscape"
        best_modules = N_land
    else:
        best_orientation = "Portrait"
        best_modules = N_port

    total_power = power_density * best_modules
    total_energy = energy_density * best_modules

    st.session_state.total_modules = best_modules
    st.session_state.total_power = total_power
    st.session_state.total_energy = total_energy

    st.success(f"Best Orientation: **{best_orientation}**")
    colS1, colS2, colS3 = st.columns(3)
    colS1.metric("Total PV Modules", best_modules)
    colS2.metric("Total Peak Power (W)", f"{total_power:,.2f}")
    colS3.metric("Total Energy (kWh/year)", f"{total_energy:,.2f}")

    st.markdown("---")

    if st.button("➡️ Proceed to Part B: Inverter Sizing", use_container_width=True):
        go("part_b")


# =====================================================
# PAGE 3: PART B
# =====================================================
elif st.session_state.page == "part_b":

    st.title("📕 Part B: Central Inverter Sizing")
    st.markdown("---")

    # ---------------- Summary ----------------
    section_box(
        "Summary of Part A",
        "Overall PV system capacity derived from module and layout sizing.",
        "#28a745"
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Total PV Modules", st.session_state.total_modules)
    c2.metric("Total Peak Power (W)", f"{st.session_state.total_power:,.2f}")
    c3.metric("Total Yearly Energy (kWh)", f"{st.session_state.total_energy:,.2f}")

    # ---------------- Step 1 ----------------
    st.markdown("---")
    section_box(
        "Step 1: DC/AC Ratio Selection",
        "Define inverter oversizing strategy."
    )

    dc_ac = st.number_input("DC/AC Ratio", value=1.2)

    # ---------------- Step 2 ----------------
    st.markdown("---")
    section_box(
        "Step 2: Inverter Nominal Power Requirement",
        "Minimum inverter rating to accommodate PV array."
    )

    inv_power = st.session_state.total_power / dc_ac
    st.metric("Required Inverter Nominal Power (W)", f"{inv_power:,.2f}")

    st.success("✅ Central inverter sizing completed successfully.")
