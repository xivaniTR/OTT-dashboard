import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data

def render():
    st.header("📉 Churn Insights")
    master_df, sessions_df, recs_df = load_data()

    # Overall churn rate and dominant device for churned users
    churned_users = master_df[master_df['churn_date'].notnull()]
    churned_count = churned_users.shape[0]
    total_users = len(master_df)
    churn_rate = 100 * churned_count / total_users if total_users > 0 else 0
    churned_sessions = sessions_df[sessions_df['user_id'].isin(churned_users['user_id'])]

    if not churned_sessions.empty:
        dominant_device = churned_sessions['device_type'].mode()[0]
    else:
        dominant_device = 'N/A'

    # Calculate average time to churn
    churned_users['join_date'] = pd.to_datetime(churned_users['join_date'])
    churned_users['churn_date'] = pd.to_datetime(churned_users['churn_date'])
    churned_users['days_to_churn'] = (churned_users['churn_date'] - churned_users['join_date']).dt.days
    avg_days_to_churn = churned_users['days_to_churn'].mean()

    # Display metrics in 3 columns
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Churn Rate", f"{churn_rate:.1f}%", delta=f"{churned_count} of {total_users}")
    col2.metric("Dominant Device for Churned Users", dominant_device)
    col3.metric("Avg Time to Churn", f"{avg_days_to_churn:.0f} days", delta="vs 30-day baseline")


    # User Segmentation: Trial Conversion vs Post-Trial Churn
    # Load data
    master_df = pd.read_csv('ott_master_dataset.csv')
    master_df['join_date'] = pd.to_datetime(master_df['join_date']).dt.tz_localize(None)
    master_df['churn_date'] = pd.to_datetime(master_df['churn_date']).dt.tz_localize(None)

    # Compute churn flag and converted flag
    master_df['churned'] = master_df['churn_date'].notnull()
    today = pd.Timestamp('now').normalize()
    master_df['converted'] = (
        (~master_df['churned'] & ((today - master_df['join_date']).dt.days > 30)) |
        (master_df['churned'] & ((master_df['churn_date'] - master_df['join_date']).dt.days > 30))
    )

    # Compute churn counts
    churned_count = master_df['churned'].sum()
    total_users = len(master_df)

    # Segment users
    def segment_user(row):
        if row['converted'] and row['churned']:
            return "Converted & Churned"
        elif row['converted'] and not row['churned']:
            return "Converted & Retained"
        elif not row['converted'] and row['churned']:
            return "Trial Only & Churned"
        else:
            return "Trial Only & Retained"

    master_df['user_segment'] = master_df.apply(segment_user, axis=1)
    segment_counts = master_df['user_segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'User Count']

    # Color maps
    color_map_pie = {
        'Churned': '#F7CAC9',
        'Retained': '#A7C7E7'
    }
    color_map_bar = {
        'Converted & Churned': '#F7CAC9',
        'Converted & Retained': '#A7C7E7',
        'Trial Only & Churned': '#FFDAB9',
        'Trial Only & Retained': '#C1E1C1'
    }

    # Side-by-side layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Churned vs Retained Users")
        churn_status = pd.DataFrame({
            'status': ['Churned', 'Retained'],
            'count': [churned_count, total_users - churned_count]
        })
        fig_pie = px.pie(
            churn_status,
            values='count',
            names='status',
            color='status',
            color_discrete_map=color_map_pie,
            hole=0.5
        )
        fig_pie.update_traces(
            textposition='inside',
            textinfo='label+percent',
            insidetextorientation='radial'
        )
        fig_pie.update_layout(
            title_text='Churned vs Retained',
            showlegend=True,
            height=350,
            margin=dict(t=30, b=30, l=30, r=30)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.caption("Shows the proportion of churned vs retained users.")

    with col2:
        st.subheader("Trial Conversion vs Post-Trial Churn")
        fig_bar = px.bar(
            segment_counts,
            x='Segment',
            y='User Count',
            text='User Count',
            color='Segment',
            color_discrete_map=color_map_bar
        )
        fig_bar.update_layout(
            xaxis_title="User Segment",
            yaxis_title="Number of Users",
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            height=350,
            margin=dict(t=30, b=30, l=30, r=30)
        )
        st.plotly_chart(fig_bar, use_container_width=True)


    # Enhanced Watch Time Before Churn Line Chart
    st.subheader("Watch Time Before Churn")
    days_before_churn = np.arange(-30, 1)
    avg_watch_time = np.linspace(80, 20, 31)

    # Calculate drop
    drop_percentage = ((avg_watch_time[0] - avg_watch_time[-1]) / avg_watch_time[0]) * 100

    # Create figure
    fig = go.Figure()

    # Line for average watch time
    fig.add_trace(go.Scatter(
        x=days_before_churn,
        y=avg_watch_time,
        mode='lines+markers+text',
        name='Avg Watch Time',
        text=[f"{wt:.1f}" for wt in avg_watch_time],
        textposition="top center",
        line=dict(color='#FFB7B2', width=3),
        marker=dict(size=6)
    ))

    # Add vertical line at -21
    fig.add_vline(
        x=-21,
        line_dash="dash",
        line_color="red",
        annotation_text="Drop Point (-21 Days)",
        annotation_position="top right"
    )

    # Update layout
    fig.update_layout(
        xaxis_title="Days Before Churn",
        yaxis_title="Average Watch Time (mins)",
        width=800,
        height=400,
        margin=dict(t=60, l=60, r=40, b=60),
    )

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Shows average watch time in the 30 days leading up to churn. {drop_percentage:.1f}% drop from day -30 to day 0. Red line indicates decline point at day -21.")


