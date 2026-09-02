from fastapi import FastAPI
from pydantic import BaseModel
import db

app = FastAPI()


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


@app.get("/api")
def home():
    return {
        "message": "Volunteer Registration API is working"
    }


@app.post("/api/register")
def register_volunteer(volunteer: Volunteer):
    data = volunteer.model_dump()

    db.add_volunteer(data)

    return {
        "success": True,
        "message": f"{data['name']} has been registered successfully!"
    }


@app.get("/api/volunteers")
def get_volunteers():
    return db.get_all_volunteers()


@app.get("/api/stats")
def get_statistics():
    return db.get_stats()


@app.delete("/api/volunteers")
def delete_volunteers():
    db.delete_all_volunteers()

    return {
        "success": True,
        "message": "All volunteer records have been deleted."
    }
