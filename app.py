import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Ni-60 Spin Cascades", layout="wide")

st.title("Microscopic Spin States of Ni-60")
st.write("Visualizing the internal neutron couplings that drive the gamma-gamma cascades.")

# --- HELPER FUNCTION: 2D SHELL SCHEMATIC ---
def draw_2d_shell(title_text):
    fig_shell = go.Figure()
    
    # Draw the Core
    fig_shell.add_shape(type="circle", x0=-2, y0=-2, x1=2, y1=2, 
                        fillcolor="lightgray", line_color="black")
    fig_shell.add_annotation(x=0, y=0, text="<b>Stable Core<br>(28p, 28n)<br>Spin = 0</b>", 
                             showarrow=False, font=dict(size=14, color="black"))
    
    # Draw Valence Shells
    fig_shell.add_shape(type="circle", x0=-3.5, y0=-3.5, x1=3.5, y1=3.5, 
                        line=dict(color="cyan", dash="dash"))
    fig_shell.add_annotation(x=0, y=3.7, text="2p3/2 Orbital", showarrow=False, font=dict(color="cyan", size=14))
    
    fig_shell.add_shape(type="circle", x0=-5, y0=-5, x1=5, y1=5, 
                        line=dict(color="lime", dash="dash"))
    fig_shell.add_annotation(x=0, y=5.2, text="1f5/2 Orbital", showarrow=False, font=dict(color="lime", size=14))
    
    # Add 4 Valence Neutrons (3 in 2p3/2, 1 in 1f5/2)
    theta_in = [np.pi/4, 3*np.pi/4, 5*np.pi/4] 
    theta_out = [7*np.pi/4]                    
    
    fig_shell.add_trace(go.Scatter(x=3.5*np.cos(theta_in), y=3.5*np.sin(theta_in), 
                                   mode='markers', marker=dict(size=15, color='cyan'), name="3 Neutrons (2p3/2)"))
    fig_shell.add_trace(go.Scatter(x=5.0*np.cos(theta_out), y=5.0*np.sin(theta_out), 
                                   mode='markers', marker=dict(size=15, color='lime'), name="1 Neutron (1f5/2)"))
    
    fig_shell.update_layout(title=title_text, 
                            xaxis=dict(visible=False, range=[-6, 6]), 
                            yaxis=dict(visible=False, range=[-6, 6], scaleanchor="x", scaleratio=1),
                            height=400, width=400, showlegend=False,
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=0, r=0, t=40, b=0))
    return fig_shell

# --- HELPER FUNCTION: 3D VECTOR COUPLING WITH ARROWHEAD ---
def plot_3d_vectors(v1, v2, target_mag, title):
    cos_theta = (target_mag**2 - v1**2 - v2**2) / (2 * v1 * v2)
    cos_theta = np.clip(cos_theta, -1.0, 1.0) 
    sin_theta = np.sqrt(1 - cos_theta**2)
    
    end_x = 0
    end_y = v2 * sin_theta
    end_z = v1 + v2 * cos_theta
    
    # Visual offset for the resultant vector so it doesn't overlap perfectly
    offset_x = 0.25 
    
    # Calculate direction for the arrowhead
    norm = np.sqrt(end_y**2 + end_z**2)
    u_dir, v_dir, w_dir = 0, 0, 1 # Default fallback
    if norm > 0:
        u_dir = 0  # Direction remains purely in YZ plane
        v_dir = end_y / norm
        w_dir = end_z / norm

    fig = go.Figure()
    
    # Vector 1 (Orbital 1)
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, v1],
                               mode='lines+markers', name=f'Orbital 1 (j={v1})', line=dict(width=8, color='cyan')))
    # Vector 2 (Orbital 2)
    fig.add_trace(go.Scatter3d(x=[0, end_x], y=[0, end_y], z=[v1, end_z],
                               mode='lines+markers', name=f'Orbital 2 (j={v2})', line=dict(width=8, color='lime')))
    
    # Resultant Vector Line (Total Spin) - Shifted by offset_x
    fig.add_trace(go.Scatter3d(x=[offset_x, offset_x], y=[0, end_y], z=[0, end_z],
                               mode='lines', name=f'Total Spin = {target_mag}', line=dict(color='yellow', width=8)))
    
    # Arrowhead (Cone) for Resultant - Shifted by offset_x
    fig.add_trace(go.Cone(x=[offset_x], y=[end_y], z=[end_z],
                          u=[u_dir], v=[v_dir], w=[w_dir],
                          sizemode="absolute", sizeref=0.8, anchor="tip",
                          colorscale=[[0, 'yellow'], [1, 'yellow']], showscale=False, name="Direction"))
    
    fig.update_layout(title=title, scene=dict(aspectmode='cube', xaxis_title='X', yaxis_title='Y', zaxis_title='Z',
                                              xaxis=dict(range=[-4, 4]), yaxis=dict(range=[-4, 4]), zaxis=dict(range=[0, 5])), 
                                              height=450, paper_bgcolor="rgba(0,0,0,0)")
    return fig


st.divider()

# ==========================================
# MAIN SECTION 1: THE INITIAL EXCITED STATE (I=4)
# ==========================================
st.header("1. The Initial Excited State (I = 4)")
st.write("Following the beta decay of Co-60, the Ni-60 nucleus is formed in a highly excited configuration with a total spin of 4.")

col1_a, col1_b = st.columns([1, 2])
with col1_a:
    st.subheader("1.1. Schematic of Ni-60")
    st.plotly_chart(draw_2d_shell("Valence Arrangement (I=4)"), use_container_width=True)
    
with col1_b:
    st.subheader("1.2. Internal Coupling in the 2p3/2 Orbital")
    st.write("Before adding both shells together, the 3 neutrons in the 2p3/2 orbital must couple. Two neutrons pair up (spin antiparallel) and cancel each other out to 0. This leaves the third unpaired neutron to define the total momentum of this orbital: **j = 1.5**.")
    
    st.subheader("1.3. Coupling the Orbitals to Reach Spin 4")
    st.write("The unpaired j=1.5 from the 2p3/2 orbital couples with the j=2.5 from the 1f5/2 orbital. To reach the maximum allowed spin of 4, the vectors must align perfectly parallel. *(Note: The yellow resultant vector is visually shifted slightly along the X-axis so it is not hidden behind the components).*")
    st.plotly_chart(plot_3d_vectors(1.5, 2.5, 4.0, "1.5 + 2.5 Re-coupled to 4"), use_container_width=True)

st.divider()

# ==========================================
# MAIN SECTION 2: THE INTERMEDIATE STATE (I=2)
# ==========================================
st.header("2. The Intermediate State (I = 2)")
st.write("The nucleus emits its first gamma quantum (1173 keV), shedding 2 units of angular momentum in a quadrupole transition. The neutrons re-align to drop the total nuclear spin to 2.")

col2_a, col2_b = st.columns([1, 2])
with col2_a:
    st.subheader("2.1. Schematic of Ni-60")
    st.write("The nucleons do not necessarily leave their respective energy shells; they can simply shift their quantum geometric alignment.")
    st.plotly_chart(draw_2d_shell("Valence Arrangement (I=2)"), use_container_width=True)

with col2_b:
    st.subheader("2.2. Re-coupling to Reach Spin 2")
    st.write("Using the exact same orbital momenta (j=1.5 and j=2.5), the vectors cant backwards against each other. This partial cancellation successfully lowers the total resulting nuclear spin (yellow arrow) to exactly 2.")
    st.plotly_chart(plot_3d_vectors(1.5, 2.5, 2.0, "1.5 + 2.5 Re-coupled to 2"), use_container_width=True)

st.divider()

# ==========================================
# MAIN SECTION 3: THE I=1 STATE
# ==========================================
st.header("3. Alternative Re-coupling (I = 1)")
st.write("While the actual Ni-60 cascade goes 4-2-0, other configurations or hypothetical cascades require different intermediate states. Here is how those same nucleons can couple to reach a total spin of 1.")

col3_a, col3_b = st.columns([1, 2])
with col3_a:
    st.subheader("3.1. Schematic of Ni-60")
    st.write("Once again, the 4 valence neutrons occupy the fp-shell, but their internal vector orientations are severely misaligned compared to the I=4 state.")
    st.plotly_chart(draw_2d_shell("Valence Arrangement (I=1)"), use_container_width=True)

with col3_b:
    st.subheader("3.2. Re-coupling to Reach Spin 1")
    st.write("To drop the total spin all the way down to 1, the j=1.5 and j=2.5 vectors must point heavily in opposite directions. The resulting total angular momentum vector shrinks significantly.")
    st.plotly_chart(plot_3d_vectors(1.5, 2.5, 1.0, "1.5 + 2.5 Re-coupled to 1"), use_container_width=True)
