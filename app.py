import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Ni-60 Spin & Angular Correlation", layout="wide")

st.title("Microscopic Origin of Nuclear Spin in Ni-60")
st.write("Exploring how 4 valence neutrons create the initial excited state for the 4-2-0 cascade.")

# --- SECTION 1: GRAPHICAL DEPICTION OF THE NUCLEUS ---
st.header("1. The Nucleus: Core vs. Valence Neutrons")
st.write("Nuclei possess discrete energy levels with total angular momentum and parity. For Ni-60, we can separate the nucleons into a stable core and an active valence space.")

c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("Structure Breakdown")
    st.markdown("""
    * **The Core:** 28 protons and 28 neutrons completely fill the lowest energy shells. 
    * **Core Spin:** Because every nucleon is perfectly paired, they cancel each other out. The core contributes exactly **0** to the total spin.
    * **The Valence Space:** The remaining **4 neutrons** occupy the outer fp-shell (orbitals like 2p3/2 and 1f5/2). 
    * **Excited State:** Right after the beta decay of Co-60, these 4 neutrons are in an excited arrangement that sums to a total nuclear spin of **4**.
    """)

with c2:
    fig_shell = go.Figure()
    
    # Draw the Core
    fig_shell.add_shape(type="circle", x0=-2, y0=-2, x1=2, y1=2, 
                        fillcolor="lightgray", line_color="black")
    fig_shell.add_annotation(x=0, y=0, text="<b>Stable Core<br>(28p, 28n)<br>Spin = 0</b>", 
                             showarrow=False, font=dict(size=14, color="black"))
    
    # Draw Valence Shells
    fig_shell.add_shape(type="circle", x0=-3.5, y0=-3.5, x1=3.5, y1=3.5, 
                        line=dict(color="blue", dash="dash"))
    fig_shell.add_annotation(x=0, y=3.7, text="2p3/2 Orbital", showarrow=False, font=dict(color="blue", size=14))
    
    fig_shell.add_shape(type="circle", x0=-5, y0=-5, x1=5, y1=5, 
                        line=dict(color="green", dash="dash"))
    fig_shell.add_annotation(x=0, y=5.2, text="1f5/2 Orbital", showarrow=False, font=dict(color="green", size=14))
    
    # Add 4 Valence Neutrons
    theta_in = [np.pi/4, 3*np.pi/4, 5*np.pi/4] 
    theta_out = [7*np.pi/4]                    
    
    fig_shell.add_trace(go.Scatter(x=3.5*np.cos(theta_in), y=3.5*np.sin(theta_in), 
                                   mode='markers', marker=dict(size=15, color='blue'), name="3 Neutrons (2p3/2)"))
    fig_shell.add_trace(go.Scatter(x=5.0*np.cos(theta_out), y=5.0*np.sin(theta_out), 
                                   mode='markers', marker=dict(size=15, color='green'), name="1 Neutron (1f5/2)"))
    
    fig_shell.update_layout(title="Schematic of Ni-60 Valence Neutrons", 
                            xaxis=dict(visible=False, range=[-6, 6]), 
                            yaxis=dict(visible=False, range=[-6, 6], scaleanchor="x", scaleratio=1),
                            height=500, width=500, showlegend=True)
    st.plotly_chart(fig_shell, use_container_width=True)

st.divider()

# --- SECTION 2: THE IN-BETWEEN STEP (INTERNAL COUPLING) ---
st.header("2. The In-Between Step: Internal Coupling in the 2p3/2 Orbital")

col_int1, col_int2 = st.columns([1, 2])

with col_int1:
    st.subheader("Where does j=1.5 come from?")
    st.write("""
    A single neutron's total momentum (j) is the sum of its orbital motion (l) and its intrinsic spin (s). 
    * **Orbit (l):** The 'p' in 2p3/2 stands for an orbital momentum of l = 1.
    * **Spin (s):** A neutron always has a built-in spin of s = 1/2.
    * **Total (j):** j = l + s = 1 + 1/2 = 1.5.
    """)
    
    st.subheader("The Pairing Effect")
    st.write("""
    Because they share the exact same orbital, the Pauli Exclusion Principle forces the 3 neutrons to arrange themselves efficiently.
    
    Two of the neutrons form a 'pair', orienting their momentum vectors in opposite directions. This internal pairing cancels their contribution to 0. 
    The total momentum of the entire orbital is therefore defined solely by the third, unpaired neutron.
    """)

with col_int2:
    fig_internal = go.Figure()
    
    # Neutron 1 (Unpaired, pointing Z)
    fig_internal.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 1.5],
                               mode='lines+markers', name='Neutron 1 (j=1.5)', line=dict(width=6, color='lightblue')))
    # Neutron 2 (Paired, pointing X)
    fig_internal.add_trace(go.Scatter3d(x=[0, 1.5], y=[0, 0], z=[0, 0],
                               mode='lines+markers', name='Neutron 2 (j=1.5)', line=dict(width=6, color='darkblue')))
    # Neutron 3 (Paired, pointing -X, canceling Neutron 2)
    fig_internal.add_trace(go.Scatter3d(x=[0, -1.5], y=[0, 0], z=[0, 0],
                               mode='lines+markers', name='Neutron 3 (j=1.5)', line=dict(width=6, color='darkblue')))
    
    # Resultant
    fig_internal.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 1.5],
                               mode='lines', name='Total Orbital j = 1.5', line=dict(dash='dash', color='red', width=8)))
    
    fig_internal.update_layout(title="Internal Vector Cancellation in 2p3/2", 
                               scene=dict(aspectmode='cube', xaxis_title='X', yaxis_title='Y', zaxis_title='Z',
                               xaxis=dict(range=[-2, 2]), yaxis=dict(range=[-2, 2]), zaxis=dict(range=[-2, 2])), 
                               height=400)
    st.plotly_chart(fig_internal, use_container_width=True)

st.divider()

# --- SECTION 3: VECTOR COUPLING TO REACH SPIN 4 ---
st.header("3. Coupling the Orbitals to Reach Spin 4")
st.write("Now we take the total momentum of the 2p3/2 orbital (1.5) and couple it with the neutron in the 1f5/2 orbital (2.5).")

def plot_3d_vectors(v1, v2, target_mag, title):
    cos_theta = (target_mag**2 - v1**2 - v2**2) / (2 * v1 * v2)
    cos_theta = np.clip(cos_theta, -1.0, 1.0) 
    sin_theta = np.sqrt(1 - cos_theta**2)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, v1],
                               mode='lines+markers', name=f'Orbital 1 (j={v1})', line=dict(width=8, color='blue')))
    fig.add_trace(go.Scatter3d(x=[0, v2*sin_theta], y=[0, 0], z=[v1, v1 + v2*cos_theta],
                               mode='lines+markers', name=f'Orbital 2 (j={v2})', line=dict(width=8, color='green')))
    fig.add_trace(go.Scatter3d(x=[0, v2*sin_theta], y=[0, 0], z=[0, v1 + v2*cos_theta],
                               mode='lines', name=f'Total Spin = {target_mag}', line=dict(dash='dash', color='red', width=6)))
    
    fig.update_layout(title=title, scene=dict(aspectmode='cube', xaxis_title='X', yaxis_title='Y', zaxis_title='Z',
                                              xaxis=dict(range=[-4, 4]), yaxis=dict(range=[-4, 4]), zaxis=dict(range=[0, 5])), 
                                              height=400)
    return fig

col_alt1, col_alt2 = st.columns(2)

with col_alt1:
    st.subheader("Alternative A: Mixed Orbitals")
    st.plotly_chart(plot_3d_vectors(1.5, 2.5, 4.0, "1.5 + 2.5 Coupling = 4"), use_container_width=True)
    st.caption("They align perfectly parallel to reach the maximum possible sum of 4.")

with col_alt2:
    st.subheader("Alternative B: Same Orbital")
    st.plotly_chart(plot_3d_vectors(2.5, 2.5, 4.0, "2.5 + 2.5 Coupling = 4"), use_container_width=True)
    st.caption("Because their combined maximum is 5, they sit at an angle to each other to sum precisely to 4.")

st.divider()

# --- SECTION 4: IMPORTANT QUANTUM CAVEATS ---
st.header("4. Important Quantum Reality Checks")
st.warning("""
While the vectors and shells above provide an intuitive picture, nature is more complex:
* **Configuration Mixing:** The real Ni-60 nucleus exists in a quantum superposition—a smeared-out mixture of multiple valid orbital arrangements at the same time. 
* **Indistinguishability:** We cannot paint a neutron red to track it. We can only measure the collective property of the nucleus transitioning from an initial state to an intermediate state.
* **Pauli Exclusion Principle:** Because neutrons are identical fermions, certain angles and couplings are strictly forbidden if they occupy the exact same orbital.
""")

st.divider()

# --- SECTION 5: THE INTERMEDIATE STATE (SPIN 2) ---
st.header("5. The Intermediate State: Dropping to Spin 2")
st.write("""
When the nucleus emits the first gamma quantum (1173 keV), it sheds 2 units of angular momentum. 
The nucleus is now in the intermediate state with a total spin of **I = 2**. 

Fascinatingly, the neutrons do not necessarily have to change which shells they live in! 
They can simply undergo a quantum 're-alignment'—shifting the angle of their vectors to cancel each other out more heavily.
""")

col_int_1, col_int_2 = st.columns(2)

with col_int_1:
    st.subheader("Re-aligning the Mixed Orbitals")
    st.write("Using the exact same orbitals from Alternative A (j=1.5 and j=2.5), watch how the vectors shift their angle to sum to 2 instead of 4.")
    st.plotly_chart(plot_3d_vectors(1.5, 2.5, 2.0, "1.5 + 2.5 Re-coupled = 2"), use_container_width=True)
    st.caption("The vectors are now 'canted' backwards against each other, successfully lowering the total nuclear spin to 2.")

with col_int_2:
    st.subheader("Re-aligning the Same Orbital")
    st.write("Using the orbitals from Alternative B (j=2.5 and j=2.5), they also shift to drop the total spin down to 2.")
    st.plotly_chart(plot_3d_vectors(2.5, 2.5, 2.0, "2.5 + 2.5 Re-coupled = 2"), use_container_width=True)
    st.caption("A sharper angle allows the two 2.5 vectors to heavily cancel, yielding the required intermediate spin of 2.")
