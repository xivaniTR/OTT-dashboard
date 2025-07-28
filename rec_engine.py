import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from utils import load_data
from config import PASTEL_THEME
import plotly.graph_objects as go


def render():
    st.header("🤖 Recommendation Engine")
    
    # Load data
    master_df, sessions_df, recs_df = load_data()
    
    # Always merge recs with sessions to get device_type and genre
    merged_data = pd.merge(recs_df, sessions_df[['session_id', 'content_genre', 'device_type', 'language']], 
                          on='session_id', how='left')
    
    # CTR by Content Genre Bar Chart
    st.subheader("CTR by Content Genre")
    ctr_by_genre = merged_data.groupby('content_genre').agg({
        'clicked': 'mean'
    }).reset_index().dropna(subset=['content_genre'])
    ctr_by_genre['ctr'] = ctr_by_genre['clicked'] * 100
    ctr_by_genre = ctr_by_genre.sort_values('ctr', ascending=False)
    chart8 = alt.Chart(ctr_by_genre).mark_bar(color='#E2F0CB').encode(
        x=alt.X('content_genre:N', title='Content Genre', sort='-y'),
        y=alt.Y('ctr:Q', title='Click-Through Rate (%)'),
        tooltip=['content_genre', 'ctr']
    ).properties(
        width=600, height=400, title="CTR by Content Genre"
    )
    text8 = chart8.mark_text(align='center', baseline='bottom', dy=-5, color='black').encode(
        x='content_genre:N', y='ctr:Q', text=alt.Text('ctr:Q', format='.1f'), color=alt.value('black')
    )
    st.altair_chart(chart8 + text8, use_container_width=True)
    st.caption("Shows click-through rate by content genre, sorted by highest CTR.")
    
    # CTR by Device Type Bar Chart
    st.subheader("CTR by Device Type")
    ctr_by_device = merged_data.groupby('device_type').agg({
        'clicked': 'mean'
    }).reset_index().dropna(subset=['device_type'])
    ctr_by_device['ctr'] = ctr_by_device['clicked'] * 100
    ctr_by_device = ctr_by_device.sort_values('ctr', ascending=False)
    chart9 = alt.Chart(ctr_by_device).mark_bar(color='#CBAACB').encode(
        x=alt.X('device_type:N', title='Device Type', sort='-y'),
        y=alt.Y('ctr:Q', title='Click-Through Rate (%)'),
        tooltip=['device_type', 'ctr']
    ).properties(
        width=600, height=300, title="CTR by Device Type"
    )
    text9 = chart9.mark_text(align='center', baseline='bottom', dy=-5, color='black').encode(
        x='device_type:N', y='ctr:Q', text=alt.Text('ctr:Q', format='.1f'), color=alt.value('black')
    )
    st.altair_chart(chart9 + text9, use_container_width=True)
    st.caption("Shows click-through rate by device type, sorted by highest CTR.")
    
    # Recommendation Funnel
    st.subheader("Recommendation Funnel")

    # Step 1: Total recommendations shown
    total_recs = len(recs_df)

    # Step 2: Recommendations clicked
    clicked_recs = recs_df[recs_df['clicked'] == True]
    clicked_count = len(clicked_recs)

    # Step 3: Simulate content watched by clicked users (only rough estimate)
    # We can assume a fixed % or simulate further if there's session data
    watched_count = int(clicked_count * 0.65)  # You can change this based on heuristics

    # Create funnel data
    funnel_data = pd.DataFrame({
        'Stage': ['Recommendations Shown', 'Recommendations Clicked', 'Content Watched (est.)'],
        'Count': [total_recs, clicked_count, watched_count]
    })

    # Use Plotly funnel chart for better clarity
    fig = go.Figure(go.Funnel(
        y=funnel_data['Stage'],
        x=funnel_data['Count'],
        textinfo="value+percent initial",
        marker={"color": ['#FFE0B2', '#FFCCBC', '#FFAB91']}
    ))

    fig.update_layout(
        title="Recommendation Funnel",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("Tracks user journey from seeing recommendations to clicking and likely watching content. Watch numbers are estimated.")

    
    # CTR by Genre and Language (Top 10 Pairs)
    st.subheader("CTR by Genre and Language (Top 10 Pairs)")
    ctr_by_genre_lang = merged_data.groupby(['content_genre', 'language']).agg({
        'clicked': 'mean',
        'event_id': 'count'
    }).reset_index().dropna(subset=['content_genre', 'language'])

    ctr_by_genre_lang['ctr'] = ctr_by_genre_lang['clicked'] * 100
    top_pairs = ctr_by_genre_lang.nlargest(10, 'event_id')

    # Plotly bar chart with grouped bars
    fig = px.bar(
        top_pairs,
        x='content_genre',
        y='ctr',
        color='language',
        text=top_pairs['ctr'].round(1).astype(str) + '%',
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_traces(
        textposition='outside',
        marker_line_width=1
    )

    fig.update_layout(
        xaxis_title="Genre",
        yaxis_title="Click-Through Rate (%)",
        height=450,
        width=700,
        margin=dict(l=20, r=20, t=60, b=80)
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("Shows click-through rate by genre and language for the top 10 pairs by recommendation volume.") 