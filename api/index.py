from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
import os

import db


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


# ---------------------------------------------------------
# VOLUNTEER DATA MODEL
# ---------------------------------------------------------

class Volunteer(BaseModel):
    name: str
    age: int
    gender: str
    email: str
    phone: str
    address: str = ""
    area_of_interest: str
    skills: str = ""
    availability: str


# ---------------------------------------------------------
# ADMIN LOGIN MODEL
# ---------------------------------------------------------

class AdminLogin(BaseModel):
    password: str


# ---------------------------------------------------------
# HOME / REGISTRATION PAGE
# ---------------------------------------------------------

@app.get("/")
def registration_page():
    return FileResponse(
        BASE_DIR / "templates" / "register.html"
    )


# ---------------------------------------------------------
# API TEST
# ---------------------------------------------------------

@app.get("/api")
def home():
    return {
        "message": "Volunteer Registration API is working"
    }


# ---------------------------------------------------------
# REGISTER VOLUNTEER
# ---------------------------------------------------------

@app.post("/register")
def register_volunteer(volunteer: Volunteer):

    data = volunteer.model_dump()

    try:
        result = db.add_volunteer(data)

        return {
            "success": True,
            "message": "Volunteer registered successfully!",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ---------------------------------------------------------
# ADMIN LOGIN
# ---------------------------------------------------------

@app.post("/admin/login")
def admin_login(login: AdminLogin):

    admin_password = os.getenv(
        "ADMIN_PASSWORD",
        "admin123"
    )

    if login.password != admin_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin password."
        )

    return {
        "success": True,
        "message": "Admin access granted."
    }


# ---------------------------------------------------------
# ADMIN DASHBOARD PAGE
# ---------------------------------------------------------

@app.get("/admin")
def admin_page():
    return FileResponse(
        BASE_DIR / "admin.html"
    )


# ---------------------------------------------------------
# ADMIN DATA
# ---------------------------------------------------------

@app.get("/admin/data")
def admin_data(
    x_admin_password: str = Header(default="")
):

    admin_password = os.getenv(
        "ADMIN_PASSWORD",
        "admin123"
    )

    if x_admin_password != admin_password:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized."
        )

    try:
        volunteers = db.get_all_volunteers()

        for volunteer in volunteers:
            if volunteer.get("registered_on"):
                volunteer["registered_on"] = (
                    volunteer["registered_on"].isoformat()
                )

        return {
            "success": True,
            "volunteers": volunteers
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------------------------------------------------
# DELETE ALL VOLUNTEERS
# ---------------------------------------------------------

@app.delete("/admin/delete-all")
def delete_all_volunteers(login: AdminLogin):

    admin_password = os.getenv(
        "ADMIN_PASSWORD",
        "admin123"
    )

    if login.password != admin_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin password."
        )

    try:
        db.delete_all_volunteers()

        return {
            "success": True,
            "message": "All volunteer records have been deleted."
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
```

