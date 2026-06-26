from fastapi import FastAPI,Depends,HTTPException, status,APIRouter,Request,Form
from backend.database.connection import get_db
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.models.admin_model import Doctor
from backend.models.patient_model import Appointment,Patient
from backend.models.doctor_model import Availability
from backend.auth.jwt_handler import hash_password, verify_password, create_access_token,get_current_doctor
from backend.database.connection import engine, Base
from backend.schemas.doctor_schema import ProfileUpdate,DoctorAvailability,AppointmentStatusUpdate
from datetime import date,time,timedelta,datetime
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse,RedirectResponse,HTMLResponse

router = APIRouter()

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")
templates1 = Jinja2Templates(directory="templates/Home/login")

@router.get("/doctor/login-page", response_class=HTMLResponse)
async def get_doctor_login_page(request: Request):
    return templates1.TemplateResponse(
        request=request, 
        name="doctor_login.html"  
    )

@router.post("/doctor/login")
async def doctor_login(form_data: OAuth2PasswordRequestForm= Depends(), db: Session= Depends(get_db)):

    doctor = db.query(Doctor).filter(Doctor.email_id == form_data.username).first()
    
    if not doctor:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")
    

    if not verify_password(form_data.password, doctor.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    
    access_token = create_access_token({"sub": doctor.email_id} )

    response = RedirectResponse(
        url="/doctor/dashboard",
        status_code=303
    )

    response.set_cookie(
        key="doctor_token",
        value=access_token,
        httponly=True,
        samesite="lax"
    )

    return response

@router.get("/doctor/register-page", response_class=HTMLResponse)
async def get_doctor_register_page(request: Request):
    return templates1.TemplateResponse(
        request=request, 
        name="doctor_register.html"   
    )


@router.get("/doctor/logout")
async def logout_doctor():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="doctor_token")   
    return response

@router.get("/doctor/profile")
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

@router.get("/doctor/profile-page", response_class=HTMLResponse)
async def get_doctor_profile_page(
    request: Request, 
    current_doctor: Doctor = Depends(get_current_doctor) 
):
    return templates.TemplateResponse(
        request=request, 
        name="doctor_profile.html", 
        context={"doctor": current_doctor}
    )

@router.post("/doctor/update-profile")
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

    
    
@router.post("/doctor/availability")
async def doctor_availability(
    request: Request,
    date_str: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    current_doctor: Doctor = Depends(get_current_doctor), 
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(Doctor.doctor_id == current_doctor.doctor_id).first()

    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    
    try:
        # Convert incoming string times from HTML form to time objects
        start = datetime.strptime(start_time, "%H:%M").time()
        end = datetime.strptime(end_time, "%H:%M").time()
        
        slots = time_slot_generator(start, end)

        if len(slots) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No slots available"
            )

        created_slots = []
        for slot in slots:
            db_slot = Availability(
                doctor_id=current_doctor.doctor_id,
                date_str=date_str,
                start_time=slot["start_time"],
                end_time=slot["end_time"],
                is_available=True
            )
            db.add(db_slot)
            created_slots.append(db_slot)

        db.commit()  # Commits ALL slots securely into the DB

        
        return templates.TemplateResponse(
            request=request,
            name="doctor_set_availability.html",
            context={
                "request": request,
                "doctor": current_doctor,
                "slots": slots,
                "selected_date": date_str,
                "success_message": "Slots saved successfully!"
            }
        )

    except Exception as e:
        db.rollback() 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.get("/doctor/appointments")
async def get_appointments(current_doctor:Doctor = Depends(get_current_doctor), db: Session= Depends(get_db)):
    appointments = (db.query(Appointment).filter(Appointment.doctor_id == current_doctor.doctor_id).order_by(Appointment.appointment_date, Appointment.start_time).all())

    result = []

    for appointment in appointments:
        patient = (db.query(Patient).filter(Patient.patient_id == appointment.patient_id).first())

        result.append({
            "patient_name": patient.name,
            "appointment_date": appointment.appointment_date,
            "start_time": appointment.start_time,
            "end_time": appointment.end_time,
            "status": appointment.status
        })

    return result

@router.patch("/doctor/update-appointments-status/{appointment_id}")
async def update_appointments_status(appointment_id: int,data:AppointmentStatusUpdate,current_doctor: Doctor = Depends(get_current_doctor),db: Session = Depends(get_db)):
    appointment = (db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first())
    if not appointment:
        raise HTTPException(status_code=404, detail="No appointment found")

    
    if appointment.doctor_id != current_doctor.doctor_id:
        raise HTTPException(status_code=403, detail="You can only update your own appointments")
        
    allowed_status = ["Scheduled", "Completed", "Cancelled"]
    if appointment.status == data.status:
        raise HTTPException(status_code=400, detail=f"Appointment is already {data.status}")
    
    if data.status not in allowed_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not valid status")
        
    if appointment.status in ["Completed", "Cancelled"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Appointment status can no longer be modified")
        
    appointment.status = data.status

    db.commit()
    db.refresh(appointment)

    return {
        "message": "Appointment status updated successfully",
        "appointment_id": appointment.appointment_id,
        "status": appointment.status
        }

@router.get("/doctor/dashboard")
async def doctor_dashboard(
    request: Request,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):

    total_doctors = db.query(Doctor).count()

    total_appointments = db.query(Appointment).count()

    pending_requests = db.query(Appointment).filter(
        Appointment.status == "Scheduled"
    ).count()

    todays_appointments = db.query(Appointment).filter(
        Appointment.doctor_id == current_doctor.doctor_id,
        Appointment.appointment_date == date.today()
    ).count()

    return templates.TemplateResponse(
    request=request,
    name="doctor_dashboard.html",
    context={
        "doctor": current_doctor,
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "pending_requests": pending_requests,
        "todays_appointments": todays_appointments
    }
)

@router.get("/doctor/appointments-page")
def doctor_appointments_page(
    request: Request,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):

    appointments = (
        db.query(Appointment)
        .filter(Appointment.doctor_id == current_doctor.doctor_id)
        .order_by(Appointment.appointment_date, Appointment.start_time)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="doctor_view_appointments.html",
        context={
            "request": request,
            "appointments": appointments
        }
    )

@router.get("/doctor/availability-page")
def doctor_availability_page(
    request: Request,
    current_doctor: Doctor = Depends(get_current_doctor)
):

    return templates.TemplateResponse(
        request=request,
        name="doctor_set_availability.html",
        context={
            "request": request,
            "doctor": current_doctor,
            "slots": []
        }
    )

@router.post("/doctor/availability-page")
async def generate_availability_slots(
    request: Request,
    date_str: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    
    start = datetime.strptime(start_time, "%H:%M").time()
    end = datetime.strptime(end_time, "%H:%M").time()
    
    slots = time_slot_generator(start, end)

    return templates.TemplateResponse(
        request=request,
        name="doctor_set_availability.html",
        context={
            "request": request,
            "doctor": current_doctor,
            "slots": slots,
            "selected_date": date_str
        }
    )

