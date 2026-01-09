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
# SESSION STATE INITIALIZATION
# -----------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "welcome"

# Storage from Part A → Part B
for key in [
    "total_modules",
    "total_power",
    "total_energy"
]:
    if key not in st.session_state:
        st.session_state[key] = None


def go_to_part_a():
    st.session_state.page = "part_a"


def go_to_part_b():
    st.session_state.page = "part_b"


# -----------------------------------------------------
# BACKGROUND IMAGE (SAFE LOAD)
# -----------------------------------------------------
def apply_background():
    try:
        with open("bg.png", "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
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
# PAGE 1: WELCOME
# =====================================================
if st.session_state.page == "welcome":

    apply_background()

    st.markdown(
        """
        <div style="text-align:center; padding:40px;
        background:rgba(255,255,255,0.88);
        border-radius:12px;">
            <h1>Interactive Online Sizing Framework for Grid-Connected PV Systems</h1>
            <p>Professional PV system sizing tool for large-scale design.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("👉 Start Sizing Tool", use_container_width=True):
        with st.spinner("Loading dashboard..."):
            time.sleep(1.5)
        go_to_part_a()
        st.rerun()


# =====================================================
# PAGE 2: PART A – PV MODULE & SITE SIZING
# =====================================================
elif st.session_state.page == "part_a":

    st.title("📘 Part A: Dimensioning of PV Modules")
    st.markdown("---")

    # -----------------------------
    # STEP 1: MODULE PARAMETERS
    # -----------------------------
    st.subheader("Step 1: Choose a PV Module")

    col1, col2 = st.columns(2)

    with col1:
        panel_length = st.number_input("Panel Length (m)", value=2.382)
        panel_width = st.number_input("Panel Width (m)", value=1.134)
        rated_power = st.number_input("Rated Power (W)", value=605)

    with col2:
        T_coef = st.number_input("Temperature Coefficient (%/°C)", value=-0.28)
        T_mod = st.number_input("Module Temperature (°C)", value=55)
        T_src = st.number_input("Reference Temperature (°C)", value=25)
        f_mm = st.number_input("Module mismatch", value=0.97)
        f_degrad = st.number_input("Degradation", value=0.975)
        peak_sun_hours = st.number_input("Peak Sun Hours (h/day)", value=4.0)

    panel_area = panel_length * panel_width
    f_temp_ave = 1 + (T_coef / 100) * (T_mod - T_src)

    power_output = (rated_power * f_mm * f_temp_ave * f_degrad) / panel_area
    yearly_energy = (peak_sun_hours * 365 * rated_power *
                     f_mm * f_temp_ave * f_degrad) / panel_area / 1000

    st.markdown("---")
    st.metric("Power Output (W/m²)", f"{power_output:.2f}")
    st.metric("Yearly Energy (kWh/m²/year)", f"{yearly_energy:.2f}")

    # -----------------------------
    # STEP 2: SITE LAYOUT
    # -----------------------------
    st.markdown("---")
    st.subheader("Step 2: Architecture Constraint")

    site_width = st.number_input("Site Width (m)", value=45.74)
    site_length = st.number_input("Site Length (m)", value=115.88)
    delta = st.number_input("Inter-module gap (m)", value=0.01)

    N_land = math.floor(site_width / (panel_width + delta)) * \
             math.floor(site_length / (panel_length + delta))

    N_port = math.floor(site_width / (panel_length + delta)) * \
             math.floor(site_length / (panel_width + delta))

    if N_land >= N_port:
        best_orientation = "Landscape"
        best_count = N_land
    else:
        best_orientation = "Portrait"
        best_count = N_port

    total_power = power_output * best_count
    total_energy = yearly_energy * best_count

    st.session_state.total_modules = best_count
    st.session_state.total_power = total_power
    st.session_state.total_energy = total_energy

    st.success(f"Best Orientation: {best_orientation}")
    st.metric("Total PV Modules", best_count)
    st.metric("Total Peak Power (W)", f"{total_power:,.2f}")
    st.metric("Total Yearly Energy (kWh/year)", f"{total_energy:,.2f}")

    st.markdown("---")

    if st.button("➡️ Proceed to Part B: Inverter Sizing", use_container_width=True):
        go_to_part_b()
        st.rerun()


# =====================================================
# PAGE 3: PART B – CENTRAL INVERTER SIZING
# =====================================================
elif st.session_state.page == "part_b":

    st.title("📕 Part B: Sizing with Central Inverter")
    st.markdown("---")

    # -----------------------------
    # SUMMARY PART A
    # -----------------------------
    st.subheader("Summary of Part A")

    colS1, colS2, colS3 = st.columns(3)
    colS1.metric("Total PV Modules", st.session_state.total_modules)
    colS2.metric("Total Peak Power (W)", f"{st.session_state.total_power:,.2f}")
    colS3.metric("Total Yearly Energy (kWh/year)", f"{st.session_state.total_energy:,.2f}")

    st.markdown("---")

    # -----------------------------
    # STEP 1: DC/AC RATIO
    # -----------------------------
    st.subheader("Step 1: Decide DC/AC Ratio")
    dc_ac = st.number_input("DC/AC Ratio", value=1.2)

    # -----------------------------
    # STEP 2: INVERTER POWER
    # -----------------------------
    st.subheader("Step 2: Determine Suitable Inverter")

    inverter_required = (
        st.session_state.total_power / dc_ac
    )

    st.metric(
        "Required Inverter Nominal Power (W)",
        f"{inverter_required:,.2f}"
    )

    st.markdown("---")

    # -----------------------------
    # STEP 3–4: STRING SIZING RANGE
    # -----------------------------
    st.subheader("Step 3 & 4: String Sizing Range")

    Voc_stc = st.number_input("Voc STC (V)", value=52.6)
    Vmp_stc = st.number_input("Vmp STC (V)", value=44.3)
    beta_voc = st.number_input("β Voc (%/°C)", value=-0.25)
    beta_vmp = st.number_input("β Vmp (%/°C)", value=-0.30)
    Tmin = st.number_input("T_mod min (°C)", value=10)
    Tmax = st.number_input("T_mod max (°C)", value=65)
    Vmax_inv = st.number_input("Inverter Max DC Voltage (V)", value=1500)
    Vmin_mppt = st.number_input("Inverter Min MPPT Voltage (V)", value=500)
    Vstart = st.number_input("Inverter Start Voltage (V)", value=600)

    Voc_max = Voc_stc * (1 + (beta_voc / 100) * (Tmin - 25))
    Voc_min = Voc_stc * (1 + (beta_voc / 100) * (Tmax - 25))

    Ns_max = math.floor(Vmax_inv / Voc_max)
    Ns_min = math.ceil(Vstart / Voc_min)

    st.metric("Final Ns_max", Ns_max)
    st.metric("Final Ns_min", Ns_min)
    st.metric("String Sizing Range", f"{Ns_min} – {Ns_max}")

    st.markdown("---")

    # -----------------------------
    # STEP 5: OPTIMUM Ns
    # -----------------------------
    st.subheader("Step 5: Optimum Modules in Series")

    Vrated = st.number_input("Inverter Rated Voltage (V)", value=1000)
    W_percent = ((Vrated - Vmin_mppt) / (Vmax_inv - Vmin_mppt)) * 100

    Ns_rec = math.floor(Ns_min + (W_percent / 100) * (Ns_max - Ns_min))

    st.metric("W% Result", f"{W_percent:.2f} %")
    st.metric("Recommended Ns", Ns_rec)

    st.markdown("---")

    # -----------------------------
    # STEP 6: MAX STRINGS PER MPPT
    # -----------------------------
    st.subheader("Step 6: Maximum Strings per MPPT")

    Isc_mppt = st.number_input("Inverter Isc Max MPPT (A)", value=26)
    Isc_stc = st.number_input("Module Isc STC (A)", value=13)
    Sf = 1.25

    Np_max = math.floor(Isc_mppt / (Isc_stc * Sf))

    st.metric("Maximum Strings per MPPT", Np_max)

    st.markdown("---")

    # -----------------------------
    # STEP 7–8: FINAL CONFIGURATION
    # -----------------------------
    st.subheader("Final PV Array Configuration")

    total_strings = math.ceil(
        st.session_state.total_modules / Ns_rec
    )

    st.metric("Total Strings Required", total_strings)
    st.metric("Modules per String", Ns_rec)
