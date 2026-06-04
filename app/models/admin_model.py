from app.database.connection import Base
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,Integer

class Admin(Base):
    __tablename__="admins"

    admin_id: Mapped[int]= mapped_column(primary_key= True, autoincrement= True)
    name: Mapped[str]= mapped_column(String(200), nullable= False)
    gender: Mapped[str]= mapped_column(String(20), nullable=True)
    phone_no: Mapped[str]= mapped_column(String(30),nullable= False)
    email_id: Mapped[str]= mapped_column(String(500), nullable= False)
    password:Mapped[str]=mapped_column(String(250),nullable=False) 
    profile_pic: Mapped[str]= mapped_column(String(150),nullable= True)


class Doctor(Base):
    __tablename__="doctors"

    doctor_id: Mapped[int]= mapped_column(primary_key= True, autoincrement= True)
    name: Mapped[str]= mapped_column(String(200), nullable= False)
    experience: Mapped[int]= mapped_column(Integer, nullable= False)
    speciality: Mapped[str]= mapped_column(String(300), nullable= False)
    gender: Mapped[str]= mapped_column(String(20), nullable=True)
    phone_no: Mapped[str]= mapped_column(String(30),nullable= False)
    email_id: Mapped[str]= mapped_column(String(500), nullable= False)
    password:Mapped[str]=mapped_column(String(250),nullable=False) 
    education: Mapped[str]= mapped_column(String(500), nullable= False)
    profile_pic: Mapped[str]= mapped_column(String(150),nullable= True)
    