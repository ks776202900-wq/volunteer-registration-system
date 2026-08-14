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
    st.subheader("Volunteer Dashboard")

    stats = db.get_stats()
    volunteers = db.get_all_volunteers()

    if stats["total"] == 0:
        st.info("No volunteers registered yet. Add some from the Register page.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Volunteers", stats["total"])
        c2.metric("Areas Covered", len(stats["by_interest"]))
        c3.metric("Latest Registration", volunteers[0]["registered_on"].strftime("%d-%m-%Y %H:%M"))

        df = pd.DataFrame(volunteers)

        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(
                pd.DataFrame(stats["by_interest"]),
                x="area_of_interest", y="c",
                labels={"area_of_interest": "Area of Interest", "c": "Volunteers"},
                title="Volunteers by Area of Interest",
            )
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = px.pie(
                pd.DataFrame(stats["by_gender"]),
                names="gender", values="c",
                title="Volunteers by Gender",
            )
            st.plotly_chart(fig2, use_container_width=True)

        df["registered_on"] = pd.to_datetime(df["registered_on"])
        trend = df.groupby(df["registered_on"].dt.date).size().reset_index(name="count")
        fig3 = px.line(trend, x="registered_on", y="count", markers=True,
                        title="Registrations Over Time",
                        labels={"registered_on": "Date", "count": "New Registrations"})
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("### All Registrations")
        search = st.text_input("Search by name, email, or area of interest")
        if search:
            mask = df.apply(lambda r: search.lower() in str(r.values).lower(), axis=1)
            df = df[mask]
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.download_button(
            "Download as CSV",
            df.to_csv(index=False).encode("utf-8"),
            "volunteers_export.csv",
            "text/csv",
        )
