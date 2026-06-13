# 🚀 PortfolioAI

### AI-Powered Career Development & Portfolio Management Platform

PortfolioAI is a comprehensive AI-powered career development platform built using Django that helps students, graduates, and professionals create professional portfolios, build ATS-friendly resumes, analyze skills, prepare for interviews, and improve career readiness.

The platform combines portfolio management, resume building, GitHub profile analysis, skill gap identification, career recommendations, and recruiter-focused tools into a single intelligent ecosystem.

---

## 🌟 Features

### 🔐 Authentication & Security

* User Registration
* Secure Login & Logout
* Email Verification
* Forgot Password via OTP
* Change Password
* Session Management
* Account Security Settings

### 👤 Profile Management

* Personal Profile Creation
* Profile Photo Upload
* Profile Banner Upload
* Social Media Links
* Public Portfolio Profile
* User Search System

### 📄 Resume Builder & Analyzer

* Resume Upload
* Resume Parsing
* AI Resume Builder
* ATS Score Analysis
* Resume Download
* Resume Improvement Suggestions

### 🎯 Portfolio Management

Manage:

* Education
* Skills
* Projects
* Certifications
* Achievements

CRUD Operations:

* Add
* Edit
* Update
* Delete

### 🧠 AI Career Modules

* Resume Analysis
* Skill Gap Analysis
* Career Recommendation System
* Interview Question Generator
* Placement Readiness Assessment
* Learning Roadmap Generation

### 💻 GitHub Analyzer

* GitHub Profile Analysis
* Repository Analysis
* Contribution Tracking
* Developer Score Generation
* Coding Activity Insights

### 🏅 Achievement & Badge System

* Profile Completion Badges
* GitHub Verification Badges
* Resume Achievement Badges
* Portfolio Milestone Badges
* Career Readiness Badges

### 🔍 Recruiter Module

* Candidate Search
* Portfolio Review
* Student Profile Viewing
* Candidate Comparison
* Recruiter Dashboard

### 📊 Analytics

* Portfolio Score
* Resume Quality Score
* GitHub Score
* Career Readiness Score
* User Progress Tracking

---

## 🏗️ Project Architecture

```text
PortfolioAI/
│
├── accounts/           # Authentication & User Management
├── analyzer/           # AI Analysis Modules
├── portfolio/          # Portfolio Management
├── recruiter/          # Recruiter Features
├── templates/          # HTML Templates
├── static/             # CSS, JS, Images
├── media/              # Uploaded Files
├── utils/              # Helper Utilities
├── docs/               # Project Documentation
├── config/             # Django Configuration
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🛠️ Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript
* Bootstrap 5
* Tailwind CSS
* Chart.js

### Backend

* Python
* Django
* Django ORM

### Database

* MySQL
* SQLite (Development)

### Authentication

* Django Authentication System
* Email OTP Verification
* Password Recovery System

### AI & Analytics

* Resume Parsing
* ATS Analysis
* Skill Gap Analysis
* Career Recommendation Engine
* GitHub Profile Analysis

### Development Tools

* Git
* GitHub
* VS Code
* SMTP Email Services

---

## 📂 Core Modules

### Accounts Module

Handles:

* Registration
* Login
* Email Verification
* User Profiles
* Password Recovery

### Portfolio Module

Handles:

* Education
* Skills
* Projects
* Certifications
* Achievements

### Analyzer Module

Handles:

* Resume Analysis
* ATS Score Generation
* GitHub Analysis
* Skill Gap Detection
* Career Recommendations
* Interview Preparation

### Recruiter Module

Handles:

* Candidate Search
* Portfolio Review
* Recruiter Dashboard

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/231FA04B79/PortfolioAI.git
cd PortfolioAI
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows

```bash
venv\Scripts\activate
```

Linux/Mac

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create `.env`

```env
SECRET_KEY=your_secret_key

DEBUG=True

EMAIL_HOST_USER=your_email@gmail.com

EMAIL_HOST_PASSWORD=your_app_password

GITHUB_TOKEN=your_github_token
```

### Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Run Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## 📈 Future Enhancements

* AI Job Description Analyzer
* ATS Match Engine
* Portfolio QR Code Generator
* Advanced Recruiter Dashboard
* Portfolio Analytics
* Multi-Resume Management
* AI Career Coach
* Public Portfolio Themes
* LinkedIn Profile Analyzer

---

## 🎯 Project Objectives

PortfolioAI aims to bridge the gap between academic learning and professional opportunities by helping users:

* Build Professional Portfolios
* Create ATS-Friendly Resumes
* Improve Employability
* Analyze Technical Skills
* Prepare for Interviews
* Showcase Achievements
* Enhance Career Readiness

---

## 👨‍💻 Developer

**Hemanth Kumar**

Student Developer | Python Developer | Django Enthusiast

GitHub:
https://github.com/231FA04B79

---

## ⭐ Support

If you find this project useful:

⭐ Star the repository

🍴 Fork the repository

🤝 Contribute improvements

📢 Share with others

---

## 📜 License

This project is developed for educational, learning, and portfolio purposes.
