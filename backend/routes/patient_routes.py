from fastapi import FastAPI ,APIRouter,Request,Form
from fastapi import Depends,HTTPException, status
from backend.schemas.patient_schema import PatientRegistration,PatientLogin,PatientProfile,ProfileUpdate, ChangePassword,ResetPassword,ForgotPassword,AppointmentData
from backend.schemas.doctor_schema import DoctorAvailability
from backend.models.patient_model import Patient,Appointment
from backend.models.doctor_model import Availability
from backend.models.admin_model import Doctor
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from backend.auth.jwt_handler import hash_password, verify_password, create_access_token, get_current_user,to_dict
from backend.database.connection import engine, Base
from backend.routes.doctor_routes import time_slot_generator
from datetime import date,datetime
from jose import jwt
from fastapi.responses import JSONResponse,RedirectResponse,HTMLResponse
from fastapi.templating import Jinja2Templates

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router=APIRouter()

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")
templates1 = Jinja2Templates(directory="templates/Home/login")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="patient/login")

@router.post("/patient/registration")
async def reg_patient(
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(..., alias="confirm password"),
    phone_no: str = Form("Not Provided"), # Default placeholder if not sent from form
    db: Session = Depends(get_db)
):
    # 1. Check if passwords match
    if password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    # 2. Check if user already exists
    existing_user = db.query(Patient).filter(Patient.email_id == email).first()
    if existing_user: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    # 3. Hash password and save to database
    hashed_password = hash_password(password)
    new_user = Patient(
        email_id=email,
        password=hashed_password,
        name=name,
        age=age,
        gender=gender,
        phone_no=phone_no
    )
    
    db.add(new_user)
    db.commit()

    # 4. Redirect cleanly to login page on success
    return RedirectResponse(url="/patient/login", status_code=303)

@router.get("/patient/register", response_class=HTMLResponse)
async def get_patient_register_page(request: Request):
    return templates1.TemplateResponse(
        request=request, 
        name="patient_register.html"  
    )

@router.get("/patient/logout")
async def logout_patient():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="patient_token") 
    return response

@router.post("/patient/login")
async def login_patient(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    existing_patient=db.query(Patient).filter(Patient.email_id== form_data.username).first()
    if not existing_patient: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password",
        )
    
    if not verify_password(form_data.password, existing_patient.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    access_token = create_access_token(
        {"sub": existing_patient.email_id}
    )

    response = RedirectResponse(
        url="/patient/dashboard",
        status_code=303
    )

    response.set_cookie(
        key="patient_token",
        value=access_token,
        httponly=True,
        samesite="lax"
    )

    return response

@router.get("/patient/login", response_class=HTMLResponse)
async def get_patient_login_page(request: Request):
    return templates1.TemplateResponse(
        request=request, 
        name="patient_login.html" # Your existing patient login HTML file name
    )


@router.get("/patient/profile")
async def get_profile( current_user: Patient = Depends(get_current_user)):
    return {
        "name": current_user.name,
        "email": current_user.email_id,
        "phone": current_user.phone_no,
        "pic": current_user.profile_pic,
        "age":current_user.age
    }

@router.get("/patient/profile-page", response_class=HTMLResponse)
async def get_patient_profile_page(
    request: Request, 
    current_user: Patient = Depends(get_current_user)
):
    return templates.TemplateResponse(
        request=request, 
        name="patient_profile.html", 
        context={"patient": current_user}
    ) 

@router.patch("/patient/profile/edit")
async def edit_profile(profile_data: ProfileUpdate, current_user: Patient = Depends(get_current_user), db: Session = Depends(get_db)):
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

    return {"message" : "Updated profile succssefully" , "User": user}    

@router.patch("/change-password")
async def change_password(change_password: ChangePassword, current_user: Patient = Depends(get_current_user),db: Session = Depends(get_db)):


    if not verify_password(change_password.password, current_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password entered is incorrect.")
    

    if change_password.new_password==change_password.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different from current password.")
    
    
    if change_password.new_password!=change_password.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password and confirm password do not match.")
    
    
    hashed_password=hash_password(change_password.new_password)

    current_user.password = hashed_password

    db.commit()
    db.refresh(current_user)

    return {
        "message":"Password changed successfully."
    }

@router.post("/forgot-password")
async def forgot_password(patient: ForgotPassword, db: Session = Depends(get_db)):
    user=db.query(Patient).filter(Patient.email_id == patient.email_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    
    reset_token = create_access_token({"sub": user.email_id})

    return {"reset_token": reset_token}

@router.post("/reset-password")
async def  reset_pasword(reset_password: ResetPassword , db: Session = Depends(get_db) ):
    try:
        payload = jwt.decode(
            reset_password.token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
            )

        email = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token."
            )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        )
    
    user = db.query(Patient).filter(Patient.email_id == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if reset_password.new_password != reset_password.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password and confirm password do not match.")
    
    user.password = hash_password(reset_password.new_password)

    db.commit()
    db.refresh(user)

    return {
        "message":"Password  reset successfull"}  


@router.get("/patient/search_doctors")
async def search_doctor(spec: str | None = None, current_patient: Patient = Depends(get_current_user),db: Session= Depends(get_db)):
    if not spec:
        return{"message": "Specialization is required" }
    
    doctors= db.query(Doctor).filter(Doctor.specialization == spec).all()

    if not doctors:
        raise HTTPException(status_code=404, detail=f"No doctors found for specialization '{spec}'")

    return{"message":"Doctors retrieved succssefully","doctor":doctors}
    
    
    

@router.get("/patient/{doctor_id}/available_dates")
async def view_availability(doctor_id : int, current_patient: Patient = Depends(get_current_user), db: Session= Depends(get_db)):
    availability=(db.query(Availability).filter(Availability.doctor_id == doctor_id, Availability.is_available == True).all())

    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No available dates found")
    
    dates = list(set([a.date_str for a in availability]))

    return {"doctor_id": doctor_id, "available_dates": dates}


@router.get("/patient/{doctor_id}/available_slots")
async def view_slots(doctor_id: int, date_str: date, current_patient: Patient = Depends(get_current_user), db: Session= Depends(get_db)):
    availability=(db.query(Availability).filter(Availability.doctor_id== doctor_id, Availability.date_str == date_str, Availability.is_available == True).first())

    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No available slots found")
    
    slots = time_slot_generator(availability.start_time, availability.end_time)

    return {"doctor_id": doctor_id, "date": date_str, "slots": slots}

@router.post("/patient/appointment")
async def patient_appointment(
    doctor_id: int = Form(...),
    appointment_date: date = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    reason_for_visit: str = Form(...),
    current_patient: Patient = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    appointment_date_str = appointment_date.strftime("%Y-%m-%d")
    start_time_obj = datetime.strptime(start_time, "%H:%M").time()
    end_time_obj = datetime.strptime(end_time, "%H:%M").time()

    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")


    if appointment_date < date.today():
        raise HTTPException(status_code=400, detail="Cannot book past date")

    if appointment_date == date.today():
        current_time = datetime.now().time()
        if start_time_obj <= current_time:
            raise HTTPException(status_code=400, detail="Cannot book past time slot")


    slot = db.query(Availability).filter(
        Availability.doctor_id == doctor_id,
        Availability.date_str == appointment_date.strftime("%Y-%m-%d"),
        Availability.start_time <= start_time_obj,
        Availability.end_time >= end_time_obj
    ).first()

    slots = db.query(Availability).filter(
    Availability.doctor_id == doctor_id
    ).all()

    existing = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.start_time == start_time_obj,
        Appointment.end_time == end_time_obj,
        Appointment.status.in_(["Scheduled", "Pending"])
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Slot already booked")

    appointment = Appointment(
        patient_id=current_patient.patient_id,
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        start_time=start_time_obj,
        end_time=end_time_obj,
        reason_for_visit=reason_for_visit,
        status="Scheduled"
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return RedirectResponse(
        url="/patient/my-appointments-page",
        status_code=303
    )

@router.get("/patient/my-appointments")
async def my_appointments(
    current_patient: Patient = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    appointments = (db.query(Appointment).filter(Appointment.patient_id == current_patient.patient_id).order_by(Appointment.appointment_date.desc(),Appointment.start_time.desc()).all())

    if not appointments:
        raise HTTPException(status_code=404,detail="No appointments found")

    result = []

    for appointment in appointments:

        doctor = (db.query(Doctor).filter(Doctor.doctor_id == appointment.doctor_id).first())

        result.append({
            "doctor_name": doctor.name,
            "specialization": doctor.specialization,
            "appointment_date": appointment.appointment_date,
            "start_time": appointment.start_time,
            "end_time": appointment.end_time,
            "status": appointment.status
        })

    return result

@router.patch("/patient/appointment/{appointment_id}/cancel")
async def cancel_appointments(appointment_id: int, current_user: Patient = Depends(get_current_user),db: Session = Depends(get_db)):
    appointment = (db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first())

    if not appointment:
        raise HTTPException(status_code=404, detail="No appointment found")

    
    if appointment.patient_id != current_user.patient_id:
        raise HTTPException(status_code=403, detail="You can only update your own appointments")
        
    if appointment.status == "Completed":
        raise HTTPException(status_code=400, detail="Completed appointment cannot be cancelled")
    
    if appointment.status == "Cancelled":
        raise HTTPException(status_code=400, detail=f"Appointment is already Cancelled")
    
    appointment.status = "Cancelled"

    db.commit()
    db.refresh(appointment)

@router.get("/patient/dashboard")
async def patient_dashboard(
    request: Request,
    current_patient: Patient = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    total_appointments = (
        db.query(Appointment)
        .filter(Appointment.patient_id == current_patient.patient_id)
        .count()
    )
    pending_appointments = (
        db.query(Appointment)
        .filter(
            Appointment.patient_id == current_patient.patient_id,
            Appointment.status == "Scheduled"
        )
        .count()
    )

    completed_appointments = (
        db.query(Appointment)
        .filter(
            Appointment.patient_id == current_patient.patient_id,
            Appointment.status == "Completed"
        )
        .count()
    )
    upcoming_appointment = (
    db.query(Appointment)
    .filter(
        Appointment.patient_id == current_patient.patient_id,
        Appointment.status == "Scheduled"
    )
    .order_by(Appointment.appointment_date, Appointment.start_time)
    .first()
    )
    

    return templates.TemplateResponse(
    request=request,
    name="patient_dashboard.html",
    context={
        "patient": current_patient,
        "appointment": upcoming_appointment,
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "completed_appointments": completed_appointments
    }
)

@router.get("/patient/book-appointment-page")
async def book_appointment_page(
    request: Request,
    current_patient: Patient = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    doctors = db.query(Doctor).all()

    return templates.TemplateResponse(
        request=request,
        name="patient_book_appointment.html",
        context={
            "patient": current_patient,
            "doctors": doctors
        }
    )


@router.get("/patient/my-appointments-page")
async def my_appointments_page(
    request: Request,
    current_patient: Patient = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    appointments = (
        db.query(Appointment)
        .filter(Appointment.patient_id == current_patient.patient_id)
        .order_by(Appointment.appointment_date.desc(), Appointment.start_time.desc())
        .all()
    )


    enriched_appointments = []
    for appt in appointments:
        doctor = db.query(Doctor).filter(Doctor.doctor_id == appt.doctor_id).first()
        enriched_appointments.append({
            "appointment_id": appt.appointment_id,
            "doctor_name": doctor.name if doctor else "Unknown Doctor",
            "specialization": doctor.specialization if doctor else "General",
            "appointment_date": appt.appointment_date.strftime("%d %B %Y"), 
            "start_time": appt.start_time.strftime("%I:%M %p"),             
            "end_time": appt.end_time.strftime("%I:%M %p"),                 
            "status": appt.status
        })

    return templates.TemplateResponse(
        request=request,
        name="patient_my_appointments.html",
        context={
            "patient": current_patient,
            "appointments": enriched_appointments
        }
    )
@router.post("/patient/select-doctor")
async def select_doctor(
    request: Request,
    specialization: str = Form(...),
    current_patient: Patient = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    doctors = db.query(Doctor).filter(
        Doctor.specialization == specialization
    ).all()

    return templates.TemplateResponse(
        "select_doctor.html",
        {
            "request": request,
            "patient": current_patient,
            "doctors": doctors,
            "specialization": specialization
        }
    )

@router.post("/patient/select-slot")
async def select_slot(
    request: Request,
    doctor_id: int = Form(...),
    specialization: str = Form(...),
    current_patient: Patient = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    availability = db.query(Availability).filter(
        Availability.doctor_id == doctor_id,
        Availability.is_available == True
    ).all()

    dates = list(set([a.date_str for a in availability]))

    return templates.TemplateResponse(
        "select_slot.html",
        {
            "request": request,
            "doctor_id": doctor_id,
            "dates": dates
        }
    )

@router.post("/patient/book-appointment")
async def book_appointment(
    doctor_id: int = Form(...),
    date_str: date = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    reason_for_visit: str = Form(...),
    current_patient: Patient = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    appointment = Appointment(
        patient_id=current_patient.patient_id,
        doctor_id=doctor_id,
        appointment_date=date_str,
        start_time=start_time,
        end_time=end_time,
        reason_for_visit=reason_for_visit,
        status="Scheduled"
    )

    db.add(appointment)
    db.commit()

    return RedirectResponse(
        "/patient/my-appointments-page",
        status_code=303
    )

@router.post("/patient/appointment/{appointment_id}/cancel")
async def cancel_appointments(
    appointment_id: int, 
    current_user: Patient = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="No appointment found")
    
    if appointment.patient_id != current_user.patient_id:
        raise HTTPException(status_code=403, detail="Unauthorized action")
        
    if appointment.status in ["Completed", "Cancelled"]:
        raise HTTPException(status_code=400, detail="Appointment cannot be altered")
    
    appointment.status = "Cancelled"
    db.commit()

    return RedirectResponse(url="/patient/my-appointments-page", status_code=303)