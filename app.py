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
# SET FIXED BACKGROUND IMAGE
# -----------------------------------------------------
def apply_background():
    with open("bg.jpg", "rb") as img_file:
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

# =====================================================
# PAGE 1: WELCOME PAGE
# =====================================================
if st.session_state.page == "welcome":

    apply_background()

    st.markdown(
        """
        <div style="text-align:center; padding-top:40px; background:rgba(255,255,255,0.8); padding:20px; border-radius:12px;">
            <h1 style='font-size:38px;'>
                <b>Interactive Online Sizing Framework for Grid-Connected Photovoltaic Systems</b>
            </h1>
            <p style='font-size:20px;'>
                Hello! This tool will assist you in designing and sizing your PV modules.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # START BUTTON WITH ANIMATION
    if st.button("👉 Start Sizing Tool", use_container_width=True):
        with st.spinner("Loading PV Sizing Dashboard..."):
            time.sleep(2)

        switch_to_dimensioning()
        st.rerun()


# =====================================================
# PAGE 2: DIMENSIONING PAGE (FORMAL LAYOUT)
# =====================================================
elif st.session_state.page == "dimensioning":

    st.markdown(
        "<h1 style='text-align:center;'>📘 Dimensioning of PV Modules</h1>",
        unsafe_allow_html=True
    )
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
            peak_sun_hours = st.number_input("Peak Sun Hours (h/day)", value=5.0)


    st.markdown("---")

    # -------------------------------------------------
    # AUTO CALC RESULTS IN A BOX
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
        st.metric("Yearly Energy (Wh/m²)", f"{yearly_energy:.3f}")

    st.markdown("---")

    # -------------------------------------------------
    # STEP 2 FORMAL BOX
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
    st.markdown("<br>", unsafe_allow_html=True)

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
        f"""
        ### 📊 Orientation: **{orientation}**
        - Modules Upwards: **{N_up}**  
        - Modules Across: **{N_across}**  
        - **Total Installable PV Modules: {N_max}**
        """
    )
