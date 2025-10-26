"""
EADA Pro - Advanced Dashboard
Beautiful, modern interface with real-time monitoring
"""

import streamlit as st
import json
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="EADA Pro Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #0A1628 0%, #1A2640 50%, #0F1B35 100%);
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(90deg, #00D9FF 0%, #7B2FFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        text-align: center;
        padding: 20px 0;
        text-shadow: 0 0 30px rgba(0, 217, 255, 0.3);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #00D9FF !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        color: #B8C5D6 !important;
        font-weight: 500 !important;
    }
    
    /* Card styling */
    .css-1r6slb0 {
        background: linear-gradient(135deg, rgba(26, 38, 64, 0.6) 0%, rgba(15, 27, 53, 0.8) 100%);
        border: 1px solid rgba(0, 217, 255, 0.2);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F1B35 0%, #1A2640 100%);
        border-right: 2px solid rgba(0, 217, 255, 0.3);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #00D9FF 0%, #7B2FFF 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 30px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(0, 217, 255, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 217, 255, 0.6);
    }
    
    /* Divider styling */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #00D9FF 50%, transparent 100%);
        margin: 30px 0;
    }
    
    /* Info boxes */
    .stAlert {
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(123, 47, 255, 0.1) 100%);
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 10px;
        color: #FFFFFF;
    }
    
    /* Subheader styling */
    h2, h3 {
        color: #00D9FF !important;
        font-weight: 600 !important;
        text-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 5px;
    }
    
    .status-active {
        background: linear-gradient(90deg, #00FF87 0%, #00D9FF 100%);
        color: #0A1628;
    }
    
    .status-inactive {
        background: linear-gradient(90deg, #FF6B6B 0%, #FF9999 100%);
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# Load metrics function
@st.cache_data(ttl=1)
def load_metrics():
    """Load metrics from JSON file"""
    metrics_file = Path("data/dashboard/metrics.json")
    if metrics_file.exists():
        try:
            with open(metrics_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return None
    return None

# Create beautiful gauge chart
def create_gauge(value, title, max_value=100, color_scheme="cyan"):
    """Create a beautiful gauge chart"""
    if color_scheme == "cyan":
        colors = ["#00D9FF", "#0099CC", "#006699"]
    elif color_scheme == "purple":
        colors = ["#7B2FFF", "#5A1FCC", "#3D1499"]
    else:
        colors = ["#00FF87", "#00CC6E", "#009955"]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20, 'color': '#FFFFFF'}},
        number={'font': {'size': 40, 'color': colors[0]}},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': colors[1]},
            'bar': {'color': colors[0]},
            'bgcolor': "rgba(26, 38, 64, 0.3)",
            'borderwidth': 2,
            'bordercolor': colors[1],
            'steps': [
                {'range': [0, max_value * 0.33], 'color': 'rgba(0, 217, 255, 0.1)'},
                {'range': [max_value * 0.33, max_value * 0.66], 'color': 'rgba(0, 217, 255, 0.2)'},
                {'range': [max_value * 0.66, max_value], 'color': 'rgba(0, 217, 255, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "#00FF87", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#FFFFFF", 'family': "Arial"},
        height=250,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

# Create line chart for real-time data
def create_line_chart(data_points, title, color="#00D9FF"):
    """Create beautiful line chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        y=data_points,
        mode='lines+markers',
        line=dict(color=color, width=3, shape='spline'),
        marker=dict(size=8, color=color, symbol='circle',
                   line=dict(color='#FFFFFF', width=2)),
        fill='tozeroy',
        fillcolor=f'rgba(0, 217, 255, 0.2)'
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=20, color='#FFFFFF')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 38, 64, 0.3)',
        font=dict(color='#FFFFFF'),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0, 217, 255, 0.1)', zeroline=False),
        height=300,
        margin=dict(l=40, r=20, t=50, b=40),
        hovermode='x unified'
    )
    
    return fig

# Create pie chart for gestures
def create_gesture_pie(gesture_counts):
    """Create beautiful pie chart for gesture distribution"""
    if not gesture_counts or sum(gesture_counts.values()) == 0:
        return None
    
    labels = [g.replace('_', ' ').title() for g in gesture_counts.keys()]
    values = list(gesture_counts.values())
    
    colors = ['#00D9FF', '#7B2FFF', '#00FF87', '#FF6B9D', '#FFD93D', '#6BCF7F']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=colors, line=dict(color='#0A1628', width=2)),
        textinfo='label+percent',
        textfont=dict(size=14, color='#FFFFFF'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(text="Gesture Distribution", font=dict(size=20, color='#FFFFFF')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(26, 38, 64, 0.6)',
            bordercolor='rgba(0, 217, 255, 0.3)',
            borderwidth=1
        ),
        height=400,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

# Create heatmap
def create_heatmap(brightness, volume, ambient_light):
    """Create environment heatmap"""
    z = [[brightness, volume, ambient_light]]
    
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=['Brightness', 'Volume', 'Ambient Light'],
        y=['Level'],
        colorscale=[[0, '#1A2640'], [0.5, '#00D9FF'], [1, '#7B2FFF']],
        text=z,
        texttemplate='%{text}',
        textfont={"size": 20, "color": "#FFFFFF"},
        colorbar=dict(
            title="Level",
            titleside="right",
            tickmode="linear",
            tick0=0,
            dtick=25,
            thickness=15,
            len=0.7
        ),
        hovertemplate='%{x}: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text="Environment Controls", font=dict(size=20, color='#FFFFFF')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        height=250,
        margin=dict(l=40, r=100, t=50, b=40)
    )
    
    return fig

# Header with animation effect
st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <h1>🚀 EADA Pro Dashboard</h1>
    <p style='color: #B8C5D6; font-size: 1.2rem; font-weight: 300;'>
        Advanced Environment & Device Automation Platform
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    st.markdown("")
    
    auto_refresh = st.checkbox("🔄 Auto Refresh", value=True)
    refresh_rate = st.slider("Refresh Rate (seconds)", 1, 10, 2)
    
    st.markdown("---")
    st.markdown("### 📊 Dashboard Info")
    st.info("Real-time monitoring of EADA Pro system metrics, gestures, and environment controls.")
    
    st.markdown("---")
    if st.button("🔄 Manual Refresh"):
        st.rerun()
    
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; padding: 10px;'>
        <p style='color: #7B2FFF; font-size: 0.9rem;'>
            Last Updated<br>
            <strong>{datetime.now().strftime('%H:%M:%S')}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Load metrics
metrics = load_metrics()

if metrics:
    # Top metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="👥 Faces Detected",
            value=metrics.get('face_count', 0),
            delta=None
        )
    
    with col2:
        fps = metrics.get('fps', 0)
        st.metric(
            label="⚡ FPS",
            value=f"{fps:.1f}",
            delta="Good" if fps > 25 else "Low"
        )
    
    with col3:
        st.metric(
            label="📏 Distance",
            value=f"{metrics.get('distance', 0):.0f} cm",
            delta=None
        )
    
    with col4:
        brightness = metrics.get('brightness', 0)
        st.metric(
            label="☀️ Brightness",
            value=f"{brightness}%",
            delta=None
        )
    
    with col5:
        volume = int(metrics.get('volume', 0) * 100)
        st.metric(
            label="🔊 Volume",
            value=f"{volume}%",
            delta=None
        )
    
    st.markdown("---")
    
    # Status row
    st.markdown("### 📡 System Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        gestures_enabled = metrics.get('gestures_enabled', False)
        status = "active" if gestures_enabled else "inactive"
        st.markdown(f"""
        <div class='status-badge status-{status}'>
            🎮 Gestures: {'ENABLED' if gestures_enabled else 'DISABLED'}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        media_paused = metrics.get('media_paused', False)
        status = "inactive" if media_paused else "active"
        st.markdown(f"""
        <div class='status-badge status-{status}'>
            {'⏸️ Media: PAUSED' if media_paused else '▶️ Media: PLAYING'}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        current_gesture = metrics.get('current_gesture', 'None')
        if current_gesture is None:
            current_gesture = 'None'
        st.markdown(f"""
        <div class='status-badge status-active'>
            ✋ Current: {str(current_gesture).upper()}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main content area - Gauges
    st.markdown("### 📊 System Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.plotly_chart(
            create_gauge(brightness, "Brightness Level", 100, "cyan"),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            create_gauge(volume, "Volume Level", 100, "purple"),
            use_container_width=True
        )
    
    with col3:
        ambient_light = metrics.get('ambient_light', 50)
        st.plotly_chart(
            create_gauge(ambient_light, "Ambient Light", 100, "green"),
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Gesture pie chart
        gesture_counts = metrics.get('gesture_counts', {})
        if gesture_counts and sum(gesture_counts.values()) > 0:
            fig = create_gesture_pie(gesture_counts)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🎮 No gesture activity yet. Start using gestures to see distribution!")
    
    with col2:
        # Environment heatmap
        st.plotly_chart(
            create_heatmap(brightness, volume, ambient_light),
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Gesture counts details
    st.markdown("### 🎮 Gesture Activity Log")
    if gesture_counts and sum(gesture_counts.values()) > 0:
        cols = st.columns(len(gesture_counts))
        for idx, (gesture, count) in enumerate(gesture_counts.items()):
            with cols[idx]:
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(123, 47, 255, 0.1) 100%);
                    border: 1px solid rgba(0, 217, 255, 0.3);
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                '>
                    <h3 style='color: #00D9FF; margin: 0;'>{count}</h3>
                    <p style='color: #B8C5D6; margin: 5px 0 0 0;'>{gesture.replace('_', ' ').title()}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("🎮 No gesture data available yet. Start using the system!")
    
    # Live performance metrics
    st.markdown("---")
    st.markdown("### ⚡ Performance Monitor")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Create fake history for demo
        fps_history = [fps] * 20
        st.plotly_chart(
            create_line_chart(fps_history, "FPS History", "#00D9FF"),
            use_container_width=True
        )
    
    with col2:
        brightness_history = [brightness] * 20
        st.plotly_chart(
            create_line_chart(brightness_history, "Brightness History", "#7B2FFF"),
            use_container_width=True
        )
    
    with col3:
        volume_history = [volume] * 20
        st.plotly_chart(
            create_line_chart(volume_history, "Volume History", "#00FF87"),
            use_container_width=True
        )

else:
    # No data available - show beautiful placeholder
    st.markdown("""
    <div style='
        text-align: center;
        padding: 100px 20px;
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.05) 0%, rgba(123, 47, 255, 0.05) 100%);
        border: 2px dashed rgba(0, 217, 255, 0.3);
        border-radius: 20px;
        margin: 50px 0;
    '>
        <h2 style='color: #00D9FF; font-size: 3rem; margin-bottom: 20px;'>🚀</h2>
        <h2 style='color: #FFFFFF; margin-bottom: 20px;'>System Starting Up...</h2>
        <p style='color: #B8C5D6; font-size: 1.2rem; margin-bottom: 30px;'>
            Waiting for EADA Pro system to initialize and start sending data.
        </p>
        <div style='
            display: inline-block;
            padding: 15px 40px;
            background: linear-gradient(90deg, #00D9FF 0%, #7B2FFF 100%);
            border-radius: 25px;
            color: white;
            font-weight: 600;
            font-size: 1.1rem;
        '>
            ⏳ Please start the main system first
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📋 Quick Start Guide")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='padding: 20px; background: rgba(26, 38, 64, 0.6); border-radius: 10px; border: 1px solid rgba(0, 217, 255, 0.2);'>
            <h3>1️⃣ Start System</h3>
            <p style='color: #B8C5D6;'>Run the main EADA Pro application to begin capturing data.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='padding: 20px; background: rgba(26, 38, 64, 0.6); border-radius: 10px; border: 1px solid rgba(123, 47, 255, 0.2);'>
            <h3>2️⃣ Enable Gestures</h3>
            <p style='color: #B8C5D6;'>Use hand gestures to control brightness, volume, and media playback.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='padding: 20px; background: rgba(26, 38, 64, 0.6); border-radius: 10px; border: 1px solid rgba(0, 255, 135, 0.2);'>
            <h3>3️⃣ Monitor</h3>
            <p style='color: #B8C5D6;'>Watch real-time metrics and system performance on this dashboard.</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 20px; color: #7B2FFF;'>
    <p style='font-size: 0.9rem; margin: 5px;'>
        <strong>EADA Pro Dashboard</strong> | Advanced Environment & Device Automation
    </p>
    <p style='font-size: 0.8rem; color: #B8C5D6;'>
        {datetime.now().strftime('%A, %B %d, %Y')}
    </p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh logic
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
