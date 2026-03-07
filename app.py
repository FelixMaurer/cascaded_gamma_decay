import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Ni-60 Spin Cascades", layout="wide")

st.title("Microscopic Spin States of Ni-60")
st.write("Visualizing the internal neutron couplings that drive the complete 4-2-0 gamma-gamma cascade.")

# --- HELPER FUNCTION: 2D SHELL SCHEMATIC ---
def draw_2d_shell(title_text, num_in=3, num_out=1):
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
    
    # Determine neutron positions dynamically based on state
    if num_in == 4:
        theta_in = [np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4]
    elif num_in == 3:
        theta_in = [np.pi/4, 3*np.pi/4, 5*np.pi/4]
    elif num_in == 2:
        theta_in = [np.pi/4, 3*np.pi/4]
    else:
        theta_in = []
        
    if num_out == 2:
        theta_out = [5*np.pi/4, 7*np.pi/4]
    elif num_out == 1:
        theta_out = [7*np.pi/4]
    else:
        theta_out = []
    
    if len(theta_in) > 0:
        fig_shell.add_trace(go.Scatter(x=3.5*np.cos(theta_in), y=3.5*np.sin(theta_in), 
                                       mode='markers', marker=dict(size=15, color='cyan'), name=f"{num_in} Neutrons (2p3/2)"))
    if len(theta_out) > 0:
        fig_shell.add_trace(go.Scatter(x=5.0*np.cos(theta_out), y=5.0*np.sin(theta_out), 
                                       mode='markers', marker=dict(size=15, color='lime'), name=f"{num_out} Neutrons (1f5/2)"))
    
    fig_shell.update_layout(title=title_text, 
                            xaxis=dict(visible=False, range=[-6, 6]), 
                            yaxis=dict(visible=False, range=[-6, 6], scaleanchor="x", scaleratio=1),
                            height=350, showlegend=False,
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=0, r=0, t=40, b=0))
    return fig_shell

# --- HELPER FUNCTION: 3D INTERNAL COUPLING ---
def plot_internal_coupling(title, mode="3_neutrons"):
    fig_internal = go.Figure()
    
    if mode == "3_neutrons":
        # Neutron 1 (Unpaired, pointing Z) - Cyan
        fig_internal.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 1.5],
                                   mode='lines+markers', name='Neutron 1 (Unpaired)', line=dict(width=6, color='cyan')))
        # Neutron 2 (Paired, pointing X) - Magenta
        fig_internal.add_trace(go.Scatter3d(x=[0, 1.5], y=[0, 0], z=[0, 0],
                                   mode='lines+markers', name='Neutron 2 (Paired)', line=dict(width=6, color='magenta')))
        # Neutron 3 (Paired, pointing -X, canceling Neutron 2) - Magenta
        fig_internal.add_trace(go.Scatter3d(x=[0, -1.5], y=[0, 0], z=[0, 0],
                                   mode='lines+markers', name='Neutron 3 (Paired)', line=dict(width=6, color='magenta')))
        
        # Resultant Orbital Vector - Dashed Cyan 
        fig_internal.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 1.5],
                                   mode='lines', name='Net Orbital j=1.5', line=dict(dash='dash', color='cyan', width=8)))
    
    elif mode == "4_neutrons":
        # All 4 neutrons perfectly paired and canceling
        fig_internal.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 1.5],
                                   mode='lines+markers', name='Pair 1 (Up)', line=dict(width=6, color='magenta')))
        fig_internal.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, -1.5],
                                   mode='lines+markers', name='Pair 1 (Down)', line=dict(width=6, color='magenta')))
        fig_internal.add_trace(go.Scatter3d(x=[0, 1.5], y=[0, 0], z=[0, 0],
                                   mode='lines+markers', name='Pair 2 (Right)', line=dict(width=6, color='magenta')))
        fig_internal.add_trace(go.Scatter3d(x=[0, -1.5], y=[0, 0], z=[0, 0],
                                   mode='lines+markers', name='Pair 2 (Left)', line=dict(width=6, color='magenta')))
        
        # Resultant is 0
        fig_internal.add_trace(go.Scatter3d(x=[0], y=[0], z=[0],
                                   mode='markers', name='Net Orbital j=0', marker=dict(size=10, color='cyan')))

    fig_internal.update_layout(title=title, 
                               scene=dict(aspectmode='cube', xaxis_title='X', yaxis_title='Y', zaxis_title='Z',
                               xaxis=dict(range=[-2, 2]), yaxis=dict(range=[-2, 2]), zaxis=dict(range=[-2, 2])), 
                               height=350, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=40, b=0),
                               legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    return fig_internal

# --- HELPER FUNCTION: 3D VECTOR COUPLING WITH ARROWHEAD ---
def plot_3d_vectors(v1, v2, target_mag, title):
    fig = go.Figure()
    
    # Handle the completely zeroed out Ground State
    if v1 == 0 and v2 == 0:
        fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0],
                                   mode='markers', name=f'Total Spin I={target_mag}', marker=dict(size=12, color='yellow')))
        # Add invisible traces to keep legend consistent
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,0], mode='lines', name='Vector A', line=dict(width=0, color='cyan')))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,0], mode='lines', name='Vector B', line=dict(width=0, color='lime')))
    else:
        cos_theta = (target_mag**2 - v1**2 - v2**2) / (2 * v1 * v2)
        cos_theta = np.clip(cos_theta, -1.0, 1.0) 
        sin_theta = np.sqrt(1 - cos_theta**2)
        
        end_x = 0
        end_y = v2 * sin_theta
        end_z = v1 + v2 * cos_theta
        
        offset_x = 0.25 
        
        norm = np.sqrt(end_y**2 + end_z**2)
        u_dir, v_dir, w_dir = 0, 0, 1
        if norm > 0:
            u_dir = 0  
            v_dir = end_y / norm
            w_dir = end_z / norm

        fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, v1],
                                   mode='lines+markers', name=f'Vector A (j={v1})', line=dict(width=8, color='cyan')))
        fig.add_trace(go.Scatter3d(x=[0, end_x], y=[0, end_y], z=[v1, end_z],
                                   mode='lines+markers', name=f'Vector B (j={v2})', line=dict(width=8, color='lime')))
        
        fig.add_trace(go.Scatter3d(x=[offset_x, offset_x], y=[0, end_y], z=[0, end_z],
                                   mode='lines', name=f'Total Spin I={target_mag}', line=dict(color='yellow', width=8)))
        
        fig.add_trace(go.Cone(x=[offset_x], y=[end_y], z=[end_z],
                              u=[u_dir], v=[v_dir], w=[w_dir],
                              sizemode="absolute", sizeref=0.8, anchor="tip",
                              colorscale=[[0, 'yellow'], [1, 'yellow']], showscale=False, name="Direction"))
    
    fig.update_layout(title=title, scene=dict(aspectmode='cube', xaxis_title='X', yaxis_title='Y', zaxis_title='Z',
                                              xaxis=dict(range=[-4, 4]), yaxis=dict(range=[-4, 4]), zaxis=dict(range=[0, 5])), 
                                              height=400, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=40, b=0),
                                              legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    return fig


st.divider()

# ==========================================
# MAIN SECTION 1: THE INITIAL EXCITED STATE (I=4)
# ==========================================
st.header("1. The Initial Excited State (I = 4)")
st.write("Following the beta decay of Co-60, the Ni-60 nucleus is formed in an excited configuration.")

col1_a, col1_b, col1_c = st.columns(3)
with col1_a:
    st.subheader("1.1. Schematic")
    st.plotly_chart(draw_2d_shell("Valence Arrangement", num_in=3, num_out=1), use_container_width=True, key="shell_1")
    
with col1_b:
    st.subheader("1.2. Internal 2p3/2 Coupling")
    st.write("Two neutrons cancel to 0 (magenta), leaving the unpaired neutron to define the orbital's j=1.5 momentum.")
    st.plotly_chart(plot_internal_coupling("3 Neutrons -> Net j=1.5", mode="3_neutrons"), use_container_width=True, key="internal_1")

with col1_c:
    st.subheader("1.3. Orbital Coupling to I=4")
    st.write("The j=1.5 and j=2.5 orbitals align parallel to reach the maximum allowed spin of 4.")
    st.plotly_chart(plot_3d_vectors(1.5, 2.5, 4.0, "1.5 + 2.5 Re-coupled to 4"), use_container_width=True, key="vector_1")

# --- SECTION 1.4: ALTERNATIVE CONFIGURATIONS (I=4) ---
st.write("---")
st.subheader("1.4. Alternative Microscopic Configurations")
col1_d, col1_e, col1_f = st.columns(3)

with col1_d:
    st.write("**Alternative Schematic:** Two neutrons promoted to 1f5/2.")
    st.plotly_chart(draw_2d_shell("Alternative Valence (I=4)", num_in=2, num_out=2), use_container_width=True, key="shell_1_alt")

with col1_e:
    st.write("The configuration above (one $j=1.5$ coupling with one $j=2.5$) is not the only way the nucleus can reach an initial state of $I=4$.")
    st.write("**Why are there many alternatives?**")
    st.write("1. **Configuration Mixing:** The nucleus exists as a *superposition* of multiple valid shell arrangements simultaneously.")
    st.write("2. **Multiple Valid Couplings:** If two neutrons occupy the $1f_{5/2}$ shell ($j=2.5$ each), they can also couple together to form $I=4$. Because their maximum combined spin is 5, they sit at an angle to sum perfectly to 4.")

with col1_f:
    st.write("**Alternative Vector Coupling**")
    st.plotly_chart(plot_3d_vectors(2.5, 2.5, 4.0, "Alternative Coupling: 2.5 + 2.5 = 4"), use_container_width=True, key="alt_vector_1")

st.divider()

# ==========================================
# MAIN SECTION 2: THE INTERMEDIATE STATE (I=2)
# ==========================================
st.header("2. The Intermediate State (I = 2)")
st.write("After the first quadrupole gamma emission (1173 keV), the nucleus sheds 2 units of angular momentum.")

col2_a, col2_b, col2_c = st.columns(3)
with col2_a:
    st.subheader("2.1. Schematic")
    st.plotly_chart(draw_2d_shell("Valence Arrangement", num_in=3, num_out=1), use_container_width=True, key="shell_2")

with col2_b:
    st.subheader("2.2. Internal 2p3/2 Coupling")
    st.write("The internal pairing of the 2p3/2 orbital remains intact, continuously providing a net j=1.5.")
    st.plotly_chart(plot_internal_coupling("3 Neutrons -> Net j=1.5", mode="3_neutrons"), use_container_width=True, key="internal_2")

with col2_c:
    st.subheader("2.3. Orbital Coupling to I=2")
    st.write("The orbitals cant backwards against each other, partially canceling to drop the total nuclear spin to 2.")
    st.plotly_chart(plot_3d_vectors(1.5, 2.5, 2.0, "1.5 + 2.5 Re-coupled to 2"), use_container_width=True, key="vector_2")

# --- SECTION 2.4: ALTERNATIVE CONFIGURATIONS (I=2) ---
st.write("---")
st.subheader("2.4. Alternative Microscopic Configurations (Dropping to 2)")
col2_d, col2_e, col2_f = st.columns(3)

with col2_d:
    st.write("**Alternative Schematic:** Two neutrons remaining in 1f5/2.")
    st.plotly_chart(draw_2d_shell("Alternative Valence (I=2)", num_in=2, num_out=2), use_container_width=True, key="shell_2_alt")

with col2_e:
    st.write("**How does the alternative configuration shed spin?**")
    st.write("Just like the primary configuration, the alternative configuration consisting of two neutrons in the $1f_{5/2}$ shell does not require the neutrons to immediately jump back down to a lower shell.")
    st.write("To emit the $\gamma_1$ photon and drop down to an intermediate spin of $I=2$, the two $j=2.5$ momentum vectors simply re-orient themselves. By pushing further apart from each other, they cancel each other out more severely, dropping their total vector sum from 4 down to exactly 2.")

with col2_f:
    st.write("**Alternative Vector Coupling**")
    st.plotly_chart(plot_3d_vectors(2.5, 2.5, 2.0, "Alternative Coupling: 2.5 + 2.5 = 2"), use_container_width=True, key="alt_vector_2")

st.divider()

# ==========================================
# MAIN SECTION 3: THE FINAL GROUND STATE (I=0)
# ==========================================
st.header("3. The Final Ground State (I = 0)")
st.write("The nucleus emits its second gamma quantum (1333 keV), shedding its final 2 units of angular momentum. The cascade is complete!")

col3_a, col3_b, col3_c = st.columns(3)
with col3_a:
    st.subheader("3.1. Schematic")
    st.write("All 4 neutrons finally drop into the lowest energy valence shell (2p3/2), which can hold exactly 4 neutrons.")
    st.plotly_chart(draw_2d_shell("Ground State Arrangement", num_in=4, num_out=0), use_container_width=True, key="shell_3")

with col3_b:
    st.subheader("3.2. Internal 2p3/2 Coupling")
    st.write("Because the shell is completely full, the 4 neutrons form two perfect pairs. Their momentum vectors perfectly cancel out in all directions.")
    st.plotly_chart(plot_internal_coupling("4 Neutrons -> Net j=0", mode="4_neutrons"), use_container_width=True, key="internal_3")

with col3_c:
    st.subheader("3.3. Orbital Coupling to I=0")
    st.write("With the 2p3/2 orbital completely canceled to 0, and the 1f5/2 orbital completely empty, the total nuclear spin is exactly 0.")
    st.plotly_chart(plot_3d_vectors(0, 0, 0, "0 + 0 Re-coupled to 0"), use_container_width=True, key="vector_3")
