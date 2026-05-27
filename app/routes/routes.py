from fastapi import FastAPI 
from schemas.patient_schema import PatientRegistration,PatientLogin,PatientProfile
from models.patient_model import Patient
from sqlalchemy.orm import session


app=FastAPI()

@app.post("/patient/registration")
async def reg_patient(patient: PatientRegistration):
    return {"message": "Patient Registered Successfully",
            "Patient": patient}

@app.post("/patient/login")
async def login_patient(patient: PatientLogin):
    existing_patient=session.query(Patient).filter(patient.email_id == Patient.email_id).first()
    if existing_patient: 
        if existing_patient.password == patient.password:
            return{"Login successful"}
    else:
        return{"message": "Invalid username/password!"}

@app.get("/patient/profile")
async def profile_patient(patient: PatientProfile):
    return PatientProfile(patient=patient)
    

