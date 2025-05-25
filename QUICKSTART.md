# Healthcare System - Quick Start Guide

## 🚀 Ready to Run!

Your healthcare system is now fully set up and ready to use. All necessary files have been created and the database has been populated with sample data.

## 📁 What's Been Created

### Core Files
- ✅ Django project with 4 apps (doctor, patient, appointment, selftest)
- ✅ SQLite database (`src/healthcare/db.sqlite3`)
- ✅ All models, views, URLs, and admin configurations
- ✅ Sample data with test users
- ✅ Requirements file with dependencies

### Project Structure
```
src/healthcare/
├── healthcare/          # Main project settings
│   ├── settings.py      # Database and app configuration
│   ├── urls.py          # Main URL routing
│   └── wsgi.py          # WSGI configuration
├── doctor/              # Doctor management app
├── patient/             # Patient management app  
├── appointment/         # Appointment booking app
├── selftest/            # AI self-testing app
├── db.sqlite3           # SQLite database (created)
└── manage.py            # Django management script
```

## 🏃‍♂️ How to Run

### 1. Install Dependencies (if not already done)
```bash
pip install -r requirements.txt
```

### 2. Navigate to Project Directory
```bash
cd src/healthcare
```

### 3. Start the Server
```bash
python manage.py runserver
```

### 4. Access the System
Open your browser and visit:
- **Main Site**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 🔑 Test Accounts

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Access**: Full admin panel access

### Doctor Accounts
- **Dr. John Smith**: `dr_smith` / `doctor123` (Cardiology)
- **Dr. Sarah Jones**: `dr_jones` / `doctor123` (Pediatrics)  
- **Dr. Michael Brown**: `dr_brown` / `doctor123` (Neurology)

### Patient Accounts
- **Alice Johnson**: `patient1` / `patient123`
- **Bob Wilson**: `patient2` / `patient123`
- **Carol Davis**: `patient3` / `patient123`

## 🌐 Available URLs

| URL | Description |
|-----|-------------|
| `/` | Home page with navigation |
| `/admin/` | Django admin panel |
| `/doctor/` | Doctor portal |
| `/doctor/dashboard/` | Doctor dashboard (login required) |
| `/patient/` | Patient portal |
| `/patient/dashboard/` | Patient dashboard (login required) |
| `/appointment/` | Appointment system |
| `/appointment/list/` | View all appointments |
| `/selftest/` | Self-test system |
| `/selftest/symptoms/` | Available symptoms |

## 📊 Sample Data Included

- 3 Doctors with different specializations
- 3 Patients with profile information
- 5 Sample symptoms (Headache, Fever, Cough, Fatigue, Nausea)
- Sample appointments between doctors and patients

## 🔧 Next Steps

This is a "Hello World" version with basic functionality. To enhance the system:

1. **Add Authentication Forms**: Create login/registration pages
2. **Improve UI**: Replace basic HTML with proper Django templates
3. **Add Form Validation**: Implement proper form handling
4. **Integrate AI**: Add real AI functionality to self-testing
5. **Add Styling**: Implement CSS and responsive design

## 🐛 Troubleshooting

### Server Won't Start
- Ensure you're in the `src/healthcare` directory
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.8 or higher

### Database Issues
- If you need to reset the database, delete `db.sqlite3` and run:
  ```bash
  python manage.py migrate
  python manage.py populate_sample_data
  ```

### Port Already in Use
- Use a different port: `python manage.py runserver 8001`

## ✅ System Status

- ✅ Django project configured
- ✅ Database created and migrated
- ✅ All apps functional
- ✅ Sample data populated
- ✅ Admin interface working
- ✅ All URLs accessible
- ✅ Ready for development and testing

**Your healthcare system is now live and ready to use!** 🎉 