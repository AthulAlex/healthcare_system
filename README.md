# 🏥 AI-Enabled Healthcare Monitoring and Medicine Management System
### For Old Age Homes

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-5.x-green?style=flat-square&logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=flat-square&logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [System Modules](#system-modules)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Models](#database-models)
- [Installation & Setup](#installation--setup)
- [Running the Project](#running-the-project)
- [User Roles & Access](#user-roles--access)
- [Screenshots](#screenshots)
- [API & AI Integration](#api--ai-integration)
- [Contributing](#contributing)

---

## 📖 About the Project

The **AI-Enabled Healthcare Monitoring and Medicine Management System** is an intelligent web-based platform designed to improve healthcare monitoring, medicine administration, and medical record management for elderly residents in old age homes.

Traditional care home systems often rely on manual records or fragmented digital tools, which can lead to medication errors, delayed health monitoring, and inefficient inventory tracking. This system introduces a centralized digital solution that integrates:

- Healthcare monitoring
- Medicine management
- AI-based health analysis
- Role-based access control
- PDF export capabilities

---

## ✨ Features

### 🔐 Authentication & Security
- Secure login and registration for all roles
- JWT-based session management
- Role-based access control (RBAC)
- Forgot password & change password functionality
- Auto-generate secure passwords for residents

### 👨‍⚕️ Caregiver Module
- Complete resident management dashboard
- Add/edit resident profiles with room assignment
- Record vital signs with auto-abnormal detection
- Upload and manage lab reports (PDF support)
- Add prescriptions and medication schedules
- Assign doctors to residents
- Overall and individual risk analysis
- AI health report generation
- Export medical records as PDF

### 👴 Resident Module
- Personal health dashboard
- View vitals history with trend indicators
- Access lab reports and prescriptions
- AI-generated health summaries
- Export complete medical report as PDF

### 👨‍⚕️ Doctor Module
- Doctor profile with specialization and department
- View assigned residents
- Write prescriptions
- Add lab reports
- Generate AI health reports
- Risk analysis for assigned residents

### 📦 Stock Keeper Module
- Complete medicine inventory management
- Low stock alerts with automatic detection
- Expiry date tracking and warnings
- Add, edit, delete medicines
- Update stock (add/remove/set)
- Export inventory report as PDF

### 🤖 AI Features
- AI-based health risk analysis (Low/Medium/High)
- Automated health report generation
- Risk score calculation (0-100)
- Key factors identification
- Clinical recommendations
- Powered by OpenRouter API

---

## 🗂️ System Modules

```
old_age_home/
├── accounts/         → Authentication, User Management
├── caregiver/        → Caregiver Dashboard & Operations
├── residents/        → Resident Profiles & Health Records
├── doctor/           → Doctor Dashboard & Operations
├── stockkeeper/      → Medicine Inventory Management
├── templates/        → HTML Templates
│   ├── accounts/
│   ├── caregiver/
│   ├── residents/
│   ├── doctor/
│   └── stockkeeper/
├── media/            → Uploaded Files (Lab Report PDFs)
├── core/             → Project Settings & URLs
└── manage.py
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12, Django 5.x |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Database** | PostgreSQL 16 |
| **Authentication** | Django Auth + JWT (SimpleJWT) |
| **AI Integration** | OpenRouter API (GPT-3.5 / Claude) |
| **PDF Generation** | ReportLab |
| **Environment** | Virtual Environment (.venv) |

---

## 🗃️ Database Models

### CustomUser (accounts)
| Field | Type | Description |
|---|---|---|
| username | CharField | Unique login username |
| role | CharField | caregiver / resident / doctor / stockkeeper |
| phone | CharField | Contact number |
| specialization | CharField | Doctor specialization (doctors only) |
| department | CharField | Hospital department (doctors only) |
| qualification | CharField | Medical qualifications |
| experience_years | IntegerField | Years of experience |

### ResidentProfile (residents)
| Field | Type | Description |
|---|---|---|
| user | OneToOneField | Links to CustomUser |
| full_name | CharField | Resident full name |
| date_of_birth | DateField | Date of birth |
| gender | CharField | Male / Female / Other |
| blood_group | CharField | Blood group |
| room_number | CharField | Room assignment |
| status | CharField | active / inactive / discharged |
| assigned_caregiver | ForeignKey | Caregiver in charge |
| assigned_doctor | ForeignKey | Treating doctor |

### VitalSign (residents)
| Field | Type | Description |
|---|---|---|
| resident | ForeignKey | Linked resident |
| blood_pressure | CharField | e.g. 120/80 |
| pulse_rate | IntegerField | Beats per minute |
| oxygen_level | FloatField | SpO2 percentage |
| temperature | FloatField | Celsius |
| blood_sugar | FloatField | mg/dL |
| is_abnormal | BooleanField | Auto-detected |

### LabReport (residents)
| Field | Type | Description |
|---|---|---|
| resident | ForeignKey | Linked resident |
| test_name | CharField | Name of the test |
| result_value | FloatField | Test result |
| normal_range | CharField | e.g. 70-110 |
| unit | CharField | mg/dL, % etc. |
| is_critical | BooleanField | Auto-detected |
| pdf_report | FileField | Uploaded PDF |

### Medicine (stockkeeper)
| Field | Type | Description |
|---|---|---|
| name | CharField | Medicine name |
| batch_number | CharField | Batch identifier |
| supplier | CharField | Supplier name |
| quantity | IntegerField | Current stock |
| minimum_stock | IntegerField | Alert threshold |
| expiry_date | DateField | Expiry date |

### Prescription (stockkeeper)
| Field | Type | Description |
|---|---|---|
| resident | ForeignKey | Linked resident |
| medicine | ForeignKey | Linked medicine |
| dosage | CharField | e.g. 1 tablet |
| frequency | CharField | e.g. twice a day |
| prescribed_by | CharField | Doctor name |
| is_active | BooleanField | Active status |

### AIHealthReport (residents)
| Field | Type | Description |
|---|---|---|
| resident | ForeignKey | Linked resident |
| risk_score | IntegerField | 0-100 score |
| risk_level | CharField | Low / Medium / High |
| factors | TextField | Key risk factors |
| summary | TextField | AI health summary |

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 16+
- Git

### Step 1 — Clone the Repository
```bash
git clone https://github.com/yourusername/old-age-home.git
cd old-age-home
```

### Step 2 — Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install django psycopg2-binary pillow djangorestframework djangorestframework-simplejwt reportlab requests gunicorn whitenoise dj-database-url
```

### Step 4 — Create PostgreSQL Database
```sql
CREATE DATABASE old_age_home_db;
```

### Step 5 — Configure Settings
Open `core/settings.py` and update:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'old_age_home_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

OPENROUTER_API_KEY = 'your-openrouter-api-key'
```

### Step 6 — Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7 — Create Superuser
```bash
python manage.py createsuperuser
```

---

## 🚀 Running the Project

```bash
# Activate virtual environment (Windows)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .venv\Scripts\Activate.ps1

# Run development server
python manage.py runserver
```

Open your browser and go to:
- **Home** → http://127.0.0.1:8000/
- **Admin** → http://127.0.0.1:8000/admin/
- **Login** → http://127.0.0.1:8000/login/
- **Register** → http://127.0.0.1:8000/register/

---

## 👥 User Roles & Access

| Role | Default URL | Access |
|---|---|---|
| **Admin** | `/admin/` | Full system access |
| **Caregiver** | `/caregiver/dashboard/` | Manage all residents, vitals, labs, prescriptions |
| **Doctor** | `/doctor/dashboard/` | View assigned residents, prescribe, add labs |
| **Resident** | `/residents/dashboard/` | View own health records, export PDF |
| **Stock Keeper** | `/stockkeeper/dashboard/` | Manage medicine inventory |

### Default Test Credentials
| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Caregiver | `caregiver_sarah` | `care1234` |
| Doctor | `dr_rajan` | `doctor1234` |
| Resident | `resident_mohan` | `res1234` |
| Stock Keeper | `stockkeeper1` | `stock1234` |

---

## 🤖 API & AI Integration

This project uses **OpenRouter API** to generate AI health reports.

### Setup
1. Go to https://openrouter.ai/
2. Create an account and generate an API key
3. Add to `core/settings.py`:
```python
OPENROUTER_API_KEY = 'your-api-key-here'
```

### Supported Models
```python
# In residents/ai_helper.py change the model:
"model": "openai/gpt-3.5-turbo"      # Default
"model": "anthropic/claude-haiku-4-5" # Claude
"model": "google/gemini-flash-1.5"    # Google
"model": "mistralai/mistral-7b-instruct" # Free
```

### AI Report Output
```json
{
    "risk_score": 80,
    "risk_level": "High",
    "factors": "Diabetes, Hypertension, High Cholesterol",
    "summary": "Patient shows elevated blood sugar..."
}
```

---

## 🌐 Deployment (Railway)

1. Push code to GitHub
2. Go to https://railway.app/
3. Create new project → Deploy from GitHub
4. Add PostgreSQL database
5. Set environment variables:
   - `SECRET_KEY`
   - `OPENROUTER_API_KEY`
   - `DATABASE_URL`
6. Run migrations via Railway shell

---

## 📝 URL Structure

```
/                           → Home (redirects based on role)
/login/                     → Login page
/register/                  → Register page
/logout/                    → Logout
/forgot-password/           → Reset password
/change-password/           → Change own password
/admin/                     → Django admin panel

/caregiver/dashboard/       → Caregiver home
/caregiver/residents/       → Resident list
/caregiver/residents/add/   → Add new resident
/caregiver/risk/            → Risk analysis

/residents/dashboard/       → Resident home
/residents/vitals/          → Vitals history
/residents/labs/            → Lab reports
/residents/ai-report/       → AI health report
/residents/export-pdf/      → Export PDF

/doctor/dashboard/          → Doctor home
/doctor/residents/          → Assigned residents

/stockkeeper/dashboard/     → Stock home
/stockkeeper/medicines/     → Medicine list
/stockkeeper/medicines/add/ → Add medicine
/stockkeeper/export-pdf/    → Export inventory PDF
```

---

## 🔒 Security Features

- CSRF protection on all forms
- Role-based access control decorators
- Password hashing (Django default PBKDF2)
- JWT session tokens
- File upload validation
- SQL injection prevention (Django ORM)

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Developer

Developed as part of **MCA Final Project**

**Institution:** Your College Name
**Year:** 2024-2026

---

## 🙏 Acknowledgements

- [Django Framework](https://www.djangoproject.com/)
- [OpenRouter API](https://openrouter.ai/)
- [ReportLab PDF Library](https://www.reportlab.com/)
- [PostgreSQL](https://www.postgresql.org/)
