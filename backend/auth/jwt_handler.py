from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import datetime, timedelta, timezone
from backend.database.connection import get_db
from backend.models.patient_model import Patient
from fastapi import Depends,HTTPException,status,Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from backend.models.admin_model import Doctor,Admin
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi import Request, HTTPException, status


pwd_context= CryptContext(schemes=["argon2"], deprecated ="auto")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(self, tokenUrl: str):
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": {}})
        super().__init__(flows=flows)

    async def __call__(self, request: Request) -> str | None:
        
        return request.cookies.get("patient_token") or request.cookies.get("doctor_token") or request.cookies.get("admin_token")


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/patient/login")
oauth2_scheme_doctor = OAuth2PasswordBearerWithCookie(tokenUrl="/doctor/login")
oauth2_scheme_admin = OAuth2PasswordBearerWithCookie(tokenUrl="/admin/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str,hashed_password: str) -> bool:
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("patient_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    

    email = payload.get("sub")

    patient = db.query(Patient).filter(
        Patient.email_id == email
    ).first()

    if not patient:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return patient

    

def get_current_doctor(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("doctor_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    email = payload.get("sub")

    doctor = db.query(Doctor).filter(
        Doctor.email_id == email
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return doctor

async def get_current_admin(
    request: Request,
    db: Session = Depends(get_db)
):

    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")

    admin = db.query(Admin).filter(Admin.email_id == email).first()

    if not admin:
        raise HTTPException(status_code=401, detail="Invalid token")

    return admin

def to_dict(self):
    return {
            'id': self.doctor_id,
            'name': self.name,
            "email_id":self.email_id,
            'specialization': self.specialization,
            'experience': self.experience,
            'education': self.education,
            'phone': self.phone_no
        }