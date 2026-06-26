# 🏥 Healthcare Hospital Management System

This Healthcare Hospital Management System is a one stop application for admin, doctor and patients for consultation, appointments and administrative management
integrated seemlessly.The system addresses crucial roles like appointment booking and doctor consultation improving patient services.

## 📺 Application Walkthrough

Below is a complete demonstration showing the core authentication flows, smart scheduling validation, and dynamic role-based dashboards.

https://github.com/user-attachments/assets/a1cb7cad-2762-47c9-bb23-3d59103608ad

## ✨ Key Features

### 👤 Patient Portal
* **Secure Registration & Login:** Form validation checks for existing records, validates email configurations, and ensures matching password credentials.
* **Cookie-Based Session Management:** Secure token tracking utilizing local browser cookies (`patient_token`) for seamless, persistent navigation.
* **Smart Appointment Booking:** Built-in timezone-aware validation logic that actively blocks double-bookings or scheduling past time slots.
* **Navigation Control:** Clean sign-out workflow that terminates the active session cookie and redirects the user directly to the home landing page.

### 🥼 Doctor Portal
* **Dedicated Authentication Flow:** A strict `POST /doctor/login` handling structure completely isolated from other workflows to eliminate method execution conflicts.
* **Personalized Dashboard:** A custom-rendered template interface tracking upcoming clinical shifts, patient charts, and dynamic assignment updates.

### 🔑 Administrator Control Panel
* **Comprehensive Oversight:** Full system orchestration backend that safely redirects into a tailored, functional template dashboard rather than raw browser JSON strings upon successful login.

---

## 🛠️ Tech Stack

* **Backend Framework:** FastAPI (Python 3.11+)
* **Frontend Engine:** Jinja2 Templates, HTML5, CSS3, Bootstrap 5
* **Authentication:** OAuth2 Password Bearer with Custom Cookie Extraction & JWT Tokens
* **Database/ORM:** SQLAlchemy ,PostgreSQL
* **Server:** Uvicorn

---

## 🚀 Local Installation & Setup

Follow these steps to set up and run the application on your local machine:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git)
   cd YOUR_REPOSITORY

2. **Create and activate a virtual environment:**
   ```bash
    python -m venv venv
    
    # On Windows:
    .\venv\Scripts\activate
    
    # On macOS/Linux:
    source venv/bin/activate

3. **Install the required dependencies:**
   ```bash
    pip install -r requirements.txt

4. **Run the Uvicorn development server:**
   ```bash
     uvicorn main:app --reload
   ```

### 🔐 Demo Credentials

You can explore the application using the following demo accounts.

### 👨‍💼 Admin
- **Email:** `admin@gmail.com`
- **Password:** `admin123`

### 👨‍⚕️ Doctor
- **Email:** `doctor@gmail.com`
- **Password:** `doctor123`

### 🧑‍🦱 Patient
- **Email:** `patient@gmail.com`
- **Password:** `patient123`

## 🌐 View Live Site:

🔗 **Application:** https://hospital-management-system-7ozp.onrender.com
