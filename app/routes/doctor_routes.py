from fastapi import FastAPI,Depends,HTTPException, status
from app.database.connection import get_db
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.admin_model import Doctor
from app.auth.jwt_handler import hash_password, verify_password, create_access_token
app = FastAPI()

@app.post("/doctor-login")
async def doctor_login(form_data: OAuth2PasswordRequestForm= Depends(), db: Session= Depends(get_db)):
    doctor = db.query(Doctor).filter(form_data.username == Doctor.email_id).first()

    if not doctor:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")
    

    if not verify_password(form_data.password, doctor.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    
    access_token = create_access_token({"sub": doctor.email_id} )

    return { "access_token": access_token, "token_type": "bearer"}