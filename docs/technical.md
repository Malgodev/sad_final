## Overview

This document outlines the technical architecture for an AI-based IDE built using DJango for fullstack. The system follows a modular microservices architecture with event-driven communication patterns.

## Technology Stack

- **Backend Framework**: DJango
- **Frontend Framework**: DJango
- **Language**: Python
- **Database**: SQL Lite
- **Authentication**: JWT

## Core Modules

### 1. Module: appointment

```python
# src/healthcare/appointment/
__init__.py
admin.py
apps.py
models.py
views.py
urls.py
serializers.py
forms.py
chatbot.py         # Custom logic for chatbot
appointment_logic.py  # Scheduling and validation
```

### 2. Module: doctor

```python
#  src/healthcare/doctor/
__init__.py
admin.py
apps.py
models.py              # Doctor profile with OneToOne to User
views.py               # Doctor dashboard, auth, profile
urls.py
serializers.py
permissions.py         # Doctor-only views
auth.py                # Doctor registration/login/logout logic
services.py            # Doctor logic and integrations
```

### 3. Module: patient

```python
# src/healthcare/patient/
__init__.py
admin.py
apps.py
models.py              # Patient profile with OneToOne to User
views.py               # Patient dashboard, auth, profile
urls.py
serializers.py
forms.py
auth.py                # Patient-specific auth handling
permissions.py         # Patient-only access controls
```

### 4. Module: selftest

```python
# src/healthcare/selftest/
__init__.py
admin.py
apps.py
models.py
views.py
urls.py
serializers.py
ai_engine.py           # AI disease detection logic
symptom_parser.py      # Symptom NLP/processing
```

### 5. Module: gateway (optional for routing or middleware)

```python
# src/healthcare/gateway/
__init__.py
views.py
urls.py
middleware.py          # Request routing, auth headers, logging
```

### 6. Project Base: healthcare

## Database Schema

### DJango setting Configuration

```python
# src/healthcare/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Installed apps (entities equivalent)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Project apps (your equivalent of entities)
    'doctor',
    'patient',
    'appointment',
    'selftest',
    'gateway',  # optional, if needed
]
```

## Development Workflow

1. **Local Development**

   ```bash
   # Start the development server
   python manage.py runserver

   # Run database migrations
    python manage.py makemigrations
    python manage.py migrate

   # Generate new migration
   python manage.py makemigrations app_name
   ```


## Recent Technical Updates

### SelfTest URL Resolution Fix (May 25, 2025)

**Issue**: NoReverseMatch error for `quick_symptom_search_api` URL pattern
```
NoReverseMatch at /selftest/quick/
Reverse for 'quick_symptom_search_api' not found. 'quick_symptom_search_api' is not a valid view function or pattern name.
```

**Root Cause**: Django URL caching issue after server restart causing URL patterns to not be properly loaded.

**Technical Solution**:
1. **URL Pattern Verification**: Confirmed all URL patterns exist in `selftest/urls.py`
2. **View Function Validation**: Verified all view functions exist in `selftest/views.py`
3. **Django Server Restart**: Proper server restart resolved caching issue
4. **Template URL References**: Validated Django URL template tags are correct

**URL Patterns Affected**:
```python
# src/healthcare/selftest/urls.py
urlpatterns = [
    # ... existing patterns ...
    path('api/quick-symptom-search/', views.quick_symptom_search_api, name='quick_symptom_search_api'),
    path('api/symptom-search/', views.symptom_search_api, name='symptom_search_api'),
    path('api/quick-analysis/', views.quick_analysis_api, name='quick_analysis_api'),
]
```

**Template Integration**:
```html
<!-- templates/selftest/quick_test.html -->
fetch(`{% url 'selftest:quick_symptom_search_api' %}?q=${encodeURIComponent(searchQuery)}`, {
    method: 'GET',
    headers: {
        'X-CSRFToken': csrfToken
    }
})
```

**Testing Implementation**:
- **SelfTestURLTests**: Validates all URL pattern resolution
- **SelfTestAPITests**: Tests API endpoint functionality
- **Comprehensive Validation Script**: Full system verification

**Status**: ✅ RESOLVED - All selftest URLs now working correctly

## Automation Testing Framework

### Test Coverage
```python
# src/healthcare/selftest/tests.py
class SelfTestURLTests(TestCase):
    """Test URL patterns and resolution"""
    
class SelfTestAPITests(TestCase):
    """Test API endpoints functionality"""
    
class SelfTestFormTests(TestCase):
    """Test form functionality and submission"""
    
class SelfTestModelTests(TestCase):
    """Test model functionality and database operations"""
```

### Validation Script
```python
# src/healthcare/run_selftest_validation.py
def test_url_resolution()      # URL pattern validation
def test_view_functions()      # View function imports
def test_page_access()         # Page accessibility
def test_api_endpoints()       # API functionality
def test_form_submission()     # Form workflows
```

**Command**: `python run_selftest_validation.py`
**Status**: All tests passing ✅

## Future Considerations

1. **Developer Experience**
   - Interactive documentation
   - Developer portal
   - API playground