# Quick Start Guide - Vercel Deployment

## 🚀 5-Minute Vercel Deployment

This guide gets your banking app deployed to Vercel in the fastest way possible.

### Step 1: Database Setup (2 minutes)

**FreeSQLDatabase Setup**
1. Go to [www.freesqldatabase.com](https://www.freesqldatabase.com) → Sign up
2. Create new database: "simple-banking-app"
3. Note the connection details:
   - Host: `sql.freedb.tech`
   - Database name, username, and password (auto-generated)

### Step 2: Vercel Setup (1 minute)

1. Go to [vercel.com](https://vercel.com) → Sign up with GitHub
2. Click "New Project" → Import your repository
3. Leave all build settings as default

### Step 3: Environment Variables (2 minutes)

In Vercel project settings → Environment Variables, add:

```
MYSQL_HOST=your-database-host
MYSQL_USER=your-database-username  
MYSQL_PASSWORD=your-database-password
MYSQL_DATABASE=your-database-name
SECRET_KEY=generate-a-long-random-string-here
FLASK_ENV=production
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 4: Deploy! (30 seconds)

Click "Deploy" in Vercel → Wait for build to complete → Done! 🎉

### Step 5: Test Your App

Visit your deployed URL and login with:
- **Admin**: `admin` / `admin123`
- **Manager**: `manager` / `manager123`

---

## 🔧 Environment Variables Quick Reference

| Variable | Example | Required |
|----------|---------|----------|
| `MYSQL_HOST` | `sql.freedb.tech` | ✅ |
| `MYSQL_USER` | `freedb_username123` | ✅ |
| `MYSQL_PASSWORD` | `auto_generated_password` | ✅ |
| `MYSQL_DATABASE` | `freedb_simple_banking` | ✅ |
| `SECRET_KEY` | `64-char-random-string` | ✅ |
| `FLASK_ENV` | `production` | ✅ |
| `REDIS_URL` | `memory://` | ❌ (optional) |

---

## 🗂️ Required Files Checklist

Make sure these files exist in your repository:

- ✅ `vercel.json` - Vercel configuration
- ✅ `api/wsgi.py` - WSGI entry point
- ✅ `.vercelignore` - Files to ignore during build
- ✅ `requirements.txt` - Python dependencies
- ✅ `app.py` - Main Flask application
- ✅ `config.py` - Configuration settings

---

## 🚨 Common Quick Fixes

**"Can't connect to database"**
- Check database host/credentials
- Ensure database allows external connections

**"Internal Server Error"**
- Check Vercel function logs
- Verify all environment variables are set

**"Build failed"**
- Check `requirements.txt` syntax
- Ensure all dependencies are available

---

## 📞 Need Help?

1. **Check logs**: Vercel dashboard → Your project → Functions tab
2. **Review full guide**: See `VERCEL_DEPLOYMENT.md` for comprehensive deployment documentation
3. **Use checklist**: See `DEPLOYMENT_CHECKLIST.md` for systematic troubleshooting

**For detailed deployment guidance including database setup, security considerations, and troubleshooting, refer to `VERCEL_DEPLOYMENT.md`**

**Default Login Credentials:**
- Admin: `admin` / `admin123`
- Manager: `manager` / `manager123`
- Test User: `testuser` / `testpassword`

Happy deploying! 🚀
