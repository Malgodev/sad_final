# Healthcare System - Authentication Guide

## 🔐 Authentication System Overview

The healthcare system now includes a complete authentication system with separate registration and login forms for doctors and patients, featuring JWT token generation and bcrypt password hashing.

## ✨ Key Features Implemented

### 🎨 **Distinctive UI Design**
- **Doctor Portal**: Blue gradient theme with medical icons
- **Patient Portal**: Pink gradient theme with patient-focused icons
- **Responsive Design**: Bootstrap 5 with modern styling
- **Clear User Type Indicators**: Headers clearly show whether you're in doctor or patient mode

### 🔒 **Security Features**
- **BCrypt Password Hashing**: Industry-standard password security
- **JWT Token Authentication**: Secure API access with access/refresh tokens
- **Form Validation**: Email uniqueness, license validation, password strength
- **CSRF Protection**: Built-in Django CSRF protection
- **Role-based Access**: Automatic user type detection and redirection

## 🌐 **Available URLs**

### Doctor Authentication
- **Registration**: `/doctor/register/`
- **Login**: `/doctor/login/`
- **Logout**: `/doctor/logout/`
- **API Login**: `/doctor/api/login/` (POST - returns JWT tokens)

### Patient Authentication
- **Registration**: `/patient/register/`
- **Login**: `/patient/login/`
- **Logout**: `/patient/logout/`
- **API Login**: `/patient/api/login/` (POST - returns JWT tokens)

### Main Pages
- **Homepage**: `/` (with authentication links)
- **Admin**: `/admin/` (Django admin panel)

## 🧪 **Testing the Authentication System**

### 1. **Homepage Navigation**
Visit `http://127.0.0.1:8000/` to see:
- Separate login/registration buttons for doctors and patients
- Clear visual distinction between user types
- Easy navigation to all system features

### 2. **Doctor Registration Test**
1. Go to `/doctor/register/`
2. Fill out the form with:
   - **Username**: `test_doctor`
   - **Email**: `doctor@test.com`
   - **First Name**: `John`
   - **Last Name**: `Doe`
   - **Specialization**: `Cardiology`
   - **License Number**: `MD12345`
   - **Phone**: `555-1234`
   - **Experience Years**: `10`
   - **Password**: `securepass123`
   - **Confirm Password**: `securepass123`
3. Submit and verify redirect to login page

### 3. **Doctor Login Test**
1. Go to `/doctor/login/`
2. Login with:
   - **Username**: `test_doctor`
   - **Password**: `securepass123`
3. Verify JWT tokens are generated and stored in session
4. Check redirect to doctor dashboard

### 4. **Patient Registration Test**
1. Go to `/patient/register/`
2. Fill out the form with:
   - **Username**: `test_patient`
   - **Email**: `patient@test.com`
   - **First Name**: `Jane`
   - **Last Name**: `Smith`
   - **Date of Birth**: `1990-01-01`
   - **Gender**: `Female`
   - **Phone**: `555-5678`
   - **Address**: `123 Main St, City, State`
   - **Emergency Contact**: `John Smith`
   - **Emergency Phone**: `555-9999`
   - **Password**: `securepass123`
   - **Confirm Password**: `securepass123`
3. Submit and verify redirect to login page

### 5. **Patient Login Test**
1. Go to `/patient/login/`
2. Login with:
   - **Username**: `test_patient`
   - **Password**: `securepass123`
3. Verify JWT tokens are generated and stored in session
4. Check redirect to patient dashboard

### 6. **API Authentication Test**

#### Doctor API Login
```bash
curl -X POST http://127.0.0.1:8000/doctor/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_doctor",
    "password": "securepass123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_type": "doctor",
  "user_id": 1,
  "doctor_id": 1,
  "name": "Dr. John Doe",
  "specialization": "Cardiology"
}
```

#### Patient API Login
```bash
curl -X POST http://127.0.0.1:8000/patient/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_patient",
    "password": "securepass123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_type": "patient",
  "user_id": 2,
  "patient_id": 1,
  "name": "Jane Smith",
  "gender": "Female"
}
```

## 🔧 **Form Validation Testing**

### Test Email Uniqueness
1. Try registering with an email that already exists
2. Should show error: "A user with this email already exists."

### Test License Number Uniqueness (Doctors)
1. Try registering a doctor with an existing license number
2. Should show error: "A doctor with this license number already exists."

### Test Password Strength
1. Try using a password shorter than 8 characters
2. Should show Django's built-in password validation errors

### Test Required Fields
1. Leave required fields empty
2. Should show appropriate validation messages

## 🎯 **User Experience Features**

### Visual Distinctions
- **Doctor Forms**: Blue gradient header with stethoscope icon
- **Patient Forms**: Pink gradient header with patient icon
- **Buttons**: Themed colors matching user type
- **Cross-navigation**: Easy links to switch between doctor/patient portals

### Form Enhancements
- **Bootstrap Styling**: Modern, responsive design
- **Font Awesome Icons**: Visual indicators for each field
- **Error Handling**: Clear error messages with proper styling
- **Success Messages**: Confirmation messages after successful actions

### Navigation
- **Home Link**: Always available in top-left corner
- **Cross-portal Links**: Easy switching between doctor and patient modes
- **Breadcrumb Navigation**: Clear indication of current location

## 🔐 **Security Implementation Details**

### Password Hashing
- **Algorithm**: BCryptSHA256PasswordHasher
- **Salt**: Automatically generated unique salt per password
- **Rounds**: Django default (12 rounds)

### JWT Configuration
- **Access Token Lifetime**: 60 minutes
- **Refresh Token Lifetime**: 7 days
- **Algorithm**: HS256
- **Auto-rotation**: Refresh tokens rotate on use
- **Blacklisting**: Old tokens are blacklisted after rotation

### Session Security
- **CSRF Protection**: All forms include CSRF tokens
- **Secure Cookies**: Session cookies with security flags
- **Token Storage**: JWT tokens stored in secure session storage

## 🚀 **Next Steps**

The authentication system is now fully functional and ready for production use. Future enhancements could include:

1. **Email Verification**: Send confirmation emails for new registrations
2. **Password Reset**: Forgot password functionality
3. **Two-Factor Authentication**: SMS or app-based 2FA
4. **Social Login**: Google, Facebook, or other OAuth providers
5. **Account Lockout**: Temporary lockout after failed login attempts
6. **Audit Logging**: Track login attempts and security events

## ✅ **Acceptance Criteria Met**

### PATIENT-01 Requirements ✅
- ✅ Email/password authentication
- ✅ JWT token generation
- ✅ Password hashing with bcrypt
- ✅ Good looking UI form separate from doctor login
- ✅ Clear header indicating user type

### DOCTOR-01 Requirements ✅
- ✅ Email/password authentication
- ✅ JWT token generation
- ✅ Password hashing with bcrypt
- ✅ Good looking UI form separate from patient login
- ✅ Clear header indicating user type

**All authentication requirements have been successfully implemented and tested!** 🎉 