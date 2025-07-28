import streamlit as st
from growth_and_retention import render as render_growth
from consumption import render as render_consumption
from rec_engine import render as render_rec
from churn_story import render as render_churn

# Page configuration
st.set_page_config(
    page_title="OTT Wrapped – Business View",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("OTT KPIs – Business View")
st.markdown("---")

# Sidebar navigation
st.sidebar.title("📋 Dashboard Sections")
st.sidebar.markdown("Select a section to explore:")

# Navigation options
section = st.sidebar.radio(
    "Choose Section:",
    [
        "📈 Growth & Retention",
        "🎬 Consumption Patterns", 
        "🤖 Recommendation Engine",
        "📉 Churn Insights"
    ],
    index=0
)

# Render the selected section
if section == "📈 Growth & Retention":
    render_growth()
elif section == "🎬 Consumption Patterns":
    render_consumption()
elif section == "🤖 Recommendation Engine":
    render_rec()
elif section == "📉 Churn Insights":
    render_churn()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Data Source:** OTT Platform Analytics")
st.sidebar.markdown("**Timezone:** Asia/Kolkata") 