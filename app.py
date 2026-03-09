import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Ni-60 Spin Cascades (3D)", layout="wide")

st.title("Ni-60 Excited States: 3D Interactive Valence Coupling")
st.write(
    "A unified 3D visual explanation of the 4→2→0 gamma-gamma cascade in "
    "Ni-60. Use the interactive viewers to rotate the nucleus and toggle "
    "different physical layers (orbits, vectors, charge distributions, and the core)."
)

st.info(
    """
    **Important interpretation note**

    This app uses **pedagogical cartoons** to build intuition. They are **not literal pictures** of the nucleus.
    - **Orbits:** Nucleons don't move on fixed classical rings, but it is a helpful proxy for angular momentum planes.
    - **Vectors:** Show the exact mathematical addition of angular momentum ($j=1.5$ for $p_{3/2}$ and $j=2.5$ for $f_{5/2}$).
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

def get_orbit_points(normal, radius, points=60):
    """Generate 3D coordinates for a circular orbit."""
    u1, u2 = get_orthogonal_vectors(normal)
    theta = np.linspace(0, 2 * np.pi, points)
    orbit = np.array([radius * np.cos(t) * u1 + radius * np.sin(t) * u2 for t in theta])
    return orbit[:, 0], orbit[:, 1], orbit[:, 2]

def get_ellipsoid(beta, radius=1.8, points=40):
    """
    Generate 3D coordinates for a charge distribution ellipsoid.
    We use beta to drive an OBLATE deformation (squished along Z, bulging in XY).
    This matches the classical picture of nucleons orbiting in the equatorial plane.
    """
    phi = np.linspace(0, 2 * np.pi, points)
    theta = np.linspace(0, np.pi, points)
    phi, theta = np.meshgrid(phi, theta)
    
    # Volume-conserving OBLATE deformation (beta > 0 squishes Z):
    rz = radius * (1 - beta)
    rxy = radius / np.sqrt(1 - beta)
    
    x = rxy * np.sin(theta) * np.cos(phi)
    y = rxy * np.sin(theta) * np.sin(phi)
    z = rz * np.cos(theta)
    return x, y, z

# =====================================================================
# Main 3D Plotting Function
# =====================================================================
def plot_3d_state(state_name, vectors, show_orbits, show_vectors, show_charge, show_core, beta, radii, colors, names):
    fig = go.Figure()
    
    # 1. Central Core
    if show_core:
        xc, yc, zc = get_ellipsoid(0, radius=0.8, points=20)
        fig.add_trace(go.Surface(x=xc, y=yc, z=zc, colorscale='Greys', showscale=False, opacity=1.0, name="Core"))

    total_j = np.zeros(3)
    vector_scale = 1.0 # 1 unit of 3D space = exactly 1 hbar of angular momentum

    # Add custom legend entries for the orbital types just once
    added_p32 = False
    added_f52 = False

    for i, v in enumerate(vectors):
        v = np.array(v)
        total_j += v
        
        show_in_legend = False
        if names[i] == "p3/2" and not added_p32:
            show_in_legend = True
            added_p32 = True
        elif names[i] == "f5/2" and not added_f52:
            show_in_legend = True
            added_f52 = True
            
        legend_group = names[i]

        # 2. Orbits (perpendicular to exact j vectors)
        if show_orbits:
            ox, oy, oz = get_orbit_points(v, radius=radii[i])
            fig.add_trace(go.Scatter3d(
                x=ox, y=oy, z=oz, mode='lines', 
                line=dict(color=colors[i], width=4, dash='dash'), 
                name=f"{names[i]} orbit",
                legendgroup=legend_group,
                showlegend=show_in_legend
            ))
            # Nucleon dot
            fig.add_trace(go.Scatter3d(
                x=[ox[0]], y=[oy[0]], z=[oz[0]], mode='markers',
                marker=dict(color=colors[i], size=8), 
                legendgroup=legend_group,
                showlegend=False
            ))
            
        # 3. Individual Vectors (lengths are exactly 1.5 and 2.5)
        if show_vectors:
            vx, vy, vz = v * vector_scale
            fig.add_trace(go.Scatter3d(
                x=[0, vx], y=[0, vy], z=[0, vz], mode='lines',
                line=dict(color=colors[i], width=6), 
                name=f"j ({names[i]} = {np.linalg.norm(v):.1f})",
                legendgroup=legend_group,
                showlegend=False
            ))
            fig.add_trace(go.Cone(
                x=[vx], y=[vy], z=[vz], u=[vx], v=[vy], w=[vz],
                sizemode="absolute", sizeref=0.4, anchor="tip", colorscale=[[0, colors[i]], [1, colors[i]]], showscale=False
            ))

    # 4. Total Vector
    if show_vectors and np.linalg.norm(total_j) > 0.1:
        tj_scaled = total_j * vector_scale
        fig.add_trace(go.Scatter3d(
            x=[0, tj_scaled[0]], y=[0, tj_scaled[1]], z=[0, tj_scaled[2]], mode='lines',
            line=dict(color='yellow', width=10), name=f"Total J={round(np.linalg.norm(total_j))}"
        ))
        fig.add_trace(go.Cone(
            x=[tj_scaled[0]], y=[tj_scaled[1]], z=[tj_scaled[2]], 
            u=[tj_scaled[0]], v=[tj_scaled[1]], w=[tj_scaled[2]],
            sizemode="absolute", sizeref=0.8, anchor="tip", colorscale=[[0, 'yellow'], [1, 'yellow']], showscale=False
        ))

    # 5. Charge Distribution Overlay
    if show_charge:
        ex, ey, ez = get_ellipsoid(beta)
        fig.add_trace(go.Surface(
            x=ex, y=ey, z=ez, colorscale='Blues', opacity=0.25, showscale=False, name="Charge Dist."
        ))

    fig.update_layout(
        title=f"State: {state_name}",
        scene=dict(
            xaxis=dict(range=[-4, 4], visible=False),
            yaxis=dict(range=[-4, 4], visible=False),
            zaxis=dict(range=[-1, 5], visible=False), # Shifted to show the tall J=4 vector
            aspectmode='cube'
        ),
        height=500,
        margin=dict(l=0, r=0, b=0, t=40),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    return fig

# =====================================================================
# State Configurations (Mathematically Exact Vectors!)
# =====================================================================

# J=4: Two p3/2 cancel in equator. One p3/2 (1.5) and one f5/2 (2.5) point straight up.
# Exact Vector sum: (0,0,1.5) + (0,0,2.5) = (0,0,4.0)
vectors_J4 = [[1.5, 0, 0], [-1.5, 0, 0], [0, 0, 1.5], [0, 0, 2.5]] 
radii_J4   = [1.5, 1.5, 1.5, 2.2]
colors_J4  = ["cyan", "cyan", "cyan", "lime"]
names_J4   = ["p3/2", "p3/2", "p3/2", "f5/2"]

# J=2: Two p3/2 cancel on Y-axis. One p3/2 points left (-1.5). The f5/2 tilts up and right (1.5, 0, 2.0).
# Length of f5/2 = sqrt(1.5^2 + 2.0^2) = sqrt(6.25) = exactly 2.5!
# Exact Vector sum: (-1.5,0,0) + (1.5,0,2.0) = (0,0,2.0)
vectors_J2 = [[0, 1.5, 0], [0, -1.5, 0], [-1.5, 0, 0], [1.5, 0, 2.0]]
radii_J2   = [1.5, 1.5, 1.5, 2.2]
colors_J2  = ["cyan", "cyan", "cyan", "lime"]
names_J2   = ["p3/2", "p3/2", "p3/2", "f5/2"]

# J=0: All 4 drop to p3/2 (length 1.5). Pair off perfectly on X and Y axes.
# Exact Vector sum: (1.5) + (-1.5) + (1.5) + (-1.5) = 0.0
vectors_J0 = [[1.5, 0, 0], [-1.5, 0, 0], [0, 1.5, 0], [0, -1.5, 0]]
radii_J0   = [1.5, 1.5, 1.5, 1.5]
colors_J0  = ["cyan", "cyan", "cyan", "cyan"]
names_J0   = ["p3/2", "p3/2", "p3/2", "p3/2"]

# =====================================================================
# Sections 1, 2, 3 (Combined 3D Views)
# =====================================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Initial State (J=4)")
    st.write("Oblate (disk-like) configuration. Nucleon orbits align in the equator to maximize angular momentum.")
    show_core_4 = st.checkbox("Show Core", value=True, key="core4")
    show_orb_4 = st.checkbox("Show Orbits", value=True, key="o4")
    show_vec_4 = st.checkbox("Show Vectors", value=True, key="v4")
    show_chg_4 = st.checkbox("Show Charge Overlay", value=True, key="c4")
    fig_4 = plot_3d_state("J=4 (Aligned)", vectors_J4, show_orb_4, show_vec_4, show_chg_4, show_core_4, beta=0.5, radii=radii_J4, colors=colors_J4, names=names_J4)
    st.plotly_chart(fig_4, use_container_width=True)

with col2:
    st.subheader("2. Intermediate State (J=2)")
    st.write("Less stretched. Some orbits cross and cancel out each other's momentum.")
    show_core_2 = st.checkbox("Show Core", value=True, key="core2")
    show_orb_2 = st.checkbox("Show Orbits", value=True, key="o2")
    show_vec_2 = st.checkbox("Show Vectors", value=True, key="v2")
    show_chg_2 = st.checkbox("Show Charge Overlay", value=True, key="c2")
    fig_2 = plot_3d_state("J=2 (Partially Cancelled)", vectors_J2, show_orb_2, show_vec_2, show_chg_2, show_core_2, beta=0.25, radii=radii_J2, colors=colors_J2, names=names_J2)
    st.plotly_chart(fig_2, use_container_width=True)

with col3:
    st.subheader("3. Ground State (J=0)")
    st.write("Spherical. All valence nucleons drop to p3/2 and move in perfectly opposing orbits.")
    show_core_0 = st.checkbox("Show Core", value=True, key="core0")
    show_orb_0 = st.checkbox("Show Orbits", value=True, key="o0")
    show_vec_0 = st.checkbox("Show Vectors", value=True, key="v0")
    show_chg_0 = st.checkbox("Show Charge Overlay", value=True, key="c0")
    fig_0 = plot_3d_state("J=0 (Spherical)", vectors_J0, show_orb_0, show_vec_0, show_chg_0, show_core_0, beta=0.0, radii=radii_J0, colors=colors_J0, names=names_J0)
    st.plotly_chart(fig_0, use_container_width=True)

st.divider()

# =====================================================================
# Section 4: Dynamic Transition & Wave Emission
# =====================================================================
st.header("4. Dynamic Transition: The 'Squish' and the Wave")
st.write(
    "When the nucleus transitions from $J=4$ to $J=2$, it sheds energy and angular momentum. "
    "Press **Play** below to watch the nucleus dynamically 'squish' from its oblate, stretched "
    "shape into a more spherical shape. This sudden reshaping is what "
    "creates the outwardly expanding E2 wave packet (the photon) carrying away $2\hbar$ of angular momentum."
)

def plot_transition_animation():
    # Grids for the mesh
    phi = np.linspace(0, 2 * np.pi, 40)
    theta = np.linspace(0, np.pi, 40)
    phi, theta = np.meshgrid(phi, theta)
    
    # E2 Radiation angular dependence (m=±2 mode)
    # Most intense in the equatorial (XY) plane
    angular_intensity = 1 - np.cos(theta)**4
    
    frames = []
    num_frames = 40
    
    # Beta squishes from 0.5 (Oblate J=4) down to 0.25 (J=2)
    betas = np.linspace(0.5, 0.25, num_frames)
    
    # Initialize base geometry for the plot
    rz_base = 1.0 * (1 - betas[0])
    rxy_base = 1.0 / np.sqrt(1 - betas[0])
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
        
        # 1. Update Nucleus Shape (Oblate relaxation)
        rz = 1.0 * (1 - beta)
        rxy = 1.0 / np.sqrt(1 - beta)
        x_n = rxy * np.sin(theta) * np.cos(phi)
        y_n = rxy * np.sin(theta) * np.sin(phi)
        z_n = rz * np.cos(theta)
        
        # 2. Update Wave Expansion
        wave_radius = 1.0 + (i * 0.15) # Expands outward
        wave_amplitude = angular_intensity * wave_radius
        
        # Fading effect as wave packet travels away
        opacity = max(0, 0.8 - (i / num_frames))
        
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
  
