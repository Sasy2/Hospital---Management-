"""
Hospital Management System - Main Application
A comprehensive hospital management system with AI-powered insights
"""

import streamlit as st
import pandas as pd
import sqlite3
import json
import google.generativeai as genai
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ========== DATABASE FUNCTIONS ==========

def init_database():
    """Initialize the SQLite database connection"""
    try:
        conn = sqlite3.connect('hospital_management.db', check_same_thread=False)
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Verify the connection by checking if Patients table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Patients'")
        if not cursor.fetchone():
            st.error("⚠️ Database not initialized. Please run database_schema.py first!")
            st.code("python database_schema.py", language="bash")
            return None
            
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection error: {str(e)}")
        return None

def get_database_schema(conn):
    """Extract schema information from SQLite database"""
    schema = {"tables": {}, "foreign_keys": []}
    
    try:
        # Get all tables
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
        
        for table in tables['name']:
            # Get columns
            columns = pd.read_sql(f"PRAGMA table_info({table});", conn)
            schema["tables"][table] = {
                "columns": columns[['name', 'type']].to_dict('records'),
                "sample_data": pd.read_sql(f"SELECT * FROM {table} LIMIT 3", conn).to_dict('records')
            }
            
            # Get foreign keys
            fks = pd.read_sql(f"PRAGMA foreign_key_list({table});", conn)
            for _, fk in fks.iterrows():
                schema["foreign_keys"].append({
                    "from_table": table,
                    "from_column": fk['from'],
                    "to_table": fk['table'],
                    "to_column": fk['to']
                })
                
        return schema
    except Exception as e:
        st.error(f"Error getting database schema: {str(e)}")
        return None

# ========== AI FUNCTIONS ==========

def configure_gemini():
    """Configure the Gemini model"""
    # Get API key from environment variable or use default (for testing only!)
    api_key = os.getenv('GOOGLE_API_KEY', 'AIzaSyAOHarK6-l2nH-zfaM5WwQyGVEzQLP7WHU')
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def ask_ai_question(model, conn, schema: dict, question: str) -> dict:
    """Ask any question about the database and get clean response"""
    prompt = f"""
    You are a helpful assistant for a hospital management system database.
    Database schema: {json.dumps(schema['tables'], indent=2)}
    Foreign keys: {json.dumps(schema['foreign_keys'], indent=2)}

    When answering questions:
    1. For simple questions, just return the answer in plain text
    2. For data requests, provide insights and recommendations
    3. Be conversational and helpful
    4. Format dates nicely (e.g., "March 15, 1985")
    5. Keep responses concise and focused on what was asked
    6. If medical advice is needed, emphasize consulting a real doctor

    Current question: "{question}"
    """

    response = model.generate_content(prompt)
    try:
        return {"response": response.text}
    except Exception as e:
        return {"response": f"Error generating response: {str(e)}"}

def execute_query(conn, query: str):
    """Execute SQL query and return results"""
    try:
        if query.strip().upper().startswith("SELECT"):
            return pd.read_sql(query, conn)
        else:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            return f"Operation completed. Rows affected: {cursor.rowcount}"
    except Exception as e:
        return f"Error executing query: {str(e)}"

# ========== UI COMPONENTS ==========

def setup_ui():
    """Configure Streamlit interface"""
    st.set_page_config(
        page_title="Hospital Management System",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 {
            font-size: 2.5rem;
            margin: 0;
            font-weight: 700;
        }
        .header p {
            font-size: 1.1rem;
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            font-size: 0.9rem;
        }
        .chat-message {
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            max-width: 80%;
        }
        .user-message {
            background-color: #e3f2fd;
            margin-left: auto;
            border-left: 4px solid #2196F3;
        }
        .assistant-message {
            background-color: #f5f5f5;
            margin-right: auto;
            border-left: 4px solid #667eea;
        }
        .stButton>button {
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 500;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.5rem;
        }
    </style>
    <div class="header">
        <h1>🏥 Hospital Management System</h1>
        <p>Comprehensive Patient Data Management with AI-Powered Insights</p>
    </div>
    """, unsafe_allow_html=True)

def display_chat_message(role, content):
    """Display a chat message with appropriate styling"""
    with st.container():
        if role == "user":
            st.markdown(f"""
            <div class='chat-message user-message'>
                <b>👤 You:</b><br>{content}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='chat-message assistant-message'>
                <b>🤖 AI Assistant:</b><br>{content}
            </div>
            """, unsafe_allow_html=True)

def display_dashboard(conn):
    """Display hospital dashboard with key metrics"""
    st.header("📊 Hospital Dashboard")
    
    # Get key statistics
    try:
        # Patient statistics
        total_patients = pd.read_sql("SELECT COUNT(*) as count FROM Patients WHERE CurrentStatus='Active'", conn).iloc[0]['count']
        total_visits = pd.read_sql("SELECT COUNT(*) as count FROM Visits", conn).iloc[0]['count']
        active_admissions = pd.read_sql("SELECT COUNT(*) as count FROM Admissions WHERE AdmissionStatus=1", conn).iloc[0]['count']
        
        # Financial statistics
        total_revenue = pd.read_sql("SELECT SUM(Total) as total FROM Bills WHERE Status='Paid'", conn).iloc[0]['total'] or 0
        pending_bills = pd.read_sql("SELECT SUM(Total) as total FROM Bills WHERE Status='Pending'", conn).iloc[0]['total'] or 0
        
        # Display metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Active Patients", f"{total_patients:,}")
        with col2:
            st.metric("Total Visits", f"{total_visits:,}")
        with col3:
            st.metric("Current Admissions", f"{active_admissions:,}")
        with col4:
            st.metric("Revenue (Paid)", f"GH₵ {total_revenue:,.2f}")
        with col5:
            st.metric("Pending Bills", f"GH₵ {pending_bills:,.2f}")
        
        st.markdown("---")
        
        # Recent activity charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Visits by Type")
            visits_by_type = pd.read_sql("""
                SELECT vt.VisitTypeName, COUNT(v.VisitID) as Count
                FROM Visits v
                JOIN VisitTypes vt ON v.VisitTypeID = vt.VisitTypeID
                GROUP BY vt.VisitTypeName
                ORDER BY Count DESC
            """, conn)
            
            if not visits_by_type.empty:
                fig = px.pie(visits_by_type, values='Count', names='VisitTypeName', 
                           color_discrete_sequence=px.colors.sequential.Viridis)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No visit data available")
        
        with col2:
            st.subheader("💊 Top Prescribed Medications")
            top_drugs = pd.read_sql("""
                SELECT d.DrugName, COUNT(da.DrugAdministeredID) as Prescriptions
                FROM Drugs d
                JOIN DrugAdministered da ON d.DrugID = da.DrugID
                GROUP BY d.DrugName
                ORDER BY Prescriptions DESC
                LIMIT 5
            """, conn)
            
            if not top_drugs.empty:
                fig = px.bar(top_drugs, x='DrugName', y='Prescriptions',
                           color='Prescriptions', 
                           color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No prescription data available")
        
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")

# ========== DATA MANAGEMENT FUNCTIONS ==========

def manage_patients(conn):
    """Patient management interface"""
    st.header("👥 Patient Management")
    
    tab1, tab2, tab3 = st.tabs(["View Patients", "Add Patient", "Search Patient"])
    
    with tab1:
        st.subheader("All Patients")
        patients = pd.read_sql("""
            SELECT PatientID, FirstName, LastName, DateOfBirth, Sex, 
                   Phone, Email, CurrentStatus
            FROM Patients
            ORDER BY RegistrationDate DESC
        """, conn)
        st.dataframe(patients, use_container_width=True)
    
    with tab2:
        st.subheader("Register New Patient")
        with st.form("new_patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name*")
                last_name = st.text_input("Last Name*")
                dob = st.date_input("Date of Birth*")
                sex = st.selectbox("Sex*", ["M", "F", "Other"])
            
            with col2:
                phone = st.text_input("Phone Number*")
                email = st.text_input("Email")
                address = st.text_area("Address")
                ghana_card = st.text_input("Ghana Card ID")
            
            submitted = st.form_submit_button("Register Patient")
            
            if submitted:
                if first_name and last_name and phone:
                    try:
                        # Generate Patient ID
                        cursor = conn.cursor()
                        cursor.execute("SELECT MAX(PatientID) FROM Patients")
                        last_id = cursor.fetchone()[0]
                        if last_id:
                            new_id = f"PAT{int(last_id[3:]) + 1:05d}"
                        else:
                            new_id = "PAT00001"
                        
                        # Insert patient
                        cursor.execute("""
                            INSERT INTO Patients (PatientID, FirstName, LastName, DateOfBirth, 
                                                Sex, Phone, Email, Address, GhanaCardID, RegistrationDate)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (new_id, first_name, last_name, dob.strftime('%Y-%m-%d'), 
                             sex, phone, email, address, ghana_card, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        
                        conn.commit()
                        st.success(f"✅ Patient registered successfully! ID: {new_id}")
                    except Exception as e:
                        st.error(f"Error registering patient: {str(e)}")
                else:
                    st.error("Please fill in all required fields (*)")
    
    with tab3:
        st.subheader("Search Patient")
        search_term = st.text_input("Search by Name, ID, or Phone")
        
        if search_term:
            results = pd.read_sql(f"""
                SELECT * FROM Patients
                WHERE PatientID LIKE '%{search_term}%'
                   OR FirstName LIKE '%{search_term}%'
                   OR LastName LIKE '%{search_term}%'
                   OR Phone LIKE '%{search_term}%'
            """, conn)
            
            if not results.empty:
                st.dataframe(results, use_container_width=True)
            else:
                st.info("No patients found")

def manage_appointments(conn):
    """Appointment/Visit management interface"""
    st.header("📅 Appointment Management")
    
    tab1, tab2 = st.tabs(["View Visits", "Schedule Visit"])
    
    with tab1:
        st.subheader("All Visits")
        visits = pd.read_sql("""
            SELECT v.VisitID, p.FirstName || ' ' || p.LastName as PatientName,
                   vt.VisitTypeName, v.VisitDate, v.Status, v.Description
            FROM Visits v
            JOIN Patients p ON v.PatientID = p.PatientID
            JOIN VisitTypes vt ON v.VisitTypeID = vt.VisitTypeID
            ORDER BY v.VisitDate DESC
        """, conn)
        st.dataframe(visits, use_container_width=True)
    
    with tab2:
        st.subheader("Schedule New Visit")
        with st.form("new_visit_form"):
            # Get patients and visit types
            patients = pd.read_sql("SELECT PatientID, FirstName || ' ' || LastName as Name FROM Patients WHERE CurrentStatus='Active'", conn)
            visit_types = pd.read_sql("SELECT VisitTypeID, VisitTypeName FROM VisitTypes", conn)
            
            patient_id = st.selectbox("Select Patient", 
                                     options=patients['PatientID'].tolist(),
                                     format_func=lambda x: patients[patients['PatientID']==x]['Name'].iloc[0])
            
            visit_type = st.selectbox("Visit Type",
                                     options=visit_types['VisitTypeID'].tolist(),
                                     format_func=lambda x: visit_types[visit_types['VisitTypeID']==x]['VisitTypeName'].iloc[0])
            
            visit_date = st.date_input("Visit Date")
            visit_time = st.time_input("Visit Time")
            description = st.text_area("Description/Reason for Visit")
            
            submitted = st.form_submit_button("Schedule Visit")
            
            if submitted:
                try:
                    cursor = conn.cursor()
                    # Generate Visit ID
                    visit_datetime = f"{visit_date} {visit_time}"
                    visit_id = f"VIS{visit_date.strftime('%Y%m%d')}{int(datetime.now().timestamp()) % 1000:03d}"
                    
                    cursor.execute("""
                        INSERT INTO Visits (VisitID, PatientID, VisitTypeID, VisitDate, Description, Status)
                        VALUES (?, ?, ?, ?, ?, 'Scheduled')
                    """, (visit_id, patient_id, visit_type, visit_datetime, description))
                    
                    conn.commit()
                    st.success(f"✅ Visit scheduled successfully! ID: {visit_id}")
                except Exception as e:
                    st.error(f"Error scheduling visit: {str(e)}")

def view_reports(conn):
    """Analytics and reports section"""
    st.header("📊 Reports & Analytics")
    
    report_type = st.selectbox("Select Report", [
        "Patient Demographics",
        "Visit Statistics",
        "Diagnosis Frequency",
        "Treatment Effectiveness",
        "Financial Summary",
        "Doctor Performance"
    ])
    
    if report_type == "Patient Demographics":
        st.subheader("Patient Demographics Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gender distribution
            gender_dist = pd.read_sql("""
                SELECT Sex, COUNT(*) as Count
                FROM Patients
                WHERE CurrentStatus='Active'
                GROUP BY Sex
            """, conn)
            
            fig = px.pie(gender_dist, values='Count', names='Sex', title='Gender Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Age distribution
            age_dist = pd.read_sql("""
                SELECT 
                    CASE
                        WHEN CAST((julianday('now') - julianday(DateOfBirth)) / 365.25 AS INTEGER) < 18 THEN '0-17'
                        WHEN CAST((julianday('now') - julianday(DateOfBirth)) / 365.25 AS INTEGER) < 30 THEN '18-29'
                        WHEN CAST((julianday('now') - julianday(DateOfBirth)) / 365.25 AS INTEGER) < 50 THEN '30-49'
                        WHEN CAST((julianday('now') - julianday(DateOfBirth)) / 365.25 AS INTEGER) < 65 THEN '50-64'
                        ELSE '65+'
                    END as AgeGroup,
                    COUNT(*) as Count
                FROM Patients
                WHERE CurrentStatus='Active'
                GROUP BY AgeGroup
                ORDER BY AgeGroup
            """, conn)
            
            fig = px.bar(age_dist, x='AgeGroup', y='Count', title='Age Distribution')
            st.plotly_chart(fig, use_container_width=True)
    
    elif report_type == "Diagnosis Frequency":
        st.subheader("Most Common Diagnoses")
        
        diagnosis_freq = pd.read_sql("""
            SELECT d.ICD10Code, d.Description, d.Severity,
                   COUNT(pd.PDiagnosisID) AS DiagnosisCount
            FROM Diagnoses d
            JOIN PatientDiagnoses pd ON d.DiagnosisID = pd.DiagnosisID
            GROUP BY d.DiagnosisID
            ORDER BY DiagnosisCount DESC
            LIMIT 10
        """, conn)
        
        if not diagnosis_freq.empty:
            st.dataframe(diagnosis_freq, use_container_width=True)
            
            fig = px.bar(diagnosis_freq, x='Description', y='DiagnosisCount',
                        color='Severity', title='Top 10 Diagnoses')
            fig.update_xaxis(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No diagnosis data available")
    
    elif report_type == "Financial Summary":
        st.subheader("Financial Summary")
        
        financial_data = pd.read_sql("""
            SELECT 
                COUNT(BillID) as TotalBills,
                SUM(Total) as TotalBilled,
                SUM(CASE WHEN Status='Paid' THEN Total ELSE 0 END) as TotalPaid,
                SUM(CASE WHEN Status='Pending' THEN Total ELSE 0 END) as TotalPending
            FROM Bills
        """, conn)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Bills", f"{financial_data.iloc[0]['TotalBills']:,}")
        with col2:
            st.metric("Total Billed", f"GH₵ {financial_data.iloc[0]['TotalBilled']:,.2f}")
        with col3:
            st.metric("Total Paid", f"GH₵ {financial_data.iloc[0]['TotalPaid']:,.2f}")
        with col4:
            st.metric("Pending", f"GH₵ {financial_data.iloc[0]['TotalPending']:,.2f}")
        
        # Payment methods breakdown
        payment_methods = pd.read_sql("""
            SELECT PaymentMethod, COUNT(*) as Count, SUM(Amount) as Total
            FROM Payments
            GROUP BY PaymentMethod
            ORDER BY Total DESC
        """, conn)
        
        if not payment_methods.empty:
            st.subheader("Payment Methods")
            fig = px.pie(payment_methods, values='Total', names='PaymentMethod',
                        title='Revenue by Payment Method')
            st.plotly_chart(fig, use_container_width=True)

# ========== MAIN APPLICATION ==========

def main():
    """Main application function"""
    setup_ui()
    
    # Initialize database
    conn = init_database()
    if conn is None:
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🏥 Navigation")
        page = st.radio("Go to", [
            "🏠 Dashboard",
            "💬 AI Assistant",
            "👥 Patient Management",
            "📅 Appointments",
            "📊 Reports & Analytics"
        ])
        
        st.markdown("---")
        st.markdown("### About")
        st.info("""
        Hospital Management System with AI-powered insights.
        
        **Features:**
        - Patient Management
        - Appointment Scheduling
        - AI Medical Assistant
        - Analytics & Reports
        """)
    
    # Main content area
    if page == "🏠 Dashboard":
        display_dashboard(conn)
    
    elif page == "💬 AI Assistant":
        st.header("🤖 AI Medical Assistant")
        st.write("Ask anything about your hospital data in natural language")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I'm your Hospital Management AI Assistant. How can I help you today?"}
            ]
        
        # Get schema for AI context
        schema = get_database_schema(conn)
        model = configure_gemini()
        
        # Display chat messages
        for message in st.session_state.messages:
            display_chat_message(message["role"], message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about patients, diagnoses, treatments..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            display_chat_message("user", prompt)
            
            # Get AI response
            with st.spinner("🤔 Thinking..."):
                response = ask_ai_question(model, conn, schema, prompt)
                ai_response = response.get("response", "I'm sorry, I couldn't process that request.")
                
                # Add assistant message
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                display_chat_message("assistant", ai_response)
                
                # Rerun to display new messages
                st.rerun()
    
    elif page == "👥 Patient Management":
        manage_patients(conn)
    
    elif page == "📅 Appointments":
        manage_appointments(conn)
    
    elif page == "📊 Reports & Analytics":
        view_reports(conn)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Hospital Management System © 2026 | Built with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
