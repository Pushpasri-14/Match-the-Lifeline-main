from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    SelectField, TextAreaField, IntegerField, DateTimeField,
    FloatField, EmailField, RadioField, HiddenField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, Optional,
    NumberRange, ValidationError
)
from models import User, UserType, NeedType, BloodGroup, UrgencyLevel, Status

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    user_type = SelectField('Register As', choices=[
        (UserType.PATIENT.value, 'Patient / Family Member'),
        (UserType.DONOR.value, 'Donor'),
        (UserType.HOSPITAL.value, 'Hospital / Medical Facility')
    ], validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=[
        (bg.value, bg.value) for bg in BloodGroup
    ], validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional(), Length(max=500)])
    city = StringField('City', validators=[Optional(), Length(max=50)])
    state = StringField('State', validators=[Optional(), Length(max=50)])
    pincode = StringField('Pincode', validators=[Optional(), Length(max=10)])
    hospital_name = StringField('Hospital Name', validators=[Optional(), Length(max=100)])
    hospital_license = StringField('Hospital License Number', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class NeedForm(FlaskForm):
    need_type = SelectField('Type of Need', choices=[
        (NeedType.ORGAN.value, 'Organ'),
        (NeedType.BLOOD.value, 'Blood'),
        (NeedType.SERUM.value, 'Serum'),
        (NeedType.PLASMA.value, 'Plasma'),
        (NeedType.PLATELETS.value, 'Platelets')
    ], validators=[DataRequired()])
    organ_name = SelectField('Organ Needed', choices=[
        ('', 'Select Organ'),
        ('heart', 'Heart'),
        ('liver', 'Liver'),
        ('kidney', 'Kidney'),
        ('lung', 'Lung'),
        ('pancreas', 'Pancreas'),
        ('intestine', 'Intestine'),
        ('cornea', 'Cornea'),
        ('skin', 'Skin'),
        ('bone', 'Bone'),
        ('heart_valve', 'Heart Valve'),
        ('other', 'Other')
    ], validators=[Optional()])
    blood_group = SelectField('Blood Group Required', choices=[
        ('', 'Select Blood Group'),
        (BloodGroup.A_POS.value, 'A+'),
        (BloodGroup.A_NEG.value, 'A-'),
        (BloodGroup.B_POS.value, 'B+'),
        (BloodGroup.B_NEG.value, 'B-'),
        (BloodGroup.AB_POS.value, 'AB+'),
        (BloodGroup.AB_NEG.value, 'AB-'),
        (BloodGroup.O_POS.value, 'O+'),
        (BloodGroup.O_NEG.value, 'O-')
    ], validators=[Optional()])
    units_needed = IntegerField('Units Needed', validators=[Optional(), NumberRange(min=1)], default=1)
    urgency = SelectField('Urgency Level', choices=[
        (UrgencyLevel.LOW.value, 'Low - Can wait weeks'),
        (UrgencyLevel.MEDIUM.value, 'Medium - Needed within days'),
        (UrgencyLevel.HIGH.value, 'High - Needed within 24 hours'),
        (UrgencyLevel.CRITICAL.value, 'Critical - Needed immediately')
    ], validators=[DataRequired()], default=UrgencyLevel.MEDIUM.value)
    patient_name = StringField('Patient Name', validators=[DataRequired(), Length(max=100)])
    patient_age = IntegerField('Patient Age', validators=[DataRequired(), NumberRange(min=0, max=120)])
    patient_gender = SelectField('Patient Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    patient_blood_group = SelectField('Patient Blood Group', choices=[
        (BloodGroup.A_POS.value, 'A+'),
        (BloodGroup.A_NEG.value, 'A-'),
        (BloodGroup.B_POS.value, 'B+'),
        (BloodGroup.B_NEG.value, 'B-'),
        (BloodGroup.AB_POS.value, 'AB+'),
        (BloodGroup.AB_NEG.value, 'AB-'),
        (BloodGroup.O_POS.value, 'O+'),
        (BloodGroup.O_NEG.value, 'O-')
    ], validators=[DataRequired()])
    patient_weight = FloatField('Patient Weight (kg)', validators=[Optional(), NumberRange(min=0, max=300)])
    medical_condition = TextAreaField('Medical Condition / Diagnosis', validators=[DataRequired(), Length(max=2000)])
    doctor_name = StringField('Treating Doctor Name', validators=[Optional(), Length(max=100)])
    hospital_name = StringField('Hospital Name', validators=[DataRequired(), Length(max=100)])
    hospital_address = TextAreaField('Hospital Address', validators=[DataRequired(), Length(max=500)])
    contact_person = StringField('Contact Person Name', validators=[DataRequired(), Length(max=100)])
    contact_phone = StringField('Contact Phone', validators=[DataRequired(), Length(min=10, max=15)])
    contact_email = EmailField('Contact Email', validators=[Optional(), Email()])
    additional_notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=1000)])
    required_by = DateTimeField('Required By (Date & Time)', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    submit = SubmitField('Post Need')

class DonationForm(FlaskForm):
    donation_type = SelectField('Type of Donation', choices=[
        (NeedType.ORGAN.value, 'Organ (from brain-dead patient)'),
        (NeedType.BLOOD.value, 'Blood'),
        (NeedType.SERUM.value, 'Serum'),
        (NeedType.PLASMA.value, 'Plasma'),
        (NeedType.PLATELETS.value, 'Platelets')
    ], validators=[DataRequired()])
    organ_name = SelectField('Organ Available', choices=[
        ('', 'Select Organ'),
        ('heart', 'Heart'),
        ('liver', 'Liver'),
        ('kidney', 'Kidney'),
        ('lung', 'Lung'),
        ('pancreas', 'Pancreas'),
        ('intestine', 'Intestine'),
        ('cornea', 'Cornea'),
        ('skin', 'Skin'),
        ('bone', 'Bone'),
        ('heart_valve', 'Heart Valve'),
        ('multiple', 'Multiple Organs'),
        ('other', 'Other')
    ], validators=[Optional()])
    blood_group = SelectField('Donor Blood Group', choices=[
        ('', 'Select Blood Group'),
        (BloodGroup.A_POS.value, 'A+'),
        (BloodGroup.A_NEG.value, 'A-'),
        (BloodGroup.B_POS.value, 'B+'),
        (BloodGroup.B_NEG.value, 'B-'),
        (BloodGroup.AB_POS.value, 'AB+'),
        (BloodGroup.AB_NEG.value, 'AB-'),
        (BloodGroup.O_POS.value, 'O+'),
        (BloodGroup.O_NEG.value, 'O-')
    ], validators=[Optional()])
    units_available = IntegerField('Units Available', validators=[Optional(), NumberRange(min=1)], default=1)
    donor_name = StringField('Donor Name', validators=[DataRequired(), Length(max=100)])
    donor_age = IntegerField('Donor Age', validators=[DataRequired(), NumberRange(min=0, max=120)])
    donor_gender = SelectField('Donor Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    donor_blood_group = SelectField('Donor Blood Group', choices=[
        (BloodGroup.A_POS.value, 'A+'),
        (BloodGroup.A_NEG.value, 'A-'),
        (BloodGroup.B_POS.value, 'B+'),
        (BloodGroup.B_NEG.value, 'B-'),
        (BloodGroup.AB_POS.value, 'AB+'),
        (BloodGroup.AB_NEG.value, 'AB-'),
        (BloodGroup.O_POS.value, 'O+'),
        (BloodGroup.O_NEG.value, 'O-')
    ], validators=[DataRequired()])
    donor_weight = FloatField('Donor Weight (kg)', validators=[Optional(), NumberRange(min=0, max=300)])
    is_brain_dead = BooleanField('Donor is Brain Dead (for organ donation)')
    cause_of_death = TextAreaField('Cause of Death / Medical History', validators=[Optional(), Length(max=2000)])
    time_of_death = DateTimeField('Time of Death (for organ donation)', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    hospital_name = StringField('Hospital Name', validators=[DataRequired(), Length(max=100)])
    hospital_address = TextAreaField('Hospital Address', validators=[DataRequired(), Length(max=500)])
    doctor_name = StringField('Certifying Doctor Name', validators=[Optional(), Length(max=100)])
    contact_person = StringField('Contact Person Name', validators=[DataRequired(), Length(max=100)])
    contact_phone = StringField('Contact Phone', validators=[DataRequired(), Length(min=10, max=15)])
    contact_email = EmailField('Contact Email', validators=[Optional(), Email()])
    additional_notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=1000)])
    available_from = DateTimeField('Available From', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    available_until = DateTimeField('Available Until', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    submit = SubmitField('Post Donation Availability')

class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    blood_group = SelectField('Blood Group', choices=[
        ('', 'Select Blood Group'),
        (BloodGroup.A_POS.value, 'A+'),
        (BloodGroup.A_NEG.value, 'A-'),
        (BloodGroup.B_POS.value, 'B+'),
        (BloodGroup.B_NEG.value, 'B-'),
        (BloodGroup.AB_POS.value, 'AB+'),
        (BloodGroup.AB_NEG.value, 'AB-'),
        (BloodGroup.O_POS.value, 'O+'),
        (BloodGroup.O_NEG.value, 'O-')
    ], validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional(), Length(max=500)])
    city = StringField('City', validators=[Optional(), Length(max=50)])
    state = StringField('State', validators=[Optional(), Length(max=50)])
    pincode = StringField('Pincode', validators=[Optional(), Length(max=10)])
    hospital_name = StringField('Hospital Name', validators=[Optional(), Length(max=100)])
    hospital_license = StringField('Hospital License Number', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Update Profile')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Send Message')

class MatchResponseForm(FlaskForm):
    match_id = HiddenField('Match ID')
    action = RadioField('Response', choices=[
        ('accept', 'Accept - I can help'),
        ('decline', 'Decline - Cannot help at this time')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Submit Response')