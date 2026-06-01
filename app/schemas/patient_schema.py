from fastapi import FastAPI 
from pydantic import BaseModel
from typing import Optional

app = FastAPI() 

class PatientRegistration(BaseModel): 
    name: str 
    age: int
    gender: str
    phone_no: str 
    email_id: str
    password: str
    
class PatientLogin(BaseModel): 
    email_id: str
    password: str

class PatientProfile(BaseModel):
    name: str
    pic: str
    email_id: str
    phone_no: str
   
class ProfileUpdate(BaseModel):
    name: str | None = None
    email_id: str | None = None
    age: int | None = None
    phone_no: str | None = None
    profile_pic: str | None = None

class ChangePassword(BaseModel):
    password: str
    new_password: str
    confirm_password: str