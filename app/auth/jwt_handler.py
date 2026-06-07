from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from app.database.connection import get_db
from app.models.patient_model import Patient
from fastapi import Depends,HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from app.models.admin_model import Doctor,Admin
pwd_context= CryptContext(schemes=["argon2"], deprecated ="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="patient/login")
oauth2_scheme_admin = OAuth2PasswordBearer(tokenUrl="admin-login")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token"
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    patient = (
        db.query(Patient)
        .filter(Patient.email_id == email)
        .first()
    )

    if patient is None:
        raise credentials_exception

    return patient

async def get_current_doctor(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token"
    )
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    doctor = (
        db.query(Doctor)
        .filter(Doctor.email_id == email)
        .first()
    )

    if doctor is None:
        raise credentials_exception

    return doctor

async def get_current_admin(
    token: str = Depends(oauth2_scheme_admin),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token"
    )

    try:
    
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        

        email = payload.get("sub")
        

        if email is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    admin = (
        db.query(Admin)
        .filter(Admin.email_id == email)
        .first()
    )
    
    if admin is None:
        raise credentials_exception

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