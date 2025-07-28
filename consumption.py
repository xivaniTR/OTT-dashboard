import streamlit as st
import pandas as pd
import altair as alt
from utils import load_data
import plotly.express as px
import numpy as np

def render():
    st.header("🎬 Consumption Patterns")
    master_df, sessions_df, recs_df = load_data()

    # Metrics: Most Watched Genre, Most Watched Language, Longest Watch Session
    most_watched_genre = sessions_df.groupby('content_genre')['watch_time_min'].sum().idxmax()
    most_watched_genre_val = sessions_df.groupby('content_genre')['watch_time_min'].sum().max()
    most_watched_language = sessions_df.groupby('language')['watch_time_min'].sum().idxmax()
    most_watched_language_val = sessions_df.groupby('language')['watch_time_min'].sum().max()
    longest_session = sessions_df['watch_time_min'].max()

    col1, col2, col3 = st.columns(3)
    col1.metric("Most Watched Genre", most_watched_genre, f"{most_watched_genre_val:.0f} min")
    col2.metric("Most Watched Language", most_watched_language, f"{most_watched_language_val:.0f} min")
    col3.metric("Longest Watch Session", f"{longest_session:.0f} min")

    # Content Consumption by Genre and  Pie Chart: Content Consumption by Language
    # Grouped data
    genre_watch_time = sessions_df.groupby('content_genre')['watch_time_min'].sum().reset_index()
    genre_watch_time = genre_watch_time.sort_values('watch_time_min', ascending=False)

    lang_watch_time = sessions_df.groupby('language')['watch_time_min'].sum().reset_index()
    lang_watch_time = lang_watch_time.sort_values('watch_time_min', ascending=False)

    # Layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Content Consumption by Genre")
        fig_genre = px.pie(
            genre_watch_time,
            names="content_genre",
            values="watch_time_min",
            title="Watch Time by Genre",
            hole=0.4,
        )
        fig_genre.update_traces(
            textinfo='label+percent',
            textposition='outside',
            pull=[0.02] * len(genre_watch_time),
            marker=dict(line=dict(color='white', width=1))
        )
        fig_genre.update_layout(
            height=350,
            margin=dict(t=30, b=30, l=30, r=30)
        )
        st.plotly_chart(fig_genre, use_container_width=True)
        st.caption("Shows which genre was watched the most based on total watch time.")

    with col2:
        st.subheader("Content Consumption by Language")
        fig_lang = px.pie(
            lang_watch_time,
            names="language",
            values="watch_time_min",
            title="Watch Time by Language",
            hole=0.4,
        )
        fig_lang.update_traces(
            textinfo='label+percent',
            textposition='outside',
            pull=[0.02] * len(lang_watch_time),
            marker=dict(line=dict(color='white', width=1))
        )
        fig_lang.update_layout(
            height=350,
            margin=dict(t=30, b=30, l=30, r=30)
        )
        st.plotly_chart(fig_lang, use_container_width=True)
        st.caption("Shows the distribution of content consumption by language.")

    # Combined Line Chart: Average Watch Time by Hour and Weekday
    st.subheader("Average Watch Time by Hour and Weekday")

    # Extract hour and weekday
    sessions_df['hour'] = sessions_df['session_date'].dt.hour
    sessions_df['weekday'] = sessions_df['session_date'].dt.day_name()

    # Group and average
    hour_weekday_watch = sessions_df.groupby(['hour', 'weekday'])['watch_time_min'].mean().reset_index()

    # Enforce weekday order
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hour_weekday_watch['weekday'] = pd.Categorical(hour_weekday_watch['weekday'], categories=weekday_order, ordered=True)

    # Plotly line chart
    fig = px.line(
        hour_weekday_watch,
        x='hour',
        y='watch_time_min',
        color='weekday',
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    # Tweak layout
    fig.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title="Average Watch Time (mins)",
        legend_title="Weekday",
        width=800,
        height=450,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("Shows average watch time per hour, with separate lines for each weekday.")

    # Average Watch Time by Device Type Bar Chart
    st.subheader("Average Watch Time by Device")
    device_watch_time = sessions_df.groupby('device_type')['watch_time_min'].mean().reset_index()
    chart6 = alt.Chart(device_watch_time).mark_bar(color='#FFDAC1').encode(
        x=alt.X('device_type:N', title='Device Type'),
        y=alt.Y('watch_time_min:Q', title='Average Watch Time (mins)'),
        tooltip=['device_type', 'watch_time_min']
    ).properties(
        width=600, height=300, title="Average Watch Time by Device Type"
    )
    text6 = chart6.mark_text(align='center', baseline='bottom', dy=-5, color='black').encode(
        x='device_type:N', y='watch_time_min:Q', text=alt.Text('watch_time_min:Q', format='.1f'), color=alt.value('black')
    )
    st.altair_chart(chart6 + text6, use_container_width=True)
    st.caption("Shows average watch time by device type.")

    # Stacked Bar Chart: Watch Time by Genre and Device
    st.subheader("Watch Time by Genre and Device")

    # Group data
    genre_device_watch = sessions_df.groupby(['content_genre', 'device_type'])['watch_time_min'].sum().reset_index()
    genre_device_watch = genre_device_watch.sort_values('watch_time_min', ascending=False)

    # Create Plotly chart
    fig = px.bar(
        genre_device_watch,
        x="content_genre",
        y="watch_time_min",
        color="device_type",
        text="watch_time_min",  # ✅ label values directly
        barmode="stack",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # Format layout and text
    fig.update_traces(
        texttemplate='%{text:,}',              # ✅ comma-separated formatting
        textposition='inside',                 # ✅ keeps it inside the bars
        insidetextanchor='middle',
        textfont=dict(color='black', size=11), # ✅ readable and compact
        hovertemplate="<b>%{x}</b><br>Device: %{legendgroup}<br>Watch Time: %{y:,} mins"
    )

    fig.update_layout(
        xaxis_title="Genre",
        yaxis_title="Watch Time (mins)",
        legend_title="Device Type",
        uniformtext_minsize=10,
        uniformtext_mode='hide',  # hides labels that won’t fit cleanly
        width=850,
        height=500
    )

    # Render
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Shows watch time by genre split across different device types.")