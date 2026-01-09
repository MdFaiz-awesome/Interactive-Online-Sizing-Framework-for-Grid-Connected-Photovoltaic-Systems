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

def go_to_part_a():
    st.session_state.page = "part_a"

def go_to_part_b():
    st.session_state.page = "part_b"

# =====================================================
# BACKGROUND
# =====================================================
def apply_background():
    try:
        with open("bg.png", "rb") as img:
            encoded = base64.b64encode(img.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except:
        pass

# =====================================================
# WELCOME PAGE
# =====================================================
if st.session_state.page == "welcome":
    apply_background()

    st.markdown(
        """
        <div style="text-align:center; padding:40px;
        background:rgba(255,255,255,0.9);
        border-radius:15px;">
        <h1>Interactive Online Sizing Framework</h1>
        <h3>Grid-Connected Photovoltaic System</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("👉 Start PV Sizing Tool", use_container_width=True):
        with st.spinner("Loading dashboard..."):
            time.sleep(1.5)
        go_to_part_a()
        st.rerun()

# =====================================================
# PART A : PV MODULE DIMENSIONING
# =====================================================
elif st.session_state.page == "part_a":

    st.title("📘 Part A: Dimensioning of PV Modules")
    st.markdown("---")

    # -------------------------------
    # STEP 1: PV MODULE PARAMETERS
    # -------------------------------
    st.subheader("Step 1: PV Module Parameters")

    col1, col2 = st.columns(2)

    with col1:
        panel_length = st.number_input("Panel Length (m)", value=2.382)
        panel_width = st.number_input("Panel Width (m)", value=1.134)
        rated_power = st.number_input("Rated Power (W)", value=605)
        isc_stc = st.number_input("Isc STC (A)", value=13.0)

    with col2:
        T_coef = st.number_input("Temperature Coefficient (%/°C)", value=-0.28)
        T_mod = st.number_input("Module Temperature (°C)", value=55)
        T_ref = st.number_input("Reference Temperature (°C)", value=25)

        f_mm = st.number_input("Module mismatch (f_mm)", value=0.97)
        f_clean = st.number_input("Soiling factor (f_clean)", value=0.96)
        f_degrad = st.number_input("Degradation factor (f_degrad)", value=0.975)
        f_unshade = st.number_input("Shading factor (f_unshade)", value=0.97)
        eta_cable = st.number_input("Cable efficiency", value=0.97)
        eta_inv = st.number_input("Inverter efficiency", value=0.98)
        psh = st.number_input("Peak Sun Hours (h/day)", value=4.0)

    # -------------------------------
    # AUTO CALC PART A
    # -------------------------------
    panel_area = panel_length * panel_width
    f_temp = 1 + ((T_coef / 100) * (T_mod - T_ref))

    yearly_energy_kwh = (
        psh * 365 * rated_power *
        f_mm * f_temp * f_clean * f_degrad *
        f_unshade * eta_cable * eta_inv
    ) / 1000

    # -------------------------------
    # STEP 2: SITE CONSTRAINT
    # -------------------------------
    st.markdown("---")
    st.subheader("Step 2: Site & Layout Constraint")

    col3, col4 = st.columns(2)

    with col3:
        site_width = st.number_input("Site Width (m)", value=45.74)
        site_length = st.number_input("Site Length (m)", value=115.88)
        delta = st.number_input("Inter-module gap (m)", value=0.01)

    with col4:
        orientation = st.selectbox(
            "Module Orientation",
            ["Landscape", "Portrait"]
        )

    if orientation == "Landscape":
        N_up = math.floor(site_width / (panel_width + delta))
        N_across = math.floor(site_length / (panel_length + delta))
    else:
        N_up = math.floor(site_width / (panel_length + delta))
        N_across = math.floor(site_length / (panel_width + delta))

    total_modules = N_up * N_across

    st.success(f"Total Installable PV Modules: {total_modules}")

    # -------------------------------
    # FINAL PART A RESULT
    # -------------------------------
    final_power = rated_power * total_modules
    final_energy = yearly_energy_kwh * total_modules

    st.markdown("---")
    st.subheader("Final Output – Part A")

    col5, col6, col7 = st.columns(3)
    col5.metric("Total PV Modules", total_modules)
    col6.metric("Total Peak Power (W)", f"{final_power:,.2f}")
    col7.metric("Total Energy (kWh/year)", f"{final_energy:,.2f}")

    # -------------------------------
    # BUTTON TO PART B
    # -------------------------------
    st.markdown("---")
    if st.button("➡️ Proceed to Part B: Inverter Sizing", use_container_width=True):
        go_to_part_b()
        st.rerun()

# =====================================================
# PART B : CENTRAL INVERTER SIZING
# =====================================================
elif st.session_state.page == "part_b":

    st.title("📕 Part B: Sizing with Central Inverter")
    st.markdown("---")

    # -------------------------------
    # SUMMARY PART A
    # -------------------------------
    st.subheader("Summary of Part A")

    colA, colB, colC = st.columns(3)
    colA.metric("Total PV Modules", total_modules)
    colB.metric("Total Peak Power (W)", f"{final_power:,.2f}")
    colC.metric("Total Energy (kWh/year)", f"{final_energy:,.2f}")

    # -------------------------------
    # STEP 1: DC/AC RATIO
    # -------------------------------
    st.markdown("---")
    st.subheader("Step 1: Decide DC/AC Ratio")
    dc_ac = st.number_input("DC/AC Ratio (fi)", value=1.2)

    # -------------------------------
    # STEP 2: INVERTER POWER
    # -------------------------------
    st.markdown("---")
    st.subheader("Step 2: Determine Suitable Inverter")

    inverter_power = (rated_power * total_modules) / dc_ac
    st.metric("Required Inverter Nominal Power (W)", f"{inverter_power:,.2f}")

    # -------------------------------
    # STEP 3 & 4: STRING RANGE
    # -------------------------------
    st.markdown("---")
    st.subheader("Step 3 & 4: String Sizing Range")

    colD, colE = st.columns(2)

    with colD:
        Voc = st.number_input("Voc STC (V)", value=49.5)
        Vp = st.number_input("Vpmax STC (V)", value=41.6)
        beta_voc = st.number_input("βVoc (%/°C)", value=-0.28)
        beta_vp = st.number_input("βVpmax (%/°C)", value=-0.34)
        Tmin = st.number_input("Tmod min (°C)", value=10)
        Tmax = st.number_input("Tmod max (°C)", value=70)

    with colE:
        Vabs = st.number_input("Inverter Vmax abs (V)", value=1500)
        Vmppt_max = st.number_input("Inverter Vmax MPPT (V)", value=1300)
        Vmppt_min = st.number_input("Inverter Vmin MPPT (V)", value=500)
        Vstart = st.number_input("Inverter Vstart (V)", value=600)
        Vsys = st.number_input("Module Vsys max (V)", value=1500)
        eff = st.number_input("Efficiency", value=0.98)

    Tstc = 25

    Voc_max = Voc * (1 + (beta_voc / 100) * (Tmin - Tstc))
    Ns_max = min(
        math.floor(Vabs / Voc_max),
        math.floor(Vmppt_max / (Vp * (1 + (beta_vp / 100) * (Tmin - Tstc)))),
        math.floor(Vsys / Voc_max)
    )

    Voc_min = Voc * (1 + (beta_voc / 100) * (Tmax - Tstc))
    Ns_min = max(
        math.ceil(Vmppt_min / (Vp * eff)),
        math.ceil(Vstart / Voc_min)
    )

    st.success(f"String Sizing Range: {Ns_min} ≤ Ns ≤ {Ns_max}")

    # -------------------------------
    # STEP 5: OPTIMUM Ns
    # -------------------------------
    st.markdown("---")
    st.subheader("Step 5: Optimum Modules in Series")

    Vrated = st.number_input("Inverter Vrated (V)", value=1000)
    Wp = ((Vrated - Vmppt_min) / (Vmppt_max - Vmppt_min)) * 100
    Ns_rec = math.floor(Ns_min + (Wp / 100) * (Ns_max - Ns_min))

    st.metric("Recommended Ns", Ns_rec)

    # -------------------------------
    # STEP 6: MAX STRINGS
    # -------------------------------
    st.markdown("---")
    st.subheader("Step 6: Maximum Strings per MPPT")

    Isc_mppt = st.number_input("Isc max MPPT (A)", value=26)
    Sf = 1.25
    Np_max = math.floor(Isc_mppt / (isc_stc * Sf))

    st.metric("Max Strings per MPPT", Np_max)

    # -------------------------------
    # STEP 7 & 8: FINAL CONFIG
    # -------------------------------
    st.markdown("---")
    st.subheader("Final PV Array Configuration")

    total_strings = math.floor(total_modules / Ns_rec)

    st.success(
        f"""
        ✔ Total Strings Required: {total_strings}  
        ✔ Modules per String (Ns): {Ns_rec}
        """
    )
