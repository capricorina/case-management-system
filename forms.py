from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Optional, Length, EqualTo, ValidationError
from datetime import datetime
from models import User

class LoginForm(FlaskForm):
    """Login form for user authentication"""
    username = StringField('Username', validators=[DataRequired()], 
                          render_kw={'placeholder': 'Enter your username'})
    password = PasswordField('Password', validators=[DataRequired()],
                           render_kw={'placeholder': 'Enter your password'})
    submit = SubmitField('Login')

class UserProfileForm(FlaskForm):
    """Form for users to update their own profile"""
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)],
                       render_kw={'placeholder': 'your.email@example.com'})
    current_password = PasswordField('Current Password', validators=[DataRequired()],
                                   render_kw={'placeholder': 'Enter your current password'})
    new_password = PasswordField('New Password (leave blank to keep current)', validators=[Optional(), Length(min=6)],
                                render_kw={'placeholder': 'Enter new password (optional)'})
    confirm_password = PasswordField('Confirm New Password', 
                                   validators=[Optional(), EqualTo('new_password', message='Passwords must match')],
                                   render_kw={'placeholder': 'Confirm new password'})
    submit = SubmitField('Update Profile')

class NewUserForm(FlaskForm):
    """Form for admin to create/edit users"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)],
                          render_kw={'placeholder': 'Enter username'})
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)],
                       render_kw={'placeholder': 'user@example.com'})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)],
                           render_kw={'placeholder': 'Enter password'})
    role = SelectField('Role', validators=[DataRequired()], choices=[
        ('volunteer', 'Volunteer - View Only Access'),
        ('coordinator', 'Coordinator - Full Case Management'),
        ('admin', 'Administrator - Full System Access')
    ])
    is_active = BooleanField('Active Account', default=True)
    submit = SubmitField('Create User')

    def validate_username(self, username):
        # Check if editing existing user
        user_id = getattr(self, '_obj_id', None) if hasattr(self, '_obj_id') else None
        
        user = User.query.filter_by(username=username.data).first()
        if user and (user_id is None or user.id != user_id):
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        # Check if editing existing user
        user_id = getattr(self, '_obj_id', None) if hasattr(self, '_obj_id') else None
        
        user = User.query.filter_by(email=email.data).first()
        if user and (user_id is None or user.id != user_id):
            raise ValidationError('Email already exists. Please choose a different one.')

class ReferralForm(FlaskForm):
    """Form for viewing/editing referral details"""
    # This form is primarily for display purposes
    # The actual referral creation happens via API
    status = SelectField('Status', choices=[
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted')
    ])
    rejection_reason = TextAreaField('Rejection Reason',
                                   render_kw={'placeholder': 'Reason for rejection...', 'rows': 3})
    submit = SubmitField('Update Status')

# Keep all existing forms from the original forms.py
class ImportantPersonForm(FlaskForm):
    """Form for important persons within participant form"""
    name = StringField('Name', validators=[Optional(), Length(max=100)],
                      render_kw={'placeholder': 'Full name'})
    role = SelectField('Role', validators=[Optional()], choices=[
        ('', 'Select Role'),
        ('parent', 'Parent'),
        ('guardian', 'Guardian'),
        ('case_manager', 'Case Manager'),
        ('social_worker', 'Social Worker'),
        ('therapist', 'Therapist'),
        ('probation_officer', 'Probation Officer'),
        ('teacher', 'Teacher'),
        ('counselor', 'School Counselor'),
        ('family_member', 'Family Member'),
        ('mentor', 'Mentor'),
        ('advocate', 'Advocate'),
        ('other', 'Other')
    ])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)],
                       render_kw={'placeholder': '(555) 123-4567'})
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)],
                       render_kw={'placeholder': 'email@example.com'})
    notes = TextAreaField('Notes', validators=[Optional()],
                         render_kw={'placeholder': 'Additional notes about this contact...', 'rows': 2})

class ParticipantForm(FlaskForm):
    """Form for creating and editing participants"""
    
    # Basic Information
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)],
                           render_kw={'placeholder': 'First name'})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)],
                          render_kw={'placeholder': 'Last name'})
    date_of_birth = DateField('Date of Birth', validators=[Optional()],
                            render_kw={'placeholder': 'MM/DD/YYYY'})
    
    # Contact Information
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)],
                       render_kw={'placeholder': '(555) 123-4567'})
    email = StringField('Email Address', validators=[Optional(), Email(), Length(max=120)],
                       render_kw={'placeholder': 'email@example.com'})
    
    # Address Information
    street_address = StringField('Street Address', validators=[Optional(), Length(max=200)],
                               render_kw={'placeholder': '123 Main St'})
    city = StringField('City', validators=[Optional(), Length(max=50)],
                      render_kw={'placeholder': 'City name'})
    state = SelectField('State', validators=[Optional()], choices=[
        ('', 'Select State'),
        ('NC', 'North Carolina'),
        ('SC', 'South Carolina'),
        ('VA', 'Virginia'),
        ('TN', 'Tennessee'),
        ('GA', 'Georgia'),
        ('KY', 'Kentucky'),
        ('WV', 'West Virginia'),
        ('AL', 'Alabama'),
        ('FL', 'Florida'),
        ('MD', 'Maryland'),
        ('DE', 'Delaware'),
        ('DC', 'District of Columbia'),
    ])
    zip_code = StringField('ZIP Code', validators=[Optional(), Length(max=10)],
                         render_kw={'placeholder': '12345'})
    
    # Emergency Contact
    emergency_contact_name = StringField('Emergency Contact Name', validators=[Optional(), Length(max=100)],
                                       render_kw={'placeholder': 'Full name'})
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[Optional(), Length(max=20)],
                                        render_kw={'placeholder': '(555) 123-4567'})
    emergency_contact_relationship = SelectField('Relationship to Participant', validators=[Optional()], choices=[
        ('', 'Select Relationship'),
        ('parent', 'Parent'),
        ('guardian', 'Guardian'),
        ('grandparent', 'Grandparent'),
        ('sibling', 'Sibling'),
        ('spouse', 'Spouse'),
        ('friend', 'Friend'),
        ('other', 'Other')
    ])
    
    # School Information
    school_name = StringField('School Name', validators=[Optional(), Length(max=100)],
                            render_kw={'placeholder': 'Name of school (leave blank if not applicable)'})
    grade_level = SelectField('Grade Level', validators=[Optional()], choices=[
        ('', 'Select Grade'),
        ('pre-k', 'Pre-K'),
        ('k', 'Kindergarten'),
        ('1', '1st Grade'),
        ('2', '2nd Grade'),
        ('3', '3rd Grade'),
        ('4', '4th Grade'),
        ('5', '5th Grade'),
        ('6', '6th Grade'),
        ('7', '7th Grade'),
        ('8', '8th Grade'),
        ('9', '9th Grade'),
        ('10', '10th Grade'),
        ('11', '11th Grade'),
        ('12', '12th Grade'),
        ('college', 'College'),
        ('adult', 'Adult/Not in School')
    ])
    
    # Demographic Information
    race = StringField('Race', validators=[Optional(), Length(max=100)],
                      render_kw={'placeholder': 'e.g., White, Black/African American, Asian, etc.'})
    ethnicity = SelectField('Ethnicity', validators=[Optional()], choices=[
        ('', 'Select Ethnicity'),
        ('hispanic_latino', 'Hispanic or Latino'),
        ('not_hispanic_latino', 'Not Hispanic or Latino'),
        ('prefer_not_to_say', 'Prefer not to say')
    ])
    gender_identity = StringField('Gender Identity', validators=[Optional(), Length(max=50)],
                                render_kw={'placeholder': 'e.g., Male, Female, Non-binary, etc.'})
    sex = SelectField('Sex Assigned at Birth', validators=[Optional()], choices=[
        ('', 'Select Sex'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('intersex', 'Intersex'),
        ('prefer_not_to_say', 'Prefer not to say')
    ])
    pronouns = StringField('Pronouns', validators=[Optional(), Length(max=50)],
                          render_kw={'placeholder': 'e.g., he/him, she/her, they/them, etc.'})
    family_structure = SelectField('Family Structure', validators=[Optional()], choices=[
        ('', 'Select Family Structure'),
        ('two_parent', 'Two Parent Household'),
        ('single_parent', 'Single Parent Household'),
        ('grandparents', 'Living with Grandparents'),
        ('foster', 'Foster Care'),
        ('kinship', 'Kinship Care'),
        ('group_home', 'Group Home'),
        ('independent', 'Independent Living'),
        ('other', 'Other')
    ])
    
    # Health Information
    allergies = TextAreaField('Allergies', validators=[Optional()],
                            render_kw={'placeholder': 'List any known allergies...', 'rows': 3})
    illnesses_disabilities = TextAreaField('Illnesses or Disabilities', validators=[Optional()],
                                         render_kw={'placeholder': 'List any relevant medical conditions or disabilities...', 'rows': 3})
    primary_care_doctor = StringField('Primary Care Doctor', validators=[Optional(), Length(max=200)],
                                    render_kw={'placeholder': 'Doctor name and contact information'})
    emergency_instructions = TextAreaField('Emergency Instructions', validators=[Optional()],
                                         render_kw={'placeholder': 'Special instructions for emergencies...', 'rows': 3})
    
    # Communication Preferences
    preferred_contact_method = SelectField('Preferred Contact Method', validators=[Optional()], choices=[
        ('', 'Select Preferred Method'),
        ('phone', 'Phone Call'),
        ('text', 'Text Message'),
        ('email', 'Email'),
        ('mail', 'Postal Mail'),
        ('in_person', 'In Person'),
        ('no_preference', 'No Preference')
    ])
    preferred_language = SelectField('Preferred Language', validators=[Optional()], choices=[
        ('', 'Select Language'),
        ('english', 'English'),
        ('spanish', 'Spanish'),
        ('french', 'French'),
        ('german', 'German'),
        ('chinese', 'Chinese'),
        ('arabic', 'Arabic'),
        ('korean', 'Korean'),
        ('vietnamese', 'Vietnamese'),
        ('tagalog', 'Tagalog'),
        ('russian', 'Russian'),
        ('italian', 'Italian'),
        ('portuguese', 'Portuguese'),
        ('japanese', 'Japanese'),
        ('other', 'Other')
    ])
    
    # Important Persons
    important_person_1_name = StringField('Name', validators=[Optional(), Length(max=100)],
                                        render_kw={'placeholder': 'Full name'})
    important_person_1_role = SelectField('Role', validators=[Optional()], choices=[
        ('', 'Select Role'),
        ('parent', 'Parent'),
        ('guardian', 'Guardian'),
        ('case_manager', 'Case Manager'),
        ('social_worker', 'Social Worker'),
        ('therapist', 'Therapist'),
        ('probation_officer', 'Probation Officer'),
        ('teacher', 'Teacher'),
        ('counselor', 'School Counselor'),
        ('family_member', 'Family Member'),
        ('mentor', 'Mentor'),
        ('advocate', 'Advocate'),
        ('other', 'Other')
    ])
    important_person_1_phone = StringField('Phone', validators=[Optional(), Length(max=20)],
                                         render_kw={'placeholder': '(555) 123-4567'})
    important_person_1_email = StringField('Email', validators=[Optional(), Email(), Length(max=120)],
                                         render_kw={'placeholder': 'email@example.com'})
    
    important_person_2_name = StringField('Name', validators=[Optional(), Length(max=100)],
                                        render_kw={'placeholder': 'Full name'})
    important_person_2_role = SelectField('Role', validators=[Optional()], choices=[
        ('', 'Select Role'),
        ('parent', 'Parent'),
        ('guardian', 'Guardian'),
        ('case_manager', 'Case Manager'),
        ('social_worker', 'Social Worker'),
        ('therapist', 'Therapist'),
        ('probation_officer', 'Probation Officer'),
        ('teacher', 'Teacher'),
        ('counselor', 'School Counselor'),
        ('family_member', 'Family Member'),
        ('mentor', 'Mentor'),
        ('advocate', 'Advocate'),
        ('other', 'Other')
    ])
    important_person_2_phone = StringField('Phone', validators=[Optional(), Length(max=20)],
                                         render_kw={'placeholder': '(555) 123-4567'})
    important_person_2_email = StringField('Email', validators=[Optional(), Email(), Length(max=120)],
                                         render_kw={'placeholder': 'email@example.com'})
    
    important_person_3_name = StringField('Name', validators=[Optional(), Length(max=100)],
                                        render_kw={'placeholder': 'Full name'})
    important_person_3_role = SelectField('Role', validators=[Optional()], choices=[
        ('', 'Select Role'),
        ('parent', 'Parent'),
        ('guardian', 'Guardian'),
        ('case_manager', 'Case Manager'),
        ('social_worker', 'Social Worker'),
        ('therapist', 'Therapist'),
        ('probation_officer', 'Probation Officer'),
        ('teacher', 'Teacher'),
        ('counselor', 'School Counselor'),
        ('family_member', 'Family Member'),
        ('mentor', 'Mentor'),
        ('advocate', 'Advocate'),
        ('other', 'Other')
    ])
    important_person_3_phone = StringField('Phone', validators=[Optional(), Length(max=20)],
                                         render_kw={'placeholder': '(555) 123-4567'})
    important_person_3_email = StringField('Email', validators=[Optional(), Email(), Length(max=120)],
                                         render_kw={'placeholder': 'email@example.com'})
    
    # Additional Information
    notes = TextAreaField('Additional Notes', validators=[Optional()],
                         render_kw={'placeholder': 'Any additional notes about the participant...', 'rows': 4})
    
    submit = SubmitField('Save Participant')

class CaseForm(FlaskForm):
    """Form for creating and editing cases"""
    
    program_type = SelectField('Program Type', validators=[DataRequired()], choices=[
        ('', 'Select Program Type'),
        ('victim-offender-mediation', 'Victim-Offender Mediation'),
        ('family-group-conferencing', 'Family Group Conferencing'),
        ('circle-process', 'Circle Process'),
        ('community-service', 'Community Service'),
        ('restitution', 'Restitution'),
        ('peer-mediation', 'Peer Mediation'),
        ('diversion', 'Diversion Program'),
        ('other', 'Other')
    ])
    
    status = SelectField('Case Status', validators=[DataRequired()], choices=[
        ('in-progress', 'In Progress'),
        ('waitlisted', 'Waitlisted'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('referred-out', 'Referred Out'),
        ('no-show', 'No Show')
    ])
    
    description = TextAreaField('Case Description', validators=[Optional()],
                              render_kw={'placeholder': 'Brief description of the case...', 'rows': 4})
    
    assigned_staff = StringField('Assigned Staff Member', validators=[Optional(), Length(max=100)],
                               render_kw={'placeholder': 'Staff member name'})
    
    referring_agency = StringField('Referring Agency', validators=[Optional(), Length(max=100)],
                                 render_kw={'placeholder': 'Agency or organization that referred this case'})
    
    referral_date = DateField('Referral Date', validators=[Optional()],
                            render_kw={'placeholder': 'Date case was referred'})
    
    intake_date = DateField('Intake Date', validators=[Optional()],
                          render_kw={'placeholder': 'Date of initial intake'})
    
    offense_type = SelectField('Offense Type', validators=[Optional()], choices=[
        ('', 'Select Offense Type'),
        ('theft', 'Theft'),
        ('assault', 'Assault'),
        ('vandalism', 'Vandalism'),
        ('harassment', 'Harassment'),
        ('substance', 'Substance-related'),
        ('traffic', 'Traffic Violation'),
        ('disorderly-conduct', 'Disorderly Conduct'),
        ('truancy', 'Truancy'),
        ('bullying', 'Bullying'),
        ('property-damage', 'Property Damage'),
        ('other', 'Other')
    ])
    
    victim_info = TextAreaField('Victim Information', validators=[Optional()],
                              render_kw={'placeholder': 'Information about victim(s) if applicable...', 'rows': 3})
    
    outcome_notes = TextAreaField('Outcome Notes', validators=[Optional()],
                                render_kw={'placeholder': 'Notes about case outcome, agreements, etc...', 'rows': 4})
    
    submit = SubmitField('Save Case')

class CaseNoteForm(FlaskForm):
    """Form for adding case notes"""
    
    note_type = SelectField('Note Type', validators=[DataRequired()], choices=[
        ('general', 'General Note'),
        ('meeting', 'Meeting'),
        ('phone_call', 'Phone Call'),
        ('email', 'Email'),
        ('visit', 'Site Visit'),
        ('court', 'Court Appearance'),
        ('follow_up', 'Follow Up')
    ])
    
    note_text = TextAreaField('Note', validators=[DataRequired()],
                            render_kw={'placeholder': 'Enter your note here...', 'rows': 6})
    
    is_confidential = SelectField('Confidentiality', choices=[
        (False, 'Standard Note'),
        (True, 'Confidential Note')
    ], coerce=lambda x: x == 'True')
    
    submit = SubmitField('Add Note')