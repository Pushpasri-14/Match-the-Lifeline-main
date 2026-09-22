from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum
from flask_login import UserMixin

db = SQLAlchemy()

class UserType(Enum):
    PATIENT = 'patient'
    DONOR = 'donor'
    HOSPITAL = 'hospital'

class NeedType(Enum):
    ORGAN = 'organ'
    BLOOD = 'blood'
    SERUM = 'serum'
    PLASMA = 'plasma'
    PLATELETS = 'platelets'

class BloodGroup(Enum):
    A_POS = 'A+'
    A_NEG = 'A-'
    B_POS = 'B+'
    B_NEG = 'B-'
    AB_POS = 'AB+'
    AB_NEG = 'AB-'
    O_POS = 'O+'
    O_NEG = 'O-'

class UrgencyLevel(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class Status(Enum):
    ACTIVE = 'active'
    MATCHED = 'matched'
    FULFILLED = 'fulfilled'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    user_type = db.Column(db.Enum(UserType), nullable=False)
    blood_group = db.Column(db.Enum(BloodGroup), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    hospital_name = db.Column(db.String(100), nullable=True)
    hospital_license = db.Column(db.String(50), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    needs = db.relationship('Need', backref='patient', lazy='dynamic', foreign_keys='Need.patient_id')
    donations = db.relationship('Donation', backref='donor', lazy='dynamic', foreign_keys='Donation.donor_id')
    matches_as_patient = db.relationship('Match', backref='patient_user', lazy='dynamic', foreign_keys='Match.patient_id')
    matches_as_donor = db.relationship('Match', backref='donor_user', lazy='dynamic', foreign_keys='Match.donor_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Need(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    need_type = db.Column(db.Enum(NeedType), nullable=False)
    organ_name = db.Column(db.String(50), nullable=True)
    blood_group = db.Column(db.Enum(BloodGroup), nullable=True)
    units_needed = db.Column(db.Integer, default=1)
    urgency = db.Column(db.Enum(UrgencyLevel), default=UrgencyLevel.MEDIUM)
    status = db.Column(db.Enum(Status), default=Status.ACTIVE)
    patient_name = db.Column(db.String(100), nullable=False)
    patient_age = db.Column(db.Integer, nullable=False)
    patient_gender = db.Column(db.String(10), nullable=False)
    patient_blood_group = db.Column(db.Enum(BloodGroup), nullable=False)
    patient_weight = db.Column(db.Float, nullable=True)
    medical_condition = db.Column(db.Text, nullable=False)
    doctor_name = db.Column(db.String(100), nullable=True)
    hospital_name = db.Column(db.String(100), nullable=True)
    hospital_address = db.Column(db.Text, nullable=True)
    contact_person = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(120), nullable=True)
    additional_notes = db.Column(db.Text, nullable=True)
    required_by = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    matches = db.relationship('Match', backref='need', lazy='dynamic')

    def __repr__(self):
        return f'<Need {self.need_type.value} for {self.patient_name}>'

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    donation_type = db.Column(db.Enum(NeedType), nullable=False)
    organ_name = db.Column(db.String(50), nullable=True)
    blood_group = db.Column(db.Enum(BloodGroup), nullable=True)
    units_available = db.Column(db.Integer, default=1)
    status = db.Column(db.Enum(Status), default=Status.ACTIVE)
    donor_name = db.Column(db.String(100), nullable=False)
    donor_age = db.Column(db.Integer, nullable=False)
    donor_gender = db.Column(db.String(10), nullable=False)
    donor_blood_group = db.Column(db.Enum(BloodGroup), nullable=False)
    donor_weight = db.Column(db.Float, nullable=True)
    is_brain_dead = db.Column(db.Boolean, default=False)
    cause_of_death = db.Column(db.Text, nullable=True)
    time_of_death = db.Column(db.DateTime, nullable=True)
    hospital_name = db.Column(db.String(100), nullable=True)
    hospital_address = db.Column(db.Text, nullable=True)
    doctor_name = db.Column(db.String(100), nullable=True)
    contact_person = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(120), nullable=True)
    additional_notes = db.Column(db.Text, nullable=True)
    available_from = db.Column(db.DateTime, nullable=True)
    available_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    matches = db.relationship('Match', backref='donation', lazy='dynamic')

    def __repr__(self):
        return f'<Donation {self.donation_type.value} from {self.donor_name}>'

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    need_id = db.Column(db.Integer, db.ForeignKey('need.id'), nullable=False)
    donation_id = db.Column(db.Integer, db.ForeignKey('donation.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    matched_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Match Need:{self.need_id} Donation:{self.donation_id}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_type = db.Column(db.String(20), nullable=True)
    related_id = db.Column(db.Integer, nullable=True)
    
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))

    def __repr__(self):
        return f'<Notification {self.title} for User:{self.user_id}>'