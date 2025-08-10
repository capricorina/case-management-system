from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
from markupsafe import Markup
import re
from functools import wraps

# Import our custom modules
from models import db, User, Participant, Case, ImportantPerson, Referral
from forms import LoginForm, ParticipantForm, CaseForm, UserProfileForm, NewUserForm, ReferralForm

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'fallback-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///case_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Custom Jinja2 filter for newline to <br> conversion
@app.template_filter('nl2br')
def nl2br_filter(text):
    """Convert newlines to HTML line breaks"""
    if not text:
        return text
    return Markup(re.sub(r'\n', '<br>', str(text)))

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Permission decorators
def require_permission(permission_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            
            permission_hierarchy = {
                'volunteer': 1,
                'coordinator': 2,
                'admin': 3
            }
            
            user_level = permission_hierarchy.get(current_user.role, 0)
            required_level = permission_hierarchy.get(permission_level, 999)
            
            if user_level < required_level:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data) and user.is_active:
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password, or account is disabled.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get summary statistics
    total_participants = Participant.query.count()
    total_referrals = Referral.query.count()
    pending_referrals = Referral.query.filter_by(status='pending').count()
    active_cases = Case.query.filter_by(status='in-progress').count()
    completed_cases = Case.query.filter_by(status='completed').count()
    waitlisted_cases = Case.query.filter_by(status='waitlisted').count()
    
    # Get recent cases and referrals based on user role
    recent_cases = Case.query.order_by(Case.created_at.desc()).limit(5).all()
    recent_referrals = Referral.query.order_by(Referral.created_at.desc()).limit(5).all() if current_user.role in ['coordinator', 'admin'] else []
    
    return render_template('dashboard.html', 
                         total_participants=total_participants,
                         total_referrals=total_referrals,
                         pending_referrals=pending_referrals,
                         active_cases=active_cases,
                         completed_cases=completed_cases,
                         waitlisted_cases=waitlisted_cases,
                         recent_cases=recent_cases,
                         recent_referrals=recent_referrals)

@app.route('/participants')
@login_required
def participants():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    if search:
        participants_query = Participant.query.filter(
            (Participant.first_name.contains(search)) |
            (Participant.last_name.contains(search)) |
            (Participant.email.contains(search))
        )
    else:
        participants_query = Participant.query
    
    participants = participants_query.order_by(Participant.last_name, Participant.first_name)\
                                   .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('participants.html', participants=participants, search=search)

@app.route('/participant/new', methods=['GET', 'POST'])
@login_required
@require_permission('coordinator')
def new_participant():
    form = ParticipantForm()
    if form.validate_on_submit():
        participant = Participant(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            date_of_birth=form.date_of_birth.data,
            phone=form.phone.data,
            email=form.email.data,
            street_address=form.street_address.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data,
            emergency_contact_name=form.emergency_contact_name.data,
            emergency_contact_phone=form.emergency_contact_phone.data,
            emergency_contact_relationship=form.emergency_contact_relationship.data,
            school_name=form.school_name.data,
            grade_level=form.grade_level.data,
            race=form.race.data,
            ethnicity=form.ethnicity.data,
            gender_identity=form.gender_identity.data,
            sex=form.sex.data,
            pronouns=form.pronouns.data,
            family_structure=form.family_structure.data,
            allergies=form.allergies.data,
            illnesses_disabilities=form.illnesses_disabilities.data,
            primary_care_doctor=form.primary_care_doctor.data,
            emergency_instructions=form.emergency_instructions.data,
            preferred_contact_method=form.preferred_contact_method.data,
            preferred_language=form.preferred_language.data,
            notes=form.notes.data,
            source='manual'  # Mark as manually created
        )
        db.session.add(participant)
        db.session.flush()  # Get the participant ID
        
        # Handle important persons
        important_persons_data = [
            {
                'name': form.important_person_1_name.data,
                'role': form.important_person_1_role.data,
                'phone': form.important_person_1_phone.data,
                'email': form.important_person_1_email.data
            },
            {
                'name': form.important_person_2_name.data,
                'role': form.important_person_2_role.data,
                'phone': form.important_person_2_phone.data,
                'email': form.important_person_2_email.data
            },
            {
                'name': form.important_person_3_name.data,
                'role': form.important_person_3_role.data,
                'phone': form.important_person_3_phone.data,
                'email': form.important_person_3_email.data
            }
        ]
        
        for person_data in important_persons_data:
            if person_data['name']:  # Only create if name is provided
                important_person = ImportantPerson(
                    participant_id=participant.id,
                    name=person_data['name'],
                    role=person_data['role'],
                    phone=person_data['phone'],
                    email=person_data['email']
                )
                db.session.add(important_person)
        
        db.session.commit()
        flash('Participant created successfully!', 'success')
        return redirect(url_for('participant_detail', id=participant.id))
    
    return render_template('participant_form.html', form=form, title='New Participant')

@app.route('/participant/<int:id>')
@login_required
def participant_detail(id):
    participant = Participant.query.get_or_404(id)
    cases = Case.query.filter_by(participant_id=id).order_by(Case.created_at.desc()).all()
    important_persons = ImportantPerson.query.filter_by(participant_id=id).all()
    referral = Referral.query.filter_by(participant_id=id).first()
    return render_template('participant_detail.html', 
                         participant=participant, 
                         cases=cases, 
                         important_persons=important_persons,
                         referral=referral)

@app.route('/participant/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@require_permission('coordinator')
def edit_participant(id):
    participant = Participant.query.get_or_404(id)
    form = ParticipantForm(obj=participant)
    
    # Populate important persons data
    important_persons = ImportantPerson.query.filter_by(participant_id=id).all()
    for i, person in enumerate(important_persons[:3], 1):  # Only first 3
        if i == 1:
            form.important_person_1_name.data = person.name
            form.important_person_1_role.data = person.role
            form.important_person_1_phone.data = person.phone
            form.important_person_1_email.data = person.email
        elif i == 2:
            form.important_person_2_name.data = person.name
            form.important_person_2_role.data = person.role
            form.important_person_2_phone.data = person.phone
            form.important_person_2_email.data = person.email
        elif i == 3:
            form.important_person_3_name.data = person.name
            form.important_person_3_role.data = person.role
            form.important_person_3_phone.data = person.phone
            form.important_person_3_email.data = person.email
    
    if form.validate_on_submit():
        form.populate_obj(participant)
        participant.updated_at = datetime.utcnow()
        
        # Update important persons
        ImportantPerson.query.filter_by(participant_id=id).delete()
        
        important_persons_data = [
            {
                'name': form.important_person_1_name.data,
                'role': form.important_person_1_role.data,
                'phone': form.important_person_1_phone.data,
                'email': form.important_person_1_email.data
            },
            {
                'name': form.important_person_2_name.data,
                'role': form.important_person_2_role.data,
                'phone': form.important_person_2_phone.data,
                'email': form.important_person_2_email.data
            },
            {
                'name': form.important_person_3_name.data,
                'role': form.important_person_3_role.data,
                'phone': form.important_person_3_phone.data,
                'email': form.important_person_3_email.data
            }
        ]
        
        for person_data in important_persons_data:
            if person_data['name']:  # Only create if name is provided
                important_person = ImportantPerson(
                    participant_id=participant.id,
                    name=person_data['name'],
                    role=person_data['role'],
                    phone=person_data['phone'],
                    email=person_data['email']
                )
                db.session.add(important_person)
        
        db.session.commit()
        flash('Participant updated successfully!', 'success')
        return redirect(url_for('participant_detail', id=participant.id))
    
    return render_template('participant_form.html', form=form, title='Edit Participant', participant=participant)

# Referral routes
@app.route('/referrals')
@login_required
@require_permission('coordinator')
def referrals():
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = Referral.query
    
    if status:
        query = query.filter(Referral.status == status)
    
    if search:
        query = query.filter(
            (Referral.first_name.contains(search)) |
            (Referral.last_name.contains(search)) |
            (Referral.referrer_name.contains(search))
        )
    
    referrals = query.order_by(Referral.created_at.desc())\
                    .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('referrals.html', referrals=referrals, status=status, search=search)

@app.route('/referral/<int:id>')
@login_required
@require_permission('coordinator')
def referral_detail(id):
    referral = Referral.query.get_or_404(id)
    return render_template('referral_detail.html', referral=referral)

@app.route('/referral/<int:id>/accept', methods=['POST'])
@login_required
@require_permission('coordinator')
def accept_referral(id):
    referral = Referral.query.get_or_404(id)
    
    if referral.participant_id:
        flash('This referral has already been processed.', 'warning')
        return redirect(url_for('referral_detail', id=id))
    
    # Create participant from referral
    participant = Participant(
        first_name=referral.first_name,
        last_name=referral.last_name,
        date_of_birth=referral.date_of_birth,
        phone=referral.phone,
        email=referral.email,
        street_address=referral.street_address,
        city=referral.city,
        state=referral.state,
        zip_code=referral.zip_code,
        emergency_contact_name=referral.emergency_contact_name,
        emergency_contact_phone=referral.emergency_contact_phone,
        emergency_contact_relationship=referral.emergency_contact_relationship,
        school_name=referral.school_name,
        grade_level=referral.grade_level,
        race=referral.race,
        ethnicity=referral.ethnicity,
        gender_identity=referral.gender_identity,
        sex=referral.sex,
        pronouns=referral.pronouns,
        family_structure=referral.family_structure,
        allergies=referral.allergies,
        illnesses_disabilities=referral.illnesses_disabilities,
        primary_care_doctor=referral.primary_care_doctor,
        emergency_instructions=referral.emergency_instructions,
        preferred_contact_method=referral.preferred_contact_method,
        preferred_language=referral.preferred_language,
        notes=referral.incident_description,
        source='referral'
    )
    
    db.session.add(participant)
    db.session.flush()
    
    # Update referral
    referral.status = 'accepted'
    referral.participant_id = participant.id
    referral.processed_at = datetime.utcnow()
    referral.processed_by = current_user.id
    
    db.session.commit()
    
    flash('Referral accepted and participant created successfully!', 'success')
    return redirect(url_for('participant_detail', id=participant.id))

@app.route('/referral/<int:id>/reject', methods=['POST'])
@login_required
@require_permission('coordinator')
def reject_referral(id):
    referral = Referral.query.get_or_404(id)
    rejection_reason = request.form.get('rejection_reason', '')
    
    referral.status = 'rejected'
    referral.rejection_reason = rejection_reason
    referral.processed_at = datetime.utcnow()
    referral.processed_by = current_user.id
    
    db.session.commit()
    
    flash('Referral rejected.', 'info')
    return redirect(url_for('referrals'))

# API endpoint for Zapier webhook
@app.route('/api/referrals', methods=['POST'])
def api_create_referral():
    """API endpoint for creating referrals via Zapier webhook"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'referrer_name', 'referrer_email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create referral
        referral = Referral(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            date_of_birth=datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            phone=data.get('phone'),
            email=data.get('email'),
            street_address=data.get('street_address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            emergency_contact_name=data.get('emergency_contact_name'),
            emergency_contact_phone=data.get('emergency_contact_phone'),
            emergency_contact_relationship=data.get('emergency_contact_relationship'),
            school_name=data.get('school_name'),
            grade_level=data.get('grade_level'),
            race=data.get('race'),
            ethnicity=data.get('ethnicity'),
            gender_identity=data.get('gender_identity'),
            sex=data.get('sex'),
            pronouns=data.get('pronouns'),
            family_structure=data.get('family_structure'),
            allergies=data.get('allergies'),
            illnesses_disabilities=data.get('illnesses_disabilities'),
            primary_care_doctor=data.get('primary_care_doctor'),
            emergency_instructions=data.get('emergency_instructions'),
            preferred_contact_method=data.get('preferred_contact_method'),
            preferred_language=data.get('preferred_language'),
            referrer_name=data.get('referrer_name'),
            referrer_email=data.get('referrer_email'),
            referrer_phone=data.get('referrer_phone'),
            referrer_organization=data.get('referrer_organization'),
            referrer_relationship=data.get('referrer_relationship'),
            incident_date=datetime.strptime(data.get('incident_date'), '%Y-%m-%d').date() if data.get('incident_date') else None,
            incident_description=data.get('incident_description'),
            desired_outcome=data.get('desired_outcome'),
            previous_interventions=data.get('previous_interventions'),
            urgency_level=data.get('urgency_level', 'medium'),
            status='pending'
        )
        
        db.session.add(referral)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'referral_id': referral.id,
            'message': 'Referral created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User management routes
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UserProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.email = form.email.data
        if form.new_password.data:
            current_user.password_hash = generate_password_hash(form.new_password.data)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', form=form)

@app.route('/users')
@login_required
@require_permission('admin')
def users():
    users = User.query.order_by(User.username).all()
    return render_template('users.html', users=users)

@app.route('/user/new', methods=['GET', 'POST'])
@login_required
@require_permission('admin')
def new_user():
    form = NewUserForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data,
            is_active=form.is_active.data
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.username} created successfully!', 'success')
        return redirect(url_for('users'))
    
    return render_template('user_form.html', form=form, title='New User')

@app.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@require_permission('admin')
def edit_user(id):
    user = User.query.get_or_404(id)
    form = NewUserForm(obj=user)
    form.password.validators = []  # Remove password requirement for editing
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        
        db.session.commit()
        flash(f'User {user.username} updated successfully!', 'success')
        return redirect(url_for('users'))
    
    return render_template('user_form.html', form=form, title='Edit User', user=user)

@app.route('/user/<int:id>/toggle', methods=['POST'])
@login_required
@require_permission('admin')
def toggle_user(id):
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:
        flash('You cannot disable your own account.', 'danger')
        return redirect(url_for('users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'enabled' if user.is_active else 'disabled'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('users'))

# Existing routes continue here...
@app.route('/cases')
@login_required
def cases():
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = Case.query.join(Participant)
    
    if status:
        query = query.filter(Case.status == status)
    
    if search:
        query = query.filter(
            (Participant.first_name.contains(search)) |
            (Participant.last_name.contains(search)) |
            (Case.case_number.contains(search))
        )
    
    cases = query.order_by(Case.created_at.desc())\
                 .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('cases.html', cases=cases, status=status, search=search)

@app.route('/case/new/<int:participant_id>', methods=['GET', 'POST'])
@login_required
@require_permission('coordinator')
def new_case(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    form = CaseForm()
    
    if form.validate_on_submit():
        # Generate case number
        case_count = Case.query.count() + 1
        case_number = f"RJ-{datetime.now().year}-{case_count:04d}"
        
        case = Case(
            participant_id=participant_id,
            case_number=case_number,
            program_type=form.program_type.data,
            status=form.status.data,
            description=form.description.data,
            assigned_staff=form.assigned_staff.data,
            referring_agency=form.referring_agency.data,
            referral_date=form.referral_date.data,
            intake_date=form.intake_date.data,
            offense_type=form.offense_type.data,
            victim_info=form.victim_info.data,
            outcome_notes=form.outcome_notes.data
        )
        db.session.add(case)
        db.session.commit()
        flash('Case created successfully!', 'success')
        return redirect(url_for('participant_detail', id=participant_id))
    
    return render_template('case_form.html', form=form, title='New Case', participant=participant)

@app.route('/case/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@require_permission('coordinator')
def edit_case(id):
    case = Case.query.get_or_404(id)
    form = CaseForm(obj=case)
    
    if form.validate_on_submit():
        form.populate_obj(case)
        case.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Case updated successfully!', 'success')
        return redirect(url_for('participant_detail', id=case.participant_id))
    
    return render_template('case_form.html', form=form, title='Edit Case', case=case)

@app.route('/api/participants/search')
@login_required
def api_participants_search():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    participants = Participant.query.filter(
        (Participant.first_name.contains(query)) |
        (Participant.last_name.contains(query))
    ).limit(10).all()
    
    results = [{
        'id': p.id,
        'name': f"{p.first_name} {p.last_name}",
        'email': p.email or ''
    } for p in participants]
    
    return jsonify(results)

def create_admin_user():
    """Create default admin user if none exists"""
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: admin/admin123")

with app.app_context():
    db.create_all()
    create_admin_user()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    app.run(debug=True, host='127.0.0.1', port=5000)