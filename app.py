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

if "bg_image" not in st.session_state:
    st.session_state.bg_image = None


def go_to_dimensioning():
    st.session_state.page = "dimensioning"


# -----------------------------------------------------
# BACKGROUND HANDLER
# -----------------------------------------------------
def set_background(image_file):
    if image_file is not None:
        encoded_img = base64.b64encode(image_file.read()).decode()
        css_code = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_img}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """
        st.markdown(css_code, unsafe_allow_html=True)


# =====================================================
# PAGE 1: WELCOME PAGE
# =====================================================
if st.session_state.page == "welcome":

    st.markdown(
        """
        <h1 style='text-align:center; padding-top:20px;'>
            Interactive Online Sizing Framework for Grid-Connected Photovoltaic Systems
        </h1>
        <p style='text-align:center; font-size:18px;'>
            Hello! It is a tool that will assist you in designing and sizing your PV modules.
        </p>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")

    # ---------------------------
    # Background Image Selector
    # ---------------------------
    st.subheader("Background Settings")

    bg_option = st.radio(
        "Choose background option:",
        ["Default Solar Image", "Upload Custom Background"],
        horizontal=True
    )

    if bg_option == "Default Solar Image":
        st.session_state.bg_image = None
        set_background(None)

        st.image(
            "https://images.unsplash.com/photo-1509395176047-4a66953fd231",
            caption="Default Solar Farm Background",
            use_column_width=True
        )

    else:
        uploaded_bg = st.file_uploader(
            "Upload your background image", type=["jpg", "png"]
        )
        if uploaded_bg:
            st.session_state.bg_image = uploaded_bg
            set_background(uploaded_bg)
            st.success("Background updated successfully!")
        else:
            st.info("Please upload an image.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------
    # START BUTTON + ANIMATION (FIXED)
    # ---------------------------
    if st.button("👉 Start Sizing Tool", use_container_width=True):
        with st.spinner("Preparing dashboard..."):
            time.sleep(2)

        st.success("Entering PV Sizing Module...")
        time.sleep(1)

        go_to_dimensioning()
        st.rerun()


# =====================================================
# PAGE 2: DIMENSIONING PAGE (ORIGINAL LAYOUT)
# =====================================================
elif st.session_state.page == "dimensioning":

    st.title("📘 Dimensioning of PV Modules")
    st.write("Follow the calculations below to size your PV modules accurately.")
    st.markdown("---")

    # -------------------------------------------------
    # STEP 1: CHOOSE A PV MODULE
    # -------------------------------------------------
    st.header("Step 1: Choose a PV Module")

    col1, col2 = st.columns(2)

    with col1:
        panel_length = st.number_input("Panel Length (m)", min_value=0.1, value=1.7)
        panel_width = st.number_input("Panel Width (m)", min_value=0.1, value=1.1)
        rated_power = st.number_input("Rated Power (W)", min_value=1, value=550)
        isc_stc = st.number_input("Isc STC (A)", min_value=0.1, value=13.0)
        isc_max_inv = st.number_input("Isc Max Inv (A)", min_value=0.1, value=15.0)

    with col2:
        T_coef = st.number_input("Temperature Coefficient (°C)", value=-0.35)
        T_mod = st.number_input("Module Temperature (°C)", value=45)
        T_src = st.number_input("Reference Temperature (°C)", value=25)

        st.subheader("Loss / Performance Factors")
        f_mm = st.number_input("Module mismatch, f_mm", value=0.98)
        f_clean = st.number_input("Soiling, f_clean", value=0.97)
        f_degrad = st.number_input("Degradation, f_degrad", value=0.99)
        f_unshade = st.number_input("Shading, f_unshade", value=0.98)
        eta_cable = st.number_input("Cable efficiency, η_cable", value=0.98)
        eta_inv = st.number_input("Inverter efficiency, η_inv", value=0.96)
        peak_sun_hours = st.number_input("Peak Sun Hours (h/day)", value=5.0)

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

    st.subheader("Calculated Results")
    colA, colB = st.columns(2)

    with colA:
        st.metric("Panel Area (m²)", f"{panel_area:.3f}")
        st.metric("f_temp-ave", f"{f_temp_ave:.4f}")

    with colB:
        st.metric("Power Output (W/m²)", f"{power_output:.3f}")
        st.metric("Yearly Energy (Wh/m²)", f"{yearly_energy:.3f}")

    st.markdown("---")

    # -------------------------------------------------
    # STEP 2: ARCHITECTURE CONSTRAINT
    # -------------------------------------------------
    st.header("Step 2: Architecture Constraint")

    colX, colY = st.columns(2)

    with colX:
        Wm = st.number_input("Width of Module, Wm (m)", value=panel_width)
        Lm = st.number_input("Length of Module, Lm (m)", value=panel_length)

    with colY:
        delta = st.number_input("Inter-module gap, ∆ (m)", value=0.02)
        site_width = st.number_input("Width of Site (m)", min_value=1.0, value=20.0)
        site_length = st.number_input("Length of Site (m)", min_value=1.0, value=30.0)

    st.markdown("---")

    orientation = st.selectbox("Orientation", ["Landscape", "Portrait"])

    if orientation == "Landscape":
        N_up = math.floor(site_width / (Wm + delta))
        N_across = math.floor(site_length / (Lm + delta))
    else:
        N_up = math.floor(site_width / (Lm + delta))
        N_across = math.floor(site_length / (Wm + delta))

    N_max = N_up * N_across

    st.success(
        f"""
        **Orientation:** {orientation}  
        ➤ Modules Upwards: **{N_up}**  
        ➤ Modules Across: **{N_across}**  
        ➤ Total Installed PV Modules: **{N_max}**
        """
    )
