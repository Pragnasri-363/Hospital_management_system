from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,Integer
from app.database.connection import Base

class Patient(Base):
    __tablename__="patients"

    patient_id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    name: Mapped[str] = mapped_column(String(50),nullable=False)
    age:Mapped[int]=mapped_column(Integer,nullable=False)
    gender:Mapped[str] = mapped_column(String(20),nullable=False)
    email_id:Mapped[str]=mapped_column(String(100),unique=True, nullable=False)
    phone_no:Mapped[str]=mapped_column(String(15),unique=True, nullable=False)
    password:Mapped[str]=mapped_column(String(250),nullable=False)  
    profile_pic:Mapped[str]=mapped_column(String(300),nullable=True)
 
