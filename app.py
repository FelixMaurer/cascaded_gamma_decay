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
    tangent_dir = -np.sin(phase) * u1 + np.cos(phase) * u2
    tangent_dir = tangent_dir / np.linalg.norm(tangent_dir)
    return orbit[:, 0], orbit[:, 1], orbit[:, 2], tangent_dir

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

        if show_orbits:
            ox, oy, oz, tangent = get_orbit_points(v, radius=radii[i], phase=phases[i])
            fig.add_trace(go.Scatter3d(
                x=ox, y=oy, z=oz, mode='lines', 
                line=dict(color=colors[i], width=4, dash='dash'), 
                name=f"{names[i]} orbit", legendgroup=legend_group, showlegend=show_in_legend
            ))
            fig.add_trace(go.Scatter3d(
                x=[ox[0]], y=[oy[0]], z=[oz[0]], mode='markers',
                marker=dict(color=colors[i], size=8), legendgroup=legend_group, showlegend=False, hoverinfo="skip"
            ))
            fig.add_trace(go.Cone(
                x=[ox[0]], y=[oy[0]], z=[oz[0]],
                u=[tangent[0]], v=[tangent[1]], w=[tangent[2]],
                sizemode="absolute", sizeref=0.6, anchor="center",
                colorscale=[[0, colors[i]], [1, colors[i]]], showscale=False, hoverinfo="skip", showlegend=False
            ))
            
        if show_vectors:
            vx, vy, vz = v * vector_scale
            fig.add_trace(go.Scatter3d(
                x=[0, vx], y=[0, vy], z=[0, vz], mode='lines',
                line=dict(color=colors[i], width=6), name=f"j ({names[i]} = {np.linalg.norm(v):.1f})",
                legendgroup=legend_group, showlegend=False
            ))
            fig.add_trace(go.Cone(
                x=[vx], y=[vy], z=[vz], u=[vx], v=[vy], w=[vz],
                sizemode="absolute", sizeref=0.4, anchor="tip", colorscale=[[0, colors[i]], [1, colors[i]]], showscale=False
            ))

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

    if show_charge:
        ex, ey, ez = get_ellipsoid(beta)
        fig.add_trace(go.Surface(x=ex, y=ey, z=ez, colorscale='Blues', opacity=0.25, showscale=False, name="Charge Dist."))

    fig.update_layout(
        title=f"State: {state_name}",
        scene=dict(
            xaxis=dict(range=[-6, 6], visible=False),
            yaxis=dict(range=[-6, 6], visible=False),
            zaxis=dict(range=[-6, 6], visible=False), 
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

# =====================================================================
# Section 4: 2D Static Storyboard Transitions
# =====================================================================
st.header("4. The Gamma Cascade (Static 2D Storyboard)")
st.write(
    "To ensure high performance, the dynamic transitions are shown as 2D structural frames. "
    "Observe how the nucleus 'squishes' from an oblate shape to a spherical one, radiating a 4-lobed E2 wave packet."
)

def plot_static_2d_transition(beta_in, beta_out, wave_type="E2", title="Transition"):
    fig = make_subplots(rows=1, cols=3, subplot_titles=("Initial Shape", "Emitted Wave", "Final Shape"))
    
    t = np.linspace(0, 2*np.pi, 100)
    
    # Initial Shape (Oblate projection: wider in X than Y)
    x_in = (1 / np.sqrt(1 - beta_in)) * np.cos(t)
    y_in = (1 - beta_in) * np.sin(t)
    fig.add_trace(go.Scatter(x=x_in, y=y_in, fill='toself', name='Initial', line_color='blue'), row=1, col=1)
    
    # Wave
    if wave_type == "E2":
        r_wave = 1 - np.cos(t)**4
    else:
        r_wave = np.ones_like(t)
        
    x_wave = r_wave * np.cos(t)
    y_wave = r_wave * np.sin(t)
    fig.add_trace(go.Scatter(x=x_wave, y=y_wave, fill='toself', name='Wave', line_color='green'), row=1, col=2)
    
    # Final Shape
    x_out = (1 / np.sqrt(1 - beta_out)) * np.cos(t)
    y_out = (1 - beta_out) * np.sin(t)
    fig.add_trace(go.Scatter(x=x_out, y=y_out, fill='toself', name='Final', line_color='purple'), row=1, col=3)
    
    fig.update_layout(
        title=title, showlegend=False, height=300,
        xaxis=dict(range=[-2, 2], visible=False), yaxis=dict(range=[-2, 2], visible=False),
        xaxis2=dict(range=[-1.2, 1.2], visible=False), yaxis2=dict(range=[-1.2, 1.2], visible=False),
        xaxis3=dict(range=[-2, 2], visible=False), yaxis3=dict(range=[-2, 2], visible=False),
    )
    return fig

col4a, col4b = st.columns(2)
with col4a:
    st.subheader("Emission 1: J=4 → J=2")
    st.markdown(r"**$\gamma_1 = 1173$ keV** | $\Delta J = 2 \rightarrow L = 2$ (E2)")
    st.plotly_chart(plot_static_2d_transition(0.5, 0.25, "E2", "First Emission"), use_container_width=True, key="p_em1")

with col4b:
    st.subheader("Emission 2: J=2 → J=0")
    st.markdown(r"**$\gamma_2 = 1333$ keV** | $\Delta J = 2 \rightarrow$ strictly $L = 2$ (E2)")
    st.plotly_chart(plot_static_2d_transition(0.25, 0.0, "E2", "Second Emission"), use_container_width=True, key="p_em2")

st.divider()

# =====================================================================
# Section 5: The Mathematical Derivation of W(theta)
# =====================================================================
st.header("5. Step-by-Step: Deriving the Angular Correlation Function")
st.write(
    "How do we get from a single substate radiation pattern (like $1-\cos^4\\theta$) to the macroscopic, "
    "averaged angular correlation function $W(\\theta)$ observed in the laboratory? It requires four rigorous mathematical steps "
    "using Clebsch-Gordan algebra."
)

st.subheader("Step 1: Defining the Quantization Axis")
st.write(
    "Initially, the $J_i=4$ nuclei in the sample are unpolarized (randomly oriented). "
    "When the first detector records $\\gamma_1$, we mathematically define the flight path of $\\gamma_1$ as the $z$-axis ($z=0$). "
    "Because photons are spin-1 bosons traveling at the speed of light, they can only carry helicity $m_\\gamma = \\pm 1$ along their direction of motion."
)

st.subheader("Step 2: Calculating Substate Populations $P(m)$")
st.write(
    "The first emission ($J_i=4 \\xrightarrow{\\gamma_1} J=2$) populates the magnetic substates ($m$) of the intermediate state. "
    "We calculate the population $P(m)$ by summing over all unpolarized initial states $m_i$ using the Clebsch-Gordan (CG) coefficients "
    "for angular momentum addition ($|J, m\\rangle$):"
)
st.latex(r"P(m) \propto \sum_{m_i=-4}^{4} |\langle J_i, m_i \ | \ J, m ; L_1, m_\gamma \rangle|^2")
st.write(
    "By plugging in $J_i=4$, $J=2$, $L_1=2$ (E2 photon), and restricting $m_\\gamma = \\pm 1$ (from Step 1), the math heavily favors specific substates. "
    "The resulting populations $P(m)$ for the intermediate $J=2$ state are not equal; the state is now **aligned**."
)

st.subheader("Step 3: Radiation Patterns of the Substates $W_m(\\theta)$")
st.write(
    "Now, the aligned $J=2$ intermediate state decays to the $J_f=0$ ground state by emitting $\\gamma_2$. "
    "The angular distribution $W_m(\\theta)$ of $\\gamma_2$ depends entirely on which substate $m$ it originated from. "
    "For an $L_2=2$ (E2) transition to a $J=0$ state, the radiation patterns are derived from Vector Spherical Harmonics:"
)
st.latex(r"W_{m=0}(\theta) \propto \sin^2\theta \cos^2\theta")
st.latex(r"W_{m=\pm 1}(\theta) \propto \cos^2\theta + \cos^2(2\theta)")
st.latex(r"W_{m=\pm 2}(\theta) \propto 1 - \cos^4\theta")
st.write(
    "*(Notice that your intuitive $1 - \cos^4\\theta$ pattern is specifically the emission profile from the $m=\\pm 2$ substates!)*"
)

st.subheader("Step 4: The Weighted Macroscopic Average")
st.write(
    "The final detector measures the average of all these patterns, weighted by the populations $P(m)$ calculated in Step 2. "
    "Mathematically, this is the dot product:"
)
st.latex(r"W(\theta) = \sum_{m=-2}^{2} P(m) W_m(\theta)")
st.write(
    "When nuclear physicists execute this summation (often simplified using Racah or Wigner 6-j symbols), the highly directional individual patterns "
    "smooth out into a combination of even Legendre polynomials $P_k(\\cos\\theta)$:"
)
st.latex(r"W(\theta) = 1 + A_2 P_2(\cos\theta) + A_4 P_4(\cos\theta)")
st.write(
    "For our specific $4(E2)2(E2)0$ cascade, the theoretical constants are exactly $A_2 = 0.102$ and $A_4 = 0.0091$. Expanding the Legendre polynomials gives the final observable equation:"
)
st.latex(r"W(\theta) = 1 + \frac{1}{8}\cos^2\theta + \frac{1}{24}\cos^4\theta")

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
    "leaving the gentle, observable " "peanut" " shape of the macroscopic $W(\\theta)$ correlation."
)
