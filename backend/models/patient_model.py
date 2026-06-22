from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,Integer,ForeignKey,UniqueConstraint
from backend.database.connection import Base
from datetime import date, time

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
 
class Appointment(Base):
    __tablename__ = "appointment"

    __table_args__ = (
        UniqueConstraint(
            "doctor_id",
            "appointment_date",
            "start_time",
            name="unique_slot_booking"
        ),
    )

    appointment_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.patient_id"),
        nullable=False
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.doctor_id"),
        nullable=False
    )

    appointment_date: Mapped[date] = mapped_column(nullable=False)

    start_time: Mapped[time] = mapped_column(nullable=False)

    end_time: Mapped[time] = mapped_column(nullable=False)

    reason_for_visit: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Pending"
    )