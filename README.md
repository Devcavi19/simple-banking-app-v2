# Simple Banking App v2 - Security Enhanced Edition

This repository contains an improved version of a simple banking application with significantly enhanced security features. This document outlines the security improvements and additional features implemented in this version compared to the original.

## Security Improvements

### Authentication and Password Management

- **Enhanced Password Security**: Implemented bcrypt for secure password hashing with built-in salt, replacing basic password hashing.
- **Strong Password Requirements**: Added comprehensive password validation requiring:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character
- **Password Reset Functionality**: Added secure password reset with time-limited tokens using URLSafeTimedSerializer.
- **Forced Password Change**: Added capability for admin-created accounts to require password change on first login.

### Session Security

- **Session Timeout**: Added automatic session expiration after 30 minutes of inactivity.
- **CSRF Protection**: Implemented Cross-Site Request Forgery protection using Flask-WTF's CSRFProtect.
- **First Login Check**: Added decorator to force password change for new accounts before accessing other features.

### Rate Limiting and Brute Force Protection

- **API Rate Limiting**: Implemented Flask-Limiter to protect against brute force attacks and DoS attempts.
- **Custom Rate Limit Handling**: Added custom error pages for rate limit exceeded events.

### Access Control

- **Role-Based Access Control**: Enhanced user role system with:
  - Regular users
  - Admin users (can manage regular users)
  - Manager users (can manage admins)
- **Decorators for Permission Control**: Implemented custom decorators for ensuring access control:
  - `@admin_required`
  - `@manager_required`
  - `@first_login_check`

### Secure Data Handling

- **UUID for Transactions**: Implemented UUID for transaction IDs to prevent sequential guessing.
- **Parameter Validation**: All form inputs have proper validation to prevent injection attacks.
- **Data Sanitization**: Implemented input sanitization to prevent XSS attacks.

## Feature Enhancements

### User Management

- **Enhanced User Profiles**: Added detailed address information with PSGC (Philippine Standard Geographic Code) API integration.
- **Account Status Management**: Implemented account status system (active, deactivated, pending).
- **Admin Dashboard**: Built comprehensive admin dashboard for user management.
- **Manager Dashboard**: Added manager-level controls for admin management.

### Banking Features

- **Improved Transfer System**: Enhanced money transfer system with:
  - Transfer by username or account number
  - Transfer confirmation step
  - Transaction history
- **Deposit Functionality**: Added deposit capability for admins to add funds to user accounts.
- **Transaction Records**: Improved transaction tracking and history.

### UI/UX Improvements

- **Responsive Interface**: Enhanced UI for better usability across devices.
- **Error Handling**: Improved error messages and validation feedback.
- **Flash Messaging**: Better user feedback system for actions and errors.

## Technical Improvements

- **Environment Variables**: Secure configuration using environment variables and dotenv.
- **Database Connection**: Enhanced database connection management with proper error handling.
- **Scalable Structure**: Organized code structure for maintainability and scalability.
- **Comprehensive Logging**: Added logging for security events and system monitoring.

## Setup and Installation

1. Clone the repository
2. Set up a virtual environment:
   ```
   python -m venv env
   env\Scripts\activate  # On Windows
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables in a `.env` file:
   ```
   SECRET_KEY=your_secret_key_here
   MYSQL_USER=your_db_user
   MYSQL_PASSWORD=your_db_password
   MYSQL_HOST=your_db_host
   MYSQL_PORT=3306
   MYSQL_DATABASE=banking_app
   ```

5. Initialize the database:
   ```
   python init_db.py
   ```

6. Run the application:
   ```
   python wsgi.py
   ```

## Comparison to Original Version

| Feature | Original Version | Improved Version |
|---------|-----------------|------------------|
| Password Storage | Basic hashing | Bcrypt with salt |
| Password Requirements | None | Complex requirements enforced |
| CSRF Protection | None | Implemented |
| Rate Limiting | None | Comprehensive |
| Session Management | Basic | Timeout, better controls |
| User Roles | Basic | Enhanced with managers |
| Transaction IDs | Sequential | UUID-based |
| User Profiles | Basic | Enhanced with PSGC integration |
| Error Handling | Basic | Comprehensive |

## Security Best Practices Implemented

- Defense in depth with multiple security layers
- Principle of least privilege for user roles
- Secure default configurations
- Regular security validation
- Input validation on both client and server sides
- Protection against common web vulnerabilities (OWASP Top 10)

## Future Enhancements

- Two-factor authentication
- IP-based anomaly detection
- Enhanced audit logging
- Additional account recovery options
- Account activity notifications

## License

[Insert appropriate license information here]