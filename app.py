import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.special import legendre

st.set_page_config(page_title="Gamma-Gamma Angular Correlation Lab", layout="wide")

# --- HEADER & CONTEXT ---
st.title("Gamma-Gamma Angular Correlation Theory")
st.write("Visualizing the 4-2-0 Cascade of $^{60}_{28}$Ni [cite: 242, 246]")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Transition Parameters")
coupling_mode = st.sidebar.radio("Neutron Coupling Alternative", 
                                ["Alternative A (Mixed Shells)", "Alternative B (High Spin Shell)"])

# --- SECTION 1: THE NUCLEUS ---
st.header("1. The $^{60}$Ni Nucleus Microstate")
c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("Shell Configuration")
    st.write("""
    * **The Core ($N=28$):** Perfectly paired neutrons in a closed core. $I_{core} = 0$[cite: 40].
    * **The Valence Space:** 4 neutrons in the $fp$-shell ($2p_{3/2}$, $1f_{5/2}$) .
    """)
    if coupling_mode == "Alternative A (Mixed Shells)":
        st.info("Configuration: $(2p_{3/2})^3 (1f_{5/2})^1$. One neutron promoted to reach $I=4$.")
        v1, v2 = 1.5, 2.5
    else:
        st.info("Configuration: $(2p_{3/2})^2 (1f_{5/2})^2$. Two neutrons coupling in $f_{5/2}$.")
        v1, v2 = 2.5, 2.5

with c2:
    # 3D Vector Coupling Plot
    def plot_vectors(v1_val, v2_val, target):
        # Law of cosines for angle
        cos_theta = (target**2 - v1_val**2 - v2_val**2) / (2 * v1_val * v2_val)
        theta = np.arccos(np.clip(cos_theta, -1, 1))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, v1_val], 
                                   name='j1', line=dict(color='blue', width=8)))
        fig.add_trace(go.Scatter3d(x=[0, v2_val*np.sin(theta)], y=[0, 0], z=[v1_val, v1_val + v2_val*np.cos(theta)], 
                                   name='j2', line=dict(color='green', width=8)))
        fig.add_trace(go.Scatter3d(x=[0, v2_val*np.sin(theta)], y=[0, 0], z=[0, v1_val + v2_val*np.cos(theta)], 
                                   name='Resultant I=4', line=dict(color='red', width=5, dash='dash')))
        fig.update_layout(scene=dict(aspectmode='cube'), margin=dict(l=0, r=0, b=0, t=0))
        return fig

    st.plotly_chart(plot_vectors(v1, v2, 4.0), use_container_width=True)

st.divider()

# --- SECTION 2: THE FIRST EMISSION ---
st.header("2. The First $\gamma$-Emission ($\gamma_1$) [cite: 246]")
st.write("""
The transition from $I=4 \\rightarrow I=2$ releases a photon of **1173 keV**.
Because $\Delta I = 2$, this is a **Quadrupole transition** ($l=2$)[cite: 26, 182].
""")



# Mathematical remark
st.latex(r"W(\vartheta) = 1 + A_2 \cos^2(\vartheta) + A_4 \cos^4(\vartheta) \quad \text{[cite: 300]}")

# --- SECTION 3: ANGULAR CORRELATION PLOT ---
st.header("3. Probability Distribution $W(\vartheta)$")
st.write("""
When we detect $\gamma_1$ at $\vartheta=0$, we align the nucleus. The probability of 
detecting $\gamma_2$ is no longer isotropic[cite: 198, 297].
""")

theta_range = np.linspace(0, 2*np.pi, 200)
# Constants for Co60 from script
A2 = 1/8  # 
A4 = 1/24 # 

def w_theta(t):
    return 1 + A2 * (np.cos(t)**2) + A4 * (np.cos(t)**4)

radius = w_theta(theta_range)

fig_polar = go.Figure()
fig_polar.add_trace(go.Scatterpolar(r=radius, theta=np.degrees(theta_range), 
                                    mode='lines', fill='toself', name='W(theta)'))
fig_polar.update_layout(title="Theoretical Angular Correlation (Point-like Detector)")
st.plotly_chart(fig_polar)

st.warning("""
**Note on Configuration:** While we visualize two neutrons coupling, the actual state 
is a collective 'Configuration Mix.' The 4 neutrons are indistinguishable fermions; 
we only measure the total angular momentum $I$ of the system [cite: 184-186].
""")

st.subheader("Next Experimental Step:")
st.write("Would you like me to explain how the finite size of the NaI(Tl) detectors 
'blurs' this theoretical curve into the **Effective Anisotropy Coefficients** ($A^{eff}$) used in the lab? [cite: 315-317]")
