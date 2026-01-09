import streamlit as st
import math
import time
import base64

# -----------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------
st.set_page_config(
    page_title="PV Sizing Tool",
    page_icon="🔆",
    layout="wide"
)

# -----------------------------------------------------
# SESSION STATE
# -----------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "welcome"

def switch_to_dimensioning():
    st.session_state.page = "dimensioning"

def switch_to_part_b():
    st.session_state.page = "part_b"

# -----------------------------------------------------
# SET FIXED BACKGROUND IMAGE (SAFE LOAD)
# -----------------------------------------------------
def apply_background():
    try:
        with open("bg.png", "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url("data:image/jpg;base64,{encoded}");
                    background-size: cover;
                    background-position: center;
                    background-attachment: fixed;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
    except FileNotFoundError:
        pass

# =====================================================
# PAGE 1: WELCOME PAGE
# =====================================================
if st.session_state.page == "welcome":

    apply_background()

    st.markdown(
        """
        <div style="text-align:center; padding-top:40px; 
        background:rgba(255,255,255,0.85); padding:20px; 
        border-radius:12px; box-shadow:2px 2px 8px rgba(0,0,0,0.2);">
            <h1 style='font-size:38px; font-weight:bold;'>
                Interactive Online Sizing Framework for Grid-Connected Photovoltaic Systems
            </h1>
            <p style='font-size:20px;'>
                Hello! This tool will assist you in designing and sizing your PV modules.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br><br>", unsafe_allow_html=True)

    if st.button("👉 Start Sizing Tool", use_container_width=True):
        with st.spinner("Loading PV Sizing Dashboard..."):
            time.sleep(2)
        switch_to_dimensioning()
        st.rerun()

# =====================================================
# PAGE 2: PART A (ASAL – TIDAK DIUBAH)
# =====================================================
elif st.session_state.page == "dimensioning":

    st.markdown(
        "<h1 style='text-align:center;'>📘 Dimensioning of PV Modules</h1>",
        unsafe_allow_html=True
    )
    st.write("Follow the structured technical steps below to complete your PV sizing process.")
    st.markdown("---")

    # =======================
    # STEP 1
    # =======================
    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; 
        background-color:#f7f9fc; border-left:6px solid #4A90E2;">
            <h2>Step 1: Choose a PV Module</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        panel_length = st.number_input("Panel Length (m)", value=1.7)
        panel_width = st.number_input("Panel Width (m)", value=1.1)
        rated_power = st.number_input("Rated Power (W)", value=550)
        isc_stc = st.number_input("Isc STC (A)", value=13.0)

    with col2:
        T_coef = st.number_input("Temperature Coefficient (%/°C)", value=-0.35)
        T_mod = st.number_input("Module Temperature (°C)", value=45)
        T_src = st.number_input("Reference Temperature (°C)", value=25)
        f_mm = st.number_input("Module mismatch", value=0.98)
        f_clean = st.number_input("Soiling factor", value=0.97)
        f_degrad = st.number_input("Degradation factor", value=0.99)
        f_unshade = st.number_input("Shading factor", value=0.98)
        eta_cable = st.number_input("Cable efficiency", value=0.98)
        eta_inv = st.number_input("Inverter efficiency", value=0.96)
        peak_sun_hours = st.number_input("Peak Sun Hours", value=4.0)

    panel_area = panel_length * panel_width
    f_temp_ave = 1 + ((T_coef / 100) * (T_mod - T_src))
    yearly_energy_kwh = (
        peak_sun_hours * 365 * rated_power *
        f_mm * f_temp_ave * f_clean * f_degrad *
        f_unshade * eta_cable * eta_inv
    ) / 1000

    # =======================
    # STEP 2
    # =======================
    st.markdown("---")
    site_width = st.number_input("Site Width (m)", value=20.0)
    site_length = st.number_input("Site Length (m)", value=30.0)
    delta = st.number_input("Inter-module gap (m)", value=0.02)
    orientation = st.selectbox("Orientation", ["Landscape", "Portrait"])

    if orientation == "Landscape":
        N_up = math.floor(site_width / (panel_width + delta))
        N_across = math.floor(site_length / (panel_length + delta))
    else:
        N_up = math.floor(site_width / (panel_length + delta))
        N_across = math.floor(site_length / (panel_width + delta))

    best_count = N_up * N_across
    final_power_output_total = rated_power * best_count
    final_yearly_energy_total = yearly_energy_kwh * best_count

    st.success(f"Total Installable PV Modules: {best_count}")

    st.markdown("---")
    st.metric("Total Power Output (W)", f"{final_power_output_total:,.2f}")
    st.metric("Total Yearly Energy (kWh/year)", f"{final_yearly_energy_total:,.2f}")

    # =======================
    # BUTTON TO PART B
    # =======================
    st.markdown("---")
    if st.button("➡️ Proceed to Part B: Central Inverter Sizing", use_container_width=True):
        switch_to_part_b()
        st.rerun()

# =====================================================
# PAGE 3: PART B – CENTRAL INVERTER
# =====================================================
elif st.session_state.page == "part_b":

    st.title("📕 Part B: Sizing with Central Inverter")
    st.markdown("---")

    # =======================
    # SUMMARY PART A
    # =======================
    st.subheader("Summary of Part A")

    colA, colB, colC = st.columns(3)
    colA.metric("Total PV Modules", best_count)
    colB.metric("Total Peak Power (W)", f"{final_power_output_total:,.2f}")
    colC.metric("Total Yearly Energy (kWh/year)", f"{final_yearly_energy_total:,.2f}")

    # =======================
    # STEP 1: DC/AC
    # =======================
    st.markdown("---")
    st.subheader("Step 1: Decide DC/AC Ratio")
    fi = st.number_input("DC/AC Ratio (fi)", value=1.2)

    # =======================
    # STEP 2: INVERTER POWER
    # =======================
    st.markdown("---")
    st.subheader("Step 2: Determine Suitable Inverter")

    req_inv_power = (rated_power * best_count) / fi
    st.metric("Required Inverter Nominal Power (W)", f"{req_inv_power:,.2f}")

    # =======================
    # STEP 3 & 4: STRING RANGE
    # =======================
    st.markdown("---")
    st.subheader("Step 3 & 4: String Sizing Range")

    Voc = st.number_input("Voc STC (V)", value=49.5)
    Vp = st.number_input("Vpmax STC (V)", value=41.6)
    beta_voc = st.number_input("βVoc (%/°C)", value=-0.28)
    beta_vp = st.number_input("βVpmax (%/°C)", value=-0.34)
    Tmin = st.number_input("Tmod min (°C)", value=10)
    Tmax = st.number_input("Tmod max (°C)", value=70)

    Vabs = st.number_input("Vmax abs inverter (V)", value=1500)
    Vmppt_max = st.number_input("Vmax MPPT inverter (V)", value=1300)
    Vmppt_min = st.number_input("Vmin MPPT inverter (V)", value=500)
    Vstart = st.number_input("Vstart inverter (V)", value=600)
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

    st.success(f"Final Ns_max = {Ns_max}")
    st.success(f"Final Ns_min = {Ns_min}")
    st.info(f"String Sizing Range: {Ns_min} – {Ns_max}")

    # =======================
    # STEP 5: OPTIMUM Ns
    # =======================
    st.markdown("---")
    st.subheader("Step 5: Optimum PV Modules in Series")

    Vrated = st.number_input("Inverter Vrated (V)", value=1000)
    W_percent = ((Vrated - Vmppt_min) / (Vmppt_max - Vmppt_min)) * 100
    Ns_rec = math.floor(Ns_min + (W_percent / 100) * (Ns_max - Ns_min))

    st.metric("W% Result", f"{W_percent:.2f} %")
    st.metric("Recommended Ns", Ns_rec)

    # =======================
    # STEP 6: MAX STRING / MPPT
    # =======================
    st.markdown("---")
    st.subheader("Step 6: Maximum Strings per MPPT")

    Isc_mppt = st.number_input("Isc max MPPT (A)", value=26.0)
    Sf1 = 1.25
    Np_max = math.floor(Isc_mppt / (isc_stc * Sf1))

    st.metric("Maximum Strings per MPPT", Np_max)

    # =======================
    # STEP 7 & 8: FINAL CONFIG
    # =======================
    st.markdown("---")
    st.subheader("Final PV Array Configuration")

    Nt = st.number_input("Total PV Modules per Inverter (Nt)", value=best_count)
    total_strings = math.floor(Nt / Ns_rec)

    st.success(f"Total Strings Required = {total_strings}")
    st.success(f"Selected Modules in Series = {Ns_rec}")
