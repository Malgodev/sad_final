#!/usr/bin/env python
import os
import django
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare.settings')
django.setup()

from django.urls import reverse, NoReverseMatch

def test_urls():
    """Test all selftest URLs for resolution"""
    urls_to_test = [
        'selftest:home',
        'selftest:dashboard',
        'selftest:start',
        'selftest:quick',
        'selftest:symptoms',
        'selftest:symptom_search_api',
        'selftest:quick_symptom_search_api',
        'selftest:quick_analysis_api',
    ]
    
    print("🚀 Testing SelfTest URL Resolution")
    print("=" * 50)
    
    for url_name in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"✅ {url_name:<30} -> {url}")
        except NoReverseMatch as e:
            print(f"❌ {url_name:<30} -> ERROR: {e}")
        except Exception as e:
            print(f"⚠️  {url_name:<30} -> UNKNOWN ERROR: {e}")
    
    print("\n" + "=" * 50)
    
    # Test the specific problematic URL
    try:
        url = reverse('selftest:quick_symptom_search_api')
        print(f"🎯 Specific test - quick_symptom_search_api: {url}")
        
        # Test if the view function exists
        from selftest.views import quick_symptom_search_api
        print(f"✅ View function exists: {quick_symptom_search_api}")
        
    except NoReverseMatch as e:
        print(f"❌ quick_symptom_search_api URL resolution failed: {e}")
    except ImportError as e:
        print(f"❌ View function import failed: {e}")
    except Exception as e:
        print(f"⚠️  Unknown error: {e}")

if __name__ == '__main__':
    test_urls() 