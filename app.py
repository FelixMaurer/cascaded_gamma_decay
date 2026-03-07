import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Ni-60 Spin & Angular Correlation", layout="wide")

st.title("Microscopic Origin of Nuclear Spin in Ni-60")
st.write("Exploring how 4 valence neutrons create the initial excited state for the 4-2-0 cascade[cite: 242, 243].")

# --- SECTION 1: GRAPHICAL DEPICTION OF THE NUCLEUS ---
st.header("1. The Nucleus: Core vs. Valence Neutrons")
st.write("Nuclei possess discrete energy levels with total angular momentum and parity[cite: 175]. For Ni-60, we can separate the nucleons into a stable core and an active valence space.")

c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("Structure Breakdown")
    st.markdown("""
    * **The Core:** 28 protons and 28 neutrons completely fill the lowest energy shells. 
    * **Core Spin:** Because every nucleon is perfectly paired, they cancel each other out. The core contributes exactly **0** to the total spin.
    * **The Valence Space:** The remaining **4 neutrons** occupy the outer *fp-shell* (orbitals like 2p3/2 and 1f5/2). 
    * **Excited State:** Right after the beta decay of Co-60, these 4 neutrons are in an excited arrangement that sums to a total nuclear spin of **4**[cite: 245, 246].
    """)

with c2:
    # 2D Plotly Graphic of the Shell Model
    fig_shell = go.Figure()
    
    # Draw the Core
    fig_shell.add_shape(type="circle", x0=-2, y0=-2, x1=2, y1=2, 
                        fillcolor="lightgray", line_color="black")
    fig_shell.add_annotation(x=0, y=0, text="Stable Core<br>(28p, 28n)<br>Spin = 0", showarrow=False, font=dict(size=14))
    
    # Draw Valence Shells (Rings)
    fig_shell.add_shape(type="circle", x0=-3.5, y0=-3.5, x1=3.5, y1=3.5, 
                        line=dict(color="blue", dash="dash"))
    fig_shell.add_annotation(x=0, y=3.7, text="2p3/2 Orbital", showarrow=False, font=dict(color="blue"))
    
    fig_shell.add_shape(type="circle", x0=-5, y0=-5, x1=5, y1=5, 
                        line=dict(color="green", dash="dash"))
    fig_shell.add_annotation(x=0, y=5.2, text="1f5/2 Orbital", showarrow=False, font=dict(color="green"))
    
    # Add 4 Valence Neutrons (Scatter points)
    # Showing a mixed state: 3 in the lower orbital, 1 promoted to the higher orbital
    theta_in = [np.pi/4, 3*np.pi/4, 5*np.pi/4] # 3 neutrons in 2p3/2
    theta_out = [7*np.pi/4]                    # 1 neutron in 1f5/2
    
    fig_shell.add_trace(go.Scatter(x=3.5*np.cos(theta_in), y=3.5*np.sin(theta_in), 
                                   mode='markers', marker=dict(size=15, color='blue'), name="Neutrons (2p3/2)"))
    fig_shell.add_trace(go.Scatter(x=5.0*np.cos(theta_out), y=5.0*np.sin(theta_out), 
                                   mode='markers', marker=dict(size=15, color='green'), name="Neutron (1f5/2)"))
    
    fig_shell.update_layout(title="Schematic of Ni-60 Valence Neutrons", 
                            xaxis=dict(visible=False, range=[-6, 6]), 
                            yaxis=dict(visible=False, range=[-6, 6]),
                            height=500, width=500, showlegend=True)
    st.plotly_chart(fig_shell, use_container_width=True)

st.divider()

# --- SECTION 2: VECTOR COUPLING TO REACH SPIN 4 ---
st.header("2. Coupling the Vectors to Reach a Spin of 4")
st.write("How do the individual angular momenta (j) of these unpaired neutrons combine to create a total momentum of 4?")

def plot_3d_vectors(v1, v2, target_mag, title, desc):
    # Calculate angle using law of cosines
    cos_theta = (target_mag**2 - v1**2 - v2**2) / (2 * v1 * v2)
    cos_theta = np.clip(cos_theta, -1.0, 1.0) # Prevent domain errors
    sin_theta = np.sqrt(1 - cos_theta**2)
    
    fig = go.Figure()
    # Vector 1 (Blue)
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, v1],
                               mode='lines+markers', name=f'j1 = {v1}', line=dict(width=8, color='blue')))
    # Vector 2 (Green)
    fig.add_trace(go.Scatter3d(x=[0, v2*sin_theta], y=[0, 0], z=[v1, v1 + v2*cos_theta],
                               mode='lines+markers', name=f'j2 = {v2}', line=dict(width=8, color='green')))
    # Resultant Vector (Red dashed)
    fig.add_trace(go.Scatter3d(x=[0, v2*sin_theta], y=[0, 0], z=[0, v1 + v2*cos_theta],
                               mode='lines', name=f'Total Spin = {target_mag}', line=dict(dash='dash', color='red', width=6)))
    
    fig.update_layout(title=title, scene=dict(aspectmode='cube', xaxis_title='X', yaxis_title='Y', zaxis_title='Z'), height=400)
    return fig

col_alt1, col_alt2 = st.columns(2)

with col_alt1:
    st.subheader("Alternative A: Mixed Orbitals")
    st.write("One unpaired neutron in the 2p3/2 shell (j=1.5) and one in the 1f5/2 shell (j=2.5).")
    st.plotly_chart(plot_3d_vectors(1.5, 2.5, 4.0, "1.5 + 2.5 Coupling", ""), use_container_width=True)
    st.caption("Notice how they must align perfectly parallel to reach the maximum possible sum of 4.")

with col_alt2:
    st.subheader("Alternative B: Same Orbital")
    st.write("Two unpaired neutrons both occupying the 1f5/2 shell (j=2.5 each).")
    st.plotly_chart(plot_3d_vectors(2.5, 2.5, 4.0, "2.5 + 2.5 Coupling", ""), use_container_width=True)
    st.caption("Because their combined maximum is 5, they sit at an angle to each other to sum precisely to 4.")

st.divider()

# --- SECTION 3: IMPORTANT QUANTUM CAVEATS ---
st.header("3. Important Quantum Reality Checks")
st.warning("""
While the vectors and shells above provide an intuitive picture, nature is more complex:
* **Configuration Mixing:** The real Ni-60 nucleus does not pick just *one* of the alternatives above. It exists in a quantum superposition—a smeared-out mixture of multiple valid orbital arrangements at the same time. 
* **Indistinguishability:** We cannot paint a neutron red to track it. We can only measure the collective property of the nucleus transitioning from an initial state to an intermediate state[cite: 177, 184].
* **Pauli Exclusion Principle:** Because neutrons are identical fermions, certain angles and couplings are strictly forbidden if they occupy the exact same orbital.
""")
