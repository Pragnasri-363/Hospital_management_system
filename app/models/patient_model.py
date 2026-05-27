from sqlalchemy import Declarativeclass
from sqlalchemy import Mapped
from sqlalchemy import mapped_column
from sqlalchemy import String,Integer,DateTime

class Base(Declarativeclass):
    pass

class Patient(Base):
    __tablename__="patients"

    patient_id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    name: Mapped[str] = mapped_column(String(30),nullable=False)
    dob:Mapped[DateTime]=mapped_column(DateTime,nullable=False)
    gender:Mapped[str] = mapped_column(String(30),nullable=False)
    email_id:Mapped[str]=mapped_column(String(20),nullable=False)
    password:Mapped[str]=mapped_column(String(20),nullable=False)  
    profile_pic:Mapped[str]=mapped_column(String)
 
