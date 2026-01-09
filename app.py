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
# BACKGROUND IMAGE
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
    except:
        pass

# =====================================================
# PAGE 1: WELCOME
# =====================================================
if st.session_state.page == "welcome":

    apply_background()

    st.markdown(
        """
        <div style="text-align:center; padding:30px; background:rgba(255,255,255,0.85);
        border-radius:12px;">
        <h1>Interactive Online Sizing Framework for Grid-Connected Photovoltaic Systems</h1>
        <p>Design and sizing tool for large-scale PV systems.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("👉 Start Sizing Tool", use_container_width=True):
        with st.spinner("Loading..."):
            time.sleep(1.5)
        switch_to_dimensioning()
        st.rerun()

# =====================================================
# PAGE 2: PART A
# =====================================================
elif st.session_state.page == "dimensioning":

    st.markdown("<h1 style='text-align:center;'>📘 Part A: Dimensioning of PV Modules</h1>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        panel_length = st.number_input("Panel Length (m)", value=2.382)
        panel_width = st.number_input("Panel Width (m)", value=1.134)
        rated_power = st.number_input("Rated Power (W)", value=605)
        peak_sun_hours = st.number_input("Peak Sun Hours (h/day)", value=4.0)

    with col2:
        T_coef = st.number_input("Temperature Coefficient (%/°C)", value=-0.28)
        T_mod = st.number_input("Module Temperature (°C)", value=55)
        T_ref = st.number_input("Reference Temperature (°C)", value=25)

    panel_area = panel_length * panel_width
    f_temp = 1 + ((T_coef / 100) * (T_mod - T_ref))

    power_output = rated_power * f_temp / panel_area
    yearly_energy = (rated_power * peak_sun_hours * 365 * f_temp) / panel_area / 1000

    st.success("Module Performance Calculated")

    site_width = st.number_input("Site Width (m)", value=45.74)
    site_length = st.number_input("Site Length (m)", value=115.88)
    gap = st.number_input("Inter-module Gap (m)", value=0.01)

    N_up = math.floor(site_width / (panel_width + gap))
    N_across = math.floor(site_length / (panel_length + gap))
    best_count = N_up * N_across

    final_power = power_output * best_count
    final_energy = yearly_energy * best_count

    st.metric("Total PV Modules", best_count)
    st.metric("Total Peak Power Output (W)", f"{final_power:,.2f}")
    st.metric("Total Yearly Energy (kWh/year)", f"{final_energy:,.2f}")

    st.markdown("---")
    if st.button("➡ Proceed to Part B: Inverter Sizing", use_container_width=True):
        switch_to_part_b()
        st.rerun()

# =====================================================
# PAGE 3: PART B
# =====================================================
elif st.session_state.page == "part_b":

    st.markdown("<h1 style='text-align:center;'>⚡ Part B: Sizing with Central Inverter</h1>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("Summary of Part A")
    st.write(f"• Total PV Modules: **{best_count}**")
    st.write(f"• Total Peak Power Output: **{final_power:,.2f} W**")
    st.write(f"• Total Yearly Energy: **{final_energy:,.2f} kWh/year**")

    st.markdown("---")

    st.subheader("Step 1: Decide DC/AC Ratio")
    fi = st.number_input("DC/AC Ratio (fᵢ)", value=1.2)

    st.subheader("Step 2: Determine Suitable Inverter")
    required_inv_power = (rated_power * best_count) / fi
    st.metric("Required Inverter Nominal Power (W)", f"{required_inv_power:,.2f}")

    st.markdown("---")
    st.subheader("Step 3 & 4: String Sizing Range")

    colA, colB = st.columns(2)
    with colA:
        Voc_stc = st.number_input("V_oc STC (V)", value=49.5)
        Vp_stc = st.number_input("V_p STC (V)", value=41.5)
        beta_voc = st.number_input("β Voc (%/°C)", value=-0.24)
        beta_vp = st.number_input("β Vpmax (%/°C)", value=-0.29)

    with colB:
        Tmin = st.number_input("T_mod min (°C)", value=15)
        Tmax = st.number_input("T_mod max (°C)", value=65)
        Vabs = st.number_input("Inverter Vmax abs (V)", value=1500)
        Vmppt_max = st.number_input("Vmax MPPT (V)", value=1300)
        Vmppt_min = st.number_input("Vmin MPPT (V)", value=500)
        Vsys = st.number_input("Module Vsys max (V)", value=1500)
        Vstart = st.number_input("Vstart inv (V)", value=600)
        eff = st.number_input("Efficiency", value=0.98)

    Voc_max = Voc_stc * (1 + (beta_voc/100)*(Tmin-25))
    Ns_max = min(
        math.floor(Vabs/Voc_max),
        math.floor(Vmppt_max/(Vp_stc)),
        math.floor(Vsys/Voc_max)
    )

    Vp_min = Vp_stc * (1 + (beta_vp/100)*(Tmax-25))
    Ns_min = max(
        math.ceil(Vmppt_min/(Vp_min*eff)),
        math.ceil(Vstart/Voc_stc)
    )

    st.metric("Final Ns_max", Ns_max)
    st.metric("Final Ns_min", Ns_min)
    st.info(f"Recommended String Range: {Ns_min} – {Ns_max}")

    st.markdown("---")
    st.subheader("Step 5: Optimum Modules in Series")

    Vrated = st.number_input("Inverter Vrated (V)", value=850)
    W_percent = ((Vrated - Vmppt_min)/(Vmppt_max - Vmppt_min))*100
    Ns_rec = math.floor(Ns_min + (W_percent/100)*(Ns_max - Ns_min))

    st.metric("W% Result", f"{W_percent:.2f}%")
    st.metric("Recommended Modules in Series (Ns_rec)", Ns_rec)

    st.markdown("---")
    st.subheader("Step 6: Maximum Strings per MPPT")

    Isc_max = st.number_input("Isc max MPPT (A)", value=30)
    Isc_stc = st.number_input("Isc STC (A)", value=13)
    Sf1 = 1.25

    Np_max = math.floor(Isc_max/(Isc_stc*Sf1))
    st.metric("Maximum Strings per MPPT", Np_max)

    st.markdown("---")
    st.subheader("Step 7: Number of Strings per MPPT")

    Nt = st.number_input("Total PV Modules per Inverter", value=best_count)
    result_config = Nt / Ns_rec
    st.metric("Result Configuration (Strings)", f"{result_config:.0f}")

    st.markdown("---")
    st.subheader("Step 8: Final PV Array Configuration")

    st.success(f"""
    ✔ Total Strings Required: {int(result_config)}
    ✔ Selected Modules in Series: {Ns_rec}
    """)
