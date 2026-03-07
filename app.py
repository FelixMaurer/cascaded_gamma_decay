import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Nickel-60 Nuclear Spin Visualization", layout="wide")

st.title("Microscopic Origin of Nuclear Spin: $^{60}_{28}\text{Ni}$")

# --- SECTION 1: INTRODUCTION ---
st.header("1. The Nuclear Foundation")
col1, col2 = st.columns(2)

with col1:
    st.write("""
    In the $^{60}\text{Ni}$ nucleus, we distinguish between two groups of nucleons:
    * **The Stable Core (28 Protons, 28 Neutrons):** This forms a 'magic number' core where all nucleons 
        are perfectly paired in closed shells, resulting in a net spin of **0**[cite: 149, 271, 272].
    * **The 4 Valence Neutrons:** These 'extra' neutrons occupy the $fp$-shell orbitals (like $2p_{3/2}$ and $1f_{5/2}$) 
        and are responsible for the nucleus's total angular momentum $I$[cite: 26, 246, 275].
    """)

with col2:
    # Simple schematic of the nucleus
    st.info("Core ($I_{core}=0$) + 4 Valence Neutrons $\\rightarrow$ Total Nuclear Spin $I$")

st.divider()

# --- SECTION 2: STATES OF MOMENTUM 4 ---
st.header("2. Generating an Initial State of $I_i = 4$")
st.write("""
The excited state of $^{60}\text{Ni}$ starts with a total spin of **$I_i = 4$**. 
Because nucleons are identical fermions, they must occupy specific orbitals and couple their 
individual angular momentum vectors ($j$) to reach this sum.
""")

def plot_vectors(v1, v2, target_mag, title):
    # Create vector components
    # We simplify by placing v1 on z-axis and v2 at an angle to reach target magnitude
    # Using law of cosines: target^2 = v1^2 + v2^2 + 2*v1*v2*cos(theta)
    cos_theta = (target_mag**2 - v1**2 - v2**2) / (2 * v1 * v2)
    sin_theta = np.sqrt(1 - cos_theta**2)
    
    fig = go.Figure()
    # Vector 1
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, v1],
                               mode='lines+markers', name=f'j1 = {v1}', line=dict(width=10)))
    # Vector 2
    fig.add_trace(go.Scatter3d(x=[0, v2*sin_theta], y=[0, 0], z=[v1, v1 + v2*cos_theta],
                               mode='lines+markers', name=f'j2 = {v2}', line=dict(width=10)))
    # Resultant
    fig.add_trace(go.Scatter3d(x=[0, v2*sin_theta], y=[0, 0], z=[0, v1 + v2*cos_theta],
                               mode='lines', name=f'Total I = {target_mag}', line=dict(dash='dash', color='red')))
    
    fig.update_layout(title=title, scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
    return fig

# --- SECTION 3: VECTOR COUPLING ---
st.header("3. Intuitive Vector Coupling (Two Alternatives)")

alt1, alt2 = st.columns(2)

with alt1:
    st.subheader("Alternative A: The Mixed Orbital Case")
    st.write("One neutron in $2p_{3/2}$ ($j=1.5$) and one in $1f_{5/2}$ ($j=2.5$).")
    st.plotly_chart(plot_vectors(1.5, 2.5, 4.0, "1.5 + 2.5 Coupling"), use_container_width=True)
    st.caption("Here, the vectors align perfectly parallel to reach the maximum possible sum.")

with alt2:
    st.subheader("Alternative B: The High-Spin Orbital Case")
    st.write("Two neutrons both in the $1f_{5/2}$ shell ($j=2.5$ each).")
    st.plotly_chart(plot_vectors(2.5, 2.5, 4.0, "2.5 + 2.5 Coupling"), use_container_width=True)
    st.caption("Here, the vectors are slightly 'canted' to sum to 4 instead of the maximum 5.")

st.divider()

# --- FINAL REMARKS ---
st.warning("""
**Important Remark:** In a real nucleus, these aren't the only two ways! 
1. **Configuration Mixing:** The nucleus exists in a *superposition* of these states simultaneously. 
2. **Pauli Exclusion:** For identical neutrons in the same orbital, certain couplings are forbidden[cite: 98, 99].
3. **Collective Motion:** The core itself can sometimes contribute slightly via tiny deformations.
""")

st.write("Next, the nucleus will emit its first $\gamma$-quantum and drop to an intermediate state of $I=2$[cite: 262, 283].")
