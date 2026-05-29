from fastapi import FastAPI 
from fastapi import Depends,HTTPException, status
from app.schemas.patient_schema import PatientRegistration,PatientLogin,PatientProfile
from app.models.patient_model import Patient
from sqlalchemy.orm import Session
from app.database.connection import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.jwt_handler import hash_password, verify_password, create_access_token

app = FastAPI()

@app.post("/patient/registration")
async def reg_patient(patient: PatientRegistration, db: Session = Depends(get_db)):
    exisiting_user= db.query(Patient).filter(patient.email_id == Patient.email_id).first()
    if exisiting_user: 
        return HTTPException{status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"}

    hashed_password= hash_password(patient.password)

    new_user = PatientRegistration(email=patient.email_id,
                password=hashed_password,
                name=patient.name,
                age= patient.age,
                gender= patient.gender, 
                phone_no= patient.phone_no
                )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"Name":new_user.name,"Age":new_user.age,"Gender":new_user.gender,"Phone_no":new_user.phone_no,"Email_id":new_user.email_id}

@app.post("/patient/login")
async def login_patient(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    existing_patient=db.query(Patient).filter(form_data.email_id == Patient.email_id).first()
    if not existing_patient: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password",
        )
    
    hashed_password= hash_password(existing_patient.password)

    if not verify_password(form_data.password, existing_patient.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    return {
        "access_token": create_access_token(user.email),
        ###"refresh_token": create_refresh_token(user.email),###
    }

@app.get("/patient/profile/fetch")
async def profile_patient(patient: PatientProfile= Depends(get_db)):
    return (PatientProfile)

@app.post("/paient/profile/update")
async def profile_update(patient:PatientProfile):
    return (

   )

    

