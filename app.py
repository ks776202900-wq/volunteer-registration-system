"""
app.py — Volunteer Registration System
Admin Dashboard

This app is for administrators only.
Volunteer registration is handled separately by public_app.py.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

import db


# ---------------------------------------------------------------- PAGE SETUP

st.set_page_config(
    page_title="Volunteer Admin Dashboard",
    layout="wide"
)

db.init_db()


# ---------------------------------------------------------------- ADMIN LOGIN

st.sidebar.title("Admin Panel")

admin_password = st.sidebar.text_input(
    "Admin Password",
    type="password"
)

if "ADMIN_PASSWORD" not in st.secrets:
    st.error(
        "Admin password is not configured. "
        "Please add ADMIN_PASSWORD to Streamlit Secrets."
    )
    st.stop()

if admin_password != st.secrets["ADMIN_PASSWORD"]:

    st.title("Admin Dashboard")

    st.info(
        "Please enter the admin password in the sidebar "
        "to access the dashboard."
    )

    st.stop()


# ---------------------------------------------------------------- ADMIN DASHBOARD

st.sidebar.success("Admin access granted")
# ---------------------------------------------------------------- CLEAR TEST DATA

st.sidebar.divider()

st.sidebar.subheader("⚠️ Data Management")

if st.sidebar.button("Delete All Volunteer Records"):
    st.session_state["confirm_delete"] = True

if st.session_state.get("confirm_delete", False):

    st.warning(
        "⚠️ This will permanently delete ALL volunteer registration records."
    )

    if st.button("Yes, Delete All Records"):
        db.delete_all_volunteers()
        st.session_state["confirm_delete"] = False
        st.success("All volunteer records have been deleted.")
        st.rerun()

    if st.button("Cancel"):
        st.session_state["confirm_delete"] = False
        st.rerun()
st.title("Volunteer Admin Dashboard")
st.caption("Overview and analytics of registered volunteers")


stats = db.get_stats()
volunteers = db.get_all_volunteers()


# ---------------------------------------------------------------- NO RECORDS

if stats["total"] == 0:

    st.info(
        "No volunteers registered yet."
    )

    st.stop()


# ---------------------------------------------------------------- DATA

df = pd.DataFrame(volunteers)

df["registered_on"] = pd.to_datetime(
    df["registered_on"]
)


# ---------------------------------------------------------------- KPI CARDS

total = len(df)

areas = df["area_of_interest"].nunique()

genders = df["gender"].nunique()

latest = df["registered_on"].max().strftime(
    "%d-%m-%Y"
)


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Volunteers",
    total
)

c2.metric(
    "Areas Covered",
    areas
)

c3.metric(
    "Gender Categories",
    genders
)

c4.metric(
    "Latest Registration",
    latest
)


st.divider()


# ---------------------------------------------------------------- FILTERS

st.subheader("Filters")

f1, f2, f3 = st.columns(3)


with f1:

    area_options = ["All"] + sorted(
        df["area_of_interest"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_area = st.selectbox(
        "Area of Interest",
        area_options
    )


with f2:

    gender_options = ["All"] + sorted(
        df["gender"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_gender = st.selectbox(
        "Gender",
        gender_options
    )


with f3:

    availability_options = ["All"] + sorted(
        df["availability"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_availability = st.selectbox(
        "Availability",
        availability_options
    )


# ---------------------------------------------------------------- APPLY FILTERS

filtered_df = df.copy()


if selected_area != "All":

    filtered_df = filtered_df[
        filtered_df["area_of_interest"] == selected_area
    ]


if selected_gender != "All":

    filtered_df = filtered_df[
        filtered_df["gender"] == selected_gender
    ]


if selected_availability != "All":

    filtered_df = filtered_df[
        filtered_df["availability"] == selected_availability
    ]


st.caption(
    f"Showing {len(filtered_df)} of {len(df)} volunteers"
)


st.divider()


# ---------------------------------------------------------------- CHARTS

st.subheader("📈 Volunteer Analytics")

col1, col2 = st.columns(2)


# ----------------------------- AREA OF INTEREST CHART

with col1:

    interest_data = (
        filtered_df["area_of_interest"]
        .value_counts()
        .reset_index()
    )

    interest_data.columns = [
        "area_of_interest",
        "count"
    ]

    fig1 = px.bar(
        interest_data,
        x="area_of_interest",
        y="count",
        title="Volunteers by Area of Interest",
        labels={
            "area_of_interest": "Area of Interest",
            "count": "Volunteers"
        }
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )


# ----------------------------- GENDER CHART

with col2:

    gender_data = (
        filtered_df["gender"]
        .value_counts()
        .reset_index()
    )

    gender_data.columns = [
        "gender",
        "count"
    ]

    fig2 = px.pie(
        gender_data,
        names="gender",
        values="count",
        title="Volunteers by Gender"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# ---------------------------------------------------------------- REGISTRATION TREND

trend = (
    filtered_df
    .groupby(
        filtered_df["registered_on"].dt.date
    )
    .size()
    .reset_index(name="count")
)


fig3 = px.line(
    trend,
    x="registered_on",
    y="count",
    markers=True,
    title="Registrations Over Time",
    labels={
        "registered_on": "Date",
        "count": "New Registrations"
    }
)


st.plotly_chart(
    fig3,
    use_container_width=True
)


st.divider()


# ---------------------------------------------------------------- VOLUNTEER RECORDS

st.subheader("Volunteer Records")


search = st.text_input(
    "🔍 Search by name, email, phone, or area of interest"
)


display_df = filtered_df.copy()


if search:

    mask = display_df.apply(
        lambda row:
        search.lower() in str(row.values).lower(),
        axis=1
    )

    display_df = display_df[mask]


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------------- DOWNLOAD CSV

st.download_button(
    "Download Volunteer Records as CSV",
    data=display_df.to_csv(index=False).encode("utf-8"),
    file_name="volunteers_export.csv",
    mime="text/csv"
)

