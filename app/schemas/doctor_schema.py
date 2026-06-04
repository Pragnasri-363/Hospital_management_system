from fastapi import FastAPI 
from pydantic import BaseModel

app = FastAPI()

class DoctorLogin(BaseModel):
    email_id: str
    password: str
    