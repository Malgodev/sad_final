# Patient App Documentation - Part 3: Templates

## 9. Template Files

### a. Base Template (templates/patient/base.html)

This is the main layout template for all patient pages with pink-themed styling.

Key features:
- Bootstrap 5 integration
- Font Awesome icons
- Patient-specific color scheme (pink theme)
- Responsive navigation
- Message display system
- Footer with emergency contacts

### b. Authentication Templates

#### i. Login Template (templates/patient/login.html)

```html
{% extends 'base.html' %}

{% block title %}{{ title }} - Healthcare System{% endblock %}

{% block content %}
<div class="auth-container">
    <div class="auth-card">
        <div class="auth-header patient-header">
            <i class="fas fa-user-injured fa-3x mb-3"></i>
            <h2>{{ user_type }} Login</h2>
            <div class="subtitle">Access your health records and appointments</div>
        </div>
        
        <div class="auth-body">
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
            
            <form method="post">
                {% csrf_token %}
                
                <div class="form-group">
                    <label for="{{ form.username.id_for_label }}" class="form-label">
                        <i class="fas fa-user me-2"></i>Username
                    </label>
                    {{ form.username }}
                    {% if form.username.errors %}
                        <div class="text-danger small mt-1">
                            {% for error in form.username.errors %}
                                <div>{{ error }}</div>
                            {% endfor %}
                        </div>
                    {% endif %}
                </div>
                
                <div class="form-group">
                    <label for="{{ form.password.id_for_label }}" class="form-label">
                        <i class="fas fa-lock me-2"></i>Password
                    </label>
                    {{ form.password }}
                    {% if form.password.errors %}
                        <div class="text-danger small mt-1">
                            {% for error in form.password.errors %}
                                <div>{{ error }}</div>
                            {% endfor %}
                        </div>
                    {% endif %}
                </div>
                
                {% if form.non_field_errors %}
                    <div class="alert alert-danger">
                        {% for error in form.non_field_errors %}
                            <div>{{ error }}</div>
                        {% endfor %}
                    </div>
                {% endif %}
                
                <div class="d-grid gap-2 mb-3">
                    <button type="submit" class="btn btn-auth btn-patient">
                        <i class="fas fa-sign-in-alt me-2"></i>Login as Patient
                    </button>
                </div>
            </form>
        </div>
        
        <div class="auth-footer">
            <p class="mb-0">
                Don't have a patient account? 
                <a href="{{ register_url }}" class="text-link">Register here</a>
            </p>
            <p class="mb-0 mt-2">
                <small>Are you a medical professional? <a href="/doctor/auth/" class="text-link">Doctor Portal</a></small>
            </p>
        </div>
    </div>
</div>
{% endblock %}
```

#### ii. Registration Template (templates/patient/register.html)

This template contains a comprehensive registration form with:
- Personal information fields
- Emergency contact information
- Password confirmation
- Form validation and error display

### c. Dashboard Template (templates/patient/dashboard.html)

Features:
- Welcome message with patient name
- Statistics cards (upcoming appointments, total appointments, completed visits)
- Upcoming appointments list
- Quick action buttons
- Patient information sidebar
- Health tips section
- Emergency contact information

### d. Profile Template (templates/patient/profile.html)

Contains:
- Editable profile form with personal information
- Emergency contact information section
- Form validation
- Profile update functionality

## 10. Appointment Templates

### a. Calendar Template (templates/patient/appointments/calendar.html)

Features:
- Monthly calendar view
- Available appointment slots display
- Doctor filtering
- Patient's existing appointments
- Navigation between months
- Legend for different appointment types
- Statistics display

Key JavaScript functionality:
- Slot booking interactions
- Calendar navigation
- Hover effects

### b. Appointment List Template (templates/patient/appointments/list.html)

Features:
- Filterable appointment list (by status and date)
- Separate sections for upcoming and past appointments
- Quick action buttons (view, cancel)
- Statistics cards
- Responsive table design

### c. Book Appointment Template (templates/patient/appointments/book.html)

Features:
- Appointment slot information display
- Doctor information card
- Patient information confirmation
- Booking form with reason field
- Important notes and guidelines
- Confirmation modal

### d. Appointment Detail Template (templates/patient/appointments/detail.html)

Features:
- Complete appointment information
- Doctor details
- Patient information
- Action buttons (cancel if applicable)
- Appointment guidelines based on status
- Contact information

### e. Cancel Appointment Template (templates/patient/appointments/cancel.html)

Features:
- Cancellation warning
- Appointment details display
- Cancellation policy information
- Alternative options
- Cancellation form with reason selection
- Final confirmation modal

## 11. Key Template Features

### a. Responsive Design
- Bootstrap 5 framework
- Mobile-first approach
- Responsive navigation and layouts

### b. Patient Theme
- Pink color scheme (`--patient-primary: #e91e63`)
- Consistent branding throughout
- Patient-specific icons and imagery

### c. Interactive Elements
- JavaScript enhancements
- Modal confirmations
- Form validation
- Hover effects and animations

### d. Accessibility
- Proper form labels
- ARIA attributes
- Semantic HTML structure
- Keyboard navigation support

### e. Error Handling
- Form validation messages
- User-friendly error displays
- Success message notifications
- Breadcrumb navigation

## 12. Template Inheritance Structure

```
base.html (general layout)
└── patient/base.html (patient-specific styling)
    ├── patient/dashboard.html
    ├── patient/profile.html
    └── patient/appointments/
        ├── calendar.html
        ├── list.html
        ├── book.html
        ├── detail.html
        └── cancel.html

Authentication templates extend directly from base.html:
├── patient/login.html
└── patient/register.html
```

## 13. CSS Custom Properties (Variables)

```css
:root {
    --patient-primary: #e91e63;
    --patient-secondary: #f8bbd9;
    --patient-success: #4caf50;
    --patient-danger: #f44336;
    --patient-warning: #ff9800;
    --patient-info: #2196f3;
    --patient-light: #fce4ec;
    --patient-dark: #880e4f;
}
```

## 14. JavaScript Features

### a. Interactive Calendar
- Slot booking functionality
- Date navigation
- Hover effects
- Real-time updates

### b. Form Enhancements
- Auto-resize textareas
- Form validation
- Confirmation modals
- Dynamic field updates

### c. User Experience
- Loading states
- Smooth animations
- Keyboard shortcuts
- Auto-refresh functionality

This comprehensive template system provides a complete, user-friendly interface for patient management within the healthcare system, with consistent styling, responsive design, and robust functionality. 