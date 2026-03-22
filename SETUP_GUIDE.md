# Setup Guide

This guide will help you set up and run the Hospital Management System on your local machine.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Google AI API Key (for chatbot functionality)

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/hospital-management-system.git
cd hospital-management-system
```

### 2. Create a Virtual Environment (Recommended)

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Google AI API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Save the key securely

**Method 1: Using .env file (Recommended)**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

**Method 2: Environment Variable**
```bash
# On Windows
set GOOGLE_API_KEY=your_api_key_here

# On macOS/Linux
export GOOGLE_API_KEY=your_api_key_here
```

### 5. Initialize the Database

Before running the app, you need to create the database:

```bash
python database_schema.py
```

This will:
- Create `hospital_management.db`
- Set up all tables with proper relationships
- Insert sample data for testing

You should see output like:
```
============================================================
Hospital Management System - Database Initialization
============================================================

Creating database schema...
✓ Database schema created successfully
Inserting sample data...
✓ Sample data inserted successfully

✓ Database initialized successfully!
  - 5 patients registered
  - Database file: hospital_management.db
```

### 6. Run the Application

**Using Streamlit:**

```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

### 6. Access the Application

- The Streamlit app will automatically open in your browser
- If not, navigate to: `http://localhost:8501`

## Troubleshooting

### Common Issues

**Issue: Module not found**
```bash
# Solution: Reinstall requirements
pip install -r requirements.txt --upgrade
```

**Issue: Database not created**
```bash
# Solution: Ensure the code has write permissions in the directory
# On Unix systems:
chmod +w .
```

**Issue: API Key Error**
```
# Solution: Verify your API key is set correctly
# Test with:
echo $GOOGLE_API_KEY  # macOS/Linux
echo %GOOGLE_API_KEY%  # Windows
```

**Issue: Port already in use**
```bash
# Solution: Use a different port
streamlit run app.py --server.port 8502
```

## Database Initialization

The database will be automatically created on first run with:
- All necessary tables
- Sample data for testing
- Relationships and constraints

## Next Steps

1. Explore the different sections in the sidebar
2. Try adding a new patient or appointment
3. Test the AI chatbot feature
4. Generate some reports

## Need Help?

- Check the main [README.md](README.md)
- Open an issue on GitHub
- Review the code comments in the notebook

## Security Reminder

⚠️ **Never commit your API keys to Git!**
- Always use environment variables or .env files
- The .gitignore is configured to exclude sensitive files
