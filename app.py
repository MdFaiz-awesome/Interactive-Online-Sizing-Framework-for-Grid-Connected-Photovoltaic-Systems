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
# SET FIXED BACKGROUND IMAGE (ONLY FOR HOME PAGE)
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
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #f2f2f2;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

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

    # START BUTTON
    if st.button("👉 Start Sizing Tool", use_container_width=True):
        with st.spinner("Loading PV Sizing Dashboard..."):
            time.sleep(2)
        switch_to_dimensioning()
        st.rerun()

# =====================================================
# PAGE 2: DIMENSIONING PAGE (PART A)
# =====================================================
elif st.session_state.page == "dimensioning":

    st.markdown("<h1 style='text-align:center;'>📘 Dimensioning of PV Modules</h1>", unsafe_allow_html=True)
    st.write("Follow the structured technical steps below to complete your PV sizing process.")
    st.markdown("---")

    # -------------------------------------------------
    # STEP 1 (BOX DESIGN)
    # -------------------------------------------------
    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; 
        background-color:#f7f9fc; border-left:6px solid #4A90E2;">
            <h2>Step 1: Choose a PV Module</h2>
            <p>Insert the module characteristics and performance factors below.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        col1, col2 = st.columns(2)

        # LEFT COLUMN
        with col1:
            st.markdown("### 🟦 Module Properties")
            panel_length = st.number_input("Panel Length (m)", min_value=0.1, value=1.7)
            panel_width = st.number_input("Panel Width (m)", min_value=0.1, value=1.1)
            rated_power = st.number_input("Rated Power (W)", min_value=1, value=550)
            isc_stc = st.number_input("Isc STC (A)", min_value=0.1, value=13.0)
            isc_max_inv = st.number_input("Isc Max Inv (A)", min_value=0.1, value=15.0)

        # RIGHT COLUMN
        with col2:
            st.markdown("### 🟩 Temperature & Performance Factors")
            T_coef = st.number_input("Temperature Coefficient (°C)", value=-0.35)
            T_mod = st.number_input("Module Temperature (°C)", value=45)
            T_src = st.number_input("Reference Temperature (°C)", value=25)

            f_mm = st.number_input("Module mismatch, f_mm", value=0.98)
            f_clean = st.number_input("Soiling, f_clean", value=0.97)
            f_degrad = st.number_input("Degradation, f_degrad", value=0.99)
            f_unshade = st.number_input("Shading, f_unshade", value=0.98)
            eta_cable = st.number_input("Cable efficiency, η_cable", value=0.98)
            eta_inv = st.number_input("Inverter efficiency, η_inv", value=0.96)
            peak_sun_hours = st.number_input("Peak Sun Hours (h/day)", value=4.0)

    st.markdown("---")

    # -------------------------------------------------
    # AUTO CALCULATIONS
    # -------------------------------------------------
    panel_area = panel_length * panel_width
    f_temp_ave = 1 + ((T_coef / 100) * (T_mod - T_src))

    power_output = (rated_power * f_mm * f_temp_ave * f_degrad) / panel_area

    yearly_energy = (
        (peak_sun_hours * 365)
        * rated_power
        * f_mm
        * f_temp_ave
        * f_clean
        * f_degrad
        * f_unshade
        * eta_cable
        * eta_inv
    ) / panel_area

    # Convert Wh → kWh
    yearly_energy_kwh = yearly_energy / 1000

    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; background-color:#eef7f2; border-left:6px solid #28a745;">
            <h2>Calculated Module Performance</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    colA, colB = st.columns(2)
    with colA:
        st.metric("Panel Area (m²)", f"{panel_area:.3f}")
        st.metric("f_temp-ave", f"{f_temp_ave:.4f}")
    with colB:
        st.metric("Power Output (W/m²)", f"{power_output:.3f}")
        st.metric("Yearly Energy (kWh/m²/year)", f"{yearly_energy_kwh:.3f}")

    st.markdown("---")

    # -------------------------------------------------
    # STEP 2: ARCHITECTURE CONSTRAINT
    # -------------------------------------------------
    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; 
        background-color:#f7f9fc; border-left:6px solid #4A90E2;">
            <h2>Step 2: Architecture Constraint</h2>
            <p>Determine the maximum installable number of modules based on site geometry.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    colX, colY = st.columns(2)
    with colX:
        st.markdown("### 📐 Module Dimensions")
        Wm = st.number_input("Width of Module, Wm (m)", value=panel_width)
        Lm = st.number_input("Length of Module, Lm (m)", value=panel_length)
    with colY:
        st.markdown("### 📏 Site Layout")
        delta = st.number_input("Inter-module gap, ∆ (m)", value=0.02)
        site_width = st.number_input("Width of Site (m)", min_value=1.0, value=20.0)
        site_length = st.number_input("Length of Site (m)", min_value=1.0, value=30.0)

    st.markdown("---")
    orientation = st.selectbox("PV Installation Orientation", ["Landscape", "Portrait"])
    if orientation == "Landscape":
        N_up = math.floor(site_width / (Wm + delta))
        N_across = math.floor(site_length / (Lm + delta))
    else:
        N_up = math.floor(site_width / (Lm + delta))
        N_across = math.floor(site_length / (Wm + delta))
    N_max = N_up * N_across

    st.success(
        f"### 📊 Orientation: **{orientation}**\n- Modules Upwards: **{N_up}**  \n- Modules Across: **{N_across}**  \n- **Total Installable PV Modules: {N_max}**"
    )

    # =====================================================
    # STEP 3: BEST ORIENTATION & FINAL SYSTEM PERFORMANCE
    # =====================================================
    N_landscape_up = math.floor(site_width / (Wm + delta))
    N_landscape_across = math.floor(site_length / (Lm + delta))
    N_landscape = N_landscape_up * N_landscape_across
    N_portrait_up = math.floor(site_width / (Lm + delta))
    N_portrait_across = math.floor(site_length / (Wm + delta))
    N_portrait = N_portrait_up * N_portrait_across

    if N_landscape >= N_portrait:
        best_orientation = "Landscape"
        best_count = N_landscape
    else:
        best_orientation = "Portrait"
        best_count = N_portrait

    st.info(
        f"### 🏆 Recommended Orientation: **{best_orientation}**\n- Maximum installable PV modules: **{best_count}**"
    )

    final_power_output_total = power_output * best_count
    final_yearly_energy_total = yearly_energy_kwh * best_count

    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; 
        background-color:#e8f5ff; border-left:6px solid #007BFF;">
            <h2>Final System Performance</h2>
            <p>The following results represent the full system output based on the optimal PV orientation and maximum number of installable modules.</p>
        </div>
        """, unsafe_allow_html=True
    )

    colF1, colF2 = st.columns(2)
    with colF1:
        st.metric("Total Power Output (W)", f"{final_power_output_total:,.2f}")
    with colF2:
        st.metric("Total Yearly Energy (kWh/year)", f"{final_yearly_energy_total:,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("👉 Continue to Part B", use_container_width=True):
        # Save Part A results for Part B
        st.session_state.best_count = best_count
        st.session_state.final_power_output_total = final_power_output_total
        st.session_state.yearly_energy_kwh = final_yearly_energy_total
        st.session_state.rated_power = rated_power
        st.session_state.page = "part_b"
        st.rerun()

# =====================================================
# PAGE 3: PART B
# =====================================================
elif st.session_state.page == "part_b":
    # MASUKKAN CODE PART B YANG SAYA BUATKAN SEBELUM INI
    # (Part B lengkap dengan semua Step 1-8, styling sama Part A, Back to Part A button)
    exec(open("part_b_code.py").read())  # contoh modular, atau letakkan terus code Part B di sini
# =====================================================
# PART B: SIZING WITH CENTRAL INVERTER
# =====================================================
if st.session_state.get("page") == "part_b":
    st.markdown("<h1 style='text-align:center;'>Part B: Sizing with Central Inverter</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # BUTTON BACK TO PART A
    if st.button("⬅️ Back to Part A", use_container_width=True):
        st.session_state.page = "dimensioning"
        st.rerun()

    # AMBIL DATA DARI PART A
    best_count = st.session_state.get("best_count", 0)
    final_power_output_total = st.session_state.get("final_power_output_total", 0)
    yearly_energy_kwh = st.session_state.get("yearly_energy_kwh", 0)
    rated_power = st.session_state.get("rated_power", 550)

    # =========================
    # SUMMARY OF PART A
    # =========================
    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; 
        background-color:#eef7f2; border-left:6px solid #28a745;">
            <h2>Summary of Part A</h2>
        </div>
        """, unsafe_allow_html=True
    )
    colA, colB, colC = st.columns(3)
    with colA:
        st.metric("Total PV Modules", f"{best_count}")
    with colB:
        st.metric("Total Peak Power Output (W)", f"{final_power_output_total:,.2f}")
    with colC:
        st.metric("Total Yearly Energy (kWh/year)", f"{yearly_energy_kwh:,.2f}")
    st.markdown("---")

    # =====================================================
    # STEP 1: Decide DC/AC Ratio
    # =====================================================
    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; 
        background-color:#f7f9fc; border-left:6px solid #4A90E2;">
            <h2>Step 1: Decide DC/AC Ratio</h2>
        </div>
        """, unsafe_allow_html=True
    )
    dc_ac_ratio = st.number_input("Enter DC/AC Ratio (fi)", value=1.2)

    # =====================================================
    # STEP 2: Determine The Suitable Inverter
    # =====================================================
    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; 
        background-color:#f7f9fc; border-left:6px solid #4A90E2;">
            <h2>Step 2: Determine The Suitable Inverter</h2>
        </div>
        """, unsafe_allow_html=True
    )
    num_pv_modules = st.number_input("Enter Number of PV Modules", value=best_count)
    pv_module_power = st.number_input("Enter PV Module Power (W)", value=rated_power)
    req_inv_power = (pv_module_power * num_pv_modules) / dc_ac_ratio
    st.success(f"Required Inverter Nominal Power > {req_inv_power:,.2f} W")

    # =====================================================
    # STEP 3 & 4: Determine String Sizing Range
    # =====================================================
    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; 
        background-color:#fff8e6; border-left:6px solid #f5a623;">
            <h2>Step 3 & 4: Determine String Sizing Range (Ns min & Ns max)</h2>
            <h4>Module and Inverter Datasheet Parameter</h4>
        </div>
        """, unsafe_allow_html=True
    )
    col1, col2 = st.columns(2)
    with col1:
        voc_stc = st.number_input("V_oc STC (V)", value=45.0)
        vp_stc = st.number_input("V_p STC (V)", value=37.0)
        beta_voc = st.number_input("Beta Voc (%/°C)", value=-0.35)
        beta_vpmax = st.number_input("Beta Vpmax (%/°C)", value=-0.3)
        t_mod_min = st.number_input("T_mod min (°C)", value=-5)
        t_mod_max = st.number_input("T_mod max (°C)", value=50)
        t_stc = 25
    with col2:
        v_max_abs_inv = st.number_input("Inverter V_max-abs-inv (V)", value=600)
        v_max_mppt_inv = st.number_input("Inverter V_max-mppt-inv (V)", value=500)
        v_sys_max = st.number_input("Module V_sys-max (V)", value=550)
        v_min_mppt_inv = st.number_input("Inverter V_min-mppt-inv (V)", value=150)
        v_start_inv = st.number_input("V_start-inv (V)", value=200)
        efficiency = st.number_input("Efficiency", value=0.96)

    # Formula untuk Ns_max & Ns_min
    voc_max = voc_stc * (1 + (beta_voc / 100) * (t_mod_min - t_stc))
    ns_max_abs = math.floor(v_max_abs_inv / voc_max)
    vpmax_max = vp_stc * (1 + (beta_vpmax / 100) * (t_mod_min - t_stc))
    ns_max_mppt = math.floor(v_max_mppt_inv / vpmax_max)
    ns_max_pv = math.floor(v_sys_max / voc_max)
    ns_max = min(ns_max_abs, ns_max_mppt, ns_max_pv)

    vpmax_min = vp_stc * (1 + (beta_vpmax / 100) * (t_mod_max - t_stc))
    ns_min_mppt = math.ceil(v_min_mppt_inv / (vpmax_min * efficiency))
    voc_min = voc_stc * (1 + (beta_voc / 100) * (t_mod_max - t_stc))
    ns_min_start = math.ceil(v_start_inv / voc_min)
    ns_min = max(ns_min_mppt, ns_min_start)

    st.info(f"Final Ns_max = {ns_max}  |  Final Ns_min = {ns_min}  |  Range for String Sizing = {ns_min} - {ns_max}")

    # =====================================================
    # STEP 5: Determine Optimum PV Modules in Series (Ns_rec)
    # =====================================================
    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; 
        background-color:#f7f9fc; border-left:6px solid #4A90E2;">
            <h2>Step 5: Determine the Optimum PV Modules in Series (Ns_rec)</h2>
            <h4>Key Parameter for Optimum Calculation</h4>
        </div>
        """, unsafe_allow_html=True
    )
    vrated_inv = st.number_input("Inverter Vrated (V)", value=400)
    vmax_mppt_inv = st.number_input("Vmax_mppt-inv (V)", value=500)
    vmin_mppt_inv = st.number_input("Vmin_mppt-inv (V)", value=150)

    w_percent = ((vrated_inv - vmin_mppt_inv) / (vmax_mppt_inv - vmin_mppt_inv)) * 100
    ns_rec = math.floor(ns_min + (w_percent / 100) * (ns_max - ns_min))

    st.info(f"W% Result = {w_percent:.2f}%  |  Recommendation Modules Result (Ns_rec) = {ns_rec}")

    # =====================================================
    # STEP 6: Maximum Number of Strings per MPPT
    # =====================================================
    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; 
        background-color:#fff8e6; border-left:6px solid #f5a623;">
            <h2>Step 6: Determine the Maximum Number of Strings per MPPT</h2>
            <h4>Key Parameters for Maximum String Calculation</h4>
        </div>
        """, unsafe_allow_html=True)
    isc_max_mppt = st.number_input("Isc_max-mppt (A)", value=13.0)
    isc_stc = st.number_input("Isc_STC (A)", value=13.0)
    sf1 = st.number_input("Safety Factor (Sf1)", value=1.25)
    np_max_mppt = math.floor(isc_max_mppt / (isc_stc * sf1))
    st.info(f"Final Maximum Strings Result = {np_max_mppt}")

    # =====================================================
    # STEP 7: Number of Strings per MPPT
    # =====================================================
    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; 
        background-color:#f7f9fc; border-left:6px solid #4A90E2;">
            <h2>Step 7: Determine the Number of Strings per MPPT</h2>
            <h4>Inverter and Array Configuration Parameters</h4>
        </div>
        """, unsafe_allow_html=True)
    nt = st.number_input("Total PV Modules per Inverter (Nt)", value=best_count)
    nmppt = ns_rec
    result_config = math.ceil(nt / nmppt)
    st.info(f"Result Configuration = {result_config}")

    # =====================================================
    # STEP 8: Final PV Array Configuration
    # =====================================================
    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; 
        background-color:#eef7f2; border-left:6px solid #28a745;">
            <h2>Step 8: Final PV Array Configuration</h2>
            <h4>Final Configuration Summary</h4>
        </div>
        """, unsafe_allow_html=True)
    st.success(f"Total Strings Required = {result_config}  |  Selected Modules in Series = {ns_rec}")
