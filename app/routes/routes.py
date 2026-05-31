from fastapi import FastAPI 
from fastapi import Depends,HTTPException, status
from app.schemas.patient_schema import PatientRegistration,PatientLogin,PatientProfile,ProfileUpdate
from app.models.patient_model import Patient
from sqlalchemy.orm import Session
from app.database.connection import get_db
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from app.auth.jwt_handler import hash_password, verify_password, create_access_token, get_current_user
from app.database.connection import engine, Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="patient/login")

@app.post("/patient/registration")
async def reg_patient(patient: PatientRegistration, db: Session = Depends(get_db)):
    exisiting_user= db.query(Patient).filter(Patient.email_id == patient.email_id).first()
    if exisiting_user: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    hashed_password= hash_password(patient.password)

    new_user = Patient(email_id=patient.email_id,
                password=hashed_password,
                name=patient.name,
                age= patient.age,
                gender= patient.gender, 
                phone_no= patient.phone_no
                )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"name":new_user.name,"age":new_user.age,"gender":new_user.gender,"phone_no":new_user.phone_no,"email_id":new_user.email_id}

@app.post("/patient/login")
async def login_patient(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    existing_patient=db.query(Patient).filter(Patient.email_id== form_data.username).first()
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
    access_token = create_access_token(
        {"sub": existing_patient.email_id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/patient/profile")
async def get_profile( current_user: Patient = Depends(get_current_user)):
    return {
        "name": current_user.name,
        "email": current_user.email_id,
        "phone": current_user.phone_no,
        "pic": current_user.profile_pic,
        "age":current_user.age
    }
    

@app.patch("/patient/profile/edit")
async def edit_profile(profile_data: ProfileUpdate, current_user: Patient = Depends(get_current_user),db: Session = Depends(get_db)):
    query=db.query(Patient).filter(Patient.email_id==current_user.email_id)
    user=query.first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )
    
    query.update(
        profile_data.model_dump(exclude_unset=True)
    )

    db.commit()
    db.refresh(user)

    return user


    

