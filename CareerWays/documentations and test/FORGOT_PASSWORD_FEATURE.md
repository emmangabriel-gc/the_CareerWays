# Forgot Password & OTP Authentication Implementation

## Overview
This document describes the forgot password feature with OTP (One-Time Password) authentication that was added to CareerWays. Users can now reset their forgotten passwords by receiving a 6-digit OTP sent to their registered email address.

## Features Implemented

### 1. Backend Changes

#### Database Model Updates (`backend/models/__init__.py`)
Added new fields to the `User` model:
- `password_reset_otp`: Stores the 6-digit OTP
- `password_reset_otp_expires`: Timestamp for OTP expiration (10 minutes)
- `password_reset_token`: Temporary token for password reset (after OTP verification)
- `password_reset_expires`: Timestamp for reset token expiration (15 minutes)

#### New API Endpoints (`backend/routes/auth_routes.py`)

**POST `/api/auth/forgot-password`**
- Request: `{ "email": "user@example.com" }`
- Generates a random 6-digit OTP
- Sends OTP to user's email
- Stores OTP in database with 10-minute expiration
- Returns 200 if email exists (security: doesn't reveal if email is registered)

**POST `/api/auth/verify-otp`**
- Request: `{ "email": "user@example.com", "otp": "123456" }`
- Validates OTP against stored value
- Checks OTP hasn't expired
- Generates temporary reset token (15-minute validity)
- Returns reset token for next step
- Returns 401 if OTP is invalid

**POST `/api/auth/reset-password`**
- Request: `{ "email": "user@example.com", "reset_token": "token", "new_password": "newpass123" }`
- Validates reset token
- Checks token hasn't expired
- Updates user's password
- Clears all reset-related fields
- Sends confirmation email to user
- Returns 200 on success

#### Email Configuration (`backend/app.py`)
- Added Flask-Mail initialization
- Configured email settings from environment variables:
  - `MAIL_SERVER`: SMTP server (default: smtp.gmail.com)
  - `MAIL_PORT`: SMTP port (default: 587)
  - `MAIL_USE_TLS`: TLS encryption (default: true)
  - `MAIL_USERNAME`: Email account username
  - `MAIL_PASSWORD`: Email account password
  - `MAIL_DEFAULT_SENDER`: From email address

### 2. Frontend Changes

#### HTML Updates (`frontend/index.html`)
- Added "Forgot Password" tab to authentication section
- Three-step form:
  1. **Step 1**: Request OTP with email address
  2. **Step 2**: Verify 6-digit OTP sent to email
  3. **Step 3**: Create new password

#### JavaScript Implementation (`frontend/js/index.js`)
Added four new handler functions:
- `handleSendOtp()`: Sends OTP to email
- `handleVerifyOtp()`: Verifies OTP and gets reset token
- `handleResendOtp()`: Resends OTP if expired
- `handleResetPassword()`: Resets password with new one

Uses `sessionStorage` to maintain state across the three-step process.

#### CSS Styling (`frontend/css/index.css`)
Added styles for:
- `.form-hint`: Help text styling
- `.switch-tab`: Link styling for tab switching
- `.form-subtitle`: Subtitle text in forms
- `.link-btn`: Button-styled links
- Form step containers with proper spacing

## Dependencies Added

Updated `requirements.txt`:
- `Flask-Mail>=0.9.1`: Email sending functionality
- `pyotp>=2.8.0`: OTP generation (can be used for future 2FA)
- `qrcode>=7.4.2`: QR code generation (optional, for future use)

## Environment Configuration

Create a `.env` file in the `CareerWays` folder with:

```env
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@careerways.com
```

### Gmail Setup Instructions
1. Enable 2-Factor Authentication on Google account
2. Visit: https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer" (or your device)
4. Copy the generated app password
5. Use this password in `MAIL_PASSWORD`

### Other Email Providers
Update `MAIL_SERVER` to your provider's SMTP server:
- Gmail: `smtp.gmail.com`
- Outlook: `smtp-mail.outlook.com`
- Yahoo: `smtp.mail.yahoo.com`
- Custom: Your organization's SMTP server

## Security Features

1. **OTP Expiration**: OTP valid for 10 minutes only
2. **Reset Token Expiration**: Token valid for 15 minutes after OTP verification
3. **Email Verification**: Users must verify OTP before resetting password
4. **Email Privacy**: Endpoint doesn't reveal if email is registered (prevents user enumeration)
5. **Password Hashing**: New password is hashed before storage
6. **Confirmation Email**: User receives confirmation after successful password reset
7. **OTP Format**: 6-digit numeric OTP (1,000,000 combinations)

## User Flow

1. User clicks "Forgot Password" tab
2. Enters registered email address
3. Clicks "Send OTP"
4. API sends 6-digit code to email (valid 10 minutes)
5. User receives email with OTP
6. User enters OTP in form
7. API verifies OTP and provides reset token
8. User enters new password and confirmation
9. API validates and updates password
10. User receives confirmation email
11. User can log in with new password

## Testing

### Manual Testing Steps
1. Go to login page
2. Click "Forgot Password" tab
3. Enter registered email
4. Check email for OTP (check spam folder)
5. Enter OTP in form
6. Enter new password
7. Verify login works with new password

### Test Email Addresses
- Development: Use personal Gmail account
- Production: Configure company email provider

## Error Handling

The implementation includes proper error handling for:
- Missing required fields
- Invalid OTP format
- Expired OTP
- Expired reset token
- Email sending failures
- Database errors
- Invalid password format

## Future Enhancements

1. **Rate Limiting**: Limit OTP requests per email (prevent spam)
2. **OTP Resend Limit**: Allow resend only after certain time
3. **2FA Option**: Allow users to enable 2FA for login
4. **Backup Codes**: Generate backup codes for account recovery
5. **Phone OTP**: Support SMS delivery in addition to email
6. **Security Questions**: Add security questions as additional verification

## Troubleshooting

### Email Not Sending
1. Check MAIL_USERNAME and MAIL_PASSWORD are correct
2. Verify MAIL_SERVER and MAIL_PORT settings
3. Check if email provider blocks application
4. Enable "Less secure app access" for Gmail (if not using app password)
5. Check Flask-Mail logs for error messages

### OTP Verification Fails
1. Verify OTP hasn't expired (10-minute window)
2. Check OTP is exactly 6 digits
3. Ensure email matches registered account email
4. Try "Resend OTP" if OTP was lost

### Reset Token Expired
1. Start over from "Forgot Password" tab
2. OTP and reset token have 10-15 minute windows
3. Process should be completed within this timeframe

## Files Modified

1. `backend/models/__init__.py` - Added OTP fields to User model
2. `backend/app.py` - Added Flask-Mail configuration
3. `backend/routes/auth_routes.py` - Added forgot password endpoints
4. `frontend/index.html` - Added forgot password form
5. `frontend/js/index.js` - Added forgot password handlers
6. `frontend/css/index.css` - Added forgot password styling
7. `requirements.txt` - Added email dependencies

## API Documentation

### Forgot Password Request
```
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}

Response 200:
{
  "message": "OTP has been sent to your email",
  "email": "user@example.com"
}
```

### OTP Verification
```
POST /api/auth/verify-otp
Content-Type: application/json

{
  "email": "user@example.com",
  "otp": "123456"
}

Response 200:
{
  "message": "OTP verified successfully",
  "reset_token": "uuid-token-here"
}
```

### Password Reset
```
POST /api/auth/reset-password
Content-Type: application/json

{
  "email": "user@example.com",
  "reset_token": "uuid-token-here",
  "new_password": "newpassword123"
}

Response 200:
{
  "message": "Password reset successful. Please log in with your new password."
}
```

## Notes

- OTP is automatically cleared after successful password reset
- Reset tokens are one-time use only
- All reset-related fields are cleared after successful reset
- Confirmation email is sent after successful password reset
- OTP delivery depends on email configuration being correct
