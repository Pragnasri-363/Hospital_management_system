from fastapi import FastAPI 
from pydantic import BaseModel

app = FastAPI()

class DoctorLogin(BaseModel):
    email_id: str
    password: str

class DoctorProfile(BaseModel):
    name: str
    email_id: str
    gender: str
    phone_no: str
    experience: str
    specialization: str 
    education: str 
    profile_pic: str


class ProfileUpdate(BaseModel):
    name: str | None = None
    email_id: str | None = None
    gender: str | None = None
    phone_no: str | None = None
    experience: str | None = None
    specialization: str | None = None
    education: str | None = None
    profile_pic: str | None = None