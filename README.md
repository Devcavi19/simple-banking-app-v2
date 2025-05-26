<div style="background-color: black; padding: 20px;">
 
<p align="center">
 <img height=200px src="./images/header.png" alt="Simple Banking App v2">
</p>

<h2 align="center">Simple Banking App v2</h2>

<div align="center">

[![Python version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)
[![Flask version](https://img.shields.io/badge/flask-2.3.0-red.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/mysql-5.7+-green.svg)](https://www.mysql.com/)
[![Bootstrap](https://img.shields.io/badge/bootstrap-5-purple.svg)](https://getbootstrap.com/)

<h4>A comprehensive Flask-based web application that simulates a modern banking system with secure user authentication, fund transfers, and administrative functions. Built with security best practices including enhanced password requirements, PIN verification, and improved session management.</h4>

</div>

-----------------------------------------

## Group 2 Members
- Herald Carl Avila
- Jamaica Mae Rosales
- Kaye Khrysna Olores

-----------------------------------------

## Introduction

Simple Banking App v2 is a comprehensive Flask-based web application that simulates a modern banking system. This application provides a secure and user-friendly platform for managing banking operations including account management, fund transfers, and administrative functions. Built with Python and Flask, it demonstrates best practices in web development, security, and database management.

The application features a multi-tier user system with regular users, administrators, and managers, each with specific roles and permissions. It integrates with the Philippine Standard Geographic Code (PSGC) API for standardized address management and implements robust security measures including password hashing, session management, and CSRF protection.

-----------------------------------------

## Branch Management

We follow a structured branch workflow to ensure smooth development and deployment.

### `main` Branch
This is the primary development branch where all local machine executions occur. Developers work in this branch to implement new features, bug fixes, and improvements. Before deploying updates, changes are thoroughly tested here.

### `deploy/vercel` Branch
This branch is reserved for production and deployment purposes. Once modifications in the `main` branch are tested and verified, they are merged into `deploy/vercel`. This guarantees that only the latest stable version is deployed on Vercel, ensuring reliability for live users.

By maintaining this separation, we ensure a streamlined workflow where development continues without disrupting the live application.

-----------------------------------------

## Objectives

The primary objectives of this Simple Banking App v2 project are:

1. **Educational Purpose**: To demonstrate the implementation of a full-stack web application using Flask framework and modern web development practices.

2. **Security Implementation**: To showcase secure coding practices including proper authentication, authorization, password hashing, and protection against common web vulnerabilities.

3. **Role-Based Access Control**: To implement and demonstrate a multi-tier user system with different permission levels (Users, Admins, Managers).

4. **Database Management**: To practice database design, ORM usage with SQLAlchemy, and proper data relationship management.

5. **API Integration**: To demonstrate third-party API integration using the Philippine Standard Geographic Code (PSGC) API for location data.

6. **User Experience**: To create an intuitive and responsive user interface that provides a smooth banking experience.

7. **Real-world Application**: To simulate real banking operations including account management, fund transfers, and transaction tracking.

-----------------------------------------

## Original Application Features

### Core Banking Features
- **User Registration & Authentication**: Secure user registration with email verification and login system
- **Account Management**: View account balance, transaction history, and personal information
- **Fund Transfers**: Transfer money between registered users with confirmation workflow
- **Transaction History**: Complete record of all account activities and transfers

### Security Features
- **Password Hashing**: Secure password storage using bcrypt encryption
- **Session Management**: Secure user session handling with Flask-Login
- **CSRF Protection**: Cross-Site Request Forgery protection for all forms
- **Rate Limiting**: API rate limiting to prevent abuse and brute force attacks
- **Token-based Password Reset**: Secure password recovery mechanism

### Administrative Features
- **User Approval System**: Admin approval workflow for new user registrations
- **Account Management**: Activate/deactivate user accounts and edit user information
- **Deposit System**: Over-the-counter deposits to user accounts
- **User Creation**: Admin capability to create new user accounts

### Manager Features
- **Admin Management**: Create and manage admin accounts
- **System Oversight**: Monitor all transfers and admin activities
- **Transaction Auditing**: View comprehensive transaction logs across the system

### Location Integration
- **PSGC API Integration**: Philippine Standard Geographic Code API for standardized addresses
- **Hierarchical Location Selection**: Region → Province → City → Barangay selection system
- **Address Validation**: Ensures location data follows Philippine geographical structure

### Technical Features
- **Responsive Design**: Mobile-friendly interface that works across all devices
- **Database Integration**: MySQL database with SQLAlchemy ORM
- **RESTful API Design**: Clean API structure for potential future mobile app integration
- **Error Handling**: Comprehensive error handling with custom error pages
- **Logging System**: Application logging for monitoring and debugging

-----------------------------------------

## Security Assessment Findings

### Vulnerabilities identified in the original application:

1. **Weak Password Creation**: The original application only enforced alphanumeric password requirements without additional complexity requirements such as special characters, minimum length variations, or strength validation.

2. **No PIN Verification in Transactions**: Financial transactions were processed without requiring additional PIN verification, creating a security gap where unauthorized users with access to logged-in sessions could perform transfers.

3. **Admin and Managerial Role Actions Without Confirmation**: Administrative and managerial functions (such as account deletion, role changes, or critical system modifications) were executed immediately without confirmation dialogs or additional authentication steps, increasing the risk of accidental or malicious actions.

4. **Multiple Device Login**: The application allowed a single account to be logged in on multiple devices simultaneously. This represents poor session management practice as it increases the attack surface and makes it difficult to track and terminate unauthorized sessions.

-----------------------------------------

## Security Improvements Implemented

### Detailed description of improvements made:

To address the security vulnerabilities identified in the original application, we implemented comprehensive security enhancements:

#### 1. **Enhanced Password Security**
- **Stronger Password Requirements**: Implemented robust password validation requiring a combination of uppercase letters, lowercase letters, numbers, and special characters
- **Minimum Length Enforcement**: Set minimum password length requirements to ensure adequate complexity
- **Password Strength Validation**: Added real-time password strength indicators to guide users in creating secure passwords
- **Regular Expression Validation**: Implemented server-side validation to enforce password complexity rules

#### 2. **PIN Verification System for Transactions**
- **Mandatory PIN Creation**: All users are now required to set up a 6-digit PIN during account registration
- **Transaction PIN Verification**: Every financial transaction now requires PIN verification before processing
- **PIN Encryption**: User PINs are securely hashed and stored using bcrypt encryption
- **PIN Reset Functionality**: Secure PIN reset mechanism for users who forget their PIN
- **Failed Attempt Lockout**: Account temporarily locked after multiple incorrect PIN attempts

#### 3. **Administrative Action Confirmation System**
- **Two-Factor Confirmation**: All critical administrative actions now require dual confirmation
- **Pop-up Confirmation Dialogs**: Interactive confirmation dialogs that clearly describe the action being performed
- **PIN Verification for Admin Actions**: Administrators must enter their PIN to confirm sensitive operations
- **Action Logging**: All administrative actions are logged with timestamps and user identification
- **Rollback Capabilities**: Implemented mechanisms to reverse certain administrative actions if needed

#### 4. **Session Management Enhancement**
- **Single Session Enforcement**: Implemented session management to allow only one active session per user account
- **Automatic Session Termination**: Previous sessions are automatically terminated when a new login occurs
- **Session Monitoring**: Real-time monitoring of active sessions with the ability to view login locations and times
- **Forced Logout Capability**: Users can remotely log out all sessions from their account settings
- **Session Expiration**: Automatic session timeout after periods of inactivity

#### 5. **Additional Security Measures**
- **Enhanced Audit Trail**: Comprehensive logging of all user activities and administrative actions
- **Security Notifications**: Email notifications for important security events (login from new device, PIN changes, etc.)
- **Account Lockout Policies**: Progressive lockout periods for repeated failed authentication attempts
- **Input Validation**: Strengthened input validation and sanitization to prevent injection attacks
- **CSRF Token Enhancement**: Improved CSRF protection with rotating tokens for all forms

These security improvements significantly enhance the overall security posture of the application, addressing all identified vulnerabilities while maintaining user experience and system functionality.

-----------------------------------------

## Penetration Testing Report

### Summary of Vulnerabilities Identified

During our security assessment of the Simple Banking App v2, we conducted comprehensive penetration testing to identify potential security vulnerabilities. The following vulnerabilities were discovered and subsequently addressed:

#### 1. **Weak Password Policy (Medium Risk)**
- **Vulnerability**: The original application accepted alphanumeric-only passwords without complexity requirements
- **Risk Level**: Medium
- **CVSS Score**: 5.3 (Medium)

**Exploitation Steps:**
1. Attempt to register with weak passwords like "password123" or "user1234"
2. Use dictionary attacks against user accounts with common passwords
3. Brute force attacks would be more successful due to limited password complexity

**Impact:**
- User accounts vulnerable to brute force attacks
- Increased risk of unauthorized access
- Potential account takeover scenarios

**Recommendation:**
- Implement strong password requirements (uppercase, lowercase, numbers, special characters)
- Enforce minimum password length of 8+ characters
- Add password strength indicators during registration

#### 2. **Missing Transaction Authentication (High Risk)**
- **Vulnerability**: Financial transactions processed without additional verification beyond login session
- **Risk Level**: High
- **CVSS Score**: 7.5 (High)

**Exploitation Steps:**
1. Gain access to an active user session (session hijacking, shoulder surfing, etc.)
2. Navigate to transfer functionality
3. Perform unauthorized money transfers without additional authentication
4. Drain victim's account balance

**Impact:**
- Unauthorized financial transactions
- Complete account balance theft
- Loss of user funds without user knowledge

**Recommendation:**
- Implement mandatory PIN verification for all financial transactions
- Add transaction confirmation via email/SMS
- Implement transaction limits and cooling-off periods

#### 3. **Insufficient Administrative Controls (High Risk)**
- **Vulnerability**: Administrative and managerial actions executed without confirmation or additional authentication
- **Risk Level**: High
- **CVSS Score**: 8.1 (High)

**Exploitation Steps:**
1. Compromise admin/manager account credentials
2. Perform critical actions like account deletion, role changes, or system modifications
3. Actions execute immediately without confirmation dialogs
4. Cause irreversible system damage or data loss

**Impact:**
- Accidental or malicious system modifications
- User data loss or corruption
- Privilege escalation attacks
- System integrity compromise

**Recommendation:**
- Implement dual-factor confirmation for critical administrative actions
- Add PIN verification for admin operations
- Create audit trails for all administrative activities
- Implement rollback capabilities where possible

#### 4. **Poor Session Management (Medium Risk)**
- **Vulnerability**: Multiple concurrent sessions allowed per user account
- **Risk Level**: Medium
- **CVSS Score**: 6.1 (Medium)

**Exploitation Steps:**
1. Obtain user credentials through various means
2. Login to user account from multiple devices/locations
3. Maintain persistent access even if user logs out from one device
4. Monitor user activities across multiple sessions

**Impact:**
- Unauthorized persistent access
- Difficulty in tracking and terminating compromised sessions
- Increased attack surface
- User unaware of unauthorized access

**Recommendation:**
- Implement single session enforcement per user account
- Add session monitoring and management capabilities
- Provide users with active session visibility
- Implement automatic session termination features

-----------------------------------------

## Remediation Plan

### Steps taken to address identified vulnerabilities:

#### **Phase 1: Password Security Enhancement**
1. **Updated Password Validation Rules**
   - Modified registration and password change forms to require 8+ character passwords
   - Added regex validation for uppercase, lowercase, numbers, and special characters
   - Implemented client-side password strength indicator

2. **Backend Enforcement**
   - Updated server-side validation in `forms.py` and `routes.py`
   - Enhanced password hashing with increased bcrypt rounds
   - Added password history to prevent reuse of recent passwords

#### **Phase 2: Transaction Security Implementation**
1. **PIN System Development**
   - Created PIN field in user database model
   - Developed PIN creation form during user registration
   - Implemented PIN verification modal for all financial transactions

2. **Transaction Flow Modification**
   - Modified transfer routes to require PIN verification
   - Added PIN validation before processing any money transfer
   - Implemented account lockout after 3 failed PIN attempts

#### **Phase 3: Administrative Controls**
1. **Confirmation System**
   - Added confirmation dialogs for all critical admin actions
   - Implemented "Are you sure?" pop-ups with action descriptions
   - Required PIN verification for admin/manager operations

2. **Audit Trail Enhancement**
   - Created comprehensive logging for all administrative actions
   - Added timestamps and user identification to all logs
   - Implemented action reversal capabilities where applicable

#### **Phase 4: Session Management Overhaul**
1. **Single Session Enforcement**
   - Modified login system to terminate existing sessions
   - Implemented session tracking in database
   - Added "Force logout from all devices" functionality

2. **Session Monitoring**
   - Created session dashboard for users to view active logins
   - Added automatic session expiration after 30 minutes of inactivity
   - Implemented real-time session termination capabilities

#### **Testing and Validation**
1. **Security Testing**
   - Conducted manual testing of all new security features
   - Verified proper functioning of PIN verification system
   - Tested session management across multiple devices

2. **User Experience Testing**
   - Ensured security enhancements don't hinder usability
   - Validated form submissions and error handling
   - Confirmed proper feedback for security actions

#### **Timeline and Priority**
- **Day 1-2**: Password security and PIN system implementation (Phase 1 & 2)
- **Day 3-4**: Administrative controls and session management (Phase 3 & 4)
- **Day 5-6**: Testing, validation, and integration
- **Day 7**: Final review and documentation

All remediation steps have been successfully implemented and tested, resulting in a significantly more secure banking application while maintaining user-friendly functionality.

-----------------------------------------

## Technology Stack

### Updated list of technologies used:

#### **Backend Framework**
- **Python 3.7+**: Core programming language
- **Flask 2.3.0**: Lightweight web framework for building the application
- **Flask-Login**: User session management and authentication
- **Flask-WTF**: Form handling and CSRF protection
- **Flask-Bcrypt**: Password hashing and encryption
- **Flask-Limiter 3.5.0**: API rate limiting and abuse prevention

#### **Database & ORM**
- **MySQL 5.7+/MariaDB 10.2+**: Primary database management system
- **SQLAlchemy**: Object-Relational Mapping (ORM) for database operations
- **PyMySQL 1.1.0**: MySQL database connector for Python

#### **Security & Authentication**
- **bcrypt**: Secure password and PIN hashing
- **cryptography**: Additional encryption utilities
- **itsdangerous 2.1.2**: Secure token generation for password resets
- **CSRF tokens**: Cross-Site Request Forgery protection

#### **Frontend Technologies**
- **HTML5**: Markup language for web pages
- **CSS3**: Styling and responsive design
- **Bootstrap 5**: Frontend framework for responsive UI components
- **JavaScript**: Client-side functionality and form validation
- **jQuery**: DOM manipulation and AJAX requests

#### **API Integration**
- **requests 2.31.0**: HTTP library for external API calls
- **PSGC API**: Philippine Standard Geographic Code integration for location data

#### **Caching & Performance**
- **Redis 4.6.0**: In-memory data structure store for caching and session management

#### **Development & Deployment Tools**
- **Git**: Version control system
- **GitHub**: Repository hosting and collaboration
- **Vercel**: Cloud platform for deployment and hosting of web applications
- **pip**: Python package manager
- **Virtual Environment (venv)**: Isolated Python environment for dependencies

#### **Security Enhancements**
- **Session Management**: Single session enforcement and monitoring
- **PIN Verification System**: Additional transaction security layer
- **Admin Confirmation System**: Dual-factor confirmation for critical actions
- **Audit Logging**: Comprehensive activity tracking and monitoring

#### **File Structure**
```
simple-banking-app-v2/
├── app.py                 # Main Flask application
├── routes.py             # URL routing and view functions
├── models.py             # Database models and relationships
├── forms.py              # WTF form definitions and validation
├── extensions.py         # Flask extensions configuration
├── init_db.py           # Database initialization script
├── psgc_api.py          # PSGC API integration functions
├── schema.sql           # Database schema definition
├── wsgi.py              # WSGI entry point for deployment
├── requirements.txt     # Python dependencies
├── static/              # CSS, JavaScript, and image files
├── templates/           # Jinja2 HTML templates
│   ├── admin/          # Admin-specific templates
│   ├── manager/        # Manager-specific templates
│   └── errors/         # Error page templates
└── env/                # Virtual environment (excluded from git)
```

#### **Key Libraries and Versions**
```
Flask==2.3.0
Flask-Login==0.6.2
Flask-WTF==1.1.1
Flask-Bcrypt==1.0.1
Flask-Limiter==3.5.0
SQLAlchemy==2.0.15
WTForms==3.0.1
email-validator==2.0.0
itsdangerous==2.1.2
pymysql==1.1.0
cryptography==41.0.1
requests==2.31.0
redis==4.6.0
```

This technology stack provides a robust, secure, and scalable foundation for the Simple Banking App v2, incorporating modern web development practices and security standards.

-----------------------------------------

## Setup Instructions

### Instructions on how to set up and run the improved application:

#### **Prerequisites**
- Python 3.7+
- MySQL Server 5.7+
- Git

#### **Local Setup Steps**

**1. Clone Repository:**
```bash
git clone https://github.com/yourusername/simple-banking-app-v2.git
cd simple-banking-app-v2
```

**2. Virtual Environment:**
```bash
python -m venv env
env\Scripts\activate  # Windows
source env/bin/activate  # macOS/Linux
```

**3. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**4. Database Setup:**
```sql
CREATE DATABASE simple_banking;
CREATE USER 'bankapp'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON simple_banking.* TO 'bankapp'@'localhost';
```

**5. Environment Configuration (.env file):**
```
DATABASE_URL=mysql+pymysql://bankapp:your_password@localhost/simple_banking
SECRET_KEY=your_secret_key
FLASK_ENV=development
```

**6. Initialize Database:**
```bash
python init_db.py
```

**7. Run Application:**
```bash
python app.py
```

Access at: `http://localhost:5000`

-----------------------------------------

## Live Deployment

### Vercel Hosting

The application is deployed and accessible on Vercel for demonstration purposes.



**Live Application URL:** [Simple Banking App v2](https://simple-banking-app-v2.vercel.app)

** Video App Demonstration: ** [Group 2 Video Demonstration](https://drive.google.com/file/d/1VLe9HNJ2FHQr8c-qlxnvHhq5pU9V-4OI/view?usp=sharing)

For instructions on how to deploy your own version of this application to Vercel, please follow [Vercel's Python deployment documentation](https://vercel.com/docs/frameworks/python).

-----------------------------------------

### Contributors

- Herald Carl Avila - [GitHub](https://github.com/Devcavi19)
- Jamaica Mae Rosales - [GitHub](https://github.com/IamJamm)
- Kaye Khrysna Olores - [GitHub](https://github.com/kikisna)

------------------------------------------

</div>
