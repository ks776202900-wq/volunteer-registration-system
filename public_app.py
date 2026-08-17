```python
import streamlit as st
import db

st.set_page_config(
    page_title="Volunteer Registration",
    page_icon="🙋",
    layout="centered"
)

db.init_db()

st.title("🙋 Volunteer Registration")
st.write("Thank you for your interest in volunteering. Please fill in the form below.")

AREAS_OF_INTEREST = [
    "Education",
    "Healthcare",
    "Environment",
    "Disaster Relief",
    "Elderly Care",
    "Animal Welfare",
    "Event Support",
    "Other"
]

AVAILABILITY = [
    "Weekdays",
    "Weekends",
    "Evenings",
    "Flexible / Anytime"
]

with st.form("registration_form", clear_on_submit=True):

    st.subheader("Personal Information")

    name = st.text_input("Full Name *")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(
            "Age *",
            min_value=15,
            max_value=100,
            step=1
        )

    with col2:
        gender = st.selectbox(
            "Gender *",
            ["Male", "Female", "Other", "Prefer not to say"]
        )

    email = st.text_input("Email *")
    phone = st.text_input("Phone *")

    address = st.text_area("Address (optional)")

    st.subheader("Volunteer Preferences")

    area = st.selectbox(
        "Area of Interest *",
        AREAS_OF_INTEREST
    )

    availability = st.selectbox(
        "Availability *",
        AVAILABILITY
    )

    skills = st.text_input(
        "Skills (optional)"
    )

    submitted = st.form_submit_button(
        "🙋 Register as Volunteer"
    )

    if submitted:

        data = {
            "name": name,
            "age": age,
            "gender": gender,
            "email": email,
            "phone": phone,
            "address": address,
            "area_of_interest": area,
            "skills": skills,
            "availability": availability,
        }

        try:
            db.add_volunteer(data)

            st.success(
                f"✅ {name} has been registered successfully!"
            )

            st.balloons()

        except db.ValidationError as e:
            st.error(f"⚠️ {e}")

        except Exception:
            st.error(
                "Something went wrong while submitting the form. "
                "Please try again later."
            )
```
