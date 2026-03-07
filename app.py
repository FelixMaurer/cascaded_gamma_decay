import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Ni-60 Spin Cascades", layout="wide")

st.title("Ni-60 Excited States: Intuitive Valence-Coupling Cartoon")
st.write(
    "A simplified visual explanation of the 4\u21922\u21920 gamma-gamma cascade in "
    "Ni-60 using shell occupancies and angular-momentum coupling cartoons."
)

st.info(
    """
    **Important interpretation note**

    This app uses **pedagogical cartoons** to build intuition. The figures are **not literal pictures**
    of the nucleus.

    - The circular shell drawings show **occupancy patterns**, not nucleons moving on fixed circular orbits.
    - The 3D arrows show **angular-momentum coupling cartoons**, not literal spin directions in space.
    - The configurations shown are **example basis configurations** that can contribute to the real state.
    - The actual nuclear states are **quantum superpositions of several configurations**, not a single unique arrangement.
    """
)

st.warning(
    """
    **What to take away**

    The main message is that the low-lying Ni-60 states can be understood intuitively as arising mainly from
    the coupling of valence-space nucleons outside an approximate inert core. The visualizations are meant
    to explain **how total angular momentum can add up to 4, 2, and 0**, not to claim a unique microscopic snapshot.
    """
)

# --- HELPER FUNCTION: 2D SHELL SCHEMATIC ---
def draw_2d_shell(title_text, num_in=3, num_out=1):
    fig_shell = go.Figure()
    
    # Draw the Core
    fig_shell.add_shape(
        type="circle", x0=-2, y0=-2, x1=2, y1=2,
        fillcolor="lightgray", line_color="black"
    )
    fig_shell.add_annotation(
        x=0, y=0,
        text="<b>Approximate Core<br>(28p, 28n)<br>J = 0</b>",
        showarrow=False,
        font=dict(size=14, color="black")
    )
    
    # Draw Valence Shells
    fig_shell.add_shape(
        type="circle", x0=-3.5, y0=-3.5, x1=3.5, y1=3.5,
        line=dict(color="cyan", dash="dash")
    )
    fig_shell.add_annotation(
        x=0, y=3.7,
        text="2p3/2 occupancy cartoon",
        showarrow=False,
        font=dict(color="cyan", size=14)
    )
    
    fig_shell.add_shape(
        type="circle", x0=-5, y0=-5, x1=5, y1=5,
        line=dict(color="lime", dash="dash")
    )
    fig_shell.add_annotation(
        x=0, y=5.2,
        text="1f5/2 occupancy cartoon",
        showarrow=False,
        font=dict(color="lime", size=14)
    )
    
    # Determine neutron positions dynamically based on state
    # These dots indicate occupancy count only, not real spatial positions.
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
        fig_shell.add_trace(
            go.Scatter(
                x=3.5*np.cos(theta_in),
                y=3.5*np.sin(theta_in),
                mode='markers',
                marker=dict(size=15, color='cyan'),
                name=f"{num_in} neutrons in 2p3/2"
            )
        )
    if len(theta_out) > 0:
        fig_shell.add_trace(
            go.Scatter(
                x=5.0*np.cos(theta_out),
                y=5.0*np.sin(theta_out),
                mode='markers',
                marker=dict(size=15, color='lime'),
                name=f"{num_out} neutrons in 1f5/2"
            )
        )
    
    fig_shell.update_layout(
        title=title_text,
        xaxis=dict(visible=False, range=[-6, 6]),
        yaxis=dict(visible=False, range=[-6, 6], scaleanchor="x", scaleratio=1),
        height=350,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig_shell

# --- HELPER FUNCTION: 3D INTERNAL COUPLING ---
def plot_internal_coupling(title, mode="3_neutrons"):
    fig_internal = go.Figure()
    
    if mode == "3_neutrons":
        # Cartoon only: illustrates how p3/2^3 can be represented by an effective net j=3/2 contribution.
        fig_internal.add_trace(
            go.Scatter3d(
                x=[0, 0], y=[0, 0], z=[0, 1.5],
                mode='lines+markers',
                name='Example effective component',
                line=dict(width=6, color='cyan')
            )
        )
        fig_internal.add_trace(
            go.Scatter3d(
                x=[0, 1.5], y=[0, 0], z=[0, 0],
                mode='lines+markers',
                name='Example paired part',
                line=dict(width=6, color='magenta')
            )
        )
        fig_internal.add_trace(
            go.Scatter3d(
                x=[0, -1.5], y=[0, 0], z=[0, 0],
                mode='lines+markers',
                name='Example paired part',
                line=dict(width=6, color='magenta')
            )
        )
        fig_internal.add_trace(
            go.Scatter3d(
                x=[0, 0], y=[0, 0], z=[0, 1.5],
                mode='lines',
                name='Net effective j = 1.5',
                line=dict(dash='dash', color='cyan', width=8)
            )
        )
    
    elif mode == "4_neutrons":
        # Cartoon only: illustrates pairwise cancellation leading to J = 0.
        fig_internal.add_trace(
            go.Scatter3d(
                x=[0, 0], y=[0, 0], z=[0, 1.5],
                mode='lines+markers',
                name='Example pair component',
                line=dict(width=6, color='magenta')
            )
        )
        fig_internal.add_trace(
            go.Scatter3d(
                x=[0, 0], y=[0, 0], z=[0, -1.5],
                mode='lines+markers',
                name='Example pair component',
                line=dict(width=6, color='magenta')
            )
        )
        fig_internal.add_trace(
            go.Scatter3d(
                x=[0, 1.5], y=[0, 0], z=[0, 0],
                mode='lines+markers',
                name='Example pair component',
                line=dict(width=6, color='magenta')
            )
        )
        fig_internal.add_trace(
            go.Scatter3d(
                x=[0, -1.5], y=[0, 0], z=[0, 0],
                mode='lines+markers',
                name='Example pair component',
                line=dict(width=6, color='magenta')
            )
        )
        fig_internal.add_trace(
            go.Scatter3d(
                x=[0], y=[0], z=[0],
                mode='markers',
                name='Net effective j = 0',
                marker=dict(size=10, color='cyan')
            )
        )

    fig_internal.update_layout(
        title=title,
        scene=dict(
            aspectmode='cube',
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            xaxis=dict(range=[-2, 2]),
            yaxis=dict(range=[-2, 2]),
            zaxis=dict(range=[-2, 2])
        ),
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    return fig_internal

# --- HELPER FUNCTION: 3D VECTOR COUPLING WITH ARROWHEAD ---
def plot_3d_vectors(v1, v2, target_mag, title):
    fig = go.Figure()
    
    # Handle the completely zeroed out Ground State
    if v1 == 0 and v2 == 0:
        fig.add_trace(
            go.Scatter3d(
                x=[0], y=[0], z=[0],
                mode='markers',
                name=f'Total J = {target_mag}',
                marker=dict(size=12, color='yellow')
            )
        )
        fig.add_trace(
            go.Scatter3d(
                x=[0,0], y=[0,0], z=[0,0],
                mode='lines',
                name='Vector A',
                line=dict(width=0, color='cyan')
            )
        )
        fig.add_trace(
            go.Scatter3d(
                x=[0,0], y=[0,0], z=[0,0],
                mode='lines',
                name='Vector B',
                line=dict(width=0, color='lime')
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
                mode='lines+markers',
                name=f'Effective vector A (j={v1})',
                line=dict(width=8, color='cyan')
            )
        )
        fig.add_trace(
            go.Scatter3d(
                x=[0, end_x], y=[0, end_y], z=[v1, end_z],
                mode='lines+markers',
                name=f'Effective vector B (j={v2})',
                line=dict(width=8, color='lime')
            )
        )
        
        fig.add_trace(
            go.Scatter3d(
                x=[offset_x, offset_x], y=[0, end_y], z=[0, end_z],
                mode='lines',
                name=f'Total J = {target_mag}',
                line=dict(color='yellow', width=8)
            )
        )
        
        fig.add_trace(
            go.Cone(
                x=[offset_x], y=[end_y], z=[end_z],
                u=[u_dir], v=[v_dir], w=[w_dir],
                sizemode="absolute", sizeref=0.8, anchor="tip",
                colorscale=[[0, 'yellow'], [1, 'yellow']],
                showscale=False, name="Direction"
            )
        )
    
    fig.update_layout(
        title=title,
        scene=dict(
            aspectmode='cube',
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            xaxis=dict(range=[-4, 4]),
            yaxis=dict(range=[-4, 4]),
            zaxis=dict(range=[0, 5])
        ),
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    return fig


st.divider()

# ==========================================
# MAIN SECTION 1: THE INITIAL EXCITED STATE (I=4)
# ==========================================
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
    st.plotly_chart(draw_2d_shell("Example Valence Occupancy", num_in=3, num_out=1), use_container_width=True, key="shell_1")
    
with col1_b:
    st.subheader("1.2. Effective Internal Coupling Cartoon")
    st.write(
        "This panel is a **coupling mnemonic**, not a literal 3D arrangement of neutron spins. "
        "It suggests how a p3/2^3 occupancy can be represented by an effective net angular-momentum contribution of j = 1.5."
    )
    st.plotly_chart(plot_internal_coupling("Cartoon: 3 Neutrons -> Effective j = 1.5", mode="3_neutrons"), use_container_width=True, key="internal_1")

with col1_c:
    st.subheader("1.3. Effective Vector Coupling to J = 4")
    st.write(
        "In this simplified vector picture, an effective j = 1.5 contribution and an effective j = 2.5 contribution are coupled to the stretched total value J = 4."
    )
    st.plotly_chart(plot_3d_vectors(1.5, 2.5, 4.0, "Effective Coupling: 1.5 + 2.5 -> J = 4"), use_container_width=True, key="vector_1")

# --- SECTION 1.4: ALTERNATIVE CONFIGURATIONS (I=4) ---
st.write("---")
st.subheader("1.4. Alternative Microscopic Possibilities")
col1_d, col1_e, col1_f = st.columns(3)

with col1_d:
    st.write("**Alternative occupancy cartoon:** two neutrons promoted to 1f5/2.")
    st.plotly_chart(draw_2d_shell("Alternative Example Occupancy (J = 4)", num_in=2, num_out=2), use_container_width=True, key="shell_1_alt")

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
    st.plotly_chart(plot_3d_vectors(2.5, 2.5, 4.0, "Alternative Effective Coupling: 2.5 + 2.5 -> J = 4"), use_container_width=True, key="alt_vector_1")

st.divider()

# ==========================================
# MAIN SECTION 2: THE INTERMEDIATE STATE (I=2)
# ==========================================
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
    st.plotly_chart(draw_2d_shell("Example Valence Occupancy", num_in=3, num_out=1), use_container_width=True, key="shell_2")

with col2_b:
    st.subheader("2.2. Effective Internal Coupling Cartoon")
    st.write(
        "The same simplified internal-coupling mnemonic is kept here. "
        "This does not mean the nucleus contains rigid little arrows; it only provides an intuitive effective j = 1.5 contribution."
    )
    st.plotly_chart(plot_internal_coupling("Cartoon: 3 Neutrons -> Effective j = 1.5", mode="3_neutrons"), use_container_width=True, key="internal_2")

with col2_c:
    st.subheader("2.3. Effective Vector Coupling to J = 2")
    st.write(
        "In this simplified vector cartoon, the effective j = 1.5 and j = 2.5 contributions are coupled differently so that the total becomes J = 2 instead of J = 4."
    )
    st.plotly_chart(plot_3d_vectors(1.5, 2.5, 2.0, "Effective Coupling: 1.5 + 2.5 -> J = 2"), use_container_width=True, key="vector_2")

# --- SECTION 2.4: ALTERNATIVE CONFIGURATIONS (I=2) ---
st.write("---")
st.subheader("2.4. Alternative Microscopic Possibilities (J = 2)")
col2_d, col2_e, col2_f = st.columns(3)

with col2_d:
    st.write("**Alternative occupancy cartoon:** two neutrons remaining in 1f5/2.")
    st.plotly_chart(draw_2d_shell("Alternative Example Occupancy (J = 2)", num_in=2, num_out=2), use_container_width=True, key="shell_2_alt")

with col2_e:
    st.write("**How can the alternative configuration contribute to J = 2?**")
    st.write(
        "Just like the previous example, this alternative occupancy does not need to be interpreted as nucleons literally moving like classical vectors in space."
    )
    st.write(
        "Instead, the point is that the same two effective j = 2.5 contributions can be coupled to a smaller total value, here J = 2, as another allowed basis component."
    )
    st.write(
        "The gamma transition is best understood as a change of the many-body coupling from a J = 4 state to a J = 2 state, rather than as a literal mechanical re-orientation."
    )

with col2_f:
    st.write("**Alternative effective vector coupling**")
    st.plotly_chart(plot_3d_vectors(2.5, 2.5, 2.0, "Alternative Effective Coupling: 2.5 + 2.5 -> J = 2"), use_container_width=True, key="alt_vector_2")

st.divider()

# ==========================================
# MAIN SECTION 3: THE FINAL GROUND STATE (I=0)
# ==========================================
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
    st.plotly_chart(draw_2d_shell("Ground-State Occupancy Cartoon", num_in=4, num_out=0), use_container_width=True, key="shell_3")

with col3_b:
    st.subheader("3.2. Effective Internal Coupling Cartoon")
    st.write(
        "Here the four neutrons are shown as two cancelling pairs. "
        "Again, this is not meant literally in 3D space; it is a pedagogical way to represent strong pairwise cancellation leading to net J = 0."
    )
    st.plotly_chart(plot_internal_coupling("Cartoon: 4 Neutrons -> Effective j = 0", mode="4_neutrons"), use_container_width=True, key="internal_3")

with col3_c:
    st.subheader("3.3. Effective Vector Coupling to J = 0")
    st.write(
        "In the ground-state cartoon, the valence contributions cancel so that the total angular momentum is J = 0."
    )
    st.plotly_chart(plot_3d_vectors(0, 0, 0, "Effective Coupling: 0 + 0 -> J = 0"), use_container_width=True, key="vector_3")

st.divider()

st.caption(
    "Summary: this app is designed to explain the cascade intuitively through occupancy cartoons and effective angular-momentum coupling. "
    "It should be read as a visual guide to how total J can arise and change, not as a literal microscopic snapshot of the nucleus."
)
