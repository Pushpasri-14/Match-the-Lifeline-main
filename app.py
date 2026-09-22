from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from config import Config
from models import db, User, Need, Donation, Match, Notification, UserType, NeedType, BloodGroup, UrgencyLevel, Status
from forms import (
    LoginForm, RegisterForm, NeedForm, DonationForm,
    ProfileForm, ChangePasswordForm, ContactForm, MatchResponseForm
)
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    def create_notification(user_id, title, message, related_type=None, related_id=None):
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            related_type=related_type,
            related_id=related_id
        )
        db.session.add(notification)
        db.session.commit()
    
    def check_compatibility(need, donation):
        if need.need_type != donation.donation_type:
            return False
        
        if need.need_type == NeedType.ORGAN:
            if need.organ_name and donation.organ_name:
                if need.organ_name != donation.organ_name and donation.organ_name != 'multiple':
                    return False
        
        if need.blood_group and donation.blood_group:
            compatible_groups = {
                BloodGroup.A_POS: [BloodGroup.A_POS, BloodGroup.A_NEG, BloodGroup.O_POS, BloodGroup.O_NEG],
                BloodGroup.A_NEG: [BloodGroup.A_NEG, BloodGroup.O_NEG],
                BloodGroup.B_POS: [BloodGroup.B_POS, BloodGroup.B_NEG, BloodGroup.O_POS, BloodGroup.O_NEG],
                BloodGroup.B_NEG: [BloodGroup.B_NEG, BloodGroup.O_NEG],
                BloodGroup.AB_POS: [bg for bg in BloodGroup],
                BloodGroup.AB_NEG: [BloodGroup.AB_NEG, BloodGroup.A_NEG, BloodGroup.B_NEG, BloodGroup.O_NEG],
                BloodGroup.O_POS: [BloodGroup.O_POS, BloodGroup.O_NEG],
                BloodGroup.O_NEG: [BloodGroup.O_NEG],
            }
            if donation.blood_group not in compatible_groups.get(need.blood_group, []):
                return False
        
        if need.units_needed > donation.units_available:
            return False
            
        return True
    
    def auto_match(need):
        donations = Donation.query.filter_by(status=Status.ACTIVE).all()
        for donation in donations:
            if check_compatibility(need, donation):
                existing_match = Match.query.filter_by(need_id=need.id, donation_id=donation.id).first()
                if not existing_match:
                    match = Match(
                        need_id=need.id,
                        donation_id=donation.id,
                        patient_id=need.patient_id,
                        donor_id=donation.donor_id,
                        status='pending'
                    )
                    db.session.add(match)
                    
                    create_notification(
                        donation.donor_id,
                        'New Match Found',
                        f'Your donation matches a need for {need.patient_name} ({need.need_type.value})',
                        'match', match.id
                    )
                    create_notification(
                        need.patient_id,
                        'Potential Donor Found',
                        f'A matching donor is available for {need.need_type.value}',
                        'match', match.id
                    )
        db.session.commit()
    
    @app.route('/')
    def index():
        active_needs = Need.query.filter_by(status=Status.ACTIVE).order_by(Need.urgency.desc(), Need.created_at.desc()).limit(10).all()
        active_donations = Donation.query.filter_by(status=Status.ACTIVE).order_by(Donation.created_at.desc()).limit(10).all()
        stats = {
            'total_needs': Need.query.count(),
            'active_needs': Need.query.filter_by(status=Status.ACTIVE).count(),
            'total_donations': Donation.query.count(),
            'active_donations': Donation.query.filter_by(status=Status.ACTIVE).count(),
            'successful_matches': Match.query.filter_by(status='completed').count(),
        }
        return render_template('index.html', active_needs=active_needs, active_donations=active_donations, stats=stats)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                user.last_login = datetime.utcnow()
                db.session.commit()
                next_page = request.args.get('next')
                flash('Welcome back!', 'success')
                return redirect(next_page or url_for('dashboard'))
            flash('Invalid email or password', 'danger')
        return render_template('auth/login.html', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        form = RegisterForm()
        if form.validate_on_submit():
            user = User(
                email=form.email.data,
                full_name=form.full_name.data,
                phone=form.phone.data,
                user_type=UserType(form.user_type.data),
                blood_group=BloodGroup(form.blood_group.data) if form.blood_group.data else None,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                pincode=form.pincode.data,
                hospital_name=form.hospital_name.data,
                hospital_license=form.hospital_license.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        return render_template('auth/register.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.user_type == UserType.PATIENT:
            my_needs = Need.query.filter_by(patient_id=current_user.id).order_by(Need.created_at.desc()).all()
            my_matches = Match.query.filter_by(patient_id=current_user.id).order_by(Match.matched_at.desc()).all()
            return render_template('dashboard/patient.html', needs=my_needs, matches=my_matches)
        elif current_user.user_type == UserType.DONOR:
            my_donations = Donation.query.filter_by(donor_id=current_user.id).order_by(Donation.created_at.desc()).all()
            my_matches = Match.query.filter_by(donor_id=current_user.id).order_by(Match.matched_at.desc()).all()
            return render_template('dashboard/donor.html', donations=my_donations, matches=my_matches)
        else:
            my_donations = Donation.query.filter_by(donor_id=current_user.id).order_by(Donation.created_at.desc()).all()
            hospital_needs = Need.query.filter_by(hospital_name=current_user.hospital_name).order_by(Need.created_at.desc()).all()
            return render_template('dashboard/hospital.html', donations=my_donations, needs=hospital_needs)
    
    @app.route('/post-need', methods=['GET', 'POST'])
    @login_required
    def post_need():
        if current_user.user_type not in [UserType.PATIENT, UserType.HOSPITAL]:
            flash('Only patients and hospitals can post needs.', 'warning')
            return redirect(url_for('dashboard'))
        
        # Check if this is for a specific donation (from query param or form data)
        match_donation_id = request.args.get('match_donation', type=int) or request.form.get('match_donation', type=int)
        match_donation = None
        if match_donation_id:
            match_donation = Donation.query.get(match_donation_id)
            if not match_donation or match_donation.status != Status.ACTIVE:
                flash('The donation you\'re trying to match is no longer available.', 'warning')
                match_donation = None
        
        form = NeedForm()
        
        # Pre-fill form if matching a specific donation
        if match_donation and request.method == 'GET':
            form.need_type.data = match_donation.donation_type.value
            form.blood_group.data = match_donation.blood_group.value if match_donation.blood_group else ''
            form.units_needed.data = match_donation.units_available
            form.patient_blood_group.data = match_donation.donor_blood_group.value
            # For organ needs, pre-select the organ
            if match_donation.donation_type == NeedType.ORGAN and match_donation.organ_name:
                form.organ_name.data = match_donation.organ_name
        
        if form.validate_on_submit():
            need = Need(
                patient_id=current_user.id,
                need_type=NeedType(form.need_type.data),
                organ_name=form.organ_name.data if form.need_type.data == NeedType.ORGAN.value else None,
                blood_group=BloodGroup(form.blood_group.data) if form.blood_group.data else None,
                units_needed=form.units_needed.data,
                urgency=UrgencyLevel(form.urgency.data),
                patient_name=form.patient_name.data,
                patient_age=form.patient_age.data,
                patient_gender=form.patient_gender.data,
                patient_blood_group=BloodGroup(form.patient_blood_group.data),
                patient_weight=form.patient_weight.data,
                medical_condition=form.medical_condition.data,
                doctor_name=form.doctor_name.data,
                hospital_name=form.hospital_name.data,
                hospital_address=form.hospital_address.data,
                contact_person=form.contact_person.data,
                contact_phone=form.contact_phone.data,
                contact_email=form.contact_email.data,
                additional_notes=form.additional_notes.data,
                required_by=form.required_by.data,
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            db.session.add(need)
            db.session.commit()
            
            # If matching a specific donation, create direct match
            if match_donation:
                if check_compatibility(need, match_donation):
                    existing_match = Match.query.filter_by(need_id=need.id, donation_id=match_donation.id).first()
                    if not existing_match:
                        match = Match(
                            need_id=need.id,
                            donation_id=match_donation.id,
                            patient_id=need.patient_id,
                            donor_id=match_donation.donor_id,
                            status='pending'
                        )
                        db.session.add(match)
                        
                        create_notification(
                            match_donation.donor_id,
                            'Direct Match Found',
                            f'A patient has responded directly to your donation for {match_donation.donor_name} ({match_donation.donation_type.value})',
                            'match', match.id
                        )
                        create_notification(
                            need.patient_id,
                            'Match Created',
                            f'Your need has been matched with {match_donation.donor_name}\'s donation',
                            'match', match.id
                        )
                        flash('Perfect! Your need has been directly matched with {}\'s donation. They have been notified!'.format(
                            match_donation.donor_name), 'success')
                else:
                    flash('Need posted, but it may not be compatible with the specific donation. We\'ll notify you of any other matches.', 'warning')
            else:
                auto_match(need)
                flash('Need posted successfully! We\'ll notify you when a match is found.', 'success')
            
            return redirect(url_for('dashboard'))
        return render_template('needs/post.html', form=form, match_donation=match_donation)
    
    @app.route('/post-donation', methods=['GET', 'POST'])
    @login_required
    def post_donation():
        if current_user.user_type not in [UserType.DONOR, UserType.HOSPITAL]:
            flash('Only donors and hospitals can post donations.', 'warning')
            return redirect(url_for('dashboard'))
        
        # Check if this is for a specific need (from query param or form data)
        match_need_id = request.args.get('match_need', type=int) or request.form.get('match_need', type=int)
        match_need = None
        if match_need_id:
            match_need = Need.query.get(match_need_id)
            if not match_need or match_need.status != Status.ACTIVE:
                flash('The need you\'re trying to match is no longer active.', 'warning')
                match_need = None
        
        form = DonationForm()
        
        # Pre-fill form if matching a specific need
        if match_need and request.method == 'GET':
            form.donation_type.data = match_need.need_type.value
            form.blood_group.data = match_need.blood_group.value if match_need.blood_group else ''
            form.units_available.data = match_need.units_needed
            # For organ donations, pre-select the organ
            if match_need.need_type == NeedType.ORGAN and match_need.organ_name:
                form.organ_name.data = match_need.organ_name
        
        if form.validate_on_submit():
            donation = Donation(
                donor_id=current_user.id,
                donation_type=NeedType(form.donation_type.data),
                organ_name=form.organ_name.data if form.donation_type.data == NeedType.ORGAN.value else None,
                blood_group=BloodGroup(form.blood_group.data) if form.blood_group.data else None,
                units_available=form.units_available.data,
                donor_name=form.donor_name.data,
                donor_age=form.donor_age.data,
                donor_gender=form.donor_gender.data,
                donor_blood_group=BloodGroup(form.donor_blood_group.data),
                donor_weight=form.donor_weight.data,
                is_brain_dead=form.is_brain_dead.data,
                cause_of_death=form.cause_of_death.data,
                time_of_death=form.time_of_death.data,
                hospital_name=form.hospital_name.data,
                hospital_address=form.hospital_address.data,
                doctor_name=form.doctor_name.data,
                contact_person=form.contact_person.data,
                contact_phone=form.contact_phone.data,
                contact_email=form.contact_email.data,
                additional_notes=form.additional_notes.data,
                available_from=form.available_from.data,
                available_until=form.available_until.data
            )
            db.session.add(donation)
            db.session.commit()
            
            # If matching a specific need, create direct match first
            if match_need:
                if check_compatibility(match_need, donation):
                    existing_match = Match.query.filter_by(need_id=match_need.id, donation_id=donation.id).first()
                    if not existing_match:
                        match = Match(
                            need_id=match_need.id,
                            donation_id=donation.id,
                            patient_id=match_need.patient_id,
                            donor_id=donation.donor_id,
                            status='pending'
                        )
                        db.session.add(match)
                        
                        create_notification(
                            match_need.patient_id,
                            'Direct Match Found',
                            f'A donor has responded directly to your need for {match_need.patient_name} ({match_need.need_type.value})',
                            'match', match.id
                        )
                        create_notification(
                            donation.donor_id,
                            'Match Created',
                            f'Your donation has been matched with {match_need.patient_name}\'s need',
                            'match', match.id
                        )
            
            # Also auto-match with other compatible needs
            needs = Need.query.filter_by(status=Status.ACTIVE).all()
            for need in needs:
                if need.id == match_need_id:
                    continue  # Already handled above
                if check_compatibility(need, donation):
                    existing_match = Match.query.filter_by(need_id=need.id, donation_id=donation.id).first()
                    if not existing_match:
                        match = Match(
                            need_id=need.id,
                            donation_id=donation.id,
                            patient_id=need.patient_id,
                            donor_id=donation.donor_id,
                            status='pending'
                        )
                        db.session.add(match)
                        
                        create_notification(
                            need.patient_id,
                            'Potential Donor Found',
                            f'A matching donor is available for {need.need_type.value}',
                            'match', match.id
                        )
                        create_notification(
                            donation.donor_id,
                            'New Match Found',
                            f'Your donation matches a need for {need.patient_name} ({need.need_type.value})',
                            'match', match.id
                        )
            db.session.commit()
            
            # Provide specific feedback about direct match
            if match_need:
                if check_compatibility(match_need, donation):
                    flash('Perfect! Your donation has been directly matched with {}\'s need for {}. They have been notified!'.format(
                        match_need.patient_name, match_need.need_type.value.capitalize()), 'success')
                else:
                    flash('Donation posted, but it may not be compatible with the specific need. We\'ll notify you of any other matches.', 'warning')
            else:
                flash('Donation availability posted successfully! We\'ll notify you when matches are found.', 'success')
            
            return redirect(url_for('dashboard'))
        return render_template('donations/post.html', form=form, match_need=match_need)
    
    @app.route('/browse-needs')
    def browse_needs():
        page = request.args.get('page', 1, type=int)
        need_type = request.args.get('type')
        urgency = request.args.get('urgency')
        blood_group = request.args.get('blood_group')
        city = request.args.get('city')
        
        query = Need.query.filter_by(status=Status.ACTIVE)
        
        if need_type:
            query = query.filter_by(need_type=NeedType(need_type))
        if urgency:
            query = query.filter_by(urgency=UrgencyLevel(urgency))
        if blood_group:
            query = query.filter_by(blood_group=BloodGroup(blood_group))
        if city:
            query = query.filter(Need.hospital_address.ilike(f'%{city}%'))
        
        needs = query.order_by(Need.urgency.desc(), Need.created_at.desc()).paginate(page=page, per_page=12)
        return render_template('needs/browse.html', needs=needs, NeedType=NeedType, UrgencyLevel=UrgencyLevel, BloodGroup=BloodGroup)
    
    @app.route('/browse-donations')
    def browse_donations():
        page = request.args.get('page', 1, type=int)
        donation_type = request.args.get('type')
        blood_group = request.args.get('blood_group')
        city = request.args.get('city')
        
        query = Donation.query.filter_by(status=Status.ACTIVE)
        
        if donation_type:
            query = query.filter_by(donation_type=NeedType(donation_type))
        if blood_group:
            query = query.filter_by(blood_group=BloodGroup(blood_group))
        if city:
            query = query.filter(Donation.hospital_address.ilike(f'%{city}%'))
        
        donations = query.order_by(Donation.created_at.desc()).paginate(page=page, per_page=12)
        return render_template('donations/browse.html', donations=donations, NeedType=NeedType, BloodGroup=BloodGroup)
    
    @app.route('/need/<int:id>')
    def view_need(id):
        need = Need.query.get_or_404(id)
        return render_template('needs/view.html', need=need)
    
    @app.route('/donation/<int:id>')
    def view_donation(id):
        donation = Donation.query.get_or_404(id)
        return render_template('donations/view.html', donation=donation)
    
    @app.route('/match/<int:id>/respond', methods=['GET', 'POST'])
    @login_required
    def respond_match(id):
        match = Match.query.get_or_404(id)
        if match.donor_id != current_user.id and match.patient_id != current_user.id:
            abort(403)
        form = MatchResponseForm()
        if form.validate_on_submit():
            match.status = 'accepted' if form.action.data == 'accept' else 'declined'
            match.responded_at = datetime.utcnow()
            match.notes = form.notes.data
            if form.action.data == 'accept':
                match.need.status = Status.MATCHED
                match.donation.status = Status.MATCHED
                create_notification(
                    match.patient_id,
                    'Match Accepted',
                    f'Your match for {match.need.need_type.value} has been accepted by the donor',
                    'match', match.id
                )
                create_notification(
                    match.donor_id,
                    'Match Confirmed',
                    f'You have accepted the match for {match.need.patient_name}',
                    'match', match.id
                )
            else:
                create_notification(
                    match.patient_id,
                    'Match Declined',
                    f'The donor has declined the match for {match.need.need_type.value}',
                    'match', match.id
                )
            db.session.commit()
            flash('Response submitted successfully.', 'success')
            return redirect(url_for('dashboard'))
        return render_template('matches/respond.html', match=match, form=form)
    
    @app.route('/match/<int:id>/complete', methods=['POST'])
    @login_required
    def complete_match(id):
        match = Match.query.get_or_404(id)
        if match.donor_id != current_user.id and match.patient_id != current_user.id:
            abort(403)
        match.status = 'completed'
        match.completed_at = datetime.utcnow()
        match.need.status = Status.FULFILLED
        match.donation.status = Status.FULFILLED
        db.session.commit()
        flash('Match marked as completed. Thank you for saving a life!', 'success')
        return redirect(url_for('dashboard'))
    
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        form = ProfileForm(obj=current_user)
        if form.validate_on_submit():
            current_user.full_name = form.full_name.data
            current_user.phone = form.phone.data
            current_user.blood_group = BloodGroup(form.blood_group.data) if form.blood_group.data else None
            current_user.address = form.address.data
            current_user.city = form.city.data
            current_user.state = form.state.data
            current_user.pincode = form.pincode.data
            current_user.hospital_name = form.hospital_name.data
            current_user.hospital_license = form.hospital_license.data
            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('profile'))
        return render_template('profile.html', form=form)
    
    @app.route('/change-password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        form = ChangePasswordForm()
        if form.validate_on_submit():
            if current_user.check_password(form.current_password.data):
                current_user.set_password(form.new_password.data)
                db.session.commit()
                flash('Password changed successfully.', 'success')
                return redirect(url_for('profile'))
            flash('Current password is incorrect.', 'danger')
        return render_template('change_password.html', form=form)
    
    @app.route('/notifications')
    @login_required
    def notifications():
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
        return render_template('notifications.html', notifications=notifications)
    
    @app.route('/notification/<int:id>/read', methods=['POST'])
    @login_required
    def mark_notification_read(id):
        notification = Notification.query.get_or_404(id)
        if notification.user_id != current_user.id:
            abort(403)
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        form = ContactForm()
        if form.validate_on_submit():
            flash('Thank you for your message. We will get back to you soon.', 'success')
            return redirect(url_for('contact'))
        return render_template('contact.html', form=form)
    
    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/how-it-works')
    def how_it_works():
        return render_template('how_it_works.html')
    
    @app.context_processor
    def utility_processor():
        def get_urgency_color(urgency):
            colors = {
                UrgencyLevel.LOW: 'success',
                UrgencyLevel.MEDIUM: 'warning',
                UrgencyLevel.HIGH: 'orange',
                UrgencyLevel.CRITICAL: 'danger'
            }
            return colors.get(urgency, 'secondary')
        
        def get_status_color(status):
            colors = {
                Status.ACTIVE: 'success',
                Status.MATCHED: 'info',
                Status.FULFILLED: 'primary',
                Status.EXPIRED: 'secondary',
                Status.CANCELLED: 'danger'
            }
            return colors.get(status, 'secondary')
        
        def timeago(dt):
            """Return human-readable time difference from now"""
            if not dt:
                return ''
            now = datetime.utcnow()
            diff = now - dt
            seconds = diff.total_seconds()
            
            if seconds < 60:
                return 'just now'
            elif seconds < 3600:
                minutes = int(seconds / 60)
                return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
            elif seconds < 86400:
                hours = int(seconds / 3600)
                return f'{hours} hour{"s" if hours > 1 else ""} ago'
            elif seconds < 604800:
                days = int(seconds / 86400)
                return f'{days} day{"s" if days > 1 else ""} ago'
            elif seconds < 2592000:
                weeks = int(seconds / 604800)
                return f'{weeks} week{"s" if weeks > 1 else ""} ago'
            else:
                return dt.strftime('%d %b %Y')
        
        return dict(get_urgency_color=get_urgency_color, get_status_color=get_status_color, timeago=timeago)
    
    with app.app_context():
        db.create_all()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)