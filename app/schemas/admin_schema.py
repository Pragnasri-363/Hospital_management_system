from fastapi import FastAPI 
from pydantic import BaseModel

class AdminRegistration(BaseModel): 
    name: str 
    gender: str
    phone_no: str 
    email_id: str
    password: str

class AdminLogin(BaseModel): 
    email_id: str
    password: str

class AdminProfile(BaseModel):
    name: str
    pic: str
    email_id: str
    phone_no: str

class ProfileUpdate(BaseModel):
    name: str | None = None
    email_id: str | None = None
    phone_no: str | None = None
    profile_pic: str | None = None

class DoctorData(BaseModel):
    name: str 
    gender: str
    phone_no: str 
    email_id: str
    password: str
    experience: str
    education: str
    specialization: str