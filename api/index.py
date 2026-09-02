from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import db


app = FastAPI()

templates = Jinja2Templates(directory="templates")


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
# HOME / REGISTRATION PAGE
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def registration_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
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

@app.post("/api/register")
def register_volunteer(volunteer: Volunteer):

    data = volunteer.model_dump()

    db.add_volunteer(data)

    return {
        "success": True,
        "message": f"{data['name']} has been registered successfully!"
    }


# ---------------------------------------------------------
# GET ALL VOLUNTEERS
# ---------------------------------------------------------

@app.get("/api/volunteers")
def get_volunteers():

    return db.get_all_volunteers()


# ---------------------------------------------------------
# GET STATISTICS
# ---------------------------------------------------------

@app.get("/api/stats")
def get_statistics():

    return db.get_stats()


# ---------------------------------------------------------
# DELETE ALL VOLUNTEERS
# ---------------------------------------------------------

@app.delete("/api/volunteers")
def delete_volunteers():

    db.delete_all_volunteers()

    return {
        "success": True,
        "message": "All volunteer records have been deleted."
    }

    return {
        "success": True,
        "message": "All volunteer records have been deleted."
    }
