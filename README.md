# Restorative Justice Case Management System

A comprehensive web application for managing participants, referrals, and cases in restorative justice programs.

## Features

### User Role-Based Access Control
- **Volunteer**: View-only access to participant information for safety coordination
- **Coordinator**: Full case management including adding/editing participants and processing referrals  
- **Administrator**: Complete system access including user management

### Referral Management
- Automatic referral intake via Google Form + Zapier integration
- Review, accept, or reject referrals with reasons
- Priority levels (low, medium, high, urgent)
- Complete referrer information tracking

### Participant Management
- Comprehensive participant profiles with demographics, health, and contact info
- Important persons tracking (family, case workers, etc.)
- Source tracking (manual entry vs. referral)

### Case Management
- Full case lifecycle tracking
- Multiple program types support
- Status tracking with visual indicators
- Outcome documentation

## Installation

1. **Clone and Setup**
```bash
git clone <repository-url>
cd case-management
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration**
Create a `.env` file:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///case_management.db
```

3. **Initialize Database**
```bash
python app.py
```

4. **Default Login**
- Username: `admin`
- Password: `admin123`
- **Important**: Change the default password immediately after first login!

## API Documentation

### Referral Webhook Endpoint

**POST /api/referrals**

Accepts referral data from Zapier/Google Forms integration.

#### Request Body (JSON)
```json
{
  // Required fields
  "first_name": "John",
  "last_name": "Doe", 
  "referrer_name": "Jane Smith",
  "referrer_email": "jane@school.edu",
  
  // Optional participant info
  "date_of_birth": "2010-05-15",
  "phone": "(555) 123-4567",
  "email": "parent@email.com",
  "street_address": "123 Main St",
  "city": "Durham",
  "state": "NC",
  "zip_code": "27701",
  
  // Emergency contact
  "emergency_contact_name": "Parent Name",
  "emergency_contact_phone": "(555) 987-6543",
  "emergency_contact_relationship": "parent",
  
  // School information
  "school_name": "Durham High School",
  "grade_level": "10",
  
  // Demographics
  "race": "Mixed",
  "ethnicity": "not_hispanic_latino",
  "gender_identity": "Male",
  "sex": "male", 
  "pronouns": "he/him",
  "family_structure": "single_parent",
  
  // Health information
  "allergies": "None known",
  "illnesses_disabilities": "ADHD",
  "primary_care_doctor": "Dr. Smith - (555) 111-2222",
  "emergency_instructions": "Has inhaler in backpack",
  
  // Communication preferences
  "preferred_contact_method": "phone",
  "preferred_language": "english",
  
  // Referrer information
  "referrer_phone": "(555) 555-5555",
  "referrer_organization": "Durham Public Schools",
  "referrer_relationship": "School Counselor",
  
  // Incident details
  "incident_date": "2024-01-15",
  "incident_description": "Description of what happened...",
  "desired_outcome": "What the referrer hopes to achieve...",
  "previous_interventions": "What has been tried before...",
  "urgency_level": "medium"  // low, medium, high, urgent
}
```

#### Response
```json
{
  "success": true,
  "referral_id": 123,
  "message": "Referral created successfully"
}
```

#### Error Response
```json
{
  "error": "Missing required field: first_name"
}
```

### Zapier Integration Setup

1. **Create Zapier Webhook**
   - Trigger: New Google Form Response
   - Action: POST to your-domain.com/api/referrals
   - Map form fields to JSON structure above

2. **Google Form Field Mapping**
   Map your form fields to the API fields:
   - Name fields → `first_name`, `last_name`
   - Contact info → `phone`, `email`, address fields
   - School info → `school_name`, `grade_level`  
   - Incident details → `incident_description`, `desired_outcome`
   - Referrer info → `referrer_name`, `referrer_email`, etc.

## User Management

### Creating Users
Only administrators can create user accounts:

1. Login as admin
2. Navigate to User Management
3. Click "Add New User"
4. Set username, email, password, and role
5. User can change password after first login

### Role Permissions

| Permission | Volunteer | Coordinator | Admin |
|------------|-----------|-------------|-------|
| View participants | ✅ | ✅ | ✅ |
| Add/edit participants | ❌ | ✅ | ✅ |
| Manage cases | ❌ | ✅ | ✅ |
| Process referrals | ❌ | ✅ | ✅ |
| User management | ❌ | ❌ | ✅ |

## Security Considerations

1. **Change Default Password**: Immediately change admin password after setup
2. **HTTPS in Production**: Use HTTPS for all production deployments
3. **Environment Variables**: Never commit secrets to version control
4. **Database Backups**: Regular backups of participant data
5. **Access Logging**: Monitor user access to sensitive information

## Data Privacy

- All participant information is confidential
- Only authorized staff have access based on role
- Volunteers have view-only access for safety coordination
- No participant data should be shared outside the organization
- Regular review of user accounts and permissions

## Support

For technical issues:
1. Check application logs for error messages
2. Verify database connectivity
3. Confirm user permissions are set correctly
4. Contact your system administrator

## Database Schema

The application uses SQLite by default but can be configured for PostgreSQL or MySQL in production.

### Key Tables
- `users`: Staff user accounts and roles
- `participants`: Individual participant records
- `referrals`: Incoming referrals from forms
- `cases`: Active case management records
- `important_persons`: Emergency contacts and key relationships
- `case_notes`: Detailed case documentation

## Deployment

For production deployment:

1. Use PostgreSQL or MySQL instead of SQLite
2. Set up proper HTTPS/SSL
3. Configure proper backup procedures  
4. Set up monitoring and logging
5. Use environment variables for all configuration
6. Consider using Docker for containerization

```bash
# Example production environment variables
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
export FLASK_ENV="production"
```