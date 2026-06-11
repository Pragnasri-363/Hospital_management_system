from fastapi import FastAPI,Depends,HTTPException, status
from app.database.connection import get_db
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.admin_model import Doctor
from app.models.doctor_model import Availability
from app.auth.jwt_handler import hash_password, verify_password, create_access_token,get_current_doctor
from app.database.connection import engine, Base
from app.schemas.doctor_schema import ProfileUpdate,DoctorAvailability
from datetime import date,time,timedelta,datetime

app = FastAPI()

Base.metadata.create_all(bind=engine)

async def doctor_login(form_data: OAuth2PasswordRequestForm= Depends(), db: Session= Depends(get_db)):

    doctor = db.query(Doctor).filter(Doctor.email_id == form_data.username).first()
    
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


def time_slot_generator(start_time: time, end_time: time):
    slots=[]
    start = datetime.combine(datetime.today().date(), start_time)

    end = datetime.combine(datetime.today().date(), end_time)

    if start >= end:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start time must be before than end time")
    
    while start < end:
        slot = start + timedelta(minutes=30)

        if slot <= end:
            slots.append({"start_time": start.time(), "end_time": slot.time() })
        start = slot
    return slots

    
    
#Set the available slots for a day/days
@app.post("/doctor/availability")
async def doctor_availability(availability_data: DoctorAvailability,current_doctor: Doctor = Depends(get_current_doctor), db: Session= Depends(get_db)):
    doctor= db.query(Doctor).filter(Doctor.doctor_id==current_doctor.doctor_id).first()

    if not doctor:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    

    try:
    
        slots = time_slot_generator(availability_data.start_time, availability_data.end_time)

        if len(slots) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No slots available"
            )

        availability = Availability(
            doctor_id=current_doctor.doctor_id,
            date_str=availability_data.date_str,
            start_time=availability_data.start_time,
            end_time=availability_data.end_time,
            is_available=availability_data.is_available
        )

        db.add(availability)
        db.commit()
        db.refresh(availability)

        return {"message": "Availability created successfully", "availability_id": availability.id, "slots": slots }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

for route in app.routes:
    print(route.path)