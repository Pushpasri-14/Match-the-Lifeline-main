# LifeLine - Organ & Blood Donation Network

A comprehensive Flask web application for connecting patients in need of organs, blood, and blood products with donors and hospitals across India.

## Features

### For Patients & Families
- **Post Urgent Needs**: Register requirements for organs (heart, liver, kidney, lung, pancreas, cornea, etc.), blood, plasma, platelets, and serum
- **Detailed Medical Information**: Include patient details, diagnosis, hospital information, urgency levels, and contact information
- **Real-time Notifications**: Get instant alerts when matching donors are available
- **Track Matches**: Monitor pending, accepted, and completed matches

### For Donors & Hospitals
- **Post Donation Availability**: Register available organs (from brain-dead patients), blood, and blood products
- **Brain Death Declaration**: Special workflow for organ donations from brain-dead patients with medical certification
- **Match Requests**: Receive and respond to match requests from patients
- **Hospital Verification**: Verified hospital accounts for added trust

### Smart Matching System
- **Automatic Compatibility Matching**: Blood group compatibility, organ type matching, urgency prioritization
- **Geographic Proximity**: Location-based matching for faster coordination
- **Real-time Notifications**: Both parties notified instantly when matches are found

### User Experience
- **Modern UI**: Clean, responsive design with Bootstrap 5
- **Role-based Dashboards**: Separate interfaces for patients, donors, and hospitals
- **Advanced Filtering**: Browse needs/donations by type, blood group, urgency, and location
- **Secure Authentication**: Password hashing, session management, role-based access control

## Tech Stack

- **Backend**: Flask 3.0, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5.3, Font Awesome 6, Vanilla JavaScript
- **Database**: SQLite (development), PostgreSQL/MySQL (production ready)
- **Forms**: Flask-WTF with WTForms validation
- **Security**: Werkzeug password hashing, CSRF protection

## Installation

1. **Clone the repository**
```bash
cd "Match the Lifeline"
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python run.py
```

5. **Access the app**
Open http://localhost:5000 in your browser

## Project Structure

```
Match the Lifeline/
├── app.py              # Main Flask application with all routes
├── config.py           # Configuration settings
├── models.py           # Database models (User, Need, Donation, Match, Notification)
├── forms.py            # WTForms for all user inputs
├── run.py              # Entry point
├── requirements.txt    # Python dependencies
├── templates/
│   ├── base.html       # Base template with navigation
│   ├── index.html      # Home page with hero and stats
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── needs/
│   │   ├── post.html   # Post patient need
│   │   ├── browse.html # Browse all needs
│   │   └── view.html   # View need details
│   ├── donations/
│   │   ├── post.html   # Post donation availability
│   │   ├── browse.html # Browse all donations
│   │   └── view.html   # View donation details
│   ├── dashboard/
│   │   ├── patient.html
│   │   ├── donor.html
│   │   └── hospital.html
│   ├── matches/
│   │   └── respond.html
│   ├── profile.html
│   ├── change_password.html
│   ├── notifications.html
│   ├── about.html
│   ├── how_it_works.html
│   └── contact.html
└── static/
    ├── css/
    │   └── style.css   # Custom styles
    └── js/
        └── main.js     # Client-side functionality
```

## User Types

1. **Patient** - Can post needs for themselves or family members
2. **Donor** - Can post blood/blood product donations
3. **Hospital** - Can post both patient needs and organ donations (including brain-dead donors)

## Key Workflows

### Patient Posts a Need
1. Register/Login as Patient
2. Click "Post a Need" 
3. Fill in: Need type, organ (if applicable), blood group, urgency, patient details, hospital info, contact info
4. System auto-matches with compatible donations
5. Get notified when matches found

### Hospital Posts Organ Donation
1. Register/Login as Hospital
2. Click "Post Donation"
3. Select "Organ (from brain-dead patient)"
4. Fill in: Donor details, brain death certification, organ(s) available, hospital info
5. System auto-matches with waiting patients
6. Coordinate with matched patient's hospital

### Match Process
1. System finds compatible match (blood group, organ, urgency, location)
2. Both parties notified
3. Donor reviews patient details and accepts/declines
4. If accepted: Direct contact for hospital coordination
5. Mark as completed after successful transplant/donation

## Configuration

Environment variables (create `.env` file):
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///lifeline.db  # Or PostgreSQL/MySQL URL
```

## Deployment

For production:
1. Set `DEBUG=False` in config
2. Use PostgreSQL/MySQL database
3. Set strong `SECRET_KEY`
4. Use Gunicorn/uWSGI with Nginx
5. Enable HTTPS
6. Set up proper logging

## License

MIT License - Feel free to use and modify for life-saving purposes.

## Support

- Email: support@lifeline.org
- Phone: 1800-11-4770 (National Organ Donation Helpline)
- Emergency: 108 (Ambulance), 104 (Blood Bank)

---

**Built with ❤️ to save lives**