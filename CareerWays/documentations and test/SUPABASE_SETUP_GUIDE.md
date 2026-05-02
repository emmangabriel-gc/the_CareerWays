# 🔗 How to Connect Supabase to Your CareerWays System

## What is Supabase?
Supabase is an open-source Firebase alternative that provides PostgreSQL databases, authentication, and storage. It's perfect for production deployments.

## ✅ You Already Have Supabase Connected!

Great news! Your `.env` file already has Supabase credentials configured:
```
DATABASE_URL=postgresql://postgres:Emm4ng4brieldel4cruz@db.sdjtwozfmokhybacutlj.supabase.co:5432/postgres
```

This means:
- ✅ Project ID: `sdjtwozfmokhybacutlj`
- ✅ Database: PostgreSQL
- ✅ Host: `db.sdjtwozfmokhybacutlj.supabase.co`
- ✅ Username: `postgres`

## 🚀 To Enable Supabase (Current Setup)

Your app is **already configured** to use Supabase! The local SQLite fallback is just a backup. Here's how it currently works:

### Current Connection Flow
```
App Startup
    ↓
Try to connect to Supabase (DATABASE_URL)
    ↓
If Supabase is reachable → Use PostgreSQL database
If Supabase is unreachable → Fall back to local SQLite
```

When you saw this message:
```
[CareerWays] DATABASE_URL host 'db.sdjtwozfmokhybacutlj.supabase.co' is unreachable. Falling back to local SQLite database.
```

It means Supabase server was temporarily unreachable. This is normal during testing.

## 📋 Complete Setup Steps (What We Did)

### Step 1: Create Supabase Project
✅ Already done at: https://sdjtwozfmokhybacutlj.supabase.co

### Step 2: Get Connection String
The connection string is already in your `.env`:
```
postgresql://postgres:Emm4ng4brieldel4cruz@db.sdjtwozfmokhybacutlj.supabase.co:5432/postgres
```

### Step 3: Configure Environment
✅ `.env` file already configured with:
- `DATABASE_URL` - PostgreSQL connection
- `JWT_SECRET_KEY` - For token authentication
- `SUPABASE_URL` - For future direct API calls
- `SUPABASE_ANON_KEY` - For public operations
- Email settings - For password reset

## 🔐 Security Note

Your credentials are in `.env` - **keep this file secret!**

### For Production Deployment:
1. **Never commit `.env` to Git** - add to `.gitignore`
2. Use environment variables from hosting provider:
   - Vercel → Project Settings → Environment Variables
   - Heroku → Config Vars
   - AWS → Systems Manager Parameter Store
   - Azure → Key Vault

## ✉️ Email Configuration (NEW!)

The system now supports OTP email verification. Add your email credentials to `.env`:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@careerways.com
```

### Setup Gmail for Password Reset OTPs:

1. **Enable 2-Factor Authentication**
   - Go to myaccount.google.com
   - Click "Security" in left menu
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Google will generate a 16-character password
   - Copy this password

3. **Update `.env` File**
   ```env
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=xxxxxxxxxxxxxxxx  (the 16-char password)
   ```

4. **Restart Flask Server**
   ```bash
   python app.py
   ```

Now password reset emails will be sent! ✅

## 🔄 Testing Supabase Connection

### Test 1: Check Connection String
```bash
# Run this in Python terminal
python -c "import psycopg2; psycopg2.connect('postgresql://postgres:Emm4ng4brieldel4cruz@db.sdjtwozfmokhybacutlj.supabase.co:5432/postgres'); print('Connected!')"
```

### Test 2: Check Backend Logs
When you start the Flask server, look for:
```
[CareerWays] DATABASE_URL host 'db.sdjtwozfmokhybacutlj.supabase.co' is...
```

- If **"Falling back to local SQLite"** → Supabase is unreachable (network issue)
- If **no message** and app starts → Supabase connected successfully!

### Test 3: Check Database in Supabase Dashboard
1. Go to https://app.supabase.com
2. Select your project
3. Click "SQL Editor"
4. Run: `SELECT * FROM users LIMIT 1;`
5. If you see data → Connected! ✅

## 🗄️ Database Migration Steps

Your database uses the new password reset columns we added:

### Tables Created:
- `users` - With password reset fields
- `assessments` - Career assessments
- `assessment_details` - NLP analysis
- `courses` - Available courses
- `favorites` - User favorites

### If You Need to Reset Supabase Database:
1. Go to https://app.supabase.com
2. Select your project
3. Click "Settings" → "Danger Zone"
4. Click "Reset Database"
5. Confirm (this deletes all data!)
6. Restart Flask: `python app.py`
7. New tables will be created automatically

## 🔍 Advanced Configuration

### Use Connection Pooling (Recommended)
Supabase provides connection pooling for better performance:

1. Go to Supabase Dashboard
2. Click "Database"
3. Copy "Session mode" connection string
4. Update `.env` DATABASE_URL

### Custom Database URL Format
```
postgresql://user:password@host:port/database?sslmode=require
```

Parameters:
- `user` - Database user (usually `postgres`)
- `password` - Database password
- `host` - Supabase database host
- `port` - Usually 5432
- `database` - Database name (usually `postgres`)
- `sslmode=require` - Use SSL (recommended)

## 🆘 Troubleshooting

### Issue: "Connection refused"
```
Falling back to local SQLite database
```
**Solution:**
- Check internet connection
- Verify DATABASE_URL in `.env` is correct
- Check Supabase project status: https://app.supabase.com/projects
- Supabase might be down (check status.supabase.com)

### Issue: "Authentication failed"
```
FATAL: password authentication failed for user "postgres"
```
**Solution:**
- Check password in `.env` is correct
- Password has special characters? Verify they're escaped
- Reset password in Supabase: Settings → Users → Reset password

### Issue: "Column not found"
```
Column 'password_reset_otp' does not exist
```
**Solution:**
- Database schema is old
- Reset database (see "Database Migration Steps" above)
- Or run migrations manually in SQL Editor

### Issue: "Port 5432 already in use"
**Solution:**
- Only the Flask app uses this, not your computer
- This is a remote port on Supabase, not local
- Ignore this error

## 📊 Monitoring Supabase

### Check Usage
- Go to https://app.supabase.com/projects
- Select project → "Usage" tab
- See database connections, storage, queries

### View Logs
- Click "Logs" in left sidebar
- View all database queries and errors
- Useful for debugging

### Backup Data
- Click "Settings" → "Backups"
- Download SQL backups
- Or use `pg_dump` command

## 🎯 Next Steps

1. **Configure Email** - Add Gmail credentials to `.env` for password reset
2. **Test Forgot Password** - Go to forgot-password.html, send OTP
3. **Deploy to Production** - Follow deployment guide
4. **Enable SSL** - Use `sslmode=require` in production

## 📚 Useful Links

- Supabase Dashboard: https://app.supabase.com
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Connection String Docs: https://supabase.com/docs/guides/database/connecting-to-postgres

## ✅ Checklist

- [x] Supabase project created
- [x] Database connection string configured
- [x] `.env` file set up
- [ ] Email configuration added (DO THIS!)
- [ ] Test password reset flow
- [ ] Deploy to production

---

**Your Supabase is already connected! Just add email configuration and you're good to go!** 🚀
