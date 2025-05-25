# Deploying Simple Banking App to Vercel

This guide provides step-by-step instructions for deploying the Simple Banking Application to Vercel with a cloud-based MySQL database.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Database Setup](#database-setup)
- [Environment Variables](#environment-variables)
- [Vercel Configuration](#vercel-configuration)
- [Deployment Steps](#deployment-steps)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have:

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Cloud MySQL Database**: Such as:
   - [PlanetScale](https://planetscale.com/) (Recommended)
   - [MySQL on Railway](https://railway.app/)
   - [FreeSQLDatabase](https://www.freesqldatabase.com/)
   - [Amazon RDS](https://aws.amazon.com/rds/)
   - Any other cloud MySQL provider

3. **GitHub Repository**: Your code should be in a GitHub repository
4. **Vercel CLI** (Optional): Install with `npm i -g vercel`

## Database Setup

### Option 1: PlanetScale (Recommended)

1. **Create Account**: Sign up at [planetscale.com](https://planetscale.com/)
2. **Create Database**:
   ```bash
   # Using PlanetScale CLI
   pscale database create simple-banking-app
   ```
3. **Get Connection String**:
   - Go to your database dashboard
   - Click "Connect"
   - Select "General" and copy the connection string
   - Format: `mysql://username:password@host:port/database`

### Option 2: FreeSQLDatabase

1. **Create Account**: Sign up at [freesqldatabase.com](https://www.freesqldatabase.com/)
2. **Create Database**: Follow their setup wizard
3. **Note Connection Details**:
   - Host: `sql.freedb.tech`
   - Port: `3306`
   - Username: Your assigned username
   - Password: Your assigned password
   - Database: Your database name

### Option 3: Railway MySQL

1. **Create Account**: Sign up at [railway.app](https://railway.app/)
2. **Deploy MySQL**: Click "New Project" → "Deploy MySQL"
3. **Get Connection Details**: From the Variables tab

## Environment Variables

### Required Environment Variables

Create these environment variables in your Vercel project:

#### Database Configuration
```env
MYSQL_HOST=your-mysql-host
MYSQL_PORT=3306
MYSQL_USER=your-mysql-username
MYSQL_PASSWORD=your-mysql-password
MYSQL_DATABASE=your-database-name
```

#### Application Configuration
```env
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
FLASK_ENV=production
```

#### Optional Configuration
```env
# Rate limiting (uses memory by default in serverless)
REDIS_URL=memory://

# For password reset functionality (if using email)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Setting Environment Variables in Vercel

#### Method 1: Vercel Dashboard
1. Go to your project in Vercel dashboard
2. Navigate to "Settings" → "Environment Variables"
3. Add each variable one by one

#### Method 2: Vercel CLI
```bash
vercel env add MYSQL_HOST
# Enter your MySQL host when prompted
vercel env add MYSQL_USER
# Continue for all variables...
```

## Vercel Configuration

### 1. Create `.vercelignore`

Create a `.vercelignore` file in your project root:

```gitignore
# .vercelignore
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git/
.mypy_cache/
.pytest_cache/
.hypothesis/

# Local development files
.env
.env.local
.env.development
.env.test
.env.production

# Database files
*.db
*.sqlite
*.sqlite3

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
schema.sql
init_db.py
README.md
```

### 2. Verify `vercel.json`

Your `vercel.json` should look like this:

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

### 3. Create `api/wsgi.py`

Ensure your `api/wsgi.py` file exists and contains:

```python
import sys
import os

# Add the parent directory to the Python path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

# Import the app as application
from app import app as application

# Initialize database on import for serverless
try:
    from app import init_db
    with application.app_context():
        init_db()
except Exception as e:
    print(f"Database initialization error: {e}")

if __name__ == '__main__':
    application.run()
```

## Deployment Steps

### Method 1: GitHub Integration (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Select the repository containing your banking app

3. **Configure Build Settings**:
   - Framework Preset: "Other"
   - Root Directory: `./` (leave default)
   - Build Command: Leave empty
   - Output Directory: Leave empty
   - Install Command: `pip install -r requirements.txt`

4. **Add Environment Variables**:
   - Before deploying, add all required environment variables
   - Click "Environment Variables" and add each one

5. **Deploy**:
   - Click "Deploy"
   - Wait for the build to complete

### Method 2: Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel --prod
   ```

4. **Follow Prompts**:
   - Set up and deploy? `Y`
   - Which scope? Select your account
   - Link to existing project? `N` (for first deployment)
   - What's your project's name? `simple-banking-app`
   - In which directory is your code located? `./`

## Post-Deployment

### 1. Database Initialization

After successful deployment, your database should be automatically initialized with:
- Default admin user: `admin` / `admin123`
- Default manager user: `manager` / `manager123`
- Sample test users and transactions

### 2. Test the Application

Visit your deployed URL and test:
1. **Registration**: Create a new user account
2. **Login**: Use admin credentials
3. **Admin Panel**: Access admin dashboard
4. **Transactions**: Test money transfers
5. **Security**: Test rate limiting and authentication

### 3. Custom Domain (Optional)

1. Go to Vercel dashboard → Your project → "Domains"
2. Add your custom domain
3. Configure DNS records as instructed

## Important Security Considerations

### 1. Environment Variables Security
- **Never commit `.env` files** to your repository
- Use strong, random `SECRET_KEY` (minimum 32 characters)
- Use strong database passwords
- Rotate credentials regularly

### 2. Database Security
- **Enable SSL/TLS** for database connections
- **Use connection pooling** if available
- **Backup your database** regularly
- **Monitor database access logs**

### 3. Application Security
- **Rate limiting** is configured to prevent abuse
- **CSRF protection** is enabled
- **Password hashing** uses bcrypt
- **Session management** with 30-minute timeout

## Troubleshooting

### Common Issues

#### 1. Database Connection Error
```
Error: (2003, "Can't connect to MySQL server")
```
**Solutions:**
- Verify database host and port
- Check if database server allows external connections
- Ensure credentials are correct
- Check if database server is running

#### 2. Environment Variables Not Loading
```
WARNING: Missing database configuration
```
**Solutions:**
- Verify environment variables are set in Vercel dashboard
- Check variable names match exactly (case-sensitive)
- Redeploy after adding variables

#### 3. Build Failures
```
ERROR: Could not install packages due to an EnvironmentError
```
**Solutions:**
- Check `requirements.txt` for syntax errors
- Ensure all dependencies are available for Linux
- Update dependency versions if needed

#### 4. Application Not Starting
```
Application error: Internal Server Error
```
**Solutions:**
- Check Vercel function logs
- Verify `api/wsgi.py` imports correctly
- Ensure database is accessible
- Check for Python syntax errors

### Debugging Tips

#### 1. View Logs
```bash
# Using Vercel CLI
vercel logs

# Or check in Vercel dashboard under "Functions"
```

#### 2. Test Database Connection
Create a test script to verify database connectivity:

```python
import os
import pymysql

try:
    connection = pymysql.connect(
        host=os.environ.get('MYSQL_HOST'),
        port=int(os.environ.get('MYSQL_PORT', 3306)),
        user=os.environ.get('MYSQL_USER'),
        password=os.environ.get('MYSQL_PASSWORD'),
        database=os.environ.get('MYSQL_DATABASE')
    )
    print("Database connection successful!")
    connection.close()
except Exception as e:
    print(f"Database connection failed: {e}")
```

#### 3. Environment Variable Check
Add this to your `wsgi.py` for debugging:

```python
print("Environment check:")
print(f"MYSQL_HOST: {'✓' if os.environ.get('MYSQL_HOST') else '✗'}")
print(f"MYSQL_USER: {'✓' if os.environ.get('MYSQL_USER') else '✗'}")
print(f"MYSQL_DATABASE: {'✓' if os.environ.get('MYSQL_DATABASE') else '✗'}")
```

## Performance Optimization

### 1. Database Optimization
- Use connection pooling
- Add database indexes for frequently queried fields
- Implement database caching where appropriate

### 2. Application Optimization
- Enable compression in Flask
- Use CDN for static assets
- Implement application-level caching

### 3. Vercel Optimization
- Use appropriate region for your users
- Monitor function execution time
- Optimize cold start performance

## Maintenance

### 1. Regular Updates
- Keep dependencies updated
- Monitor security advisories
- Update Python runtime as needed

### 2. Monitoring
- Set up Vercel monitoring
- Monitor database performance
- Track application errors

### 3. Backups
- Regular database backups
- Version control for code
- Document configuration changes

## Support

If you encounter issues:

1. **Check Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
2. **Review Flask Deployment Guides**: [flask.palletsprojects.com](https://flask.palletsprojects.com/)
3. **Database Provider Support**: Check your MySQL provider's documentation
4. **Community Support**: Stack Overflow, Reddit, Discord communities

---

**Note**: This application handles financial data. Always ensure proper security measures, regular backups, and compliance with relevant regulations in your jurisdiction.
