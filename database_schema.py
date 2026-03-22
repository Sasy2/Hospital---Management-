"""
Hospital Management System - Database Schema
This module creates and initializes the SQLite database with all necessary tables and sample data.
"""

import sqlite3
import random
from datetime import datetime, timedelta

def create_database(db_path='hospital_management.db'):
    """Create the complete hospital management database with schema and sample data"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    print("Creating database schema...")
    
    # Create all tables
    cursor.executescript("""
    /* ========== CORE ENTITIES ========== */
    
    -- Patients Table
    CREATE TABLE IF NOT EXISTS Patients (
        PatientID TEXT PRIMARY KEY,
        FirstName TEXT NOT NULL,
        MiddleName TEXT,
        LastName TEXT NOT NULL,
        DateOfBirth TEXT NOT NULL,
        Sex TEXT CHECK(Sex IN ('M', 'F', 'Other')) NOT NULL,
        Address TEXT,
        Phone TEXT NOT NULL,
        Email TEXT,
        GhanaCardID TEXT UNIQUE,
        LanguagePreference TEXT DEFAULT 'English',
        RegistrationDate TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CurrentStatus TEXT CHECK(CurrentStatus IN ('Active', 'Inactive', 'Deceased')) DEFAULT 'Active'
    );

    -- Emergency Contacts
    CREATE TABLE IF NOT EXISTS EmergencyContacts (
        ContactID TEXT PRIMARY KEY,
        PatientID TEXT NOT NULL,
        FirstName TEXT NOT NULL,
        MiddleName TEXT,
        LastName TEXT NOT NULL,
        Relationship TEXT NOT NULL,
        Phone TEXT NOT NULL,
        Email TEXT,
        Address TEXT,
        IsPrimaryContact INTEGER DEFAULT 0,
        FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE
    );

    /* ========== STAFF MANAGEMENT ========== */
    
    -- Doctors
    CREATE TABLE IF NOT EXISTS Doctors (
        DoctorID TEXT PRIMARY KEY,
        FirstName TEXT NOT NULL,
        MiddleName TEXT,
        LastName TEXT NOT NULL,
        DateOfBirth TEXT NOT NULL,
        Sex TEXT CHECK(Sex IN ('M', 'F', 'Other')) NOT NULL,
        Address TEXT,
        Phone TEXT NOT NULL,
        Email TEXT,
        GhanaCardID TEXT UNIQUE,
        Specialty TEXT NOT NULL,
        HireDate TEXT NOT NULL,
        IsActive INTEGER DEFAULT 1
    );

    -- Nurses
    CREATE TABLE IF NOT EXISTS Nurses (
        NurseID TEXT PRIMARY KEY,
        FirstName TEXT NOT NULL,
        MiddleName TEXT,
        LastName TEXT NOT NULL,
        DateOfBirth TEXT NOT NULL,
        Sex TEXT CHECK(Sex IN ('M', 'F', 'Other')) NOT NULL,
        Address TEXT,
        Phone TEXT NOT NULL,
        Email TEXT,
        GhanaCardID TEXT UNIQUE,
        Level TEXT NOT NULL,
        HireDate TEXT NOT NULL,
        IsActive INTEGER DEFAULT 1
    );

    -- Administrative Staff
    CREATE TABLE IF NOT EXISTS Admins (
        AdminID TEXT PRIMARY KEY,
        FirstName TEXT NOT NULL,
        MiddleName TEXT,
        LastName TEXT NOT NULL,
        DateOfBirth TEXT NOT NULL,
        Sex TEXT CHECK(Sex IN ('M', 'F', 'Other')) NOT NULL,
        Address TEXT,
        Phone TEXT NOT NULL,
        Email TEXT,
        GhanaCardID TEXT UNIQUE,
        HireDate TEXT NOT NULL,
        IsActive INTEGER DEFAULT 1
    );

    /* ========== FACILITY MANAGEMENT ========== */
    
    -- Wards
    CREATE TABLE IF NOT EXISTS Wards (
        WardID TEXT PRIMARY KEY,
        WardName TEXT NOT NULL,
        WardType TEXT NOT NULL,
        BuildingName TEXT NOT NULL,
        BuildingID TEXT,
        Capacity INTEGER DEFAULT 0
    );

    -- Rooms
    CREATE TABLE IF NOT EXISTS Rooms (
        RoomID TEXT PRIMARY KEY,
        WardID TEXT NOT NULL,
        FloorNumber INTEGER NOT NULL,
        Building TEXT NOT NULL,
        RoomNumber TEXT NOT NULL UNIQUE,
        Status INTEGER DEFAULT 1,
        Type TEXT CHECK(Type IN ('ICU', 'General', 'Private', 'Semi-Private', 'Emergency')) NOT NULL,
        FOREIGN KEY (WardID) REFERENCES Wards(WardID)
    );

    -- Beds
    CREATE TABLE IF NOT EXISTS Beds (
        BedID TEXT PRIMARY KEY,
        RoomID TEXT NOT NULL,
        BedNumber TEXT NOT NULL,
        Status INTEGER DEFAULT 1,
        FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID)
    );

    /* ========== VISIT & ADMISSION MANAGEMENT ========== */
    
    -- Visit Types
    CREATE TABLE IF NOT EXISTS VisitTypes (
        VisitTypeID TEXT PRIMARY KEY,
        VisitTypeName TEXT NOT NULL,
        Notes TEXT
    );

    -- Visits
    CREATE TABLE IF NOT EXISTS Visits (
        VisitID TEXT PRIMARY KEY,
        PatientID TEXT NOT NULL,
        VisitTypeID TEXT,
        VisitDate TEXT NOT NULL,
        Description TEXT,
        Status TEXT CHECK(Status IN ('Scheduled', 'In Progress', 'Completed', 'Cancelled')) DEFAULT 'Scheduled',
        FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
        FOREIGN KEY (VisitTypeID) REFERENCES VisitTypes(VisitTypeID)
    );

    -- Admissions
    CREATE TABLE IF NOT EXISTS Admissions (
        AdmissionID TEXT PRIMARY KEY,
        PatientID TEXT NOT NULL,
        VisitID TEXT NOT NULL,
        NurseID TEXT NOT NULL,
        BedID TEXT NOT NULL,
        AdmissionStatus INTEGER DEFAULT 1,
        AdmissionDateTime TEXT NOT NULL,
        ExpectedDischarge TEXT,
        DischargeDateTime TEXT,
        DischargeNotes TEXT,
        FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
        FOREIGN KEY (VisitID) REFERENCES Visits(VisitID),
        FOREIGN KEY (NurseID) REFERENCES Nurses(NurseID),
        FOREIGN KEY (BedID) REFERENCES Beds(BedID)
    );

    /* ========== MEDICAL RECORDS ========== */
    
    -- Diagnoses (ICD-10 codes)
    CREATE TABLE IF NOT EXISTS Diagnoses (
        DiagnosisID TEXT PRIMARY KEY,
        ICD10Code TEXT NOT NULL,
        Description TEXT NOT NULL,
        IsChronic INTEGER DEFAULT 0,
        Severity TEXT CHECK(Severity IN ('Mild', 'Moderate', 'Severe', 'Critical'))
    );

    -- Patient Diagnoses
    CREATE TABLE IF NOT EXISTS PatientDiagnoses (
        PDiagnosisID TEXT PRIMARY KEY,
        DiagnosisID TEXT NOT NULL,
        VisitID TEXT NOT NULL,
        DoctorID TEXT NOT NULL,
        DiagnosisDetails TEXT,
        DateTime TEXT NOT NULL,
        FOREIGN KEY (DiagnosisID) REFERENCES Diagnoses(DiagnosisID),
        FOREIGN KEY (VisitID) REFERENCES Visits(VisitID),
        FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID)
    );

    -- Treatments
    CREATE TABLE IF NOT EXISTS Treatments (
        TreatmentID TEXT PRIMARY KEY,
        PDiagnosisID TEXT NOT NULL,
        VisitID TEXT NOT NULL,
        TreatmentPlan TEXT,
        Notes TEXT,
        StartDate TEXT,
        EndDate TEXT,
        Status TEXT CHECK(Status IN ('Planned', 'In Progress', 'Completed', 'Cancelled')) DEFAULT 'Planned',
        FOREIGN KEY (PDiagnosisID) REFERENCES PatientDiagnoses(PDiagnosisID),
        FOREIGN KEY (VisitID) REFERENCES Visits(VisitID)
    );

    -- Vitals
    CREATE TABLE IF NOT EXISTS Vitals (
        VitalID TEXT PRIMARY KEY,
        VisitID TEXT NOT NULL,
        Temperature REAL,
        BloodPressure TEXT,
        Pulse INTEGER,
        OxygenSaturation INTEGER,
        Weight REAL,
        Height REAL,
        BMI REAL,
        DateMeasured TEXT NOT NULL,
        FOREIGN KEY (VisitID) REFERENCES Visits(VisitID)
    );

    /* ========== PHARMACY & MEDICATIONS ========== */
    
    -- Drugs
    CREATE TABLE IF NOT EXISTS Drugs (
        DrugID TEXT PRIMARY KEY,
        DrugName TEXT NOT NULL,
        DrugPrice REAL NOT NULL,
        DrugDescription TEXT,
        PharmaceuticalCompany TEXT,
        StockQuantity INTEGER DEFAULT 0,
        ReorderLevel INTEGER DEFAULT 10
    );

    -- Drugs Administered
    CREATE TABLE IF NOT EXISTS DrugAdministered (
        DrugAdministeredID TEXT PRIMARY KEY,
        VisitID TEXT NOT NULL,
        DrugID TEXT NOT NULL,
        Quantity INTEGER NOT NULL,
        Dosage TEXT,
        Frequency TEXT,
        Notes TEXT,
        DrugDateTime TEXT NOT NULL,
        FOREIGN KEY (VisitID) REFERENCES Visits(VisitID),
        FOREIGN KEY (DrugID) REFERENCES Drugs(DrugID)
    );

    /* ========== SERVICES & BILLING ========== */
    
    -- Services
    CREATE TABLE IF NOT EXISTS Services (
        ServiceID TEXT PRIMARY KEY,
        ServiceName TEXT NOT NULL,
        ServicePrice REAL NOT NULL,
        SDescription TEXT,
        Category TEXT
    );

    -- Service Rendered
    CREATE TABLE IF NOT EXISTS ServiceRendered (
        ServiceRenderedID TEXT PRIMARY KEY,
        VisitID TEXT NOT NULL,
        ServiceID TEXT NOT NULL,
        Quantity INTEGER DEFAULT 1,
        Notes TEXT,
        ServiceDateTime TEXT NOT NULL,
        FOREIGN KEY (VisitID) REFERENCES Visits(VisitID),
        FOREIGN KEY (ServiceID) REFERENCES Services(ServiceID)
    );

    -- Bills
    CREATE TABLE IF NOT EXISTS Bills (
        BillID TEXT PRIMARY KEY,
        VisitID TEXT NOT NULL,
        SubtotalAmount REAL NOT NULL,
        TaxAmount REAL DEFAULT 0,
        DiscountAmount REAL DEFAULT 0,
        Total REAL NOT NULL,
        BillDate TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        Status TEXT CHECK(Status IN ('Pending', 'Partially Paid', 'Paid', 'Cancelled')) DEFAULT 'Pending',
        FOREIGN KEY (VisitID) REFERENCES Visits(VisitID)
    );

    -- Payments
    CREATE TABLE IF NOT EXISTS Payments (
        PaymentID TEXT PRIMARY KEY,
        BillID TEXT NOT NULL,
        Amount REAL NOT NULL,
        PaymentMethod TEXT CHECK(PaymentMethod IN ('Cash', 'Credit Card', 'Debit Card', 'Mobile Money', 'Insurance', 'Bank Transfer')) NOT NULL,
        ProcessedBy TEXT NOT NULL,
        TransactionRef TEXT,
        Date TEXT NOT NULL,
        FOREIGN KEY (BillID) REFERENCES Bills(BillID),
        FOREIGN KEY (ProcessedBy) REFERENCES Admins(AdminID)
    );

    /* ========== REFERRALS & PARTNERSHIPS ========== */
    
    -- Partner Hospitals
    CREATE TABLE IF NOT EXISTS PartnerHospitals (
        PartnerHospitalID TEXT PRIMARY KEY,
        HospitalName TEXT NOT NULL,
        Address TEXT,
        PhoneNumber TEXT,
        Email TEXT,
        Specialties TEXT
    );

    -- Referrals
    CREATE TABLE IF NOT EXISTS Referrals (
        ReferralID TEXT PRIMARY KEY,
        PDiagnosisID TEXT NOT NULL,
        PartnerHospitalID TEXT NOT NULL,
        ReferralReason TEXT NOT NULL,
        TreatmentID TEXT,
        ServiceID TEXT,
        Date TEXT NOT NULL,
        Status TEXT CHECK(Status IN ('Pending', 'Accepted', 'Completed', 'Rejected')) DEFAULT 'Pending',
        FOREIGN KEY (PDiagnosisID) REFERENCES PatientDiagnoses(PDiagnosisID),
        FOREIGN KEY (PartnerHospitalID) REFERENCES PartnerHospitals(PartnerHospitalID),
        FOREIGN KEY (TreatmentID) REFERENCES Treatments(TreatmentID),
        FOREIGN KEY (ServiceID) REFERENCES Services(ServiceID)
    );

    /* ========== AUDIT & LOGGING ========== */
    
    -- Audit Log
    CREATE TABLE IF NOT EXISTS AuditLog (
        LogID INTEGER PRIMARY KEY AUTOINCREMENT,
        TableName TEXT NOT NULL,
        RecordID TEXT NOT NULL,
        ActionType TEXT CHECK(ActionType IN ('INSERT', 'UPDATE', 'DELETE')) NOT NULL,
        ActionBy TEXT NOT NULL,
        ActionDate TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        OldValues TEXT,
        NewValues TEXT
    );

    /* ========== INDEXES FOR PERFORMANCE ========== */
    
    CREATE INDEX IF NOT EXISTS idx_patients_name ON Patients(LastName, FirstName);
    CREATE INDEX IF NOT EXISTS idx_patients_status ON Patients(CurrentStatus);
    CREATE INDEX IF NOT EXISTS idx_visits_patient ON Visits(PatientID);
    CREATE INDEX IF NOT EXISTS idx_visits_date ON Visits(VisitDate);
    CREATE INDEX IF NOT EXISTS idx_admissions_patient ON Admissions(PatientID);
    CREATE INDEX IF NOT EXISTS idx_bills_status ON Bills(Status);
    CREATE INDEX IF NOT EXISTS idx_diagnoses_icd ON Diagnoses(ICD10Code);
    """)
    
    conn.commit()
    print("✓ Database schema created successfully")
    
    return conn

def insert_sample_data(conn):
    """Insert comprehensive sample data into the database"""
    cursor = conn.cursor()
    
    print("Inserting sample data...")
    
    cursor.executescript("""
    -- Sample Patients
    INSERT OR IGNORE INTO Patients (PatientID, FirstName, MiddleName, LastName, DateOfBirth, Sex, Address, Phone, Email, GhanaCardID, RegistrationDate)
    VALUES
    ('PAT00001', 'Kwame', 'Kofi', 'Mensah', '1985-03-15', 'M', 'Accra, Greater Accra', '+233241234567', 'kwame.mensah@email.com', 'GHA-123456789-1', '2023-01-10'),
    ('PAT00002', 'Akua', 'Abena', 'Osei', '1990-07-22', 'F', 'Kumasi, Ashanti', '+233242345678', 'akua.osei@email.com', 'GHA-234567890-2', '2023-01-15'),
    ('PAT00003', 'Yaw', 'Kwabena', 'Boateng', '1978-11-05', 'M', 'Takoradi, Western', '+233243456789', 'yaw.boateng@email.com', 'GHA-345678901-3', '2023-02-01'),
    ('PAT00004', 'Ama', 'Afua', 'Addo', '1995-02-14', 'F', 'Cape Coast, Central', '+233244567890', 'ama.addo@email.com', 'GHA-456789012-4', '2023-02-10'),
    ('PAT00005', 'Kofi', 'Kwesi', 'Asante', '1982-09-30', 'M', 'Tema, Greater Accra', '+233245678901', 'kofi.asante@email.com', 'GHA-567890123-5', '2023-03-01');

    -- Sample Doctors
    INSERT OR IGNORE INTO Doctors (DoctorID, FirstName, LastName, DateOfBirth, Sex, Phone, Email, Specialty, HireDate)
    VALUES
    ('DOC001', 'Dr. Kwame', 'Nkrumah', '1975-05-20', 'M', '+233201111111', 'k.nkrumah@hospital.com', 'General Medicine', '2020-01-15'),
    ('DOC002', 'Dr. Akosua', 'Agyeman', '1980-08-12', 'F', '+233202222222', 'a.agyeman@hospital.com', 'Pediatrics', '2019-06-01'),
    ('DOC003', 'Dr. Kofi', 'Annan', '1978-03-25', 'M', '+233203333333', 'k.annan@hospital.com', 'Cardiology', '2021-03-10'),
    ('DOC004', 'Dr. Ama', 'Darko', '1985-11-30', 'F', '+233204444444', 'a.darko@hospital.com', 'Obstetrics & Gynecology', '2022-01-20');

    -- Sample Nurses
    INSERT OR IGNORE INTO Nurses (NurseID, FirstName, LastName, DateOfBirth, Sex, Phone, Email, Level, HireDate)
    VALUES
    ('NUR001', 'Grace', 'Owusu', '1988-04-10', 'F', '+233211111111', 'g.owusu@hospital.com', 'Senior', '2018-05-01'),
    ('NUR002', 'Emmanuel', 'Mensah', '1992-07-15', 'M', '+233212222222', 'e.mensah@hospital.com', 'Staff Nurse', '2020-08-15'),
    ('NUR003', 'Abena', 'Sarpong', '1990-01-25', 'F', '+233213333333', 'a.sarpong@hospital.com', 'Staff Nurse', '2021-02-01');

    -- Sample Admins
    INSERT OR IGNORE INTO Admins (AdminID, FirstName, LastName, DateOfBirth, Sex, Phone, Email, HireDate)
    VALUES
    ('ADM001', 'Samuel', 'Owusu', '1985-06-12', 'M', '+233221111111', 's.owusu@hospital.com', '2019-01-01'),
    ('ADM002', 'Esther', 'Adom', '1990-09-08', 'F', '+233222222222', 'e.adom@hospital.com', '2020-03-15');

    -- Sample Wards
    INSERT OR IGNORE INTO Wards (WardID, WardName, WardType, BuildingName, Capacity)
    VALUES
    ('WRD001', 'General Ward A', 'General', 'Main Building', 20),
    ('WRD002', 'ICU Ward', 'ICU', 'Main Building', 10),
    ('WRD003', 'Maternity Ward', 'Maternity', 'West Wing', 15),
    ('WRD004', 'Pediatric Ward', 'Pediatric', 'East Wing', 12);

    -- Sample Rooms
    INSERT OR IGNORE INTO Rooms (RoomID, WardID, FloorNumber, Building, RoomNumber, Type)
    VALUES
    ('RM001', 'WRD001', 1, 'Main Building', 'G101', 'General'),
    ('RM002', 'WRD001', 1, 'Main Building', 'G102', 'General'),
    ('RM003', 'WRD002', 2, 'Main Building', 'ICU201', 'ICU'),
    ('RM004', 'WRD003', 1, 'West Wing', 'MAT101', 'Private'),
    ('RM005', 'WRD004', 1, 'East Wing', 'PED101', 'General');

    -- Sample Beds
    INSERT OR IGNORE INTO Beds (BedID, RoomID, BedNumber)
    VALUES
    ('BED001', 'RM001', 'B1'),
    ('BED002', 'RM001', 'B2'),
    ('BED003', 'RM002', 'B1'),
    ('BED004', 'RM003', 'B1'),
    ('BED005', 'RM004', 'B1'),
    ('BED006', 'RM005', 'B1'),
    ('BED007', 'RM005', 'B2');

    -- Sample Visit Types
    INSERT OR IGNORE INTO VisitTypes (VisitTypeID, VisitTypeName, Notes)
    VALUES
    ('VT001', 'Regular Checkup', 'Routine health check'),
    ('VT002', 'Emergency', 'Urgent medical attention'),
    ('VT003', 'Follow-up', 'Post-treatment follow-up'),
    ('VT004', 'Specialist', 'Specialist consultation'),
    ('VT005', 'Prenatal', 'Pregnancy-related visit');

    -- Sample Diagnoses
    INSERT OR IGNORE INTO Diagnoses (DiagnosisID, ICD10Code, Description, IsChronic, Severity)
    VALUES
    ('DX001', 'E11.65', 'Type 2 diabetes mellitus with hyperglycemia', 1, 'Moderate'),
    ('DX002', 'I10', 'Essential (primary) hypertension', 1, 'Moderate'),
    ('DX003', 'J18.9', 'Pneumonia, unspecified organism', 0, 'Severe'),
    ('DX004', 'J45.90', 'Unspecified asthma, uncomplicated', 1, 'Mild'),
    ('DX005', 'M54.5', 'Low back pain', 0, 'Mild'),
    ('DX006', 'O80', 'Encounter for full-term uncomplicated delivery', 0, 'Moderate'),
    ('DX007', 'A09', 'Infectious gastroenteritis and colitis', 0, 'Mild'),
    ('DX008', 'E78.5', 'Hyperlipidemia, unspecified', 1, 'Moderate');

    -- Sample Services
    INSERT OR IGNORE INTO Services (ServiceID, ServiceName, ServicePrice, SDescription, Category)
    VALUES
    ('SRV001', 'General Consultation', 50.00, 'Doctor consultation', 'Consultation'),
    ('SRV002', 'Emergency Visit', 100.00, 'Emergency room visit', 'Emergency'),
    ('SRV003', 'X-Ray', 80.00, 'Standard x-ray imaging', 'Imaging'),
    ('SRV004', 'Ultrasound', 120.00, 'Diagnostic ultrasound', 'Imaging'),
    ('SRV005', 'Blood Test', 35.00, 'Basic metabolic panel', 'Laboratory'),
    ('SRV006', 'CT Scan', 250.00, 'Computed tomography', 'Imaging'),
    ('SRV007', 'Normal Delivery', 500.00, 'Natural childbirth delivery', 'Maternity');

    -- Sample Drugs
    INSERT OR IGNORE INTO Drugs (DrugID, DrugName, DrugPrice, DrugDescription, PharmaceuticalCompany, StockQuantity)
    VALUES
    ('DRG001', 'Paracetamol 500mg', 5.00, 'Pain reliever and fever reducer', 'GSK', 500),
    ('DRG002', 'Amoxicillin 500mg', 8.50, 'Antibiotic', 'Pfizer', 300),
    ('DRG003', 'Atorvastatin 20mg', 10.00, 'Cholesterol medication', 'Pfizer', 200),
    ('DRG004', 'Ibuprofen 400mg', 7.50, 'NSAID pain reliever', 'Johnson & Johnson', 400),
    ('DRG005', 'Lisinopril 10mg', 12.00, 'ACE inhibitor for hypertension', 'AstraZeneca', 250),
    ('DRG006', 'Metformin 850mg', 9.80, 'Diabetes medication', 'Merck', 350),
    ('DRG007', 'Salbutamol Inhaler', 18.50, 'Bronchodilator for asthma', 'Novartis', 100);

    -- Sample Visits
    INSERT OR IGNORE INTO Visits (VisitID, PatientID, VisitTypeID, VisitDate, Description, Status)
    VALUES
    ('VIS20230501001', 'PAT00001', 'VT001', '2023-05-01 09:30:00', 'Routine diabetes checkup', 'Completed'),
    ('VIS20230502001', 'PAT00002', 'VT002', '2023-05-02 14:15:00', 'Severe abdominal pain', 'Completed'),
    ('VIS20230503001', 'PAT00003', 'VT003', '2023-05-03 11:00:00', 'Post-surgical follow-up', 'Completed'),
    ('VIS20230504001', 'PAT00004', 'VT005', '2023-05-04 10:30:00', 'First prenatal visit', 'Completed'),
    ('VIS20230505001', 'PAT00005', 'VT002', '2023-05-05 08:45:00', 'Severe headache and fever', 'Completed');

    -- Sample Vitals
    INSERT OR IGNORE INTO Vitals (VitalID, VisitID, Temperature, BloodPressure, Pulse, OxygenSaturation, Weight, Height, BMI, DateMeasured)
    VALUES
    ('VIT00001', 'VIS20230501001', 36.8, '135/85', 72, 98, 75.5, 175.0, 24.7, '2023-05-01 09:45:00'),
    ('VIT00002', 'VIS20230502001', 38.5, '140/90', 95, 92, 68.0, 168.0, 24.1, '2023-05-02 14:30:00'),
    ('VIT00003', 'VIS20230503001', 37.2, '130/85', 78, 97, 80.2, 182.0, 24.2, '2023-05-03 11:15:00'),
    ('VIT00004', 'VIS20230504001', 36.5, '110/70', 68, 99, 62.3, 165.0, 22.9, '2023-05-04 10:45:00'),
    ('VIT00005', 'VIS20230505001', 38.9, '145/92', 92, 95, 75.0, 178.0, 23.7, '2023-05-05 09:00:00');

    -- Sample Patient Diagnoses
    INSERT OR IGNORE INTO PatientDiagnoses (PDiagnosisID, DiagnosisID, VisitID, DoctorID, DiagnosisDetails, DateTime)
    VALUES
    ('PDIAG00001', 'DX001', 'VIS20230501001', 'DOC001', 'Elevated blood sugar levels, requires insulin adjustment', '2023-05-01 10:00:00'),
    ('PDIAG00002', 'DX002', 'VIS20230501001', 'DOC001', 'Blood pressure 135/85, continue medication', '2023-05-01 10:05:00'),
    ('PDIAG00003', 'DX003', 'VIS20230502001', 'DOC002', 'Fever, cough, chest pain - bacterial pneumonia', '2023-05-02 15:00:00'),
    ('PDIAG00004', 'DX004', 'VIS20230503001', 'DOC003', 'Wheezing and shortness of breath', '2023-05-03 11:30:00'),
    ('PDIAG00005', 'DX006', 'VIS20230504001', 'DOC004', 'Healthy pregnancy, 12 weeks', '2023-05-04 11:00:00');

    -- Sample Treatments
    INSERT OR IGNORE INTO Treatments (TreatmentID, PDiagnosisID, VisitID, TreatmentPlan, Notes, StartDate, Status)
    VALUES
    ('TRT00001', 'PDIAG00001', 'VIS20230501001', 'Adjust insulin dosage', 'Monitor blood sugar twice daily', '2023-05-01', 'Completed'),
    ('TRT00002', 'PDIAG00002', 'VIS20230501001', 'Continue Lisinopril 10mg daily', 'Check BP weekly', '2023-05-01', 'In Progress'),
    ('TRT00003', 'PDIAG00003', 'VIS20230502001', 'IV antibiotics and oxygen therapy', 'Admit for observation', '2023-05-02', 'Completed'),
    ('TRT00004', 'PDIAG00004', 'VIS20230503001', 'Inhaler therapy', 'Use as needed', '2023-05-03', 'In Progress'),
    ('TRT00005', 'PDIAG00005', 'VIS20230504001', 'Prenatal vitamins and monitoring', 'Monthly checkups', '2023-05-04', 'In Progress');

    -- Sample Bills
    INSERT OR IGNORE INTO Bills (BillID, VisitID, SubtotalAmount, TaxAmount, Total, Status)
    VALUES
    ('BIL00001', 'VIS20230501001', 85.00, 8.50, 93.50, 'Paid'),
    ('BIL00002', 'VIS20230502001', 230.00, 23.00, 253.00, 'Paid'),
    ('BIL00003', 'VIS20230503001', 50.00, 5.00, 55.00, 'Paid'),
    ('BIL00004', 'VIS20230504001', 155.00, 15.50, 170.50, 'Paid'),
    ('BIL00005', 'VIS20230505001', 100.00, 10.00, 110.00, 'Pending');

    -- Sample Payments
    INSERT OR IGNORE INTO Payments (PaymentID, BillID, Amount, PaymentMethod, ProcessedBy, TransactionRef, Date)
    VALUES
    ('PAY00001', 'BIL00001', 93.50, 'Cash', 'ADM001', 'CASH20230501001', '2023-05-01 11:00:00'),
    ('PAY00002', 'BIL00002', 150.00, 'Insurance', 'ADM001', 'INS20230502001', '2023-05-02 16:00:00'),
    ('PAY00003', 'BIL00002', 103.00, 'Credit Card', 'ADM002', 'CC20230502002', '2023-05-03 10:00:00'),
    ('PAY00004', 'BIL00003', 55.00, 'Mobile Money', 'ADM002', 'MM20230503001', '2023-05-03 12:00:00'),
    ('PAY00005', 'BIL00004', 170.50, 'Cash', 'ADM001', 'CASH20230504001', '2023-05-04 12:30:00');
    """)
    
    conn.commit()
    print("✓ Sample data inserted successfully")

def initialize_database():
    """Main function to create and initialize the database"""
    print("\n" + "="*60)
    print("Hospital Management System - Database Initialization")
    print("="*60 + "\n")
    
    conn = create_database()
    insert_sample_data(conn)
    
    # Verify database
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Patients")
    patient_count = cursor.fetchone()[0]
    
    print(f"\n✓ Database initialized successfully!")
    print(f"  - {patient_count} patients registered")
    print(f"  - Database file: hospital_management.db")
    print("\n" + "="*60 + "\n")
    
    conn.close()
    return True

if __name__ == "__main__":
    initialize_database()
