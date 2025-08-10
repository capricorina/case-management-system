from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for staff authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='volunteer')  # volunteer, coordinator, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    processed_referrals = db.relationship('Referral', backref='processor', lazy=True, foreign_keys='Referral.processed_by')
    
    @property
    def role_display(self):
        return self.role.title()
    
    @property
    def permissions(self):
        """Return list of permissions based on role"""
        perms = ['view_participants']
        if self.role in ['coordinator', 'admin']:
            perms.extend(['add_participants', 'edit_participants', 'manage_cases', 'manage_referrals'])
        if self.role == 'admin':
            perms.extend(['manage_users', 'system_admin'])
        return perms
    
    def has_permission(self, permission):
        return permission in self.permissions
    
    def __repr__(self):
        return f'<User {self.username}>'

class Participant(db.Model):
    """Participant model for individuals in the restorative justice program"""
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date)
    
    # Contact Information
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Address Information
    street_address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(20))
    zip_code = db.Column(db.String(10))
    
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relationship = db.Column(db.String(50))
    
    # School Information
    school_name = db.Column(db.String(100))
    grade_level = db.Column(db.String(20))
    
    # Demographic Information
    race = db.Column(db.String(100))
    ethnicity = db.Column(db.String(100))
    gender_identity = db.Column(db.String(50))
    sex = db.Column(db.String(20))
    pronouns = db.Column(db.String(50))
    family_structure = db.Column(db.String(100))
    
    # Health Information
    allergies = db.Column(db.Text)
    illnesses_disabilities = db.Column(db.Text)
    primary_care_doctor = db.Column(db.String(200))
    emergency_instructions = db.Column(db.Text)
    
    # Communication Preferences
    preferred_contact_method = db.Column(db.String(50))
    preferred_language = db.Column(db.String(50))
    
    # Additional Information
    notes = db.Column(db.Text)
    source = db.Column(db.String(20), default='manual')  # manual, referral
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cases = db.relationship('Case', backref='participant', lazy=True, cascade='all, delete-orphan')
    important_persons = db.relationship('ImportantPerson', backref='participant', lazy=True, cascade='all, delete-orphan')
    referral = db.relationship('Referral', backref='participant_record', lazy=True, uselist=False)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        if self.date_of_birth:
            today = datetime.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    @property
    def active_cases(self):
        return [case for case in self.cases if case.status == 'in-progress']
    
    def __repr__(self):
        return f'<Participant {self.full_name}>'

class Referral(db.Model):
    """Referral model for incoming referrals from Google Form via Zapier"""
    __tablename__ = 'referrals'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=True)
    
    # Basic Information (matches Participant model)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date)
    
    # Contact Information
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Address Information
    street_address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(20))
    zip_code = db.Column(db.String(10))
    
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relationship = db.Column(db.String(50))
    
    # School Information
    school_name = db.Column(db.String(100))
    grade_level = db.Column(db.String(20))
    
    # Demographic Information
    race = db.Column(db.String(100))
    ethnicity = db.Column(db.String(100))
    gender_identity = db.Column(db.String(50))
    sex = db.Column(db.String(20))
    pronouns = db.Column(db.String(50))
    family_structure = db.Column(db.String(100))
    
    # Health Information
    allergies = db.Column(db.Text)
    illnesses_disabilities = db.Column(db.Text)
    primary_care_doctor = db.Column(db.String(200))
    emergency_instructions = db.Column(db.Text)
    
    # Communication Preferences
    preferred_contact_method = db.Column(db.String(50))
    preferred_language = db.Column(db.String(50))
    
    # Referral-specific information
    referrer_name = db.Column(db.String(100), nullable=False)
    referrer_email = db.Column(db.String(120), nullable=False)
    referrer_phone = db.Column(db.String(20))
    referrer_organization = db.Column(db.String(100))
    referrer_relationship = db.Column(db.String(100))
    
    # Incident Information
    incident_date = db.Column(db.Date)
    incident_description = db.Column(db.Text)
    desired_outcome = db.Column(db.Text)
    previous_interventions = db.Column(db.Text)
    urgency_level = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    
    # Processing Information
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, waitlisted
    processed_at = db.Column(db.DateTime)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    rejection_reason = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        if self.date_of_birth:
            today = datetime.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    @property
    def status_badge_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'pending': 'warning',
            'accepted': 'success',
            'rejected': 'danger',
            'waitlisted': 'info'
        }
        return status_classes.get(self.status, 'secondary')
    
    @property
    def urgency_badge_class(self):
        """Return CSS class for urgency badge"""
        urgency_classes = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'urgent': 'danger'
        }
        return urgency_classes.get(self.urgency_level, 'secondary')
    
    def __repr__(self):
        return f'<Referral {self.full_name} - {self.status}>'

class ImportantPerson(db.Model):
    """Important persons associated with a participant"""
    __tablename__ = 'important_persons'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # parent, guardian, case_manager, etc.
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ImportantPerson {self.name} - {self.role}>'

class Case(db.Model):
    """Case model for tracking individual cases"""
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    
    # Case Information
    case_number = db.Column(db.String(50), unique=True, nullable=False)
    program_type = db.Column(db.String(100))
    status = db.Column(db.String(20), default='in-progress')  # completed, in-progress, waitlisted, paused, referred-out, no-show
    description = db.Column(db.Text)
    assigned_staff = db.Column(db.String(100))
    
    # Important Dates
    referral_date = db.Column(db.Date)
    intake_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    
    # Additional Fields
    referring_agency = db.Column(db.String(100))
    offense_type = db.Column(db.String(100))
    victim_info = db.Column(db.Text)
    outcome_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def status_badge_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'completed': 'success',
            'in-progress': 'primary',
            'waitlisted': 'warning',
            'paused': 'secondary',
            'referred-out': 'info',
            'no-show': 'danger'
        }
        return status_classes.get(self.status, 'secondary')
    
    @property
    def days_active(self):
        """Calculate days since case was created"""
        if self.status == 'completed' and self.completion_date:
            return (self.completion_date - self.created_at.date()).days
        else:
            return (datetime.now().date() - self.created_at.date()).days
    
    def __repr__(self):
        return f'<Case {self.case_number}>'

class CaseNote(db.Model):
    """Case notes for detailed case tracking"""
    __tablename__ = 'case_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    note_text = db.Column(db.Text, nullable=False)
    note_type = db.Column(db.String(50), default='general')  # general, meeting, phone_call, email, etc.
    is_confidential = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    case = db.relationship('Case', backref='notes')
    user = db.relationship('User', backref='notes')
    
    def __repr__(self):
        return f'<CaseNote {self.id} for Case {self.case_id}>'