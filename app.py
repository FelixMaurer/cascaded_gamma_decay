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
ict(width=0, color="lime")
            )
        )
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

        fig.add_trace(
            go.Scatter3d(
                x=[0, 0], y=[0, 0], z=[0, v1],
                mode="lines+markers",
                name=f"Effective vector A (j={v1})",
                line=dict(width=8, color="cyan")
            )
        )
        fig.add_trace(
            go.Scatter3d(
                x=[0, end_x], y=[0, end_y], z=[v1, end_z],
                mode="lines+markers",
                name=f"Effective vector B (j={v2})",
                line=dict(width=8, color="lime")
            )
        )
        fig.add_trace(
            go.Scatter3d(
                x=[offset_x, offset_x], y=[0, end_y], z=[0, end_z],
                mode="lines",
                name=f"Total J = {target_mag}",
                line=dict(color="yellow", width=8)
            )
        )
        fig.add_trace(
            go.Cone(
                x=[offset_x], y=[end_y], z=[end_z],
                u=[u_dir], v=[v_dir], w=[w_dir],
                sizemode="absolute", sizeref=0.8, anchor="tip",
                colorscale=[[0, "yellow"], [1, "yellow"]],
                showscale=False, name="Direction"
            )
        )

    fig.update_layout(
        title=title,
        scene=dict(
            aspectmode="cube",
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            xaxis=dict(range=[-4, 4]),
            yaxis=dict(range=[-4, 4]),
            zaxis=dict(range=[0, 5]),
        ),
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    return fig


# -------------------------------------------------------------------
# Helper: transition selection-rule cartoon
# -------------------------------------------------------------------
def draw_transition_rule_cartoon():
    fig = go.Figure()

    # -----------------------------
    # Left state: example J = 4
    # -----------------------------
    xL, y0 = -4.3, 0.0

    # effective j = 1.5
    fig.add_trace(go.Scatter(
        x=[xL, xL], y=[y0, y0 + 1.6],
        mode="lines+markers",
        line=dict(color="cyan", width=7),
        marker=dict(size=6, color="cyan"),
        showlegend=False
    ))

    # effective j = 2.5
    fig.add_trace(go.Scatter(
        x=[xL, xL + 1.6], y=[y0 + 1.6, y0 + 2.8],
        mode="lines+markers",
        line=dict(color="lime", width=7),
        marker=dict(size=6, color="lime"),
        showlegend=False
    ))

    # total J = 4
    fig.add_trace(go.Scatter(
        x=[xL - 0.45, xL - 0.45], y=[y0, y0 + 3.9],
        mode="lines+markers",
        line=dict(color="yellow", width=8),
        marker=dict(size=6, color="yellow"),
        showlegend=False
    ))

    # -----------------------------
    # Right state: example J = 2
    # -----------------------------
    xR = 3.4

    # effective j = 1.5
    fig.add_trace(go.Scatter(
        x=[xR, xR], y=[y0, y0 + 1.6],
        mode="lines+markers",
        line=dict(color="cyan", width=7),
        marker=dict(size=6, color="cyan"),
        showlegend=False
    ))

    # effective j = 2.5
    fig.add_trace(go.Scatter(
        x=[xR, xR + 2.0], y=[y0 + 1.6, y0 + 1.8],
        mode="lines+markers",
        line=dict(color="lime", width=7),
        marker=dict(size=6, color="lime"),
        showlegend=False
    ))

    # total J = 2
    fig.add_trace(go.Scatter(
        x=[xR - 0.45, xR - 0.45], y=[y0, y0 + 2.0],
        mode="lines+markers",
        line=dict(color="yellow", width=8),
        marker=dict(size=6, color="yellow"),
        showlegend=False
    ))

    # Gamma arrow in the middle
    fig.add_annotation(
        x=1.0, y=2.35, ax=-1.0, ay=2.35,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True,
        arrowhead=3,
        arrowsize=1.4,
        arrowwidth=3,
        arrowcolor="orange"
    )

    fig.add_annotation(
        x=0.0, y=3.10,
        text="<b>γ₁ = 1173 keV</b>",
        showarrow=False,
        font=dict(size=14, color="orange")
    )

    fig.add_annotation(
        x=0.0, y=2.55,
        text="dominant E2<br>carries away 2ħ",
        showarrow=False,
        font=dict(size=12, color="orange")
    )

    # Top labels
    fig.add_annotation(
        x=-4.9, y=4.55,
        text="<b>Before</b><br>example coupling to J = 4",
        showarrow=False,
        align="center",
        font=dict(size=13)
    )

    fig.add_annotation(
        x=4.5, y=4.55,
        text="<b>After</b><br>example coupling to J = 2",
        showarrow=False,
        align="center",
        font=dict(size=13)
    )

    # Side labels for left state
    fig.add_annotation(
        x=-5.55, y=1.0,
        text="<span style='color:cyan'><b>effective<br>j = 1.5</b></span>",
        showarrow=False,
        align="right",
        font=dict(size=12)
    )
    fig.add_annotation(
        x=-2.15, y=3.05,
        text="<span style='color:lime'><b>effective<br>j = 2.5</b></span>",
        showarrow=False,
        align="left",
        font=dict(size=12)
    )
    fig.add_annotation(
        x=-5.55, y=3.7,
        text="<span style='color:yellow'><b>total<br>J = 4</b></span>",
        showarrow=False,
        align="right",
        font=dict(size=12)
    )

    # Side labels for right state
    fig.add_annotation(
        x=2.55, y=1.0,
        text="<span style='color:cyan'><b>effective<br>j = 1.5</b></span>",
        showarrow=False,
        align="right",
        font=dict(size=12)
    )
    fig.add_annotation(
        x=6.05, y=1.95,
        text="<span style='color:lime'><b>effective<br>j = 2.5</b></span>",
        showarrow=False,
        align="left",
        font=dict(size=12)
    )
    fig.add_annotation(
        x=2.4, y=1.8,
        text="<span style='color:yellow'><b>total<br>J = 2</b></span>",
        showarrow=False,
        align="right",
        font=dict(size=12)
    )

    # Central note
    fig.add_annotation(
        x=0.0, y=0.35,
        text="<b>Selection rule cartoon</b><br>same valence space, different total coupling",
        showarrow=False,
        font=dict(size=12)
    )

    fig.update_layout(
        title="First emission: example recoupling from J = 4 to J = 2",
        xaxis=dict(visible=False, range=[-6.6, 6.6]),
        yaxis=dict(visible=False, range=[-0.9, 5.1], scaleanchor="x", scaleratio=1),
        height=390,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False
    )

    return fig

# -------------------------------------------------------------------
# Helper: gamma1 defines axis cartoon
# -------------------------------------------------------------------
def draw_axis_selection_cartoon():
    fig = go.Figure()

    # Nucleus
    fig.add_shape(
        type="circle", x0=-0.6, y0=-0.6, x1=0.6, y1=0.6,
        fillcolor="lightgray", line_color="black"
    )
    fig.add_annotation(
        x=0, y=0,
        text="<b>Intermediate<br>state</b>",
        showarrow=False, font=dict(size=13)
    )

    # First gamma defines axis
    fig.add_annotation(
        x=4.0, y=0.0, ax=0.7, ay=0.0,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowsize=1.4, arrowwidth=3,
        arrowcolor="orange"
    )
    fig.add_annotation(
        x=2.3, y=0.45,
        text="<b>detected γ₁</b><br>defines the reference axis",
        showarrow=False, font=dict(size=13, color="orange")
    )

    # Dashed axis
    fig.add_trace(go.Scatter(
        x=[0.0, 4.5], y=[0.0, 0.0],
        mode="lines",
        line=dict(color="orange", width=2, dash="dash"),
        name="γ₁ axis"
    ))

    # Example gamma2 direction
    theta = np.deg2rad(60)
    r = 3.6
    x2 = r * np.cos(theta)
    y2 = r * np.sin(theta)

    fig.add_annotation(
        x=x2, y=y2, ax=0.65, ay=0.0,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowsize=1.2, arrowwidth=3,
        arrowcolor="deepskyblue"
    )
    fig.add_annotation(
        x=2.2, y=2.2,
        text="<b>γ₂</b> emitted at angle θ",
        showarrow=False, font=dict(size=13, color="deepskyblue")
    )

    # Angle arc
    arc_t = np.linspace(0, theta, 80)
    fig.add_trace(go.Scatter(
        x=1.2 * np.cos(arc_t), y=1.2 * np.sin(arc_t),
        mode="lines",
        line=dict(color="magenta", width=3),
        name="θ"
    ))
    fig.add_annotation(
        x=1.0 * np.cos(theta / 2) + 0.15,
        y=1.0 * np.sin(theta / 2) + 0.1,
        text="θ",
        showarrow=False,
        font=dict(size=16, color="magenta")
    )

    fig.add_annotation(
        x=0, y=-1.6,
        text="The source is initially unpolarized.<br>Once γ₁ is observed, its direction tags an axis for the γ₂ measurement.",
        showarrow=False, font=dict(size=12)
    )

    fig.update_layout(
        title="How the first gamma sets the axis for the angular-correlation measurement",
        xaxis=dict(visible=False, range=[-1.8, 5.2]),
        yaxis=dict(visible=False, range=[-2.1, 3.2], scaleanchor="x", scaleratio=1),
        height=360,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False
    )
    return fig


# -------------------------------------------------------------------
# Helper: angular probability plot
# -------------------------------------------------------------------
def plot_angular_probability():
    theta_deg = np.linspace(0, 360, 721)
    theta_rad = np.deg2rad(theta_deg)

    W = 1 + (1 / 8.0) * (np.cos(theta_rad) ** 2) + (1 / 24.0) * (np.cos(theta_rad) ** 4)
    W = W / np.max(W)

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=W,
        theta=theta_deg,
        mode="lines",
        line=dict(color="gold", width=4),
        fill="toself",
        fillcolor="rgba(255,215,0,0.30)",
        name="Relative probability"
    ))

    for ang, label in [(0, "max"), (90, "min"), (180, "max")]:
        rr = 1 + (1 / 8.0) * (np.cos(np.deg2rad(ang)) ** 2) + (1 / 24.0) * (np.cos(np.deg2rad(ang)) ** 4)
        rr = rr / (1 + 1 / 8.0 + 1 / 24.0)
        fig.add_trace(go.Scatterpolar(
            r=[rr],
            theta=[ang],
            mode="markers+text",
            text=[label],
            textposition="top center",
            marker=dict(size=8, color="crimson"),
            showlegend=False
        ))

    fig.update_layout(
        title="Relative angular probability for γ₂ after γ₁ has defined the axis",
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1.05]),
            angularaxis=dict(direction="counterclockwise", rotation=0),
        ),
        height=360,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        showlegend=False
    )
    return fig
def draw_parity_cartoon():
    fig = go.Figure()

    # level lines
    fig.add_trace(go.Scatter(
        x=[-1.8, 1.8], y=[3.2, 3.2],
        mode="lines",
        line=dict(width=4, color="royalblue"),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=[-1.8, 1.8], y=[1.2, 1.2],
        mode="lines",
        line=dict(width=4, color="seagreen"),
        showlegend=False
    ))

    fig.add_annotation(x=2.2, y=3.2, text="<b>4⁺</b>", showarrow=False, font=dict(size=16, color="royalblue"))
    fig.add_annotation(x=2.2, y=1.2, text="<b>2⁺</b>", showarrow=False, font=dict(size=16, color="seagreen"))

    # inversion cartoon
    fig.add_annotation(
        x=-2.8, y=2.2,
        text="<b>Parity</b><br>behavior under spatial inversion<br><span style='font-size:16px'>r → −r</span>",
        showarrow=False, align="center", font=dict(size=13)
    )

    # gamma arrow
    fig.add_annotation(
        x=0.0, y=1.35, ax=0.0, ay=3.05,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowsize=1.4, arrowwidth=3,
        arrowcolor="orange"
    )

    fig.add_annotation(
        x=0.7, y=2.2,
        text="<b>E2</b><br>ΔJ = 2<br>Δπ = +1",
        showarrow=False, font=dict(size=14, color="orange")
    )

    fig.add_annotation(
        x=0.0, y=0.2,
        text="Both levels have positive parity, so the first emission must preserve parity.",
        showarrow=False, font=dict(size=12)
    )

    fig.update_layout(
        title="Parity and multipolarity for the first emission",
        xaxis=dict(visible=False, range=[-4.2, 4.2]),
        yaxis=dict(visible=False, range=[-0.4, 4.1]),
        height=340,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False
    )
    return fig


def plot_first_gamma_probability():
    theta_deg = np.linspace(0, 360, 721)
    r = np.ones_like(theta_deg)

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=r,
        theta=theta_deg,
        mode="lines",
        line=dict(color="gold", width=4),
        fill="toself",
        fillcolor="rgba(255,215,0,0.25)",
        showlegend=False
    ))

    fig.update_layout(
        title="First emission alone: isotropic angular probability",
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1.05]),
            angularaxis=dict(direction="counterclockwise", rotation=0)
        ),
        height=340,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        showlegend=False
    )
    return fig

st.divider()

# =====================================================================
# SECTION 1
# =====================================================================
st.header("1. The Initial Excited State (J = 4)")
st.write(
    "Following the beta decay of Co-60, Ni-60 is formed in an excited state. "
    "Below, one intuitive example basis configuration is shown together with an effective angular-momentum coupling cartoon."
)

col1_a, col1_b, col1_c = st.columns(3)

with col1_a:
    st.subheader("1.1. Occupancy Cartoon")
    st.write(
        "This panel shows one possible **valence-shell occupancy cartoon**. "
        "The dots represent how neutrons are distributed among the valence orbitals in a simplified way."
    )
    st.plotly_chart(
        draw_2d_shell("Example Valence Arrangement", num_in=3, num_out=1),
        use_container_width=True,
        key="shell_1"
    )

with col1_b:
    st.subheader("1.2. Effective Internal Coupling Cartoon")
    st.write(
        "This panel is a **coupling mnemonic**, not a literal 3D arrangement of neutron spins. "
        "It suggests how a p3/2^3 occupancy can be represented by an effective net angular-momentum contribution of j = 1.5."
    )
    st.plotly_chart(
        plot_internal_coupling("Cartoon: 3 Neutrons → Effective j = 1.5", mode="3_neutrons"),
        use_container_width=True,
        key="internal_1"
    )

with col1_c:
    st.subheader("1.3. Effective Vector Coupling to J = 4")
    st.write(
        "In this simplified vector picture, an effective j = 1.5 contribution and an effective j = 2.5 contribution are coupled to the stretched total value J = 4."
    )
    st.plotly_chart(
        plot_3d_vectors(1.5, 2.5, 4.0, "Effective Coupling: 1.5 + 2.5 → J = 4"),
        use_container_width=True,
        key="vector_1"
    )

st.write("---")
st.subheader("1.4. Alternative Microscopic Possibilities")
col1_d, col1_e, col1_f = st.columns(3)

with col1_d:
    st.write("**Alternative occupancy cartoon:** two neutrons promoted to 1f5/2.")
    st.plotly_chart(
        draw_2d_shell("Alternative Example Arrangement (J = 4)", num_in=2, num_out=2),
        use_container_width=True,
        key="shell_1_alt"
    )

with col1_e:
    st.write(
        "The configuration above is **not the only way** the nucleus can reach a state with total J = 4."
    )
    st.write("**Why are there alternatives?**")
    st.write("1. **Configuration mixing:** the physical nuclear state is a superposition of several shell-model basis configurations.")
    st.write("2. **Multiple allowed couplings:** different orbital occupancies can also couple to the same total angular momentum.")
    st.write(
        "For example, two neutrons in the 1f5/2 shell can be coupled to a total J = 4 as one allowed basis component."
    )

with col1_f:
    st.write("**Alternative effective vector coupling**")
    st.plotly_chart(
        plot_3d_vectors(2.5, 2.5, 4.0, "Alternative Effective Coupling: 2.5 + 2.5 → J = 4"),
        use_container_width=True,
        key="alt_vector_1"
    )

st.divider()

# =====================================================================
# SECTION 2
# =====================================================================
st.header("2. The Intermediate State (J = 2)")
st.write(
    "After the first gamma emission (1173 keV), the nucleus changes to the intermediate J = 2 state. "
    "The panels below again show one intuitive basis picture and one effective coupling cartoon."
)

col2_a, col2_b, col2_c = st.columns(3)

with col2_a:
    st.subheader("2.1. Occupancy Cartoon")
    st.write(
        "This shows the **same example occupancy pattern** as above, but now interpreted as contributing to a state with a different total coupling."
    )
    st.plotly_chart(
        draw_2d_shell("Example Valence Arrangement", num_in=3, num_out=1),
        use_container_width=True,
        key="shell_2"
    )

with col2_b:
    st.subheader("2.2. Effective Internal Coupling Cartoon")
    st.write(
        "The same simplified internal-coupling mnemonic is kept here. "
        "This does not mean the nucleus contains rigid little arrows; it only provides an intuitive effective j = 1.5 contribution."
    )
    st.plotly_chart(
        plot_internal_coupling("Cartoon: 3 Neutrons → Effective j = 1.5", mode="3_neutrons"),
        use_container_width=True,
        key="internal_2"
    )

with col2_c:
    st.subheader("2.3. Effective Vector Coupling to J = 2")
    st.write(
        "In this simplified vector cartoon, the effective j = 1.5 and j = 2.5 contributions are coupled differently so that the total becomes J = 2 instead of J = 4. "
        "The first gamma can then be understood as carrying away the difference in angular momentum."
    )
    st.plotly_chart(
        plot_3d_vectors(1.5, 2.5, 2.0, "Effective Coupling: 1.5 + 2.5 → J = 2"),
        use_container_width=True,
        key="vector_2"
    )

st.write("---")
st.subheader("2.4. Alternative Microscopic Possibilities (J = 2)")
col2_d, col2_e, col2_f = st.columns(3)

with col2_d:
    st.write("**Alternative occupancy cartoon:** two neutrons remaining in 1f5/2.")
    st.plotly_chart(
        draw_2d_shell("Alternative Example Arrangement (J = 2)", num_in=2, num_out=2),
        use_container_width=True,
        key="shell_2_alt"
    )

with col2_e:
    st.write("**How can the alternative configuration contribute to J = 2?**")
    st.write(
        "Just like the previous example, this alternative occupancy does not need to be interpreted as nucleons literally moving like classical vectors in space."
    )
    st.write(
        "Instead, the point is that the same two effective j = 2.5 contributions can be coupled to a smaller total value, here J = 2, as another allowed basis component."
    )
    st.write(
        "The gamma transition is best understood as a change of the many-body coupling from a J = 4 state to a J = 2 state, rather than as a literal mechanical re-orientation of rigid neutron arrows."
    )

with col2_f:
    st.write("**Alternative effective vector coupling**")
    st.plotly_chart(
        plot_3d_vectors(2.5, 2.5, 2.0, "Alternative Effective Coupling: 2.5 + 2.5 → J = 2"),
        use_container_width=True,
        key="alt_vector_2"
    )

st.divider()

# =====================================================================
# SECTION 3
# =====================================================================
st.header("3. The Final Ground State (J = 0)")
st.write(
    "After the second gamma emission (1333 keV), the cascade reaches the ground state. "
    "The panels below show a standard intuitive cartoon for a strongly paired low-energy valence configuration."
)

col3_a, col3_b, col3_c = st.columns(3)

with col3_a:
    st.subheader("3.1. Occupancy Cartoon")
    st.write(
        "This panel shows the familiar simplified picture in which all four valence neutrons occupy the lowest available valence orbital. "
        "This is a useful cartoon for the paired J = 0 ground state."
    )
    st.plotly_chart(
        draw_2d_shell("Ground State Arrangement", num_in=4, num_out=0),
        use_container_width=True,
        key="shell_3"
    )

with col3_b:
    st.subheader("3.2. Effective Internal Coupling Cartoon")
    st.write(
        "Here the four neutrons are shown as two cancelling pairs. "
        "Again, this is not meant literally in 3D space; it is a pedagogical way to represent strong pairwise cancellation leading to net J = 0."
    )
    st.plotly_chart(
        plot_internal_coupling("Cartoon: 4 Neutrons → Effective j = 0", mode="4_neutrons"),
        use_container_width=True,
        key="internal_3"
    )

with col3_c:
    st.subheader("3.3. Effective Vector Coupling to J = 0")
    st.write(
        "In the ground-state cartoon, the valence contributions cancel so that the total angular momentum is J = 0."
    )
    st.plotly_chart(
        plot_3d_vectors(0, 0, 0, "Effective Coupling: 0 + 0 → J = 0"),
        use_container_width=True,
        key="vector_3"
    )

st.divider()

# =====================================================================
# SECTION 4
# =====================================================================
st.header("4. The First Transition (J = 4 → J = 2)")
st.write(
    "This section focuses only on the first gamma emission. "
    "The aim is to connect the intuitive recoupling picture to parity, selection rules, "
    "and the angular probability of γ₁ itself."
)

st.info(
    """
    **Interpretation note**

    The drawings below are still cartoons.
    They explain:
    - what parity means in this transition,
    - where the electromagnetic selection rules come from,
    - why the first emission is dominantly E2,
    - and what the angular probability looks like for γ₁ alone.

    They are not literal pictures of neutron motion in space.
    """
)

col4_a, col4_b, col4_c = st.columns(3)

with col4_a:
    st.subheader("4.1. Parity")
    st.write(
        "Parity describes how a nuclear wavefunction behaves under spatial inversion **r → −r**. "
        "A **+** state keeps its sign, while a **−** state changes sign. "
        "Because both the initial and final states here are positive (**4⁺ → 2⁺**), the first transition must preserve parity."
    )
    st.plotly_chart(
        draw_parity_cartoon(),
        use_container_width=True,
        key="parity_cartoon"
    )

with col4_b:
    st.subheader("4.2. Where the Auswahlregeln come from")
    st.write(
        "The selection rules come from conservation of **angular momentum** and **parity** in electromagnetic decay. "
        "For the first emission, the nucleus changes from **J = 4** to **J = 2**, so the photon must carry angular momentum away. "
        "Since there is no parity change, the lowest allowed multipole is **E2**, which is therefore the dominant first-emission character."
    )
    st.plotly_chart(
        draw_transition_rule_cartoon(),
        use_container_width=True,
        key="transition_rule_cartoon"
    )

with col4_c:
    st.subheader("4.3. Single-nucleus angular probability of γ₁")
    st.write(
        "Instead of averaging over many nuclei, this panel shows one **single oriented nucleus**. "
        "To make the angular pattern well-defined, we choose a quantization axis and one example E2 component."
    )
    st.write(
        r"A useful illustrative choice is the stretched component $m_i = 4 \rightarrow m_f = 2$, "
        r"for which the emitted first gamma carries the quadrupole component $q = \Delta m = 2$."
    )
    st.plotly_chart(
        plot_single_nucleus_first_gamma(mode="m=+2"),
        use_container_width=True,
        key="single_nucleus_first_gamma"
    )

st.write("---")
st.subheader("4.4. Why a single nucleus gives this shape")
st.write(
    "For one nucleus in a definite magnetic substate, the first gamma is emitted relative to that nucleus's own quantization axis. "
    "The pattern is therefore not spherical. It reflects the angular structure of the **E2 quadrupole field**."
)
st.write(
    "In this example we chose the stretched component "
    r"$m_i = 4 \rightarrow m_f = 2$. "
    "That component is strongest away from the axis and vanishes along it, so the radiation is concentrated around the equatorial region."
)
st.write(
    r"More generally, different allowed values of $\Delta m = m_i - m_f$ correspond to different quadrupole components, "
    "and each component has its own characteristic angular pattern."
)

st.write("---")
st.subheader("4.5. How the pattern is calculated")
st.write(
    "The selection rules first determine the allowed multipolarity: here the first emission is dominantly **E2**. "
    "Then, for a chosen single-nucleus substate, one specifies which magnetic component of the quadrupole field is emitted."
)
st.write(
    "For the illustrative **m = ±2** quadrupole mode, the angular dependence is:"
)
st.latex(r"\frac{dP}{d\Omega} \propto 1-\cos^4\theta")
st.write(
    "After normalization, that gives the polar pattern shown above. "
    "This is the right object to visualize when you want the first emission from **one oriented nucleus**, not yet the bulk sample."
)

st.divider()

# =====================================================================
# SECTION 5
# =====================================================================
st.header("5. Why exactly is it a Quadrupole (E2) Transition?")
st.write(
    "It is a very intuitive guess to think about the photon's intrinsic spin! You are absolutely right "
    "that a single photon has an intrinsic spin of 1. However, to understand why this transition is a "
    "quadrupole ($L=2$) rather than a dipole ($L=1$), we have to look at how the photon actually leaves the nucleus."
)

st.info(
    """
    **Intrinsic Spin vs. Total Angular Momentum**

    While a photon does have an intrinsic spin of 1, it can also carry **orbital angular momentum** depending on 
    the "shape" of the wave it forms as it radiates away from the nucleus. 
    
    The **total** angular momentum ($L$) carried away by the photon is the combination of its intrinsic spin and 
    its orbital angular momentum. Therefore, a photon can carry away $L = 1, 2, 3$, etc.
    """
)

st.subheader("5.1. The Math: Conservation of Angular Momentum")
st.write(
    "In our cascade, the nucleus transitions from $J = 4$ to $J = 2$. By the laws of quantum mechanics, "
    "the total angular momentum must be conserved. The angular momentum carried away by the photon ($L$) "
    "must bridge the gap between the initial and final states:"
)
st.latex(r"|J_i - J_f| \leq L \leq J_i + J_f")
st.write(
    "Since $|4 - 2| = 2$, the photon **must** carry away at least 2 units of angular momentum. "
    "It physically cannot bridge a $\Delta J = 2$ gap with only $L=1$ (a dipole). Because the minimum required "
    "angular momentum is 2, and parity does not change ($+ \rightarrow +$), the transition is classified as "
    "an **Electric Quadrupole (E2)**."
)

st.subheader("5.2. The Physics: What is a Quadrupole, Intuitively?")
st.write(
    "If a photon carries away $L=1$ (dipole), it implies the center of positive charge in the nucleus briefly "
    "sloshed back and forth relative to the center of mass. "
    "But in this low-energy transition, the protons and neutrons are tightly bound and moving around the center together."
)
st.write(
    "Instead of the center of charge shifting, the **overall shape** of the charge distribution changes. "
    "Imagine the nucleus transitioning from a stretched, rugby-ball shape (high angular momentum, $J=4$) to "
    "a more compact, spherical shape ($J=2$).  "
    "This stretching and compressing of the charge distribution—without shifting its center—is the exact physical definition "
    "of a changing electric quadrupole moment. That changing shape is what acts as the 'antenna' to broadcast the E2 photon!"
)
st.divider()

# =====================================================================
# SECTION 6
# =====================================================================
st.header("6. Animation: The Changing Nuclear Antenna")
st.write(
    "To truly visualize why this is an E2 (quadrupole) transition, we can look at the changing shape "
    "of the nucleus. When the nucleus drops from the J = 4 state to the J = 2 state, its overall charge "
    "distribution becomes less stretched."
)

st.info(
    """
    **How to use this animation:**
    Click the **Play** button below the 3D plot to watch the nucleus transition from a deformed, rugby-ball 
    shape (prolate) to a more spherical shape. 
    
    This exact 'squishing' motion of the positive protons creates a changing electric quadrupole moment in space, 
    which acts as the antenna to broadcast the E2 photon!
    """
)

def plot_quadrupole_animation():
    # Create a base grid for the sphere/ellipsoid
    phi = np.linspace(0, 2 * np.pi, 50)
    theta = np.linspace(0, np.pi, 50)
    phi, theta = np.meshgrid(phi, theta)
    
    frames = []
    # Deformation parameter (beta) goes from 0.4 (stretched) down to 0.0 (spherical)
    betas = np.linspace(0.4, 0.0, 30)
    
    # Calculate the initial surface (beta = 0.4)
    beta0 = betas[0]
    # To conserve volume roughly, if z stretches by (1+beta), x and y shrink by sqrt(1+beta)
    rz0 = 1.0 * (1 + beta0)
    rx0 = 1.0 / np.sqrt(1 + beta0)
    
    x0 = rx0 * np.sin(theta) * np.cos(phi)
    y0 = rx0 * np.sin(theta) * np.sin(phi)
    z0 = rz0 * np.cos(theta)
    
    fig = go.Figure(
        data=[go.Surface(x=x0, y=y0, z=z0, colorscale='Plasma', showscale=False)],
        layout=go.Layout(
            title="Nuclear Shape Transition: Deformed to Spherical",
            scene=dict(
                xaxis=dict(range=[-1.5, 1.5], visible=False),
                yaxis=dict(range=[-1.5, 1.5], visible=False),
                zaxis=dict(range=[-1.5, 1.5], visible=False),
                aspectmode='cube'
            ),
            height=500,
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=40, b=0),
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                y=0,
                x=0.5,
                xanchor="center",
                yanchor="top",
                buttons=[dict(
                    label="▶ Play Transition",
                    method="animate",
                    args=[None, dict(frame=dict(duration=80, redraw=True), 
                                     transition=dict(duration=0),
                                     fromcurrent=True,
                                     mode='immediate')]
                )]
            )]
        )
    )
    
    # Generate the frames for the animation
    for i, beta in enumerate(betas):
        rz = 1.0 * (1 + beta)
        rx = 1.0 / np.sqrt(1 + beta)
        
        x = rx * np.sin(theta) * np.cos(phi)
        y = rx * np.sin(theta) * np.sin(phi)
        z = rz * np.cos(theta)
        
        frames.append(go.Frame(data=[go.Surface(x=x, y=y, z=z)], name=str(i)))
        
    fig.frames = frames
    return fig

col6_a, col6_b = st.columns([2, 1])

with col6_a:
    st.plotly_chart(plot_quadrupole_animation(), use_container_width=True, key="quad_anim")

with col6_b:
    st.write("### The Radiated Wave")
    st.write(
        "As the nucleus changes shape in the animation, the changing electric field ripples outward. "
        "Because the motion is symmetric (the top and bottom squish in together, and the equator bulges out), "
        "the resulting photon wave has a distinct four-lobed 'quadrupole' pattern rather than a simple 'up-down' dipole pattern."
    )
    st.write(
        "This complex wave geometry is exactly what allows the photon to carry away the 2 units of angular "
        "momentum required by the J = 4 to J = 2 transition rules."
    )

st.divider()

# =====================================================================
# SECTION 7
# =====================================================================
st.header("7. Visualizing the 'Why': Dipole vs. Quadrupole")
st.write(
    "To understand why we get an E2 (Quadrupole) instead of an E1 (Dipole) photon, we have to look "
    "at how the nucleus moves. A photon is created by moving electrical charges. "
)

col7_a, col7_b = st.columns(2)

with col7_a:
    st.subheader("7.1. Dipole (L=1) - The 'Slosh'")
    st.write(
        "In a dipole transition, the center of positive charge oscillates back and forth relative to the center of mass. "
        "This requires breaking apart the tightly bound core, which takes immense energy (Giant Dipole Resonance). "
        "It doesn't happen in our low-energy Ni-60 cascade."
    )
    
    # Dipole Animation (2D)
    t_vals = np.linspace(0, 2*np.pi, 30)
    theta_circ = np.linspace(0, 2*np.pi, 100)
    dipole_frames = []
    
    for i, t in enumerate(t_vals):
        y_shift = 0.5 * np.sin(t)
        x = np.cos(theta_circ)
        y = np.sin(theta_circ) + y_shift
        dipole_frames.append(go.Frame(data=[go.Scatter(x=x, y=y, mode="lines", fill="toself", fillcolor="rgba(255,100,100,0.6)", line_color="red")], name=str(i)))

    fig_dipole = go.Figure(
        data=[go.Scatter(x=np.cos(theta_circ), y=np.sin(theta_circ), mode="lines", fill="toself", fillcolor="rgba(255,100,100,0.6)", line_color="red")],
        layout=go.Layout(
            xaxis=dict(range=[-2, 2], visible=False), yaxis=dict(range=[-2, 2], visible=False),
            height=300, margin=dict(l=0, r=0, t=0, b=0),
            updatemenus=[dict(type="buttons", showactive=False, y=0, x=0.5, xanchor="center", yanchor="top",
                              buttons=[dict(label="▶ Play Dipole", method="animate", args=[None, dict(frame=dict(duration=50, redraw=True), transition=dict(duration=0), mode='immediate')])])]
        ), frames=dipole_frames
    )
    st.plotly_chart(fig_dipole, use_container_width=True, key="anim_dipole")

with col7_b:
    st.subheader("7.2. Quadrupole (L=2) - The 'Squish'")
    st.write(
        "In a quadrupole transition, the center of mass stays perfectly still. Instead, the *shape* "
        "stretches and compresses. The valence nucleons rearrange their orbits from a stretched state ($J=4$) "
        "to a round state ($J=2$), 'squishing' the charge and emitting the E2 photon."
    )
    
    # Quadrupole Animation (2D)
    quad_frames = []
    for i, t in enumerate(t_vals):
        stretch = 1 + 0.3 * np.sin(t)
        shrink = 1 / stretch
        x = shrink * np.cos(theta_circ)
        y = stretch * np.sin(theta_circ)
        quad_frames.append(go.Frame(data=[go.Scatter(x=x, y=y, mode="lines", fill="toself", fillcolor="rgba(100,100,255,0.6)", line_color="blue")], name=str(i)))

    fig_quad = go.Figure(
        data=[go.Scatter(x=np.cos(theta_circ), y=np.sin(theta_circ), mode="lines", fill="toself", fillcolor="rgba(100,100,255,0.6)", line_color="blue")],
        layout=go.Layout(
            xaxis=dict(range=[-2, 2], visible=False), yaxis=dict(range=[-2, 2], visible=False),
            height=300, margin=dict(l=0, r=0, t=0, b=0),
            updatemenus=[dict(type="buttons", showactive=False, y=0, x=0.5, xanchor="center", yanchor="top",
                              buttons=[dict(label="▶ Play Quadrupole", method="animate", args=[None, dict(frame=dict(duration=50, redraw=True), transition=dict(duration=0), mode='immediate')])])]
        ), frames=quad_frames
    )
    st.plotly_chart(fig_quad, use_container_width=True, key="anim_quad")

st.divider()

# =====================================================================
# SECTION 8
# =====================================================================
st.header("8. Animation: The Emitted E2 Radiation Pattern")
st.write(
    "Because the nucleus is 'squishing' symmetrically (as seen above), the photon wave it creates doesn't just travel in one direction. "
    "It creates a complex, 4-lobed wave geometry in space. This animation shows the intensity of the E2 ($m=\pm2$) radiation field "
    "pulsing outward from the nucleus. Notice how the radiation is strictly zero along the vertical (quantization) axis!"
)

# 3D Pulsing Wave Animation
phi_3d = np.linspace(0, 2 * np.pi, 60)
theta_3d = np.linspace(0, np.pi, 60)
phi_3d, theta_3d = np.meshgrid(phi_3d, theta_3d)

# Angular dependence for m=2 E2
angular_part = 1 - np.cos(theta_3d)**4

wave_frames = []
for i, t in enumerate(t_vals):
    # Pulse amplitude outward
    r = angular_part * (0.5 + 0.5 * abs(np.sin(t)))
    
    x = r * np.sin(theta_3d) * np.cos(phi_3d)
    y = r * np.sin(theta_3d) * np.sin(phi_3d)
    z = r * np.cos(theta_3d)
    wave_frames.append(go.Frame(data=[go.Surface(x=x, y=y, z=z, colorscale='Viridis', showscale=False)], name=str(i)))

r_init = angular_part * 0.5
fig_wave = go.Figure(
    data=[go.Surface(x=r_init * np.sin(theta_3d) * np.cos(phi_3d), 
                     y=r_init * np.sin(theta_3d) * np.sin(phi_3d), 
                     z=r_init * np.cos(theta_3d), colorscale='Viridis', showscale=False)],
    layout=go.Layout(
        scene=dict(xaxis=dict(range=[-1.5, 1.5], visible=False), yaxis=dict(range=[-1.5, 1.5], visible=False), zaxis=dict(range=[-1.5, 1.5], visible=False), aspectmode='cube'),
        height=500, margin=dict(l=0, r=0, t=0, b=0),
        updatemenus=[dict(type="buttons", showactive=False, y=0.05, x=0.5, xanchor="center", yanchor="bottom",
                          buttons=[dict(label="▶ Animate E2 Wave", method="animate", args=[None, dict(frame=dict(duration=80, redraw=True), transition=dict(duration=0), mode='immediate')])])]
    ), frames=wave_frames
)
st.plotly_chart(fig_wave, use_container_width=True, key="anim_wave")

st.divider()

# =====================================================================
# SECTION 9
# =====================================================================
st.header("9. Animation: Vectors in Motion (Conserving Angular Momentum)")
st.write(
    "Finally, let's look at the vector math in motion. The nucleus starts with $J=4$. It transitions down to $J=2$. "
    "To conserve angular momentum in the universe, the photon **must** fly away carrying an angular momentum vector of $L=2$. "
    "Watch the $J=4$ vector split into the new nuclear state and the emitted photon."
)

vector_frames = []
num_steps = 30
for i in range(num_steps):
    progress = i / (num_steps - 1)
    
    # Nuclear vector shrinks from 4 to 2
    current_j = 4.0 - (2.0 * progress)
    
    # Photon vector grows out of the difference and moves away radially
    photon_len = 2.0 * progress
    photon_x = 3.0 * progress  # moves to the right
    photon_z = current_j + (photon_len / 2) # offset slightly for visual clarity

    frame_data = [
        # Nuclear Vector (shrinking)
        go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, current_j], mode="lines+markers", line=dict(width=10, color="yellow"), marker=dict(size=[0, 8], color="yellow")),
        # Photon Vector (moving away)
        go.Scatter3d(x=[photon_x, photon_x], y=[0, 0], z=[photon_z, photon_z + photon_len], mode="lines+markers", line=dict(width=6, color="orange"), marker=dict(size=[0, 5], color="orange"))
    ]
    vector_frames.append(go.Frame(data=frame_data, name=str(i)))

fig_vectors = go.Figure(
    data=[
        go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 4], mode="lines+markers", line=dict(width=10, color="yellow"), marker=dict(size=[0, 8], color="yellow"), name="Nuclear J"),
        go.Scatter3d(x=[0, 0], y=[0, 0], z=[4, 4], mode="lines+markers", line=dict(width=6, color="orange"), marker=dict(size=[0, 5], color="orange"), name="Photon L")
    ],
    layout=go.Layout(
        scene=dict(xaxis=dict(range=[-1, 4], title="Distance"), yaxis=dict(range=[-1, 1], visible=False), zaxis=dict(range=[0, 5], title="Angular Momentum (z)"), aspectmode='cube'),
        height=450, margin=dict(l=0, r=0, t=0, b=0),
        updatemenus=[dict(type="buttons", showactive=False, y=0.9, x=0.2, xanchor="center", yanchor="top",
                          buttons=[dict(label="▶ Split Vectors", method="animate", args=[None, dict(frame=dict(duration=60, redraw=True), transition=dict(duration=0), mode='immediate')])])]
    ), frames=vector_frames
)
st.plotly_chart(fig_vectors, use_container_width=True, key="anim_vectors")
    
st.divider()

# =====================================================================
# SECTION 10
# =====================================================================
st.header("10. Deep Dive Animation: Orbital Alignment vs. Shape")
st.write(
    "To fully grasp why the $J=4$ state is 'more stretched' than the $J=0$ state, we "
    "must visually look at how individual nucleon orbits align or cancel out."
)

st.info(
    """
    **Interpretation Note: The Classical Cartoon**
    
    Quantum mechanics tells us nucleons don't have fixed orbits like planets. However, to build intuition "without more math," we can use a classical analogy. 
    
    Think of individual nucleons moving in circular paths. The mass and positive charge of the nucleon "pile up" along that path. 
    * **The total angular momentum vector ($j$)** is perpendicular to that orbital plane. 
    * **Total J** is the sum of these vectors.
    """
)

def plot_orbital_alignment_animation(state="J=4"):
    phi = np.linspace(0, 2*np.pi, 50)
    theta_dots = np.linspace(0, 2*np.pi, 40) # Animation steps
    
    fig = go.Figure()
    
    # Static elements (central core)
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode="markers", marker=dict(size=12, color="gray"), showlegend=False))

    colors = ["cyan", "lime", "orange", "magenta"]
    frames = []

    # Define the orbital planes based on state
    if state == "J=4 (Aligned)":
        # The 4 vectors align around the Z-axis. Classically, the orbits all 
        # lie roughly in the equatorial (XY) plane.
        
        # Tilt matrices (small variations to show distinct orbits clumping)
        planes_angles = [
            (0, 0),    # Plane 1: purely XY
            (10, 5),   # Plane 2: slightly tilted
            (-10, -5), # Plane 3: tilted opposite
            (5, -10)   # Plane 4: tilted slightly
        ]
        text_explanation = (
            "**J=4 (Stretched):** The individual angular momentum vectors align near the Z-axis. "
            "To achieve this, the nucleon orbital planes must all 'clump' together around the "
            "equator (XY plane). This piling up of mass creates a collective bulge or 'stretched' disk shape."
        )

    else: # J=0
        # The 4 vectors pair up and cancel perfectly. J=0 is inherently spherical.
        # Classically, two pair in the XY plane, two pair perpendicularly in the XZ plane.
        
        # Tilt matrices for cancellation (perpendicular coupling)
        planes_angles = [
            (0, 0),     # Orbit 1: XY plane
            (180, 0),   # Orbit 2: XY plane (opposite rotation)
            (90, 0),    # Orbit 3: XZ plane
            (90, 180)   # Orbit 4: XZ plane (opposite rotation)
        ]
        text_explanation = (
            "**J=0 (Spherical):** The individual angular momentum vectors pair up in opposite directions, "
            "cancelling each other perfectly. Classically, this looks like nucleon orbits crossing "
            "perpendicularly or randomly. Over time, the movement averages out equally in all directions, resulting in a sphere."
        )

    # Helper to rotate points in 3D
    def rotate_point(p, alpha_deg, beta_deg):
        alpha, beta = np.deg2rad(alpha_deg), np.deg2rad(beta_deg)
        # Rotation around Y (tilt)
        Ry = np.array([[np.cos(alpha), 0, np.sin(alpha)], [0, 1, 0], [-np.sin(alpha), 0, np.cos(alpha)]])
        # Rotation around Z (orientation)
        Rz = np.array([[np.cos(beta), -np.sin(beta), 0], [np.sin(beta), np.cos(beta), 0], [0, 0, 1]])
        return Rz @ (Ry @ p)

    # Create static "rings" showing the paths
    for i, (alpha, beta) in enumerate(planes_angles):
        radius = 1.0
        # Base circular path
        x_base = radius * np.cos(phi)
        y_base = radius * np.sin(phi)
        z_base = np.zeros_like(phi)
        
        rotated_path = [rotate_point(np.array([x, y, z]), alpha, beta) for x, y, z in zip(x_base, y_base, z_base)]
        xr = [p[0] for p in rotated_path]
        yr = [p[1] for p in rotated_path]
        zr = [p[2] for p in rotated_path]
        
        fig.add_trace(go.Scatter3d(x=xr, y=yr, z=zr, mode="lines", line=dict(color=colors[i], width=3, dash='dash'), showlegend=False, opacity=0.4))
        
    # Animate 4 dots moving along these paths
    for t_idx in range(len(theta_dots)):
        frame_data = [
            # Keep central core static
            go.Scatter3d(x=[0], y=[0], z=[0], mode="markers", marker=dict(size=12, color="gray"))
        ]
        
        # Add the rings again for the frame
        for i, (alpha, beta) in enumerate(planes_angles):
            radius = 1.0
            x_base = radius * np.cos(phi)
            y_base = radius * np.sin(phi)
            z_base = np.zeros_like(phi)
            rotated_path = [rotate_point(np.array([x, y, z]), alpha, beta) for x, y, z in zip(x_base, y_base, z_base)]
            xr, yr, zr = [p[0] for p in rotated_path], [p[1] for p in rotated_path], [p[2] for p in rotated_path]
            frame_data.append(go.Scatter3d(x=xr, y=yr, z=zr, mode="lines", line=dict(color=colors[i], width=3, dash='dash'), opacity=0.4))

        # Add the moving dots
        for i, (alpha, beta) in enumerate(planes_angles):
            # Calculate dot position at time t_idx
            # Add offset to dots to prevent overlaps initially
            current_theta = theta_dots[t_idx] + (i * np.pi/2) 
            radius = 1.0
            
            p_base = np.array([radius * np.cos(current_theta), radius * np.sin(current_theta), 0])
            pr = rotate_point(p_base, alpha, beta)
            
            # Use 'effective vector' mnemonic color consistency if possible
            # Here let's stick to distinctive colors for clarity
            dot_color = colors[i] 

            frame_data.append(go.Scatter3d(x=[pr[0]], y=[pr[1]], z=[pr[2]], mode="markers", marker=dict(size=10, color=dot_color)))
            
        frames.append(go.Frame(data=frame_data, name=str(t_idx)))

    # Use first frame data for initial plot
    for data in frames[0].data[1:]: # Skip static core added earlier
        fig.add_trace(data)
    
    fig.frames = frames

    fig.update_layout(
        title=dict(text=f"Cartoon of Orbiting Alignment for {state}", x=0.5),
        scene=dict(
            aspectmode="cube",
            xaxis=dict(range=[-1.5, 1.5], visible=False),
            yaxis=dict(range=[-1.5, 1.5], visible=False),
            zaxis=dict(range=[-1.5, 1.5], visible=False),
        ),
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=50, b=0),
        showlegend=False,
        updatemenus=[dict(
            type="buttons", showactive=False, y=0.05, x=0.5, xanchor="center", yanchor="bottom",
            buttons=[dict(label=f"▶ Animate {state} Orbits", method="animate", args=[None, dict(frame=dict(duration=80, redraw=True), transition=dict(duration=0), mode='immediate')])]
        )]
    )
    return fig, text_explanation

col10_a, col10_b = st.columns(2)

with col10_a:
    fig_j4, text_j4 = plot_orbital_alignment_animation(state="J=4 (Aligned)")
    st.plotly_chart(fig_j4, use_container_width=True, key="anim_j4_orbits")
    st.markdown(text_j4)

with col10_b:
    fig_j0, text_j0 = plot_orbital_alignment_animation(state="J=0 (Cancelled)")
    st.plotly_chart(fig_j0, use_container_width=True, key="anim_j0_orbits")
    st.markdown(text_j0)

st.write(
    "By comparing the animations, you can visually see that the aligned movement "
    "of the J=4 state 'carves out' a flat, stretched disk shape in space, "
    "while the crossing movements of the J=0 state 'carve out' a sphere."
        )
            
