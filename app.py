"""
app.py — Volunteer Registration System (Streamlit UI)

Two views in one app:
  1. Register  — data entry form, validated and saved to SQLite
  2. Dashboard — live analysis of everyone registered so far

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px

import db

st.set_page_config(page_title="Volunteer Registration", layout="wide")
db.init_db()

st.title("🙋 Volunteer Registration System")

page = st.sidebar.radio("Navigate", ["Register", "Dashboard"])

AREAS_OF_INTEREST = [
    "Education", "Healthcare", "Environment", "Disaster Relief",
    "Elderly Care", "Animal Welfare", "Event Support", "Other"
]
AVAILABILITY = ["Weekdays", "Weekends", "Evenings", "Flexible / Anytime"]

# ---------------------------------------------------------------- REGISTER
if page == "Register":
    st.subheader("New Volunteer Registration")

    with st.form("registration_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
            age = st.number_input("Age *", min_value=15, max_value=100, step=1)
            gender = st.selectbox("Gender *", ["Male", "Female", "Other", "Prefer not to say"])
            email = st.text_input("Email *")
        with col2:
            phone = st.text_input("Phone *")
            area = st.selectbox("Area of Interest *", AREAS_OF_INTEREST)
            availability = st.selectbox("Availability *", AVAILABILITY)
            skills = st.text_input("Skills (optional)")
        address = st.text_area("Address (optional)")

        submitted = st.form_submit_button("Register")

        if submitted:
            data = {
                "name": name, "age": age, "gender": gender, "email": email,
                "phone": phone, "address": address, "area_of_interest": area,
                "skills": skills, "availability": availability,
            }
            try:
                db.add_volunteer(data)
                st.success(f"✅ {name} has been registered successfully!")
            except db.ValidationError as e:
                st.error(f"⚠️ {e}")


# ---------------------------------------------------------------- DASHBOARD
else:
    st.title("📊 Volunteer Dashboard")
    st.caption("Overview and analytics of registered volunteers")

    stats = db.get_stats()
    volunteers = db.get_all_volunteers()

    if stats["total"] == 0:
        st.info("No volunteers registered yet. Add some from the Register page.")
    else:
        df = pd.DataFrame(volunteers)
        df["registered_on"] = pd.to_datetime(df["registered_on"])

        # ================================================================
        # KPI CARDS
        # ================================================================
        total = len(df)
        areas = df["area_of_interest"].nunique()
        genders = df["gender"].nunique()
        latest = df["registered_on"].max().strftime("%d-%m-%Y")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("👥 Total Volunteers", total)
        c2.metric("📍 Areas Covered", areas)
        c3.metric("⚧ Gender Categories", genders)
        c4.metric("📅 Latest Registration", latest)

        st.divider()

        # ================================================================
        # FILTERS
        # ================================================================
        st.subheader("🔎 Filters")

        f1, f2, f3 = st.columns(3)

        with f1:
            area_options = ["All"] + sorted(
                df["area_of_interest"].dropna().unique().tolist()
            )
            selected_area = st.selectbox(
                "Area of Interest",
                area_options
            )

        with f2:
            gender_options = ["All"] + sorted(
                df["gender"].dropna().unique().tolist()
            )
            selected_gender = st.selectbox(
                "Gender",
                gender_options
            )

        with f3:
            availability_options = ["All"] + sorted(
                df["availability"].dropna().unique().tolist()
            )
            selected_availability = st.selectbox(
                "Availability",
                availability_options
            )

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

        # ================================================================
        # CHARTS
        # ================================================================
        st.subheader("📈 Volunteer Analytics")

        col1, col2 = st.columns(2)

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

        # ================================================================
        # REGISTRATION TREND
        # ================================================================
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

              # ================================================================
        # VOLUNTEER RECORDS
        # ================================================================
        st.subheader("📋 Volunteer Records")

        search = st.text_input(
            "🔍 Search by name, email, phone, or area of interest"
        )

        display_df = filtered_df.copy()

        if search:
            mask = display_df.apply(
                lambda row: search.lower() in str(row.values).lower(),
                axis=1
            )
            display_df = display_df[mask]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        # ================================================================
        # DOWNLOAD CSV
        # ================================================================
        st.download_button(
            "⬇️ Download Volunteer Records as CSV",
            data=display_df.to_csv(index=False).encode("utf-8"),
            file_name="volunteers_export.csv",
            mime="text/csv"
        )
