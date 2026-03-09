import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Ni-60 Spin Cascades (3D)", layout="wide")

st.title("Ni-60 Excited States: 3D Interactive Valence Coupling")
st.write(
    "A unified 3D visual explanation of the 4→2→0 gamma-gamma cascade in "
    "Ni-60. Use the interactive viewers to rotate the nucleus and toggle "
    "different physical layers (orbits, vectors, and charge distributions)."
)

st.info(
    """
    **Important interpretation note**

    This app uses **pedagogical cartoons** to build intuition. They are **not literal pictures** of the nucleus.
    - **Orbits:** Nucleons don't move on fixed classical rings, but it is a helpful proxy for angular momentum planes.
    - **Vectors:** Show the addition of angular momentum, not literal arrows in space.
    - **Charge Distribution:** Represents the smeared-out probability cloud of the valence nucleons.
    """
)

st.divider()

# =====================================================================
# Helper Functions for 3D Geometry
# =====================================================================
def get_orthogonal_vectors(v):
    """Find two orthogonal unit vectors to a given normal vector."""
    v = np.array(v) / np.linalg.norm(v)
    if abs(v[0]) < 0.9:
        u1 = np.array([1, 0, 0])
    else:
        u1 = np.array([0, 1, 0])
    u1 = u1 - np.dot(u1, v) * v
    u1 = u1 / np.linalg.norm(u1)
    u2 = np.cross(v, u1)
    return u1, u2

def get_orbit_points(normal, radius=1.5, points=50):
    """Generate 3D coordinates for a circular orbit."""
    u1, u2 = get_orthogonal_vectors(normal)
    theta = np.linspace(0, 2 * np.pi, points)
    orbit = np.array([radius * np.cos(t) * u1 + radius * np.sin(t) * u2 for t in theta])
    return orbit[:, 0], orbit[:, 1], orbit[:, 2]

def get_ellipsoid(beta, radius=1.8, points=40):
    """Generate 3D coordinates for a charge distribution ellipsoid."""
    phi = np.linspace(0, 2 * np.pi, points)
    theta = np.linspace(0, np.pi, points)
    phi, theta = np.meshgrid(phi, theta)
    
    # Volume-conserving deformation:
    rz = radius * (1 + beta)
    rxy = radius / np.sqrt(1 + beta)
    
    x = rxy * np.sin(theta) * np.cos(phi)
    y = rxy * np.sin(theta) * np.sin(phi)
    z = rz * np.cos(theta)
    return x, y, z

# =====================================================================
# Main 3D Plotting Function
# =====================================================================
def plot_3d_state(state_name, vectors, show_orbits, show_vectors, show_charge, beta, colors):
    fig = go.Figure()
    
    # 1. Central Core (always visible)
    xc, yc, zc = get_ellipsoid(0, radius=0.8, points=20)
    fig.add_trace(go.Surface(x=xc, y=yc, z=zc, colorscale='Greys', showscale=False, opacity=1.0, name="Core"))

    total_j = np.zeros(3)

    for i, v in enumerate(vectors):
        v = np.array(v)
        total_j += v
        
        # 2. Orbits
        if show_orbits:
            ox, oy, oz = get_orbit_points(v)
            fig.add_trace(go.Scatter3d(
                x=ox, y=oy, z=oz, mode='lines', 
                line=dict(color=colors[i], width=4, dash='dash'), 
                name=f"Orbit {i+1}"
            ))
            # Nucleon dot
            fig.add_trace(go.Scatter3d(
                x=[ox[0]], y=[oy[0]], z=[oz[0]], mode='markers',
                marker=dict(color=colors[i], size=8), showlegend=False
            ))
            
        # 3. Individual Vectors
        if show_vectors:
            fig.add_trace(go.Scatter3d(
                x=[0, v[0]], y=[0, v[1]], z=[0, v[2]], mode='lines',
                line=dict(color=colors[i], width=6), name=f"j {i+1}"
            ))
            fig.add_trace(go.Cone(
                x=[v[0]], y=[v[1]], z=[v[2]], u=[v[0]], v=[v[1]], w=[v[2]],
                sizemode="absolute", sizeref=0.3, anchor="tip", colorscale=[[0, colors[i]], [1, colors[i]]], showscale=False
            ))

    # 4. Total Vector
    if show_vectors and np.linalg.norm(total_j) > 0.1:
        fig.add_trace(go.Scatter3d(
            x=[0, total_j[0]], y=[0, total_j[1]], z=[0, total_j[2]], mode='lines',
            line=dict(color='yellow', width=10), name=f"Total J={round(np.linalg.norm(total_j))}"
        ))
        fig.add_trace(go.Cone(
            x=[total_j[0]], y=[total_j[1]], z=[total_j[2]], 
            u=[total_j[0]], v=[total_j[1]], w=[total_j[2]],
            sizemode="absolute", sizeref=0.6, anchor="tip", colorscale=[[0, 'yellow'], [1, 'yellow']], showscale=False
        ))

    # 5. Charge Distribution Overlay
    if show_charge:
        ex, ey, ez = get_ellipsoid(beta)
        fig.add_trace(go.Surface(
            x=ex, y=ey, z=ez, colorscale='Blues', opacity=0.3, showscale=False, name="Charge Dist."
        ))

    fig.update_layout(
        title=f"State: {state_name}",
        scene=dict(
            xaxis=dict(range=[-4, 4], visible=False),
            yaxis=dict(range=[-4, 4], visible=False),
            zaxis=dict(range=[-4, 4], visible=False),
            aspectmode='cube'
        ),
        height=500,
        margin=dict(l=0, r=0, b=0, t=40),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    return fig

# =====================================================================
# State Configurations
# =====================================================================
colors = ["cyan", "lime", "magenta", "orange"]

# J=4: Vectors aligned upward. 
vectors_J4 = [
    [0.3, 0, 1.0], 
    [-0.3, 0, 1.0], 
    [0, 0.3, 1.0], 
    [0, -0.3, 1.0]
] # Sums close to (0,0,4)

# J=2: Two vectors pair off and cancel, two point slightly up.
vectors_J2 = [
    [1.5, 0, 0], 
    [-1.5, 0, 0], 
    [0, 0.5, 1.0], 
    [0, -0.5, 1.0]
] # Sums close to (0,0,2)

# J=0: All vectors pair off and perfectly cancel.
vectors_J0 = [
    [1.5, 0, 0], 
    [-1.5, 0, 0], 
    [0, 1.5, 0], 
    [0, -1.5, 0]
] # Sums to (0,0,0)

# =====================================================================
# Sections 1, 2, 3 (Combined 3D Views)
# =====================================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Initial State (J=4)")
    st.write("Stretched configuration. Nucleon orbits align to create a high total angular momentum.")
    show_orb_4 = st.checkbox("Show Orbits", value=True, key="o4")
    show_vec_4 = st.checkbox("Show Vectors", value=True, key="v4")
    show_chg_4 = st.checkbox("Show Charge Overlay", value=True, key="c4")
    fig_4 = plot_3d_state("J=4 (Aligned)", vectors_J4, show_orb_4, show_vec_4, show_chg_4, beta=0.4, colors=colors)
    st.plotly_chart(fig_4, use_container_width=True)

with col2:
    st.subheader("2. Intermediate State (J=2)")
    st.write("Less stretched. Some orbits begin to cross and cancel out each other's momentum.")
    show_orb_2 = st.checkbox("Show Orbits", value=True, key="o2")
    show_vec_2 = st.checkbox("Show Vectors", value=True, key="v2")
    show_chg_2 = st.checkbox("Show Charge Overlay", value=True, key="c2")
    fig_2 = plot_3d_state("J=2 (Partially Cancelled)", vectors_J2, show_orb_2, show_vec_2, show_chg_2, beta=0.2, colors=colors)
    st.plotly_chart(fig_2, use_container_width=True)

with col3:
    st.subheader("3. Ground State (J=0)")
    st.write("Spherical. All valence nucleons are paired off, moving in perfectly opposing orbits.")
    show_orb_0 = st.checkbox("Show Orbits", value=True, key="o0")
    show_vec_0 = st.checkbox("Show Vectors", value=True, key="v0")
    show_chg_0 = st.checkbox("Show Charge Overlay", value=True, key="c0")
    fig_0 = plot_3d_state("J=0 (Spherical)", vectors_J0, show_orb_0, show_vec_0, show_chg_0, beta=0.0, colors=colors)
    st.plotly_chart(fig_0, use_container_width=True)

st.divider()

# =====================================================================
# Section 4: Dynamic Transition & Wave Emission
# =====================================================================
st.header("4. Dynamic Transition: The 'Squish' and the Wave")
st.write(
    "When the nucleus transitions from $J=4$ to $J=2$, it sheds energy and angular momentum. "
    "Press **Play** below to watch the nucleus dynamically 'squish' from its stretched, aligned "
    "shape into a more compact shape. This exact reshaping of the charge distribution is what "
    "creates the outwardly expanding E2 wave packet (the photon) carrying away $2\hbar$ of angular momentum."
)

def plot_transition_animation():
    # Grids for the mesh
    phi = np.linspace(0, 2 * np.pi, 40)
    theta = np.linspace(0, np.pi, 40)
    phi, theta = np.meshgrid(phi, theta)
    
    # E2 Radiation angular dependence (m=±2 mode)
    angular_intensity = 1 - np.cos(theta)**4
    
    frames = []
    num_frames = 40
    
    # Beta squishes from 0.4 (J=4) down to 0.2 (J=2)
    betas = np.linspace(0.4, 0.2, num_frames)
    
    # Initialize base geometry for the plot
    rz_base = 1.0 * (1 + betas[0])
    rxy_base = 1.0 / np.sqrt(1 + betas[0])
    x_nuc = rxy_base * np.sin(theta) * np.cos(phi)
    y_nuc = rxy_base * np.sin(theta) * np.sin(phi)
    z_nuc = rz_base * np.cos(theta)
    
    fig = go.Figure(
        data=[
            # Nucleus
            go.Surface(x=x_nuc, y=y_nuc, z=z_nuc, colorscale='Plasma', showscale=False, name="Nucleus"),
            # Wave (Starts hidden inside nucleus)
            go.Surface(x=x_nuc*0, y=y_nuc*0, z=z_nuc*0, colorscale='Viridis', opacity=0.5, showscale=False, name="Wave")
        ],
        layout=go.Layout(
            scene=dict(
                xaxis=dict(range=[-4, 4], visible=False),
                yaxis=dict(range=[-4, 4], visible=False),
                zaxis=dict(range=[-4, 4], visible=False),
                aspectmode='cube'
            ),
            height=600,
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=0),
            updatemenus=[dict(
                type="buttons", showactive=False, y=0.1, x=0.5, xanchor="center", yanchor="bottom",
                buttons=[dict(
                    label="▶ Play Transition & Wave Emission",
                    method="animate",
                    args=[None, dict(frame=dict(duration=60, redraw=True), transition=dict(duration=0), mode='immediate')]
                )]
            )]
        )
    )
    
    for i in range(num_frames):
        beta = betas[i]
        
        # 1. Update Nucleus Shape
        rz = 1.0 * (1 + beta)
        rxy = 1.0 / np.sqrt(1 + beta)
        x_n = rxy * np.sin(theta) * np.cos(phi)
        y_n = rxy * np.sin(theta) * np.sin(phi)
        z_n = rz * np.cos(theta)
        
        # 2. Update Wave Expansion
        wave_radius = 1.0 + (i * 0.15) # Expands outward
        wave_amplitude = angular_intensity * wave_radius
        
        # Fading effect as wave expands
        opacity = max(0, 1.0 - (i / num_frames))
        
        x_w = wave_amplitude * np.sin(theta) * np.cos(phi)
        y_w = wave_amplitude * np.sin(theta) * np.sin(phi)
        z_w = wave_amplitude * np.cos(theta)
        
        frames.append(go.Frame(
            data=[
                go.Surface(x=x_n, y=y_n, z=z_n),
                go.Surface(x=x_w, y=y_w, z=z_w, opacity=opacity)
            ],
            name=str(i)
        ))
        
    fig.frames = frames
    return fig

st.plotly_chart(plot_transition_animation(), use_container_width=True, key="anim_squish_wave")
