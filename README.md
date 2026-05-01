# 🧠 Sahar: AI-Powered Mental Health Support System

<div align="center">

![Project Status](https://img.shields.io/badge/status-production-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)
![Flask](https://img.shields.io/badge/Flask-2.0+-000000?logo=flask)
![License](https://img.shields.io/badge/license-MIT-green)

**An intelligent real-time suicide risk detection and mental health support platform**

[Live Demo](https://omerdo1.wixsite.com/suicide-risk-assesso) • [Report Bug](https://github.com/omerdor001/Sahar-Online-Mental-Health-Support/issues) • [Request Feature](https://github.com/omerdor001/Sahar-Online-Mental-Health-Support/issues)

</div>

---

## 📋 Table of Contents

- [About The Project](#-about-the-project)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [Team](#-team)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🎯 About The Project

**Sahar** is a production-grade mental health support system developed for the Sahar Organization (Israel's national suicide prevention hotline). The platform assists volunteers and administrators in managing conversations with help-seekers by leveraging advanced AI/NLP algorithms to provide:

- **Real-time suicide risk assessment** (~85% accuracy)
- **Automated conversation summarization**
- **Risk factor explanation and insights**
- **Emergency mobile alerts** for high-risk cases

The system currently supports **~200 daily users** and helps save lives by enabling faster, more informed responses from trained volunteers.

---

## ✨ Key Features

### 🔍 **Real-Time Risk Analysis**
- Continuous monitoring of active chat conversations
- AI-powered risk classification (Low / Medium / High)
- Instant visual alerts for volunteers
- Mobile push notifications for emergency responders

### 📊 **Conversation Management**
- **Smart Filtering**: Search and locate conversations by unique identifiers
- **Historical Analysis**: Access past conversation data and predictions
- **Live Monitoring**: Track multiple conversations simultaneously

### 📝 **AI-Powered Summarization**
- Generate concise summaries of conversations
- Available during active sessions and in call history
- Helps volunteers quickly understand context

### ⚙️ **Algorithm Configuration**
- Toggle AI functionalities (risk detection, explanations, summaries)
- Fine-tune sensitivity and alert thresholds
- Admin control panel for system management

### 🔗 **LivePerson Integration**
- Automatic data fetching every 5 seconds
- Seamless integration with existing chat infrastructure
- Real-time synchronization

---

## 🛠️ Tech Stack

### **Backend**
- **Framework**: Flask (Python 3.8+)
- **Server**: Gunicorn + Nginx
- **Database**: SQLite
- **AI/ML**: PyTorch, NumPy, pandas
- **NLP Models**: 
  - GSR/IMSR (General/Immediate Suicidal Risk)
  - Custom summarization model
  - Risk explanation model
- **API Integration**: LivePerson REST API

### **Frontend**
- **Framework**: React.js 18+
- **UI Library**: Material-UI (MUI)
- **State Management**: React Hooks
- **HTTP Client**: Axios
- **Build Tool**: Webpack

### **DevOps & Infrastructure**
- **Web Server**: Nginx (HTTPS)
- **Deployment**: BGU University Server
- **Version Control**: Git
- **API Testing**: Postman
- **OS**: Linux

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT (React.js)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Dashboard   │  │Conversations │  │ Admin Panel  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS (Nginx)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVER (Flask + Gunicorn)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              REST API Endpoints                       │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Risk AI    │  │ Summary AI   │  │Explanation AI│    │
│  │  (PyTorch)   │  │    Model     │  │    Model     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            SQLite Database (Predictions)              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │  LivePerson API    │
                    │  (Chat Platform)   │
                    └────────────────────┘
```

### **Data Flow**
1. **LivePerson API** → Server fetches conversation data every 5 seconds
2. **AI Processing** → NLP models analyze text for risk indicators
3. **Database** → Predictions and metadata stored in SQLite
4. **Real-Time Updates** → Frontend receives risk alerts via REST API
5. **Mobile Alerts** → High-risk cases trigger immediate notifications

---

## 🚀 Getting Started

### Prerequisites

```bash
# Python 3.8+
python --version

# Node.js 14+ and npm
node --version
npm --version

# Git
git --version
```

### Installation

#### 1️⃣ Clone the Repository
```bash
git clone https://github.com/omerdor001/Sahar-Online-Mental-Health-Support.git
cd Sahar-Online-Mental-Health-Support
```

#### 2️⃣ Backend Setup (ServerProject)

```bash
cd server_project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt 

# Set environment variables
export FLASK_APP=server.py
export FLASK_ENV=development
export LIVEPERSON_API_KEY=your_api_key_here


# Run Flask development server
python server.py
```

#### 3️⃣ Frontend Setup (ClientProject)

```bash
cd ../Client_Project production/app

# Install dependencies
npm install

# Run React development server
npm run dev
```

#### 4️⃣ Production Deployment (Nginx + Gunicorn)

```bash
# Install Nginx
sudo apt-get install nginx

# Configure Gunicorn
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app

# Configure Nginx (see nginx.conf in repo)
sudo systemctl restart nginx
```

### API Endpoints

```http
GET  /api/conversations              # Get all conversations
GET  /api/conversations/:id          # Get specific conversation
POST /api/analyze                    # Analyze conversation for risk
GET  /api/summary/:id                # Get conversation summary
POST /api/config                     # Update algorithm configuration
GET  /api/logs                       # Fetch system logs
```

---

## 📊 Project Impact

- 🌍 **200+ daily active users**
- 📈 **~85% prediction accuracy**
- ⏱️ **Real-time analysis** (<2 seconds per conversation)
- 🚨 **Immediate alerts** for high-risk cases
- 💬 **Thousands of conversations** analyzed since deployment

---

## 📧 Contact

**Omer Dor** - Full Stack Developer  
📧 Email: omerdor01@gmail.com  
💼 LinkedIn: [linkedin.com/in/omer-dor-548802339](https://www.linkedin.com/in/omer-dor-548802339/)  
🐙 GitHub: [@omerdor001](https://github.com/omerdor001)

**Project Link**: [https://github.com/omerdor001/Sahar-Online-Mental-Health-Support](https://github.com/omerdor001/Sahar-Online-Mental-Health-Support)

**Live Demo**: [https://omerdo1.wixsite.com/suicide-risk-assesso](https://omerdo1.wixsite.com/suicide-risk-assesso)

---

## 🙏 Acknowledgments

- [Sahar Organization](https://www.sahar.org.il/) for the opportunity to work on this life-saving project
- Ben-Gurion University Software Engineering Department
- LivePerson for API integration support
- All volunteers who use this system to help people in crisis


Made with ❤️ by the Sahar Development Team

</div>
