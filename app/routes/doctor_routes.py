from fastapi import FastAPI,Depends,HTTPException, status
from app.database.connection import get_db
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.admin_model import Doctor
from app.auth.jwt_handler import hash_password, verify_password, create_access_token,get_current_doctor
from app.database.connection import engine, Base
from app.schemas.doctor_schema import ProfileUpdate
app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post("/doctor/login")
async def doctor_login(form_data: OAuth2PasswordRequestForm= Depends(), db: Session= Depends(get_db)):
    doctor = db.query(Doctor).filter(form_data.username == Doctor.email_id).first()

    if not doctor:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")
    

    if not verify_password(form_data.password, doctor.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    
    access_token = create_access_token({"sub": doctor.email_id} )

    return { "access_token": access_token, "token_type": "bearer"}

@app.get("/doctor/profile")
async def get_profile( current_user: Doctor = Depends(get_current_doctor)):
    return {
        "name": current_user.name,
        "email_id": current_user.email_id,
        "gender":current_user.gender,
        "phone_no": current_user.phone_no,
        "profile_pic": current_user.profile_pic,
        "experience":current_user.experience,
        "specialization":current_user.specialization,
        "education":current_user.education
    }


@app.post("/doctor/update-profile")
async def update_profile(profile_data: ProfileUpdate, current_doctor: Doctor = Depends(get_current_doctor), db: Session= Depends(get_db)):
    query=db.query(Doctor).filter(Doctor.email_id==current_doctor.email_id)
    user=query.first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )
    
    query.update(
        profile_data.model_dump(exclude_unset=True)
    )

    db.commit()
    db.refresh(user)

    return {"message" : "Updated profile succssefully" , "User": user}