import pandas as pd
import streamlit as st

def ensure_kolkata_tz(dt_series):
    if pd.api.types.is_datetime64_any_dtype(dt_series):
        if dt_series.dt.tz is not None:
            return dt_series.dt.tz_convert("Asia/Kolkata")
        else:
            return dt_series.dt.tz_localize("Asia/Kolkata")
    return dt_series

@st.cache_data(show_spinner=False)
def load_data():
    """Load and cache the three CSV files with proper timezone handling"""
    
    master_df = pd.read_csv("ott_master_dataset.csv", parse_dates=["join_date", "trial_end_date", "churn_date"])
    sessions_df = pd.read_csv("ott_sessions_dataset.csv", parse_dates=["session_date"])
    recs_df = pd.read_csv("ott_recommendation_events.csv", parse_dates=["event_date"])
    
    # Ensure session_date and other datetimes are tz-aware in Asia/Kolkata
    master_df["join_date"] = ensure_kolkata_tz(master_df["join_date"])
    master_df["trial_end_date"] = ensure_kolkata_tz(master_df["trial_end_date"])
    master_df["churn_date"] = ensure_kolkata_tz(master_df["churn_date"])
    sessions_df["session_date"] = ensure_kolkata_tz(sessions_df["session_date"])
    recs_df["event_date"] = ensure_kolkata_tz(recs_df["event_date"])
    
    return master_df, sessions_df, recs_df 