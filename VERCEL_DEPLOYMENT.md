# Vercel Deployment Guide for Simple Banking App

This comprehensive guide covers deploying the Simple Banking App to Vercel with a focus on cloud-based MySQL database integration using FreeSQLDatabase.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Cloud Database Setup](#cloud-database-setup)
3. [Project Configuration](#project-configuration)
4. [Environment Variables](#environment-variables)
5. [Vercel Configuration](#vercel-configuration)
6. [Deployment Process](#deployment-process)
7. [Post-Deployment Setup](#post-deployment-setup)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting the deployment process, ensure you have:

- A GitHub account with your project repository
- A Vercel account (sign up at [vercel.com](https://vercel.com))
- Basic knowledge of environment variables and database connections

## Cloud Database Setup

### Using FreeSQLDatabase (Recommended)

This project is configured to work with **FreeSQLDatabase** (www.freesqldatabase.com), a free cloud MySQL hosting service that's perfect for development and small-scale applications.

#### Step 1: Create FreeSQLDatabase Account

1. Visit [www.freesqldatabase.com](https://www.freesqldatabase.com)
2. Click "Sign Up" and create a new account
3. Verify your email address

#### Step 2: Create Database

1. Login to your FreeSQLDatabase dashboard
2. Click "Create Database"
3. Choose a database name (e.g., `simple_banking_app`)
4. Note down the following connection details:
   - **Host**: `sql.freedb.tech`
   - **Port**: `3306` (default MySQL port)
   - **Database Name**: Your chosen database name
   - **Username**: Automatically generated
   - **Password**: Automatically generated

#### Step 3: Database Connection Details

Your connection details will look similar to:
```
Host: sql.freedb.tech
Port: 3306
Database: freedb_simple_banking_app
Username: freedb_username123
Password: auto_generated_password
```

> **Important**: Keep these credentials secure and never commit them to your repository. They will be stored as environment variables in Vercel.

## Project Configuration

### Required Files for Vercel Deployment

Ensure your project contains these essential files:

#### 1. `vercel.json` - Vercel Configuration

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/wsgi.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production"
  }
}
```

#### 2. `api/wsgi.py` - WSGI Entry Point

```python
from app import app

if __name__ == "__main__":
    app.run()
```

#### 3. `.vercelignore` - Files to Exclude from Deployment

```plaintext
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database
*.db
*.sqlite3

# Environment variables (these should be set in Vercel dashboard)
.env
.env.local
.env.production

# Git
.git/
.gitignore

# Documentation
README.md

# Development files
init_db.py
schema.sql
```

## Environment Variables

### Required Environment Variables

Configure these variables in your Vercel project dashboard:

| Variable | Description | Example Value | Required |
|----------|-------------|---------------|----------|
| `MYSQL_HOST` | FreeSQLDatabase host | `sql.freedb.tech` | ✅ |
| `MYSQL_USER` | Database username | `freedb_username123` | ✅ |
| `MYSQL_PASSWORD` | Database password | `auto_generated_password` | ✅ |
| `MYSQL_DATABASE` | Database name | `freedb_simple_banking` | ✅ |
| `MYSQL_PORT` | Database port | `3306` | ✅ |
| `SECRET_KEY` | Flask secret key | `64-character-random-string` | ✅ |
| `FLASK_ENV` | Flask environment | `production` | ✅ |
| `DATABASE_URL` | Complete database URL | Auto-generated in config.py | ❌ |
| `REDIS_URL` | Redis URL for rate limiting | `memory://` | ❌ |

### Generating a Secure SECRET_KEY

Generate a strong secret key using Python:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

This will output a 64-character hexadecimal string that you should use as your `SECRET_KEY`.

### Setting Environment Variables in Vercel

1. Go to your Vercel project dashboard
2. Click on "Settings"
3. Navigate to "Environment Variables"
4. Add each variable with its corresponding value
5. Make sure to select the appropriate environments (Production, Preview, Development)

## Vercel Configuration

### Database Connection Configuration

The application uses `config.py` to handle database connections. Make sure your configuration supports both local development and production deployment:

```python
import os
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key'
    
    # MySQL connection details
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'simple_banking')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    
    # URL-encode password to handle special characters
    encoded_password = quote_plus(MYSQL_PASSWORD)
    
    # Database URI construction
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'mysql+pymysql://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### Rate Limiting Configuration

For production deployment, the app can use either:
- **Memory-based storage** (default): Suitable for single-instance deployments
- **Redis storage**: Recommended for high-traffic applications

Since Vercel functions are stateless, memory-based rate limiting will reset with each function cold start. For persistent rate limiting, consider upgrading to a Redis service.

## Deployment Process

### Step 1: Prepare Your Repository

1. Ensure all required files are in your repository
2. Commit and push your latest changes to GitHub
3. Verify that sensitive data is not committed (use `.gitignore`)

### Step 2: Import Project to Vercel

1. Login to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect it as a Python project

### Step 3: Configure Build Settings

Vercel should automatically configure the build settings. If needed, verify:

- **Framework Preset**: Other
- **Build Command**: (leave empty - handled by `vercel.json`)
- **Output Directory**: (leave empty)
- **Install Command**: `pip install -r requirements.txt`

### Step 4: Set Environment Variables

Before deploying, add all required environment variables in the Vercel dashboard:

1. Go to project settings
2. Click "Environment Variables"
3. Add each variable from the table above
4. Click "Save"

### Step 5: Deploy

1. Click "Deploy"
2. Wait for the build process to complete
3. Vercel will provide you with a deployment URL

## Post-Deployment Setup

### Database Initialization

After successful deployment, you need to initialize your database:

1. Access your FreeSQLDatabase dashboard
2. Use the SQL editor or connect via a MySQL client
3. Run the schema creation scripts to set up tables

Alternatively, you can use a database management tool like phpMyAdmin (often provided by FreeSQLDatabase) to import your schema.

### Default User Accounts

The application comes with default accounts for testing:

- **Admin User**: 
  - Username: `admin`
  - Password: `admin123`

- **Manager User**: 
  - Username: `manager`
  - Password: `manager123`

- **Test User**: 
  - Username: `testuser`
  - Password: `testpassword`

> **Security Note**: Change these default passwords immediately in production!

### Testing the Deployment

1. Visit your Vercel deployment URL
2. Try logging in with the default accounts
3. Test key functionality:
   - User registration
   - Account balance viewing
   - Money transfers
   - Admin features (if applicable)

## Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Errors

**Error**: "Can't connect to MySQL server"

**Solutions**:
- Verify all database environment variables are correctly set
- Check if FreeSQLDatabase service is operational
- Ensure the database allows external connections (FreeSQLDatabase allows this by default)
- Verify the database exists and credentials are correct

#### 2. Build Failures

**Error**: "Build failed" or dependency issues

**Solutions**:
- Check `requirements.txt` for syntax errors
- Ensure all dependencies are available on PyPI
- Review Vercel build logs for specific error messages

#### 3. Runtime Errors

**Error**: "Internal Server Error" (500)

**Solutions**:
- Check Vercel function logs in the dashboard
- Verify all environment variables are set
- Ensure `SECRET_KEY` is properly configured
- Check for missing or misconfigured database tables

#### 4. Rate Limiting Issues

**Error**: Rate limit exceeded

**Solutions**:
- Consider implementing Redis for persistent rate limiting
- Adjust rate limiting configuration in the application
- Monitor traffic patterns and adjust limits accordingly

### Debugging Tips

1. **Check Vercel Logs**: Go to your project dashboard → Functions → View function logs
2. **Test Locally**: Ensure the application works locally with the same environment variables
3. **Database Access**: Use FreeSQLDatabase's web interface to verify database connectivity
4. **Environment Variables**: Double-check all variables are set correctly in Vercel

### Performance Optimization

1. **Database Indexing**: Ensure proper indexes on frequently queried columns
2. **Connection Pooling**: Consider implementing connection pooling for better performance
3. **Caching**: Implement caching strategies for frequently accessed data
4. **Rate Limiting**: Use Redis for better rate limiting performance

## Security Considerations

### Production Security Checklist

- [ ] Change all default passwords
- [ ] Use strong, unique `SECRET_KEY`
- [ ] Enable HTTPS (automatic with Vercel)
- [ ] Regularly update dependencies
- [ ] Monitor access logs
- [ ] Implement proper input validation
- [ ] Use environment variables for all sensitive data
- [ ] Regular database backups

### Database Security

- [ ] Use strong database passwords
- [ ] Limit database access to necessary IPs only (if supported by provider)
- [ ] Regular security updates
- [ ] Monitor for suspicious database activity

## Support and Resources

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **FreeSQLDatabase Support**: Available through their website
- **Flask Documentation**: [flask.palletsprojects.com](https://flask.palletsprojects.com)
- **Project Repository**: Your GitHub repository for issues and updates

## Conclusion

Following this guide should result in a successful deployment of your Simple Banking App to Vercel with FreeSQLDatabase. The combination provides a cost-effective solution for hosting a Flask application with cloud-based MySQL database connectivity.

Remember to monitor your application's performance and security regularly, and keep all dependencies updated for optimal operation.
