# 🏥 Hospital Management System

A comprehensive hospital management system built with Python, SQLite, and Streamlit, featuring AI-powered medical insights using Google's Generative AI.

## 📋 Overview

This project implements a full-featured hospital management system that handles patient records, appointments, treatments, medical staff, room assignments, and more. The system includes an intelligent chatbot for medical queries and comprehensive reporting capabilities.

## ✨ Features

### Core Functionality
- **Patient Management**: Register, update, and track patient information
- **Appointment Scheduling**: Book, view, and manage patient appointments
- **Treatment Tracking**: Record and monitor patient treatments and costs
- **Medical Staff Management**: Manage doctors, nurses, and their specializations
- **Room & Bed Allocation**: Assign patients to rooms and track bed availability
- **Pharmacy Integration**: Track medications and prescriptions
- **Medical Records**: Store and retrieve patient diagnoses and test results

### Advanced Features
- **AI Medical Chatbot**: Get medical information and answers using Google's Generative AI
- **Interactive Dashboard**: Real-time hospital statistics and visualizations
- **Analytics & Reports**: 
  - Patient demographics analysis
  - Appointment and visit statistics
  - Diagnosis frequency analysis
  - Treatment effectiveness reports
  - Financial summaries and payment tracking
  - Doctor performance metrics
- **Search Functionality**: Quick search across patients, doctors, and appointments

## 🛠️ Technology Stack

- **Database**: SQLite3
- **Backend**: Python 3.8+
- **Frontend**: Streamlit
- **AI Integration**: Google Generative AI (Gemini)
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Plotly
- **Environment Management**: python-dotenv

## 📂 Project Structure

```
hospital-management-system/
├── app.py                      # Main Streamlit application
├── database_schema.py          # Database creation and initialization
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── SETUP_GUIDE.md            # Detailed setup instructions
├── CONTRIBUTING.md           # Contribution guidelines
├── TODO.md                   # Future enhancements
└── LICENSE                   # MIT License
```

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Google AI API Key

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hospital-management-system.git
   cd hospital-management-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```bash
   GOOGLE_API_KEY=your_google_ai_api_key_here
   ```
   
   Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

4. **Initialize the database**
   ```bash
   python database_schema.py
   ```
   
   This creates `hospital_management.db` with all tables and sample data

5. **Run the application**
   ```bash
   streamlit run app.py
   ```
   
   The app will open in your browser at `http://localhost:8501`

## 🚀 Usage

### Main Features

**Dashboard** 🏠
- View key hospital metrics at a glance
- Monitor active patients, visits, and admissions
- Track financial performance
- Visualize visit types and medication trends

**AI Assistant** 💬
- Ask questions in natural language
- Get insights about patient data
- Query diagnoses, treatments, and statistics
- Receive AI-powered medical information

**Patient Management** 👥
- View all registered patients
- Add new patients with complete details
- Search patients by name, ID, or phone
- Track patient status and history

**Appointment Management** 📅
- View all scheduled visits
- Schedule new appointments
- Track visit types and statuses
- Manage follow-ups

**Reports & Analytics** 📊
- Patient demographics analysis
- Diagnosis frequency reports
- Financial summaries
- Payment method breakdowns
- Custom data visualizations

## 🗄️ Database Schema

The system uses a normalized relational database with 20+ tables including:

**Core Tables:**
- Patients, EmergencyContacts
- Doctors, Nurses, Admins
- Visits, Admissions
- Diagnoses, Treatments
- Medications, Prescriptions

**Support Tables:**
- Wards, Rooms, Beds
- Services, Bills, Payments
- Partner Hospitals, Referrals
- Audit Logs

All tables include proper foreign key relationships and constraints.

## 🔒 Security Considerations

⚠️ **Important**: This is a demonstration project. For production use:

- ✅ Use environment variables for all API keys (never commit them!)
- ✅ Implement proper authentication and authorization
- ✅ Add data encryption for sensitive medical information
- ✅ Implement comprehensive logging and audit trails
- ✅ Follow HIPAA compliance guidelines (if applicable)
- ✅ Use HTTPS for all communications
- ✅ Regular security audits and updates

## 📸 Screenshots

_Add screenshots of your application here_

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Quick steps:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Future Enhancements

See [TODO.md](TODO.md) for the complete roadmap. Highlights include:

- [ ] User authentication system
- [ ] Export reports to PDF/Excel
- [ ] Email notifications
- [ ] Mobile app
- [ ] Telemedicine features
- [ ] Advanced ML predictions


- Google Generative AI for the medical chatbot functionality
- Streamlit for the intuitive web interface
- Plotly for beautiful data visualizations
- The open-source community

## 📧 Support

For questions or issues:
- Open an issue on GitHub
- Check the [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions
- Review existing issues and discussions

---

⭐ **If you find this project useful, please consider giving it a star!**
