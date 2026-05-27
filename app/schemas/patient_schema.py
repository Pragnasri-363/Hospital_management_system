from fastapi import FastAPI
from pydantic import BaseModel

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
   
