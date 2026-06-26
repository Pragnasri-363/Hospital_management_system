from fastapi import FastAPI,Depends,HTTPException,status,APIRouter,Form
from fastapi.security import OAuth2PasswordRequestForm
from backend.database.connection import get_db
from sqlalchemy.orm import Session
from backend.models.admin_model import Admin, Doctor
from backend.models.patient_model import Appointment,Patient
from backend.auth.jwt_handler import hash_password,create_access_token,verify_password
from backend.database.connection import engine, Base
from backend. schemas.admin_schema import AdminLogin, AdminProfile, AdminRegistration, ProfileUpdate, DoctorData 
from backend.auth.jwt_handler import get_current_admin,to_dict
from fastapi import Request
from datetime import date
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse,RedirectResponse,HTMLResponse

router = APIRouter()
Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")
templates1 = Jinja2Templates(directory="templates/Home/login")

@router.post("/admin-registration")
async def reg_admin(admin: AdminRegistration, db: Session = Depends(get_db)):
    exisiting_user= db.query(Admin).filter(Admin.email_id == admin.email_id).first()
    if exisiting_user: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    hashed_password= hash_password(admin.password)

    new_user = Admin(email_id=admin.email_id,
                password=hashed_password,
                name=admin.name,
                gender= admin.gender, 
                phone_no= admin.phone_no
                )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"name":new_user.name,"gender":new_user.gender,"phone_no":new_user.phone_no,"email_id":new_user.email_id}

@router.get("/admin/login-page", response_class=HTMLResponse)
async def get_admin_login_page(request: Request):
    return templates1.TemplateResponse(
        request=request, 
        name="admin_login.html"   # Your admin login HTML file name
    )

@router.post("/admin/login")
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email_id == form_data.username).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password"
        )

    if not verify_password(form_data.password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    access_token = create_access_token({"sub": admin.email_id})

    response = RedirectResponse(
        url="/admin/dashboard",
        status_code=303
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax"
    )

    return response


@router.get("/admin/logout")
async def logout_admin():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="admin_token")    # Matches your admin login cookie key
    return response

@router.get("/admin-profile")
async def get_profile(current_admin: Admin = Depends(get_current_admin)):
    return {
        "name": current_admin.name,
        "gender":current_admin.gender,
        "email": current_admin.email_id,
        "phone": current_admin.phone_no,
        "pic": current_admin.profile_pic,
    }
@router.get("/admin/profile-page", response_class=HTMLResponse)
async def get_profile(request: Request, current_admin: Admin = Depends(get_current_admin)):
    admin_data = {
        "name": current_admin.name,
        "gender": current_admin.gender,
        "email": current_admin.email_id,
        "phone": current_admin.phone_no,
        "pic": current_admin.profile_pic,
    }
    return templates.TemplateResponse(
        request=request, 
        name="admin_profile.html", 
        context={"admin": admin_data}
    )

# 2. The POST Route to capture data updates via HTML Form Parameters
@router.post("/admin/profile/edit-submit")
async def edit_admin_profile_submit(
    name: str = Form(...),
    phone_no: str = Form(...),
    gender: str = Form(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    admin_record = db.query(Admin).filter(Admin.email_id == current_admin.email_id).first()
    if not admin_record:
        raise HTTPException(status_code=404, detail="Admin record missing")
        
    
    admin_record.name = name
    admin_record.phone_no = phone_no
    admin_record.gender = gender
    
    db.commit()
    
    
    return RedirectResponse(url="/admin/profile-page", status_code=303)

@router.patch("/admin/profile/edit")
async def edit_profile(profile_data: ProfileUpdate, current_user: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    query=db.query(Admin).filter(Admin.email_id==current_user.email_id)
    user=query.first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Admin not found"
        )
    
    query.update(
        profile_data.model_dump(exclude_unset=True)
    )

    db.commit()
    db.refresh(user)

    return {"message" : "Updated profile succssefully" , "User": user}

@router.post("/admin/add_doctor")
async def add_doctor(doctor: DoctorData, db: Session= Depends(get_db)):
    exisiting_doc= db.query(Doctor).filter(Doctor.email_id == doctor.email_id).first()
    if exisiting_doc: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    hashed_password= hash_password(doctor.password)

    new_doc = Doctor(email_id=doctor.email_id,
                password=hashed_password,
                name=doctor.name,
                gender= doctor.gender, 
                phone_no= doctor.phone_no,
                experience= doctor.experience,
                education= doctor.education,
                specialization= doctor.specialization
                )
    
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return {"message":"Doctor adeed successfully","name":new_doc.name,"gender":new_doc.gender,"phone_no":new_doc.phone_no,"email_id":new_doc.email_id,"experience":new_doc.experience,"education":new_doc.education,"speciality":new_doc.specialization}

@router.post("/admin/add_doctor_form")
async def add_doctor_form(
    name: str = Form(...),
    email_id: str = Form(...),
    password: str = Form(...),
    phone_no: str = Form(...),
    specialization: str = Form(...),
    experience: str = Form(...),
    education: str = Form(...),
    gender: str = Form(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):

    existing_doc = (
        db.query(Doctor)
        .filter(Doctor.email_id == email_id)
        .first()
    )

    if existing_doc:
        raise HTTPException(
            status_code=400,
            detail="Doctor already exists"
        )

    hashed_password = hash_password(password)

    new_doc = Doctor(
        name=name,
        email_id=email_id,
        password=hashed_password,
        phone_no=phone_no,
        specialization=specialization,
        experience=experience,
        education=education,
        gender=gender
    )

    db.add(new_doc)
    db.commit()

    return RedirectResponse(
        url="/admin/doctors",
        status_code=303
    )

#Get the list of doctors present
@router.get("/admin/get_doctors")
async def get_doctors(current_admin: Admin = Depends(get_current_admin),db: Session= Depends(get_db)):

    doctors=db.query(Doctor).all()
    data=[]

    for doctor in doctors:
        data.append(to_dict(doctor))

    return{"message":"List of doctors retrieved sucsessfully","data": {"doctors": data}}
    

#Search a particular doctor using name or specilization
@router.get("/admin/search_doctor")
async def search_doctor(name: str | None = None,spec: str | None = None,current_admin: Admin = Depends(get_current_admin),db: Session= Depends(get_db)):
    
    if name:
        data=db.query(Doctor).filter(name == Doctor.name).all()

        return{"message":"Doctor found","doctor":data}
    
    if spec:
        data=db.query(Doctor).filter(spec == Doctor.specialization).all()

        return{"message":"Doctor found","doctor":data}
    
    if not name and not spec:
        return{"message": "Search query or specialization is required" }
    
def get_all_appointments(db: Session) -> list:
    appointments = (
        db.query(Appointment)
        .order_by(
            Appointment.appointment_date.desc(),
            Appointment.start_time
        )
        .all()
    )

    result = []

    for appointment in appointments:

        patient = (
            db.query(Patient)
            .filter(Patient.patient_id == appointment.patient_id)
            .first()
        )

        doctor = (
            db.query(Doctor)
            .filter(Doctor.doctor_id == appointment.doctor_id)
            .first()
        )

        result.append({
            "appointment_id": appointment.appointment_id,
            "doctor_name": doctor.name,
            "patient_name": patient.name,
            "appointment_date": appointment.appointment_date,
            "start_time": appointment.start_time,
            "end_time": appointment.end_time,
            "status": appointment.status
        })

    return result

@router.get("/admin/dashboard")
async def admin_dashboard(
    request: Request,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    total_doctors = db.query(Doctor).count()

    total_appointments = db.query(Appointment).count()

    return templates.TemplateResponse(
    request=request,
    name="admin_dashboard.html",
    context={
        "total_doctors": total_doctors,
        "total_appointments": total_appointments
    }
)

@router.get("/admin/doctors")
async def doctors_page(
    request: Request,
    name: str | None = None,
    spec: str | None = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    query = db.query(Doctor)

    if name:
        query = query.filter(
            Doctor.name.ilike(f"%{name}%")
        )

    if spec:
        query = query.filter(
            Doctor.specialization.ilike(f"%{spec}%")
        )

    doctors = query.all()

    return templates.TemplateResponse(
        request=request,
        name="admin_manage_doctors.html",
        context={
            "doctors": doctors
        }
    )

@router.get("/admin/appointments_page")
async def appointments_page(
    request: Request,
    search: str | None = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    query = db.query(Appointment, Patient, Doctor)\
            .join(Patient, Appointment.patient_id == Patient.patient_id)\
            .join(Doctor, Appointment.doctor_id == Doctor.doctor_id)

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        query = query.filter(
            (Patient.name.ilike(search_term)) | 
            (Doctor.name.ilike(search_term))
        )

    records = query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.start_time
    ).all()

    
    result = []
    for appointment, patient, doctor in records:
        result.append({
            "appointment_id": appointment.appointment_id,
            "doctor_name": doctor.name,
            "patient_name": patient.name,
            "appointment_date": appointment.appointment_date,
            "start_time": appointment.start_time,
            "end_time": appointment.end_time,
            "status": appointment.status
        })


    return templates.TemplateResponse(
        request=request,
        name="admin_appointments.html",
        context={
            "appointments": result,
            "search": search
        }
    )

@router.get("/admin/appointments")
async def get_appointments(current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)):

    return get_all_appointments(db)