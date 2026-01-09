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

# -----------------------------------------------------
# SET FIXED BACKGROUND IMAGE (SAFE LOAD) ONLY HOME PAGE
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
    # STEP 1: Module Properties & Performance
    # -------------------------------------------------
    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; 
        background-color:#f7f9fc; border-left:6px solid #4A90E2;">
            <h2>Step 1: Choose a PV Module</h2>
            <p>Insert the module characteristics and performance factors below.</p>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🟦 Module Properties")
            panel_length = st.number_input("Panel Length (m)", min_value=0.1, value=1.7)
            panel_width = st.number_input("Panel Width (m)", min_value=0.1, value=1.1)
            rated_power = st.number_input("Rated Power (W)", min_value=1, value=550)
            isc_stc = st.number_input("Isc STC (A)", min_value=0.1, value=13.0)
            isc_max_inv = st.number_input("Isc Max Inv (A)", min_value=0.1, value=15.0)
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

    # -------------------------------------------------
    # AUTO CALCULATIONS PART A
    # -------------------------------------------------
    panel_area = panel_length * panel_width
    f_temp_ave = 1 + ((T_coef / 100) * (T_mod - T_src))
    power_output = (rated_power * f_mm * f_temp_ave * f_degrad) / panel_area
    yearly_energy = ((peak_sun_hours*365) * rated_power * f_mm * f_temp_ave * f_clean * f_degrad * f_unshade * eta_cable * eta_inv)/panel_area
    yearly_energy_kwh = yearly_energy / 1000

    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; background-color:#eef7f2; border-left:6px solid #28a745;">
            <h2>Calculated Module Performance</h2>
        </div>
        """, unsafe_allow_html=True
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
    # STEP 2: Architecture Constraint
    # -------------------------------------------------
    st.markdown(
        """
        <div style="padding:15px; border-radius:10px; 
        background-color:#f7f9fc; border-left:6px solid #4A90E2;">
            <h2>Step 2: Architecture Constraint</h2>
            <p>Determine the maximum installable number of modules based on site geometry.</p>
        </div>
        """, unsafe_allow_html=True
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

    orientation = st.selectbox("PV Installation Orientation", ["Landscape", "Portrait"])
    if orientation == "Landscape":
        N_up = math.floor(site_width / (Wm + delta))
        N_across = math.floor(site_length / (Lm + delta))
    else:
        N_up = math.floor(site_width / (Lm + delta))
        N_across = math.floor(site_length / (Wm + delta))
    N_max = N_up * N_across
    st.success(f"### 📊 Orientation: **{orientation}**\n- Modules Upwards: **{N_up}**  \n- Modules Across: **{N_across}**  \n- **Total Installable PV Modules: {N_max}**")

    # -------------------------------------------------
    # STEP 3: Best Orientation & Final System Performance
    # -------------------------------------------------
    N_landscape_up = math.floor(site_width / (Wm + delta))
    N_landscape_across = math.floor(site_length / (Lm + delta))
    N_landscape = N_landscape_up * N_landscape_across
    N_portrait_up = math.floor(site_width / (Lm + delta))
    N_portrait_across = math.floor(site_length / (Wm + delta))
    N_portrait = N_portrait_up * N_portrait_across
    if N_landscape >= N_portrait:
        best_count = N_landscape
        best_orientation = "Landscape"
    else:
        best_count = N_portrait
        best_orientation = "Portrait"
    final_power_output_total = power_output * best_count
    final_yearly_energy_total = yearly_energy_kwh * best_count
    st.info(f"### 🏆 Recommended Orientation: **{best_orientation}**\n- Maximum installable PV modules: **{best_count}**")

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

    # =====================================================
    # BUTTON KE PART B
    # =====================================================
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➡️ Go to Part B: Sizing with Central Inverter", use_container_width=True):
        st.session_state.best_count = best_count
        st.session_state.final_power_output_total = final_power_output_total
        st.session_state.yearly_energy_kwh = final_yearly_energy_total
        st.session_state.rated_power = rated_power
        st.session_state.page = "part_b"
        st.rerun()

# =====================================================
# PART B: SIZING WITH CENTRAL INVERTER
# =====================================================
if st.session_state.get("page") == "part_b":
    st.markdown("<h1 style='text-align:center;'>Part B: Sizing with Central Inverter</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # AMBIL DATA DARI PART A
    best_count = st.session_state.get("best_count", 0)
    final_power_output_total = st.session_state.get("final_power_output_total", 0)
    yearly_energy_kwh = st.session_state.get("yearly_energy_kwh", 0)
    rated_power = st.session_state.get("rated_power", 550)

    # =========================
    # SUMMARY OF PART A
    # =========================
    st.markdown("### Summary of Part A")
    st.metric("Total PV Modules", f"{best_count}")
    st.metric("Total Peak Power Output (W)", f"{final_power_output_total:,.2f}")
    st.metric("Total Yearly Energy (kWh/year)", f"{yearly_energy_kwh:,.2f}")
    st.markdown("---")

    # ======= PART B STEPS DARI SEBELUM =========
    # [STEP 1 hingga STEP 8 ikut coding saya hantar sebelum ini]
    # (boleh copy paste coding Part B yang saya tulis sebelum ini)

    # =========================
    # STEP 1: Decide DC/AC Ratio
    # =========================
    st.markdown("### Step 1: Decide DC/AC Ratio")
    fi = st.number_input("Enter DC/AC Ratio (fi)", min_value=0.1, value=1.1)

    # =========================
    # STEP 2: Determine The Suitable Inverter
    # =========================
    st.markdown("### Step 2: Determine The Suitable Inverter")
    st.write("Enter the following parameters:")
    num_modules = st.number_input("Number of PV Modules", min_value=1, value=best_count)
    pv_power = st.number_input("PV Module Power (W)", min_value=1, value=rated_power)
    P_inv_required = (pv_power * num_modules) / fi
    st.metric("Required Inverter Nominal Power (W)", f"{P_inv_required:,.2f}")

    # =========================
    # STEP 3 & 4: Determine String Sizing Range (Ns min & Ns max)
    # =========================
    st.markdown("### Step 3 & 4: Determine String Sizing Range (Ns min & Ns max)")
    st.markdown("#### Module and Inverter Datasheet Parameter")
    col1, col2 = st.columns(2)
    with col1:
        Voc_STC = st.number_input("V_oc STC (V)", value=42.0)
        Vp_STC = st.number_input("V_p STC (V)", value=35.0)
        beta_Voc = st.number_input("Beta V_oc (%/°C)", value=-0.3)
        beta_Vpmax = st.number_input("Beta V_pmax (%/°C)", value=-0.25)
        T_mod_min = st.number_input("T_mod min (°C)", value=0)
        T_mod_max = st.number_input("T_mod max (°C)", value=50)
        T_STC = 25
    with col2:
        V_max_abs_inv = st.number_input("Inverter V_max-abs-inv (V)", value=1000)
        V_max_mppt_inv = st.number_input("Inverter V_max-mppt-inv (V)", value=850)
        V_sys_max = st.number_input("Module V_sys-max (V)", value=1000)
        V_min_mppt_inv = st.number_input("Inverter V_min-mppt-inv (V)", value=200)
        V_start_inv = st.number_input("V_start-inv (V)", value=250)
        efficiency = st.number_input("Efficiency", value=0.95)

    Voc_max = Voc_STC * (1 + (beta_Voc / 100) * (T_mod_min - T_STC))
    Ns_max_abs = math.floor(V_max_abs_inv / Voc_max)
    Vpmax_max = Vp_STC * (1 + (beta_Vpmax / 100) * (T_mod_min - T_STC))
    Ns_max_mppt = math.floor(V_max_mppt_inv / Vpmax_max)
    Ns_max_pv = math.floor(V_sys_max / Voc_max)
    Ns_max = min(Ns_max_abs, Ns_max_mppt, Ns_max_pv)

    Vpmax_min = Vp_STC * (1 + (beta_Vpmax / 100) * (T_mod_max - T_STC))
    Ns_min_mppt = math.ceil(V_min_mppt_inv / (Vpmax_min * efficiency))
    Voc_min = Voc_STC * (1 + (beta_Voc / 100) * (T_mod_max - T_STC))
    Ns_min_start = math.ceil(V_start_inv / Voc_min)
    Ns_min = max(Ns_min_mppt, Ns_min_start)

    st.success(f"Final Ns_max: {Ns_max} | Final Ns_min: {Ns_min} | Range for String Sizing: {Ns_min}-{Ns_max}")

    # =========================
    # STEP 5: Determine The Optimum PV Modules in Series (Ns_rec)
    # =========================
    st.markdown("### Step 5: Determine The Optimum PV Modules in Series (Ns_rec)")
    st.markdown("#### Key Parameter For Optimum Calculation")
    Vrated = st.number_input("Inverter Vrated (V)", value=600)
    Vmax_mppt_inv = st.number_input("Vmax_mppt-inv (V)", value=850)
    Vmin_mppt_inv = st.number_input("Vmin_mppt-inv (V)", value=200)
    W_percent = ((Vrated - Vmin_mppt_inv) / (Vmax_mppt_inv - Vmin_mppt_inv)) * 100
    Ns_rec = math.floor(Ns_min + (W_percent/100)*(Ns_max-Ns_min))
    st.metric("W% result", f"{W_percent:.2f}%")
    st.metric("Recommendation Modules Result (Ns_rec)", f"{Ns_rec}")

    # =========================
    # STEP 6: Determine the Maximum Number of String per MPPT (Np_max per MPPT)
    # =========================
    st.markdown("### Step 6: Determine the Maximum Number of String per MPPT (Np_max per MPPT)")
    st.markdown("#### Key Parameters for Maximum String Calculation")
    Isc_max_mppt = st.number_input("Isc_max-mppt (A)", value=15.0)
    Isc_STC_input = st.number_input("Isc_STC (A)", value=13.0)
    Sf1 = 1.25
    Np_max_per_MPPT = math.floor(Isc_max_mppt / (Isc_STC_input * Sf1))
    st.metric("Final Maximum Strings Result", f"{Np_max_per_MPPT}")

    # =========================
    # STEP 7: Determine the Number of Strings per MPPT
    # =========================
    st.markdown("### Step 7: Determine the Number of Strings per MPPT")
    st.markdown("#### Inverter and Array Configuration Parameters")
    Nt = st.number_input("Total PV Modules per Inverter (Nt)", value=best_count)
    Nmppt = Ns_rec
    strings_per_MPPT = math.ceil(Nt / Ns_rec)
    st.metric("Result Configuration", f"{strings_per_MPPT}")

    # =========================
    # STEP 8: Final PV Array Configuration
    # =========================
    st.markdown("### Step 8: Final PV Array Configuration")
    st.markdown("#### Final Configuration Summary")
    st.metric("Total Strings Required", f"{strings_per_MPPT}")
    st.metric("Selected Modules in Series", f"{Ns_rec}")
