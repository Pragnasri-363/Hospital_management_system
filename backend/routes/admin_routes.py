from fastapi import FastAPI,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from backend.database.connection import get_db
from sqlalchemy.orm import Session
from backend.models.admin_model import Admin, Doctor
from backend.models.patient_model import Appointment,Patient
from backend.auth.jwt_handler import hash_password,create_access_token,verify_password
from backend.database.connection import engine, Base
from backend. schemas.admin_schema import AdminLogin, AdminProfile, AdminRegistration, ProfileUpdate, DoctorData 
from backend.auth.jwt_handler import get_current_admin,to_dict

app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.post("/admin-registration")
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


@app.post("/admin-login")
async def admin_login(form_data: OAuth2PasswordRequestForm= Depends(), db: Session= Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email_id== form_data.username).first()
    

    if not admin:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")
    

    if not verify_password(form_data.password, admin.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    
    access_token = create_access_token({"sub": admin.email_id} )

    return {"access_token": access_token,
    "token_type": "bearer"}
   

@app.get("/admin-profile")
async def get_profile(current_admin: Admin = Depends(get_current_admin)):
    return {
        "name": current_admin.name,
        "gender":current_admin.gender,
        "email": current_admin.email_id,
        "phone": current_admin.phone_no,
        "pic": current_admin.profile_pic,
    }

@app.patch("/admin/profile/edit")
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

@app.post("/admin/add_doctor")
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

#Get the list of doctors present
@app.get("/admin/get_doctors")
async def get_doctors(current_admin: Admin = Depends(get_current_admin),db: Session= Depends(get_db)):

    doctors=db.query(Doctor).all()
    data=[]

    for doctor in doctors:
        data.append(to_dict(doctor))

    return{"message":"List of doctors retrieved sucsessfully","data": {"doctors": data}}
    

#Search a particular doctor using name or specilization
@app.get("/admin/search_doctor")
async def search_doctor(name: str | None = None,spec: str | None = None,current_admin: Admin = Depends(get_current_admin),db: Session= Depends(get_db)):
    
    if name:
        data=db.query(Doctor).filter(name == Doctor.name).all()

        return{"message":"Doctor found","doctor":data}
    
    if spec:
        data=db.query(Doctor).filter(spec == Doctor.specialization).all()

        return{"message":"Doctor found","doctor":data}
    
    if not name and not spec:
        return{"message": "Search query or specialization is required" }
    

@app.get("/admin/appointments")
async def get_appointments(current_admin: Admin = Depends(get_current_admin), db: Session= Depends(get_db)):
    appointments = (db.query(Appointment).order_by(Appointment.appointment_date.desc(), Appointment.start_time).all())

    if not appointments:
        raise HTTPException(status_code=404, detail="No appointments found")
    result = []

    for appointment in appointments:
        patient = (db.query(Patient).filter(Patient.patient_id == appointment.patient_id).first())

        doctor = (db.query(Doctor).filter(Doctor.doctor_id == appointment.doctor_id).first())

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