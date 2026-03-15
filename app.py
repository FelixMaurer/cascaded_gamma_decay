import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Ni-60 Spin Cascades", layout="wide")

st.title("Ni-60 Excited States: 3D Interactive Valence Coupling")
st.write(
    "A unified visual explanation of the 4→2→0 gamma-gamma cascade in "
    "Ni-60. Use the interactive viewers to rotate the nucleus and toggle "
    "different physical layers."
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
    v = np.array(v) / np.linalg.norm(v)
    if abs(v[0]) < 0.9:
        u1 = np.array([1, 0, 0])
    else:
        u1 = np.array([0, 1, 0])
    u1 = u1 - np.dot(u1, v) * v
    u1 = u1 / np.linalg.norm(u1)
    u2 = np.cross(v, u1)
    return u1, u2

def get_orbit_points(normal, radius, phase=0.0, points=60):
    u1, u2 = get_orthogonal_vectors(normal)
    theta = np.linspace(phase, 2 * np.pi + phase, points)
    orbit = np.array([radius * np.cos(t) * u1 + radius * np.sin(t) * u2 for t in theta])
    return orbit[:, 0], orbit[:, 1], orbit[:, 2], theta, u1, u2

def get_ellipsoid(beta, radius=1.8, points=40):
    phi = np.linspace(0, 2 * np.pi, points)
    theta = np.linspace(0, np.pi, points)
    phi, theta = np.meshgrid(phi, theta)
    rz = radius * (1 - beta)
    rxy = radius / np.sqrt(1 - beta)
    x = rxy * np.sin(theta) * np.cos(phi)
    y = rxy * np.sin(theta) * np.sin(phi)
    z = rz * np.cos(theta)
    return x, y, z

# =====================================================================
# Main 3D Plotting Function (Sections 1-3)
# =====================================================================
def plot_3d_state(state_name, vectors, show_orbits, show_vectors, show_charge, show_core, beta, radii, phases, colors, names):
    fig = go.Figure()
    
    if show_core:
        xc, yc, zc = get_ellipsoid(0, radius=0.8, points=20)
        fig.add_trace(go.Surface(x=xc, y=yc, z=zc, colorscale='Greys', showscale=False, opacity=1.0, name="Core"))

    total_j = np.zeros(3)
    vector_scale = 1.0
    added_p32 = False
    added_f52 = False

    nucleon_positions = []
    orbit_data = []
    for i, v in enumerate(vectors):
        ox, oy, oz, theta_arr, u1, u2 = get_orbit_points(v, radius=radii[i], phase=phases[i])
        nucleon_positions.append(np.array([ox[0], oy[0], oz[0]]))
        orbit_data.append((ox, oy, oz, theta_arr, u1, u2))

    nucleon_positions = np.array(nucleon_positions)

    # --- Nucleon Repulsion Logic ---
    M0_M2_ratio = 1.0 / 2.0  
    
    for _ in range(10):  
        for i in range(len(nucleon_positions)):
            for j in range(i + 1, len(nucleon_positions)):
                dist_vec = nucleon_positions[i] - nucleon_positions[j]
                dist = np.linalg.norm(dist_vec)
                
                if dist < 1e-4:
                    dist_vec = np.array([0.05 * (i+1), -0.05 * (j+1), 0.05])
                    dist = np.linalg.norm(dist_vec)
                    
                if dist < 1.2:  
                    repulsion_force = (dist_vec / dist) * M0_M2_ratio * 0.3
                    nucleon_positions[i] += repulsion_force
                    nucleon_positions[j] -= repulsion_force

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
        ox, oy, oz, theta_arr, u1, u2 = orbit_data[i]

        if show_orbits:
            fig.add_trace(go.Scatter3d(
                x=ox, y=oy, z=oz, mode='lines', 
                line=dict(color=colors[i], width=3, dash='dash'), 
                name=f"{names[i]} orbit", legendgroup=legend_group, showlegend=show_in_legend
            ))
            
            fig.add_trace(go.Scatter3d(
                x=[nucleon_positions[i][0]], y=[nucleon_positions[i][1]], z=[nucleon_positions[i][2]], mode='markers',
                marker=dict(color=colors[i], size=8, line=dict(color='white', width=1)), 
                legendgroup=legend_group, showlegend=False, hoverinfo="skip"
            ))
            
            arrow_indices = [15, 30, 45]
            for idx in arrow_indices:
                t_dir = -np.sin(theta_arr[idx]) * u1 + np.cos(theta_arr[idx]) * u2
                t_dir = t_dir / np.linalg.norm(t_dir)
                fig.add_trace(go.Cone(
                    x=[ox[idx]], y=[oy[idx]], z=[oz[idx]],
                    u=[t_dir[0]], v=[t_dir[1]], w=[t_dir[2]],
                    sizemode="absolute", sizeref=0.25, anchor="tail",
                    colorscale=[[0, colors[i]], [1, colors[i]]], showscale=False, hoverinfo="skip", showlegend=False
                ))
            
        if show_vectors:
            vx, vy, vz = v * vector_scale
            fig.add_trace(go.Scatter3d(
                x=[0, vx], y=[0, vy], z=[0, vz], mode='lines',
                line=dict(color=colors[i], width=5), name=f"j ({names[i]} = {np.linalg.norm(v):.1f})",
                legendgroup=legend_group, showlegend=False
            ))
            fig.add_trace(go.Cone(
                x=[vx], y=[vy], z=[vz], u=[vx], v=[vy], w=[vz],
                sizemode="absolute", sizeref=0.3, anchor="tip", colorscale=[[0, colors[i]], [1, colors[i]]], showscale=False
            ))

    if show_vectors and np.linalg.norm(total_j) > 0.1:
        tj_scaled = total_j * vector_scale
        fig.add_trace(go.Scatter3d(
            x=[0, tj_scaled[0]], y=[0, tj_scaled[1]], z=[0, tj_scaled[2]], mode='lines',
            line=dict(color='yellow', width=8), name=f"Total J={round(np.linalg.norm(total_j))}"
        ))
        fig.add_trace(go.Cone(
            x=[tj_scaled[0]], y=[tj_scaled[1]], z=[tj_scaled[2]], 
            u=[tj_scaled[0]], v=[tj_scaled[1]], w=[tj_scaled[2]],
            sizemode="absolute", sizeref=0.6, anchor="tip", colorscale=[[0, 'yellow'], [1, 'yellow']], showscale=False
        ))

    if show_charge:
        ex, ey, ez = get_ellipsoid(beta)
        fig.add_trace(go.Surface(x=ex, y=ey, z=ez, colorscale='Blues', opacity=0.25, showscale=False, name="Charge Dist."))

    fig.update_layout(
        title=f"State: {state_name}",
        scene=dict(
            xaxis=dict(range=[-5, 5], visible=False),
            yaxis=dict(range=[-5, 5], visible=False),
            zaxis=dict(range=[-5, 5], visible=False), 
            aspectmode='cube'
        ),
        height=500, margin=dict(l=0, r=0, b=0, t=40), paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    return fig

phases_all = [0.0, np.pi/2, np.pi, 3*np.pi/2]

vectors_J4 = [[1.5, 0, 0], [-1.5, 0, 0], [0, 0, 1.5], [0, 0, 2.5]] 
radii_J4   = [1.5, 1.5, 1.5, 2.2]
colors_J4  = ["cyan", "cyan", "cyan", "lime"]
names_J4   = ["p3/2", "p3/2", "p3/2", "f5/2"]

vectors_J2 = [[0, 1.5, 0], [0, -1.5, 0], [-1.5, 0, 0], [1.5, 0, 2.0]]
radii_J2   = [1.5, 1.5, 1.5, 2.2]
colors_J2  = ["cyan", "cyan", "cyan", "lime"]
names_J2   = ["p3/2", "p3/2", "p3/2", "f5/2"]

vectors_J0 = [[1.5, 0, 0], [-1.5, 0, 0], [0, 1.5, 0], [0, -1.5, 0]]
radii_J0   = [1.5, 1.5, 1.5, 1.5]
colors_J0  = ["cyan", "cyan", "cyan", "cyan"]
names_J0   = ["p3/2", "p3/2", "p3/2", "p3/2"]

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Initial State (J=4)")
    show_core_4 = st.checkbox("Show Core", value=True, key="core4")
    show_orb_4 = st.checkbox("Show Orbits", value=True, key="o4")
    show_vec_4 = st.checkbox("Show Vectors", value=True, key="v4")
    show_chg_4 = st.checkbox("Show Charge Overlay", value=True, key="c4")
    fig_4 = plot_3d_state("J=4 (Aligned)", vectors_J4, show_orb_4, show_vec_4, show_chg_4, show_core_4, beta=0.5, radii=radii_J4, phases=phases_all, colors=colors_J4, names=names_J4)
    st.plotly_chart(fig_4, use_container_width=True, key="c_s4")

with col2:
    st.subheader("2. Intermediate State (J=2)")
    show_core_2 = st.checkbox("Show Core", value=True, key="core2")
    show_orb_2 = st.checkbox("Show Orbits", value=True, key="o2")
    show_vec_2 = st.checkbox("Show Vectors", value=True, key="v2")
    show_chg_2 = st.checkbox("Show Charge Overlay", value=True, key="c2")
    fig_2 = plot_3d_state("J=2 (Partially Cancelled)", vectors_J2, show_orb_2, show_vec_2, show_chg_2, show_core_2, beta=0.25, radii=radii_J2, phases=phases_all, colors=colors_J2, names=names_J2)
    st.plotly_chart(fig_2, use_container_width=True, key="c_s2")

with col3:
    st.subheader("3. Ground State (J=0)")
    show_core_0 = st.checkbox("Show Core", value=True, key="core0")
    show_orb_0 = st.checkbox("Show Orbits", value=True, key="o0")
    show_vec_0 = st.checkbox("Show Vectors", value=True, key="v0")
    show_chg_0 = st.checkbox("Show Charge Overlay", value=True, key="c0")
    fig_0 = plot_3d_state("J=0 (Spherical)", vectors_J0, show_orb_0, show_vec_0, show_chg_0, show_core_0, beta=0.0, radii=radii_J0, phases=phases_all, colors=colors_J0, names=names_J0)
    st.plotly_chart(fig_0, use_container_width=True, key="c_s0")

st.divider()

st.header("4. Animated Emission Waves")
st.write(
    "Press **Play** below to watch how the stretched nucleus radiating energy squeezes back into a spherical shape. "
    "Observe the specific angular lobes of the emitted photons traveling outward."
)

def plot_animated_emission(beta_in, beta_out, wave_type="E2", title="Transition"):
    fig = go.Figure()
    
    t = np.linspace(0, 2*np.pi, 200)
    num_frames = 30
    
    # Calculate initial shapes
    if wave_type == "E2":
        x_in = (1 / np.sqrt(1 - beta_in)) * np.cos(t)
        y_in = (1 - beta_in) * np.sin(t)
    else:
        # E1: Start spherical, center of charge will slosh
        x_in = np.cos(t)
        y_in = np.sin(t)
        
    # Base Wave 
    r_base_init = 1.0
    if wave_type == "E2":
        r_wave_init = r_base_init + 1.5 * np.abs(np.sin(2*t))
        wave_color = 'rgba(0, 200, 100, {opacity})'
    else:
        r_wave_init = r_base_init + 1.8 * np.abs(np.cos(t))
        wave_color = 'rgba(255, 100, 50, {opacity})'
        
    fig.add_trace(go.Scatter(x=r_wave_init*np.cos(t), y=r_wave_init*np.sin(t), mode='lines', 
                             line=dict(color=wave_color.format(opacity=1.0), dash='dot', width=3), 
                             name='Wave', showlegend=False, hoverinfo="skip"))
                             
    fig.add_trace(go.Scatter(x=x_in, y=y_in, fill='toself', name='Nucleus', 
                             line_color='royalblue', fillcolor='rgba(65, 105, 225, 0.7)', hoverinfo="skip"))

    # Generate Frames
    frames = []
    for i in range(num_frames):
        tau = i / (num_frames - 1)
        
        if wave_type == "E2":
            # Quadrupole: Symmetrical stretching/squeezing
            beta_curr = beta_in + (beta_out - beta_in) * tau
            x_nuc = (1 / np.sqrt(1 - beta_curr)) * np.cos(t)
            y_nuc = (1 - beta_curr) * np.sin(t)
        else:
            # Dipole: Symmetrical shape, but center of charge sloshes back and forth
            slosh_amplitude = 0.5
            slosh = slosh_amplitude * np.sin(tau * 4 * np.pi) # 2 full up/down oscillations
            x_nuc = np.cos(t)
            y_nuc = np.sin(t) + slosh
        
        # Expand and fade the wave
        opacity = max(0.0, 1.0 - tau)
        r_base = 1.0 + 4.0 * tau
        
        if wave_type == "E2":
            r_wave = r_base + 1.5 * np.abs(np.sin(2*t))
        else:
            r_wave = r_base + 1.8 * np.abs(np.cos(t))
            
        x_w = r_wave * np.cos(t)
        y_w = r_wave * np.sin(t)
        
        frames.append(go.Frame(data=[
            go.Scatter(x=x_w, y=y_w, line=dict(color=wave_color.format(opacity=opacity))),
            go.Scatter(x=x_nuc, y=y_nuc)
        ], name=f"frame{i}"))

    fig.frames = frames

    fig.update_layout(
        title=title, showlegend=False, height=400,
        xaxis=dict(range=[-5, 5], visible=False), 
        yaxis=dict(range=[-5, 5], visible=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=10, r=10, b=10, t=40),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            y=-0.1, x=0.5, xanchor="center", yanchor="top",
            direction="left",
            buttons=[
                dict(label="▶ Play", method="animate",
                     args=[None, dict(frame=dict(duration=40, redraw=False), 
                                      transition=dict(duration=0),
                                      fromcurrent=True, mode="immediate")]),
                dict(label="⏸ Pause", method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False), 
                                        mode="immediate", transition=dict(duration=0))])
            ]
        )]
    )
    return fig

col4a, col4b, col4c = st.columns(3)
with col4a:
    st.subheader("1st Emission: J=4 → J=2")
    st.markdown("**1173 keV** | $\Delta J = 2 \\rightarrow L = 2$ (E2)")
    st.plotly_chart(plot_animated_emission(0.4, 0.2, "E2", "E2 Quadrupole Animation"), use_container_width=True, key="p_em1")

with col4b:
    st.subheader("2nd Emission: J=2 → J=0")
    st.markdown("**1333 keV** | $\Delta J = 2 \\rightarrow$ strictly $L = 2$ (E2)")
    st.plotly_chart(plot_animated_emission(0.2, 0.0, "E2", "E2 Quadrupole Animation"), use_container_width=True, key="p_em2")

with col4c:
    st.subheader("Comparison Example")
    st.markdown("Hypothetical | $\Delta J = 1 \\rightarrow L = 1$ (E1)")
    st.plotly_chart(plot_animated_emission(0.3, 0.1, "E1", "E1 Dipole Animation"), use_container_width=True, key="p_em3")

st.divider()



# --- START DROP-IN EXPLANATION ---
with st.expander("💡 Wait, neutrons are neutral! Why does the charge distribution change?"):
    st.write(
        "It's a great observation: isolated neutrons have an electric charge of exactly 0. "
        "If only the valence neutrons were moving, there would be no changing electric field, "
        "and therefore no electric quadrupole (E2) radiation."
    )
    st.markdown(
        """
        **The secret is Core Polarization:**
        * **The Core:** Ni-60 consists of a tightly bound, spherical core of 28 protons and 28 neutrons (the doubly-magic Ni-56 core), plus your 4 valence neutrons orbiting on the outside.
        * **The Strong Force Tug-of-War:** As those 4 valence neutrons settle into an aligned, non-spherical equator (the oblate $J=4$ state), they interact with the core via the strong nuclear force.
        * **The Charge Follows the Mass:** The valence neutrons physically drag the core protons out of their perfect spherical shape. The core bulges out to follow the neutrons. When the nucleus "squeezes" back into a sphere during the transition, the radiation is actually coming from the **protons in the core** snapping back into place!
        
        **The Mathematical Trick: Effective Charge**
        Because tracking the movement of 28 individual core protons is a mathematical nightmare, nuclear physicists use a trick called **effective charge** ($e_{eff}$). Instead of calculating the core's deformation, they pretend the core stays perfectly spherical and assign a fake electric charge (usually around $+0.5e$) to the valence neutrons. This perfectly accounts for the amount of core-proton-drag they create.
        """
    )

# =====================================================================
# Section 5: The Mathematical Derivation of W(theta)
# =====================================================================
st.header("5. Step-by-Step: Deriving the Angular Correlation Function")
st.write(
    "The leap from a single substate radiation pattern to the macroscopic "
    "angular correlation function $W(\\theta)$ observed in the laboratory can feel abstract. "
    "Let's break down the four mathematical steps required to get there."
)

st.subheader("Step 1: Defining the Quantization Axis")
st.write(
    "Initially, the $J_i=4$ nuclei in your sample are unpolarized (oriented randomly in all directions). "
    "We have no reference frame. However, the moment the first detector records $\\gamma_1$, "
    "we mathematically define the flight path of that specific photon as our $z$-axis ($z=0$)."
)

def plot_quantization_axis():
    fig = go.Figure()
    
    # Initial random spin J_i
    fig.add_trace(go.Scatter3d(
        x=[0, -2], y=[0, 2], z=[0, 1.5], mode='lines',
        line=dict(color='royalblue', width=6), name="Initial Random Spin (J_i=4)"
    ))
    fig.add_trace(go.Cone(
        x=[-2], y=[2], z=[1.5], u=[-2], v=[2], w=[1.5],
        sizemode="absolute", sizeref=0.4, anchor="tip",
        colorscale=[[0, 'royalblue'], [1, 'royalblue']], showscale=False, hoverinfo="skip"
    ))

    # Nucleus
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0], mode='markers',
        marker=dict(size=12, color='gray', line=dict(color='white', width=2)),
        name="Nucleus"
    ))
    
    # Gamma 1 defining the Z-axis
    fig.add_trace(go.Scatter3d(
        x=[0, 0], y=[0, 0], z=[0, 4], mode='lines',
        line=dict(color='yellow', width=6, dash='dot'), name="γ₁ Flight Path defines Z-Axis"
    ))
    fig.add_trace(go.Cone(
        x=[0], y=[0], z=[4], u=[0], v=[0], w=[2],
        sizemode="absolute", sizeref=0.5, anchor="tail",
        colorscale=[[0, 'yellow'], [1, 'yellow']], showscale=False, hoverinfo="skip"
    ))

    # X and Y reference axes (faint)
    fig.add_trace(go.Scatter3d(x=[0, 3], y=[0, 0], z=[0, 0], mode='lines', line=dict(color='rgba(100,100,100,0.5)', width=2), showlegend=False))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 3], z=[0, 0], mode='lines', line=dict(color='rgba(100,100,100,0.5)', width=2), showlegend=False))

    fig.update_layout(
        title="Detector 1 Freezes the Coordinate System",
        scene=dict(
            xaxis=dict(range=[-4, 4], showbackground=False, visible=False),
            yaxis=dict(range=[-4, 4], showbackground=False, visible=False),
            zaxis=dict(range=[-4, 4], showbackground=False, visible=False),
            aspectmode='cube'
        ),
        height=400, margin=dict(l=0, r=0, b=0, t=40), paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    return fig

st.plotly_chart(plot_quantization_axis(), use_container_width=True, key="p_axis")

st.write(
    "Because photons are spin-1 bosons traveling at the speed of light, they can only carry "
    "angular momentum (helicity) of $m_\\gamma = \\pm 1$ along their direction of motion. "
    "This restriction forces the nucleus into specific alignments relative to this new $z$-axis."
)

st.subheader("Step 2: Substate Populations P(m) & Clebsch-Gordan Pathways")
st.write(
    "What is a substate population $P(m)$? Intuitively, the magnetic substate $m$ represents the "
    "**tilt** (the $z$-axis projection) of the total nuclear spin. "
    "$P(m)$ is the percentage of nuclei in our sample that end up with a specific tilt "
    "after emitting the first photon."
)

st.info(
    """
    **The Quantum Precession Cone** \n
    In quantum mechanics, an angular momentum vector can **never** point perfectly straight along an axis! 
    Because its true length is $\sqrt{J(J+1)}$, it is always longer than its maximum $z$-projection ($m$). 
    The Uncertainty Principle dictates that the vector must tilt and "precess" (spin like a top) around the $z$-axis, tracing out a cone.
    """
)

show_cones = st.checkbox("Show Quantum Precession Cones", value=False, key="chk_cones")

st.write(
    "To find the substate percentages, we use **Clebsch-Gordan (CG) coefficients**. Because angular momentum is strictly conserved, "
    "the initial state vector must be the exact sum of the final state and the emitted photon ($\\vec{J}_i = \\vec{J}_f + \\vec{L}_\\gamma$). "
    "There are multiple geometric pathways to reach the exact same final state. Look at the two vector additions below:"
)

def plot_cg_pathways(show_cones):
    fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'scene'}, {'type': 'scene'}]], 
                        subplot_titles=("Pathway A: m_i=3 → m_f=2", "Pathway B: m_i=1 → m_f=2"))

    def get_cone_surface(z_height, radius, points=30):
        theta = np.linspace(0, 2*np.pi, points)
        # Handle zero height to avoid division by zero
        if z_height == 0:
            z_vals = np.array([0, 0])
        else:
            z_vals = np.linspace(0, z_height, points)
        Theta, Z = np.meshgrid(theta, z_vals)
        R = (Z / z_height) * radius if z_height != 0 else 0
        X = R * np.cos(Theta)
        Y = R * np.sin(Theta)
        return X, Y, Z

    def add_vector_addition(fig, row, col, v_f, v_gam, v_i, m_gam_label, show_legend, mag_f, mag_i):
        # Optional: Draw the precession cones
        if show_cones:
            rad_f = np.sqrt(max(0, mag_f**2 - v_f[2]**2))
            Xf, Yf, Zf = get_cone_surface(v_f[2], rad_f)
            fig.add_trace(go.Surface(
                x=Xf, y=Yf, z=Zf, colorscale=[[0, 'lime'], [1, 'lime']], 
                opacity=0.2, showscale=False, hoverinfo="skip"
            ), row=row, col=col)
            
            rad_i = np.sqrt(max(0, mag_i**2 - v_i[2]**2))
            Xi, Yi, Zi = get_cone_surface(v_i[2], rad_i)
            fig.add_trace(go.Surface(
                x=Xi, y=Yi, z=Zi, colorscale=[[0, 'royalblue'], [1, 'royalblue']], 
                opacity=0.15, showscale=False, hoverinfo="skip"
            ), row=row, col=col)

        # 1. Final State J_f (starts at origin)
        fig.add_trace(go.Scatter3d(
            x=[0, v_f[0]], y=[0, v_f[1]], z=[0, v_f[2]], mode='lines+markers',
            line=dict(color='lime', width=6), marker=dict(size=5, color='lime'), 
            name="Final J_f (J=2)", legendgroup="jf", showlegend=show_legend
        ), row=row, col=col)
        
        # 2. Photon (starts at tip of J_f, goes to tip of J_i)
        fig.add_trace(go.Scatter3d(
            x=[v_f[0], v_i[0]], y=[v_f[1], v_i[1]], z=[v_f[2], v_i[2]], mode='lines',
            line=dict(color='yellow', width=5, dash='dash'), 
            name="Photon Angular Momentum (L=2)", legendgroup="gam", showlegend=show_legend
        ), row=row, col=col)
        
        # Cone for photon direction
        fig.add_trace(go.Cone(
            x=[v_i[0]], y=[v_i[1]], z=[v_i[2]], u=[v_gam[0]], v=[v_gam[1]], w=[v_gam[2]],
            sizemode="absolute", sizeref=0.4, anchor="tip",
            colorscale=[[0, 'yellow'], [1, 'yellow']], showscale=False, hoverinfo="skip"
        ), row=row, col=col)

        # 3. Initial State J_i (starts at origin)
        fig.add_trace(go.Scatter3d(
            x=[0, v_i[0]], y=[0, v_i[1]], z=[0, v_i[2]], mode='lines+markers',
            line=dict(color='royalblue', width=6), marker=dict(size=5, color='royalblue'), 
            name="Initial J_i (J=4)", legendgroup="ji", showlegend=show_legend
        ), row=row, col=col)

        # 4. Projection lines to the Z-axis
        fig.add_trace(go.Scatter3d(
            x=[v_i[0], 0], y=[v_i[1], 0], z=[v_i[2], v_i[2]], mode='lines',
            line=dict(color='royalblue', width=2, dash='dot'), showlegend=False, hoverinfo="skip"
        ), row=row, col=col)
        fig.add_trace(go.Scatter3d(
            x=[v_f[0], 0], y=[v_f[1], 0], z=[v_f[2], v_f[2]], mode='lines',
            line=dict(color='lime', width=2, dash='dot'), showlegend=False, hoverinfo="skip"
        ), row=row, col=col)
        
        # Highlight the z-axis projections with markers
        fig.add_trace(go.Scatter3d(
            x=[0, 0], y=[0, 0], z=[v_i[2], v_f[2]], mode='markers',
            marker=dict(color=['royalblue', 'lime'], size=6), showlegend=False, hoverinfo="skip"
        ), row=row, col=col)

        # Z-axis line
        fig.add_trace(go.Scatter3d(
            x=[0, 0], y=[0, 0], z=[0, 4.5], mode='lines',
            line=dict(color='white', width=2), name="Z-axis", showlegend=False, hoverinfo="skip"
        ), row=row, col=col)

    # True Quantum Magnitudes: sqrt(J(J+1))
    mag_f = np.sqrt(2 * 3) # J=2 -> ~2.45
    mag_i = np.sqrt(4 * 5) # J=4 -> ~4.47

    # Pathway A: Initial m_i=3, Final m_f=2, Photon m_gamma=+1
    rad_f_A = np.sqrt(mag_f**2 - 2**2)
    rad_i_A = np.sqrt(mag_i**2 - 3**2)
    
    v_f_A = [rad_f_A, 0, 2]         
    v_i_A = [rad_i_A, 0, 3]         
    v_gam_A = [v_i_A[0]-v_f_A[0], 0, 1]    
    add_vector_addition(fig, 1, 1, v_f_A, v_gam_A, v_i_A, "m_γ = +1", show_legend=True, mag_f=mag_f, mag_i=mag_i)

    # Pathway B: Initial m_i=1, Final m_f=2, Photon m_gamma=-1
    rad_f_B = np.sqrt(mag_f**2 - 2**2)
    rad_i_B = np.sqrt(mag_i**2 - 1**2)

    v_f_B = [rad_f_B, 0, 2]         
    v_i_B = [rad_i_B, 0, 1]         
    v_gam_B = [v_i_B[0]-v_f_B[0], 0, -1]   
    add_vector_addition(fig, 1, 2, v_f_B, v_gam_B, v_i_B, "m_γ = -1", show_legend=False, mag_f=mag_f, mag_i=mag_i)

    fig.update_layout(
        height=450, margin=dict(l=0, r=0, b=0, t=40), paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), 
            zaxis=dict(range=[0, 4], title="Z (m projection)", showbackground=False)
        ),
        scene2=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), 
            zaxis=dict(range=[0, 4], title="Z (m projection)", showbackground=False)
        ),
        showlegend=True
    )
    return fig

st.plotly_chart(plot_cg_pathways(show_cones), use_container_width=True, key="p_cg")

st.write(
    "Because multiple initial states can lead to the exact same final state, we must **sum over all possibilities**. "
    "The CG coefficients calculate the exact geometrical probability of each specific triangle forming:"
)
st.latex(r"P(m) \propto \sum_{m_i=-4}^{4} |\langle J_i, m_i \ | \ J, m ; L_1, m_\gamma \rangle|^2")
st.write(
    "By plugging in $J_i=4$, $J=2$, $L_1=2$ (E2 photon), and $m_\\gamma = \\pm 1$, the math heavily favors specific tilts. "
    "The resulting populations $P(m)$ for the intermediate $J=2$ state are not equal; the nuclear ensemble is now physically **aligned**."
)

st.info(
    """
    **The Quantum Precession Cone & Photon Spin** \n
    In quantum mechanics, an angular momentum vector can **never** point perfectly straight along an axis! 
    Because its true length is mathematically longer than its maximum vertical projection, 
    the Uncertainty Principle dictates that the vector must tilt and "precess" (spin like a top) around the axis, tracing out a cone. \n
    **For the yellow photon vector:** Its total angular momentum (L=2) is a fusion of its **intrinsic spin** (s=1) and the **orbital angular momentum** generated by the changing shape of the nucleus. Because a wave cannot orbit its own forward flight path, the vertical projection of this vector is 100% pure intrinsic spin, while the outward "tilt" of its cone carries the orbital shape of the radiation!
    """
)

st.subheader("Step 3: Radiation Patterns of the Substates W_m(θ)")
st.write(
    "Now, the aligned $J=2$ intermediate state decays to the $J_f=0$ ground state by emitting $\\gamma_2$. "
    "The angular distribution $W_m(\\theta)$ of $\\gamma_2$ depends entirely on the tilt ($m$) it originated from. "
    "For an $L_2=2$ (E2) transition to a $J=0$ state, the radiation patterns are derived from **Vector Spherical Harmonics**."
)

with st.expander("🔍 Deep Dive: How do Vector Spherical Harmonics generate these equations?"):
    st.write(
        "If you've studied electron orbitals, you know **Scalar Spherical Harmonics** ($Y_{l,m}$). "
        "They describe the 3D shape of a field with only magnitude (like a probability cloud). "
        "But a photon is an electromagnetic wave; it has an electric and magnetic field pointing in specific directions (polarization). "
        "To describe a vector field, we need **Vector Spherical Harmonics** ($\\mathbf{X}_{L,m}$)."
    )
    st.markdown(
        """
        1. **Building the Vector:** The math literally multiplies the spatial shape ($Y_{l,m}$) by the photon's intrinsic spin-1 vector. 
        2. **Squaring for Intensity:** A detector doesn't measure the raw electric field; it measures the *intensity* (power) of the wave. To get the intensity $W_m(\\theta)$, we calculate the absolute square of the vector field's magnitude in the far distance: $W_m(\\theta) \propto |\\mathbf{X}_{L,m}(\\theta, \\phi)|^2$.
        3. **The Result:** When you square those complex vectors, the math simplifies beautifully into pure trigonometric polynomials!
        """
    )

st.write("For our E2 transition, squaring the Vector Spherical Harmonics yields these exact intensity profiles:")
st.latex(r"W_{m=0}(\theta) \propto \sin^2\theta \cos^2\theta")
st.latex(r"W_{m=\pm 1}(\theta) \propto \cos^2\theta + \cos^2(2\theta)")
st.latex(r"W_{m=\pm 2}(\theta) \propto 1 - \cos^4\theta")
st.write(
    "*(Notice that your intuitive $1 - \cos^4\\theta$ pattern from the earlier animation is specifically the emission profile from the $m=\\pm 2$ substates!)*"
)


st.subheader("Step 4: The Weighted Macroscopic Average")
st.write(
    "By writing out the math, we can see exactly how the deep crevices of the single $1 - \cos^4\theta$ pattern "
    "are filled in by the other substates, leaving the gentle, observable 'peanut' shape of the macroscopic $W(\theta)$ correlation."
)
st.latex(r"W(\theta) = \sum_{m=-2}^{2} P(m) W_m(\theta)")
st.write(
    "When nuclear physicists execute this summation, "
    "the highly directional individual patterns smooth out into a combination of even Legendre polynomials $P_k(\\cos\\theta)$:"
)
st.latex(r"W(\theta) = 1 + A_2 P_2(\cos\theta) + A_4 P_4(\cos\theta)")
st.write(
    "For our specific $4(E2)2(E2)0$ cascade, the theoretical constants evaluate exactly to $A_2 = 0.102$ and $A_4 = 0.0091$. "
    "Expanding the Legendre polynomials gives the final observable equation:"
)
st.latex(r"W(\theta) = 1 + \frac{1}{8}\cos^2\theta + \frac{1}{24}\cos^4\theta")
st.write(
    "The final detector measures the average of all these patterns, weighted by the percentages $P(m)$ "
    "we calculated in Step 2. Mathematically, this is the dot product:"
)
st.latex(r"W(\theta) = P(0)W_0(\theta) + 2P(1)W_1(\theta) + 2P(2)W_2(\theta)")

with st.expander("🧮 See the full algebraic derivation"):
    st.write("First, we convert all the $W_m(\theta)$ radiation patterns into powers of $\cos\theta$ so we can add them easily:")
    st.latex(r"W_0: \sin^2\theta \cos^2\theta \xrightarrow{\text{becomes}} \cos^2\theta - \cos^4\theta")
    st.latex(r"W_{\pm 1}: \cos^2\theta + \cos^2(2\theta) \xrightarrow{\text{becomes}} 1 - 3\cos^2\theta + 4\cos^4\theta")
    st.latex(r"W_{\pm 2}: 1 - \cos^4\theta \xrightarrow{\text{stays}} 1 - \cos^4\theta")
    
    st.write("Next, we substitute these into our weighted sum equation. The Clebsch-Gordan coefficients for our $4 \rightarrow 2$ transition dictate the exact population weights $P(m)$. When we plug those specific fractions in, the sum looks like this:")
    st.latex(r"W(\theta) \propto \underbrace{c_0(\cos^2\theta - \cos^4\theta)}_{m=0 \text{ contribution}} + \underbrace{c_1(1 - 3\cos^2\theta + 4\cos^4\theta)}_{m=\pm 1 \text{ contribution}} + \underbrace{c_2(1 - \cos^4\theta)}_{m=\pm 2 \text{ contribution}}")
    
    st.write("Finally, we simply group the terms by their power of $\cos\theta$:")
    st.latex(r"\text{Constant: } c_1 + c_2")
    st.latex(r"\cos^2\theta \text{ terms: } c_0 - 3c_1")
    st.latex(r"\cos^4\theta \text{ terms: } -c_0 + 4c_1 - c_2")

st.write(
    "When you crunch the exact Clebsch-Gordan fractions for those $c$ constants and normalize the equation, "
    "all the messy terms collapse into the beautiful, final observable formula:"
)
st.latex(r"W(\theta) = 1 + \frac{1}{8}\cos^2\theta + \frac{1}{24}\cos^4\theta")

def plot_final_correlation():
    theta_deg = np.linspace(0, 360, 721)
    theta_rad = np.deg2rad(theta_deg)
    # The mathematical formula we just derived
    W = 1 + (1 / 8.0) * (np.cos(theta_rad) ** 2) + (1 / 24.0) * (np.cos(theta_rad) ** 4)
    W = W / np.max(W) 

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=W, theta=theta_deg, mode="lines", line=dict(color="gold", width=4),
        fill="toself", fillcolor="rgba(255,215,0,0.30)"
    ))
    fig.update_layout(
        title="Final Macroscopic Angular Correlation W(θ)",
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1.05]),
            angularaxis=dict(direction="counterclockwise", rotation=0),
        ),
        height=400, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig

st.plotly_chart(plot_final_correlation(), use_container_width=True, key="p_final")


def plot_final_correlation():
    theta_deg = np.linspace(0, 360, 721)
    theta_rad = np.deg2rad(theta_deg)
    W = 1 + (1 / 8.0) * (np.cos(theta_rad) ** 2) + (1 / 24.0) * (np.cos(theta_rad) ** 4)
    W = W / np.max(W) 

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=W, theta=theta_deg, mode="lines", line=dict(color="gold", width=4),
        fill="toself", fillcolor="rgba(255,215,0,0.30)"
    ))
    fig.update_layout(
        title="Final Macroscopic Angular Correlation W(θ)",
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1.05]),
            angularaxis=dict(direction="counterclockwise", rotation=0),
        ),
        height=400, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig

st.plotly_chart(plot_final_correlation(), use_container_width=True, key="p_final")
st.write(
    "By mathematically averaging over all configurations, the deep crevices of the single $1 - \cos^4\\theta$ pattern are smoothed out, "
    "leaving the gentle, observable 'peanut' shape of the macroscopic $W(\\theta)$ correlation."
)
