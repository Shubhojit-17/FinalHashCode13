"""
EADA Pro Dashboard Launcher
Starts both the main system and the Streamlit dashboard in parallel
"""

import subprocess
import sys
import os
import time
from pathlib import Path
import signal

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class DashboardLauncher:
    """Manages launching main system and dashboard"""
    
    def __init__(self):
        self.system_process = None
        self.dashboard_process = None
        self.python_exe = sys.executable
    
    def start(self):
        """Start both processes"""
        print("=" * 60)
        print("🎯 EADA Pro - Starting Dashboard System")
        print("=" * 60)
        
        # Start main system first
        print("\n📹 Starting main EADA Pro system...")
        self.system_process = subprocess.Popen(
            [self.python_exe, "src/main.py"],
            cwd=project_root,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        
        # Wait a bit for system to initialize
        print("⏳ Waiting for system initialization (3 seconds)...")
        time.sleep(3)
        
        # Start Streamlit dashboard
        print("\n📊 Starting Streamlit dashboard...")
        dashboard_path = project_root / "dashboard" / "app.py"
        
        # Check if dashboard file exists
        if not dashboard_path.exists():
            print(f"❌ Dashboard file not found: {dashboard_path}")
            print("Creating simple dashboard...")
            self._create_simple_dashboard()
            dashboard_path = project_root / "dashboard" / "app.py"
        
        self.dashboard_process = subprocess.Popen(
            [
                self.python_exe, "-m", "streamlit", "run",
                str(dashboard_path),
                "--server.headless", "true",
                "--theme.base", "dark",
                "--theme.primaryColor", "#00D9FF",
                "--theme.backgroundColor", "#0A1628",
                "--theme.secondaryBackgroundColor", "#1A2640",
                "--theme.textColor", "#FFFFFF"
            ],
            cwd=project_root
        )
        
        print("\n✅ Both processes started successfully!")
        print("\n" + "=" * 60)
        print("📊 Dashboard URL: http://localhost:8501")
        print("📹 Main system running in separate console")
        print("=" * 60)
        print("\n💡 Press Ctrl+C to stop both processes\n")
        
        # Keep script running and monitor processes
        try:
            while True:
                time.sleep(1)
                
                # Check if processes are still running
                if self.system_process.poll() is not None:
                    print("\n⚠️  Main system process ended")
                    break
                    
                if self.dashboard_process.poll() is not None:
                    print("\n⚠️  Dashboard process ended")
                    break
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down...")
            self.stop()
    
    def _create_simple_dashboard(self):
        """Create a simple dashboard if it doesn't exist"""
        dashboard_dir = project_root / "dashboard"
        dashboard_dir.mkdir(exist_ok=True)
        
        dashboard_content = '''"""
EADA Pro - Simple Dashboard
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="EADA Pro Dashboard",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 EADA Pro Dashboard")
st.markdown("---")

# Load metrics
def load_metrics():
    metrics_file = Path("data/dashboard/metrics.json")
    if metrics_file.exists():
        try:
            with open(metrics_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

metrics = load_metrics()

if metrics:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Faces", metrics.get('face_count', 0))
    
    with col2:
        st.metric("⚡ FPS", f"{metrics.get('fps', 0):.1f}")
    
    with col3:
        st.metric("☀️ Brightness", f"{metrics.get('brightness', 0)}%")
    
    with col4:
        st.metric("🔊 Volume", f"{int(metrics.get('volume', 0) * 100)}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 System Info")
        st.write(f"Distance: {metrics.get('distance', 0):.1f} cm")
        st.write(f"Gestures: {'✅ Enabled' if metrics.get('gestures_enabled') else '❌ Disabled'}")
        st.write(f"Media: {'⏸️ Paused' if metrics.get('media_paused') else '▶️ Playing'}")
    
    with col2:
        st.subheader("🎮 Gesture Counts")
        if 'gesture_counts' in metrics:
            for gesture, count in metrics['gesture_counts'].items():
                st.write(f"{gesture}: {count}")
else:
    st.info("⏳ Waiting for system data...")

# Auto refresh
if st.button("🔄 Refresh"):
    st.rerun()

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
'''
        
        with open(dashboard_dir / "app.py", 'w', encoding='utf-8') as f:
            f.write(dashboard_content)
        
        print("Created simple dashboard")
    
    def stop(self):
        """Stop both processes"""
        print("Stopping dashboard...")
        if self.dashboard_process:
            try:
                self.dashboard_process.terminate()
                self.dashboard_process.wait(timeout=5)
            except:
                if self.dashboard_process.poll() is None:
                    self.dashboard_process.kill()
        
        print("Stopping main system...")
        if self.system_process:
            try:
                self.system_process.terminate()
                self.system_process.wait(timeout=5)
            except:
                if self.system_process.poll() is None:
                    self.system_process.kill()
        
        print("✅ All processes stopped")


def main():
    """Main entry point"""
    launcher = DashboardLauncher()
    try:
        launcher.start()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        launcher.stop()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
