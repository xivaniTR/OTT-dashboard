import streamlit as st
import pandas as pd
import altair as alt
from utils import load_data
import plotly.express as px
import plotly.graph_objects as go

def render():
    st.header("📈 Growth & Retention")
    master_df, sessions_df, recs_df = load_data()


    # Overall growth % metric and avg weekly sessions
    monthly_users = master_df.groupby(master_df['join_date'].dt.to_period('M')).size().reset_index()
    monthly_users.columns = ['month', 'new_users']
    monthly_users['month'] = pd.to_datetime(monthly_users['month'].astype(str))
    growth_pct = 100 * (monthly_users['new_users'].iloc[-1] - monthly_users['new_users'].iloc[0]) / max(1, monthly_users['new_users'].iloc[0])


    # Calculate avg weekly sessions for long-term users
    long_term_users = master_df[
        (master_df['churn_date'].isnull()) &
        (master_df['join_date'] < (pd.Timestamp.now(tz='Asia/Kolkata') - pd.DateOffset(months=12)))
    ]
    long_term_sessions = sessions_df[sessions_df['user_id'].isin(long_term_users['user_id'])]

    if not long_term_sessions.empty:
        session_stats = long_term_sessions.groupby('user_id').agg(
            total_sessions=('session_id', 'count'),
            min_date=('session_date', 'min'),
            max_date=('session_date', 'max')
        ).reset_index()
        session_stats['active_weeks'] = ((session_stats['max_date'] - session_stats['min_date']).dt.days // 7 + 1).clip(lower=1)
        session_stats['avg_sessions_per_week'] = session_stats['total_sessions'] / session_stats['active_weeks']
        avg_weekly_sessions = session_stats['avg_sessions_per_week'].mean()
    else:
        avg_weekly_sessions = None

    retained_count = master_df['churn_date'].isnull().sum()
    total_users = len(master_df)
    retention_rate = 100 * retained_count / total_users if total_users > 0 else 0


    col1, col2, col3 = st.columns(3)

    # 1. Overall Growth Rate
    col1.metric("Overall Growth in New Users", f"{growth_pct:.1f}%", delta=f"{monthly_users['new_users'].iloc[-1] - monthly_users['new_users'].iloc[0]}")

    # 2. Avg Weekly Visits for Long-Term Users
    if avg_weekly_sessions is not None:
        col2.metric("Avg Weekly Platform Visits – Loyal Users (12+ Months)", f"{avg_weekly_sessions:.2f}")
    else:
        col2.metric("Avg Weekly Platform Visits – Loyal Users (12+ Months)", "N/A")

    # 3. Overall Retention Rate
    col3.metric("Overall Retention Rate", f"{retention_rate:.1f}%", delta=f"{retained_count} of {total_users}")



    # Monthly User Signups Line Chart
    st.subheader("Monthly User Signups")
    monthly_users['month_str'] = monthly_users['month'].dt.strftime('%Y-%m')
    chart1 = alt.Chart(monthly_users).mark_line(point=True, color='#A7C7E7').encode(
        x=alt.X('month_str:N', title='Month', sort=None),
        y=alt.Y('new_users:Q', title='New Users'),
        tooltip=['month_str', 'new_users']
    ).properties(
        width=600, height=300, title="New Users by Month"
    )
    # Value labels
    text1 = alt.Chart(monthly_users).mark_text(align='center', baseline='bottom', dy=-5).encode(
        x='month_str:N', y='new_users:Q', text='new_users:Q'
    )
    st.altair_chart(chart1 + text1, use_container_width=True)
    st.caption("Shows the number of new users who joined each month.")

    # Conversion by Most-Watched Genre Bar Chart
    st.subheader("Conversion by Most-Watched Genre")
    # Step 1: Aggregate watch time per user per genre
    user_genre_watch = sessions_df.groupby(['user_id', 'content_genre'])['watch_time_min'].sum().reset_index()

    # Step 2: Get each user's most-watched genre
    user_most_watched = user_genre_watch.loc[user_genre_watch.groupby('user_id')['watch_time_min'].idxmax()]

    # Step 3: Merge with conversion status
    conversion_by_genre = pd.merge(user_most_watched, master_df[['user_id', 'converted']], on='user_id')

    # Step 4: Group by genre and conversion status
    genre_conversion = conversion_by_genre.groupby(['content_genre', 'converted']).size().reset_index()
    genre_conversion.columns = ['genre', 'converted', 'user_count']

    # Step 5: Plot with Plotly
    fig = px.bar(
        genre_conversion,
        x='genre',
        y='user_count',
        color='converted',
        barmode='stack',
        text='user_count',
        color_discrete_sequence=px.colors.qualitative.Pastel1,
        labels={'genre': 'Most-Watched Genre', 'user_count': 'User Count', 'converted': 'Converted'}
    )

    fig.update_traces(
        textposition='outside',
        textfont_size=12,
        cliponaxis=False
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis=dict(title='User Count'),
        height=500,
        margin=dict(l=40, r=40, t=60, b=100),
        legend_title_text='Converted'
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("Shows the number of users who converted vs. didn't convert, grouped by their most-watched genre.")


    # Cohort retention trend line chart
    st.subheader("Retention Trend by Year")
    # Step 1: Extract year and month from join/session dates
    master_df['cohort_year'] = master_df['join_date'].dt.year
    sessions_df['session_year'] = sessions_df['session_date'].dt.year
    sessions_df['session_month'] = sessions_df['session_date'].dt.month

    # Step 2: Compute cohort size per year
    cohort_sizes = master_df.groupby('cohort_year')['user_id'].nunique()
    retention = []

    # Step 3: For each cohort year, calculate monthly retention
    for year in cohort_sizes.index:
        cohort_users = master_df[master_df['cohort_year'] == year]['user_id']
        for month in range(1, 13):
            active_users = sessions_df[
                (sessions_df['user_id'].isin(cohort_users)) &
                (sessions_df['session_year'] == year) &
                (sessions_df['session_month'] == month)
            ]['user_id'].nunique()

            rate = 100 * active_users / cohort_sizes[year] if cohort_sizes[year] else 0
            retention.append({
                'cohort_year': str(year),
                'calendar_month': month,
                'retention_rate': round(rate, 1)
            })

    retention_df = pd.DataFrame(retention)

    # Step 4: Create Plotly line chart
    fig = px.line(
        retention_df,
        x='calendar_month',
        y='retention_rate',
        color='cohort_year',
        markers=True,
        labels={
            'calendar_month': 'Month (1 = Jan, 12 = Dec)',
            'retention_rate': 'Retention Rate (%)',
            'cohort_year': 'Cohort Year'
        }
    )

    fig.update_layout(
        xaxis=dict(dtick=1),
        hovermode='x unified',
        height=500,
        width=900,
        margin=dict(l=40, r=40, t=50, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("Each line shows how a cohort (based on join year) retained users through each month of the same year.")


    # World map/choropleth for user distribution by country
    st.subheader("User Distribution by Country")

    # Prep data
    country_counts = master_df['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'user_count']
    country_counts['country'] = country_counts['country'].replace({
        'US': 'United States',
        'UK': 'United Kingdom'
    })

    # Base choropleth map
    fig = px.choropleth(
        country_counts,
        locations="country",
        locationmode="country names",
        color="user_count",
        hover_name="country",
        color_continuous_scale="Blues",
        title="User Distribution by Country"
    )

    # Add top-N visible labels to avoid clutter
    top_countries = country_counts.head(30)

    # Get lat/lon of countries (approximate via px built-in)
    country_centers = px.choropleth(locations=top_countries['country'], locationmode='country names')
    centroids = country_centers.data[0]['locations']  # this part is just a placeholder

    # Add text as scattergeo
    label_trace = go.Scattergeo(
        locationmode='country names',
        locations=top_countries['country'],
        text=top_countries['user_count'],
        mode='text',
        textfont=dict(size=11, color='black'),
        showlegend=False,
        hoverinfo='skip'
    )

    fig.add_trace(label_trace)

    # Layout tweaks
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth'),
        margin=dict(l=0, r=0, t=40, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)


    # Gender distribution for active users
    st.subheader("Gender Distribution (Active Users)")
    active_users = master_df[master_df['churn_date'].isnull()]
    gender_counts = active_users['gender'].value_counts().reset_index()
    gender_counts.columns = ['gender', 'count']
    chart_gender = alt.Chart(gender_counts).mark_bar().encode(
        x=alt.X('gender:N', title='Gender'),
        y=alt.Y('count:Q', title='Active Users'),
        color=alt.Color('gender:N', scale=alt.Scale(scheme='pastel1'), legend=None),
        tooltip=['gender', 'count']
    ).properties(
        width=400, height=300, title="Gender Distribution (Active Users)"
    )
    # Add value labels
    text_gender = chart_gender.mark_text(align='center', baseline='bottom', dy=-2).encode(
        text='count:Q'
    )
    st.altair_chart(chart_gender + text_gender, use_container_width=True)