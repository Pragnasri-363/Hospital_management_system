from fastapi import FastAPI, Request  
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates  

from backend.routes.admin_routes import router as admin_router
from backend.routes.doctor_routes import router as doctor_router
from backend.routes.patient_routes import router as patient_router
from backend.database.connection import Base, engine

app = FastAPI()

# 1. Point Jinja2 to the specific 'Home' subfolder
templates = Jinja2Templates(directory="templates/Home")

app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)

@app.get("/home", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # 2. Match the exact filename inside that subfolder
    return templates.TemplateResponse(request=request, name="home.html")


app.include_router(admin_router)
app.include_router(doctor_router)
app.include_router(patient_router)