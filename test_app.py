import requests
import json
import time
import sys
import re
from bs4 import BeautifulSoup

BASE_URL = 'http://127.0.0.1:5000'
session = requests.Session()

def get_csrf_token(html):
    """Extract CSRF token from HTML form"""
    soup = BeautifulSoup(html, 'html.parser')
    # Look for csrf_token input field
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        return csrf_input.get('value')
    return None

def test_endpoint(method, url, data=None, expected_status=200, description="", get_csrf=False):
    """Test an endpoint and return response"""
    try:
        if method == 'GET':
            resp = session.get(url, allow_redirects=False)
        elif method == 'POST':
            if get_csrf and data is not None:
                # First GET the form page to get CSRF token
                # We need to know which form page to get
                form_url = url  # This won't work for all cases
                # Better approach: pass form_url separately
                pass
            resp = session.post(url, data=data, allow_redirects=False)
        else:
            return False, f"Unknown method: {method}"
        
        success = resp.status_code == expected_status or (expected_status == 200 and resp.status_code in [200, 302])
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {method} {url} - {resp.status_code} {description}")
        if not success:
            print(f"    Expected: {expected_status}, Got: {resp.status_code}")
            if resp.text:
                print(f"    Response preview: {resp.text[:300]}")
        return success, resp
    except Exception as e:
        print(f"  [ERROR] {method} {url} - {e}")
        return False, None

def test_form_submission(form_url, post_url, form_data, expected_status=302, description=""):
    """Get form page, extract CSRF, then POST"""
    # GET form page
    resp = session.get(form_url)
    if resp.status_code != 200:
        print(f"  [FAIL] GET {form_url} - {resp.status_code} (getting form)")
        return False, resp
    
    csrf_token = get_csrf_token(resp.text)
    if not csrf_token:
        print(f"  [WARN] No CSRF token found in {form_url}")
    
    # Add CSRF token to form data
    if csrf_token:
        form_data['csrf_token'] = csrf_token
    
    # POST form
    resp = session.post(post_url, data=form_data, allow_redirects=False)
    success = resp.status_code == expected_status or (expected_status == 200 and resp.status_code in [200, 302])
    status = "PASS" if success else "FAIL"
    print(f"  [{status}] POST {post_url} - {resp.status_code} {description}")
    if not success:
        print(f"    Expected: {expected_status}, Got: {resp.status_code}")
        if resp.text:
            print(f"    Response preview: {resp.text[:500]}")
    return success, resp

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def main():
    print("Starting LifeLine App Test Suite")
    print("="*60)
    
    # Test 1: Home page
    print_section("1. HOME PAGE")
    test_endpoint('GET', BASE_URL, description="Home page")
    
    # Test 2: Register Patient
    print_section("2. REGISTER PATIENT")
    patient_data = {
        'full_name': 'Test Patient',
        'email': 'patient@test.com',
        'phone': '9876543210',
        'password': 'password123',
        'confirm_password': 'password123',
        'user_type': 'patient',
        'blood_group': 'A+',
        'address': '123 Test Street',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'pincode': '400001'
    }
    test_form_submission(f'{BASE_URL}/register', f'{BASE_URL}/register', patient_data, expected_status=302, description="Register patient")
    
    # Test 3: Login Patient
    print_section("3. LOGIN PATIENT")
    login_data = {'email': 'patient@test.com', 'password': 'password123', 'remember_me': 'y'}
    test_form_submission(f'{BASE_URL}/login', f'{BASE_URL}/login', login_data, expected_status=302, description="Login patient")
    
    # Test 4: Patient Dashboard
    print_section("4. PATIENT DASHBOARD")
    test_endpoint('GET', f'{BASE_URL}/dashboard', description="Patient dashboard")
    
    # Test 5: Post Need (Patient)
    print_section("5. POST NEED (Patient)")
    need_data = {
        'need_type': 'blood',
        'blood_group': 'A+',
        'units_needed': '2',
        'urgency': 'high',
        'patient_name': 'Test Patient',
        'patient_age': '35',
        'patient_gender': 'male',
        'patient_blood_group': 'A+',
        'patient_weight': '70',
        'medical_condition': 'Severe anemia requiring urgent blood transfusion',
        'doctor_name': 'Dr. Test Doctor',
        'hospital_name': 'Test Hospital',
        'hospital_address': '456 Hospital Road, Mumbai',
        'contact_person': 'Test Contact',
        'contact_phone': '9876543210',
        'contact_email': 'contact@test.com',
        'additional_notes': 'Urgent need',
        'required_by': '2024-12-31T23:59'
    }
    test_form_submission(f'{BASE_URL}/post-need', f'{BASE_URL}/post-need', need_data, expected_status=302, description="Post blood need")
    
    # Test 6: Browse Needs
    print_section("6. BROWSE NEEDS")
    test_endpoint('GET', f'{BASE_URL}/browse-needs', description="Browse needs")
    
    # Test 7: Logout
    print_section("7. LOGOUT")
    test_endpoint('GET', f'{BASE_URL}/logout', expected_status=302, description="Logout")
    
    # Test 8: Register Donor
    print_section("8. REGISTER DONOR")
    donor_data = {
        'full_name': 'Test Donor',
        'email': 'donor@test.com',
        'phone': '9876543211',
        'password': 'password123',
        'confirm_password': 'password123',
        'user_type': 'donor',
        'blood_group': 'A+',
        'address': '789 Donor Lane',
        'city': 'Delhi',
        'state': 'Delhi',
        'pincode': '110001'
    }
    test_form_submission(f'{BASE_URL}/register', f'{BASE_URL}/register', donor_data, expected_status=302, description="Register donor")
    
    # Test 9: Login Donor
    print_section("9. LOGIN DONOR")
    login_data = {'email': 'donor@test.com', 'password': 'password123', 'remember_me': 'y'}
    test_form_submission(f'{BASE_URL}/login', f'{BASE_URL}/login', login_data, expected_status=302, description="Login donor")
    
    # Test 10: Donor Dashboard
    print_section("10. DONOR DASHBOARD")
    test_endpoint('GET', f'{BASE_URL}/dashboard', description="Donor dashboard")
    
    # Test 11: Post Donation (Donor)
    print_section("11. POST DONATION (Donor)")
    donation_data = {
        'donation_type': 'blood',
        'blood_group': 'A+',
        'units_available': '1',
        'donor_name': 'Test Donor',
        'donor_age': '30',
        'donor_gender': 'male',
        'donor_blood_group': 'A+',
        'donor_weight': '75',
        'hospital_name': 'Donor Hospital',
        'hospital_address': '789 Hospital Ave, Delhi',
        'doctor_name': 'Dr. Donor Doctor',
        'contact_person': 'Donor Contact',
        'contact_phone': '9876543211',
        'contact_email': 'donorcontact@test.com',
        'additional_notes': 'Regular donor',
        'available_from': '2024-12-01T09:00',
        'available_until': '2024-12-31T17:00'
    }
    test_form_submission(f'{BASE_URL}/post-donation', f'{BASE_URL}/post-donation', donation_data, expected_status=302, description="Post blood donation")
    
    # Test 12: Browse Donations
    print_section("12. BROWSE DONATIONS")
    test_endpoint('GET', f'{BASE_URL}/browse-donations', description="Browse donations")
    
    # Test 13: Logout
    print_section("13. LOGOUT")
    test_endpoint('GET', f'{BASE_URL}/logout', expected_status=302, description="Logout")
    
    # Test 14: Register Hospital
    print_section("14. REGISTER HOSPITAL")
    hospital_data = {
        'full_name': 'Test Hospital Admin',
        'email': 'hospital@test.com',
        'phone': '9876543212',
        'password': 'password123',
        'confirm_password': 'password123',
        'user_type': 'hospital',
        'blood_group': 'B+',
        'address': '100 Hospital Complex',
        'city': 'Bangalore',
        'state': 'Karnataka',
        'pincode': '560001',
        'hospital_name': 'Test Medical Center',
        'hospital_license': 'LIC123456'
    }
    test_form_submission(f'{BASE_URL}/register', f'{BASE_URL}/register', hospital_data, expected_status=302, description="Register hospital")
    
    # Test 15: Login Hospital
    print_section("15. LOGIN HOSPITAL")
    login_data = {'email': 'hospital@test.com', 'password': 'password123', 'remember_me': 'y'}
    test_form_submission(f'{BASE_URL}/login', f'{BASE_URL}/login', login_data, expected_status=302, description="Login hospital")
    
    # Test 16: Hospital Dashboard
    print_section("16. HOSPITAL DASHBOARD")
    test_endpoint('GET', f'{BASE_URL}/dashboard', description="Hospital dashboard")
    
    # Test 17: Post Organ Donation (Hospital - Brain Dead)
    print_section("17. POST ORGAN DONATION (Hospital)")
    organ_donation_data = {
        'donation_type': 'organ',
        'organ_name': 'kidney',
        'blood_group': 'B+',
        'units_available': '2',
        'donor_name': 'Brain Dead Donor',
        'donor_age': '45',
        'donor_gender': 'male',
        'donor_blood_group': 'B+',
        'donor_weight': '80',
        'is_brain_dead': 'y',
        'cause_of_death': 'Traumatic brain injury',
        'time_of_death': '2024-12-01T10:00',
        'hospital_name': 'Test Medical Center',
        'hospital_address': '100 Hospital Complex, Bangalore',
        'doctor_name': 'Dr. Neuro Surgeon',
        'contact_person': 'Hospital Coordinator',
        'contact_phone': '9876543212',
        'contact_email': 'coordinator@hospital.com',
        'additional_notes': 'Both kidneys available',
        'available_from': '2024-12-01T10:00',
        'available_until': '2024-12-01T18:00'
    }
    test_form_submission(f'{BASE_URL}/post-donation', f'{BASE_URL}/post-donation', organ_donation_data, expected_status=302, description="Post organ donation")
    
    # Test 18: Post Patient Need (Hospital)
    print_section("18. POST PATIENT NEED (Hospital)")
    hospital_need_data = {
        'need_type': 'organ',
        'organ_name': 'kidney',
        'blood_group': 'B+',
        'units_needed': '1',
        'urgency': 'critical',
        'patient_name': 'Hospital Patient',
        'patient_age': '50',
        'patient_gender': 'female',
        'patient_blood_group': 'B+',
        'patient_weight': '65',
        'medical_condition': 'End stage renal disease',
        'doctor_name': 'Dr. Nephrologist',
        'hospital_name': 'Test Medical Center',
        'hospital_address': '100 Hospital Complex, Bangalore',
        'contact_person': 'Patient Family',
        'contact_phone': '9876543213',
        'contact_email': 'family@test.com',
        'additional_notes': 'On dialysis',
        'required_by': '2024-12-15T23:59'
    }
    test_form_submission(f'{BASE_URL}/post-need', f'{BASE_URL}/post-need', hospital_need_data, expected_status=302, description="Post organ need")
    
    # Test 19: Profile Page
    print_section("19. PROFILE PAGE")
    test_endpoint('GET', f'{BASE_URL}/profile', description="Profile page")
    
    # Test 20: Notifications
    print_section("20. NOTIFICATIONS")
    test_endpoint('GET', f'{BASE_URL}/notifications', description="Notifications page")
    
    # Test 21: Static Pages
    print_section("21. STATIC PAGES")
    test_endpoint('GET', f'{BASE_URL}/about', description="About page")
    test_endpoint('GET', f'{BASE_URL}/how-it-works', description="How it works page")
    test_endpoint('GET', f'{BASE_URL}/contact', description="Contact page")
    
    # Test 22: Logout
    print_section("22. FINAL LOGOUT")
    test_endpoint('GET', f'{BASE_URL}/logout', expected_status=302, description="Final logout")
    
    # Test 23: Unauthenticated Access Protection
    print_section("23. AUTH PROTECTION")
    test_endpoint('GET', f'{BASE_URL}/dashboard', expected_status=302, description="Dashboard redirect to login")
    test_endpoint('GET', f'{BASE_URL}/post-need', expected_status=302, description="Post need redirect to login")
    test_endpoint('GET', f'{BASE_URL}/post-donation', expected_status=302, description="Post donation redirect to login")
    
    # Test 24: Test Matching - View Need and Donation
    print_section("24. VIEW NEED/DONATION DETAILS")
    test_endpoint('GET', f'{BASE_URL}/need/1', description="View need #1")
    test_endpoint('GET', f'{BASE_URL}/donation/1', description="View donation #1")
    
    print_section("TEST SUITE COMPLETE")
    print("All tests executed. Check for any FAIL/ERROR above.")

if __name__ == '__main__':
    # Install beautifulsoup4 if needed
    try:
        import bs4
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'beautifulsoup4'])
        import bs4
    
    # Wait for server to be ready
    time.sleep(2)
    main()