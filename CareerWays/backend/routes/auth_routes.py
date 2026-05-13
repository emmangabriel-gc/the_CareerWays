"""
Authentication Routes for CareerWays
"""

from flask import Blueprint, request, jsonify, redirect, current_app
from app import db, mail
from models import User
from flask_mail import Message
import jwt
import os
from datetime import datetime, timedelta
import uuid
import random
import string
import logging

auth_bp = Blueprint('auth', __name__)
_log = logging.getLogger(__name__)


def _log_mail_error(message, exc=None):
    try:
        if exc is not None:
            current_app.logger.error("%s: %s", message, exc, exc_info=exc)
        else:
            current_app.logger.error(message)
    except RuntimeError:
        if exc is not None:
            _log.error("%s: %s", message, exc, exc_info=exc)
        else:
            _log.error(message)


def mail_credentials_configured():
    """True if Flask-Mail has credentials (SMTP cannot send without them)."""
    try:
        u = (current_app.config.get('MAIL_USERNAME') or '').strip()
        p = (current_app.config.get('MAIL_PASSWORD') or '').strip()
        return bool(u and p)
    except RuntimeError:
        return False


def get_public_backend_url():
    """Public HTTPS base for API links in emails (no trailing slash)."""
    explicit = os.getenv('BACKEND_URL', '').strip().rstrip('/')
    if explicit:
        return explicit
    domain = os.getenv('RAILWAY_PUBLIC_DOMAIN', '').strip()
    if domain:
        if domain.startswith('http'):
            return domain.rstrip('/')
        return f'https://{domain}'.rstrip('/')
    return 'https://thecareerways-production.up.railway.app'


JWT_SECRET = os.getenv(
    'JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 30  # days


def create_token(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(days=JWT_EXPIRATION)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}


def send_verification_email(email, token, user_name):
    frontend_url = os.getenv('FRONTEND_URL', 'https://the-career-ways.vercel.app')
    try:
        subject = 'CareerWays – Please verify your email'
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="background-color: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">Welcome to CareerWays, {user_name}!</h2>
                    <p>Thanks for signing up. Please verify your email address by clicking the button below:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{get_public_backend_url()}/api/auth/confirm-email?token={token}"
                           style="background-color: #4a90d9; color: white; padding: 14px 28px;
                                  border-radius: 6px; text-decoration: none; font-weight: bold;
                                  display: inline-block;">
                            Verify My Email
                        </a>
                    </div>
                    <p style="color: #666;">This link expires in <strong>24 hours</strong>.</p>
                    <p style="color: #666;">If you didn't create a CareerWays account, you can safely ignore this email.</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #999; font-size: 12px;">CareerWays – AI-Powered Course Guidance</p>
                </div>
            </body>
        </html>
        """
        msg = Message(subject=subject, recipients=[email], html=html)
        mail.send(msg)
        return True
    except Exception as e:
        _log_mail_error("Error sending verification email", e)
        return False


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(email, otp, user_name):
    try:
        subject = 'CareerWays - Password Reset OTP'
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="background-color: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">Password Reset Request</h2>
                    <p>Hi {user_name},</p>
                    <p>We received a request to reset your password. Use the OTP below to proceed:</p>
                    <div style="background-color: #f0f0f0; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #007bff; letter-spacing: 5px; margin: 0;">{otp}</h1>
                    </div>
                    <p style="color: #666;">This OTP is valid for 10 minutes. Do not share it with anyone.</p>
                    <p style="color: #666;">If you didn't request a password reset, please ignore this email.</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #999; font-size: 12px;">CareerWays - AI-Powered Course Guidance</p>
                </div>
            </body>
        </html>
        """
        msg = Message(subject=subject, recipients=[email], html=html)
        mail.send(msg)
        return True
    except Exception as e:
        _log_mail_error("Error sending OTP email", e)
        return False


@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['name', 'email', 'password']):
            return jsonify({'message': 'Missing required fields'}), 400

        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']

        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered'}), 409

        verification_token = str(uuid.uuid4())
        verification_expires = datetime.utcnow() + timedelta(hours=24)

        user = User(name=name, email=email)
        user.set_password(password)
        user.is_verified = False
        user.verification_token = verification_token
        user.verification_token_expires = verification_expires

        db.session.add(user)
        db.session.flush()

        if not mail_credentials_configured():
            db.session.rollback()
            return jsonify({
                'message': (
                    'Email is not configured on the server (MAIL_USERNAME / MAIL_PASSWORD). '
                    'Add SMTP credentials in Railway, then try again.'
                )
            }), 503

        if not send_verification_email(email, verification_token, user.name):
            db.session.rollback()
            return jsonify({
                'message': (
                    'Could not send verification email. Check MAIL_SERVER, MAIL_PORT, '
                    'MAIL_USE_TLS/MAIL_USE_SSL, and sender settings on the server.'
                )
            }), 503

        db.session.commit()

        return jsonify({'message': 'Account created. Please check your email to verify your account.'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({'message': 'Missing email or password'}), 400

        email = data['email'].strip().lower()
        password = data['password']

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({'message': 'Invalid email or password'}), 401

        if not user.is_verified:
            return jsonify({
                'message': 'Please verify your email before logging in.',
                'code': 'EMAIL_NOT_VERIFIED'
            }), 403

        token = create_token(user)
        return jsonify({'message': 'Login successful', 'token': token, 'user': user.to_dict()}), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/confirm-email', methods=['GET'])
def confirm_email():
    frontend_url = os.getenv('FRONTEND_URL', 'https://the-career-ways.vercel.app')
    token = request.args.get('token', '').strip()

    if not token:
        return redirect(f"{frontend_url}/index.html?verified=expired")

    user = User.query.filter_by(verification_token=token).first()

    if not user:
        return redirect(f"{frontend_url}/index.html?verified=expired")

    if user.verification_token_expires < datetime.utcnow():
        return redirect(f"{frontend_url}/index.html?verified=expired")

    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    db.session.commit()

    return redirect(f"{frontend_url}/index.html?verified=true")


@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'message': 'Email is required'}), 400

        email = data['email'].strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user or user.is_verified:
            return jsonify({'message': 'If an unverified account exists, a new email has been sent.'}), 200

        verification_token = str(uuid.uuid4())
        user.verification_token = verification_token
        user.verification_token_expires = datetime.utcnow() + timedelta(hours=24)

        if not mail_credentials_configured():
            db.session.rollback()
            return jsonify({
                'message': (
                    'Email is not configured on the server. '
                    'Set MAIL_USERNAME and MAIL_PASSWORD in Railway.'
                )
            }), 503

        if not send_verification_email(email, verification_token, user.name):
            db.session.rollback()
            return jsonify({
                'message': (
                    'Could not send verification email. Check SMTP settings on the server.'
                )
            }), 503

        db.session.commit()

        return jsonify({'message': 'Verification email resent.'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/verify', methods=['POST'])
def verify():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Missing authorization header'}), 401

        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'message': 'Invalid authorization header'}), 401

        payload = verify_token(token)
        if 'error' in payload:
            return jsonify({'message': payload['error']}), 401

        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'message': 'User not found'}), 404

        return jsonify({'message': 'Token valid', 'user': user.to_dict()}), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Missing authorization header'}), 401

        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'message': 'Invalid authorization header'}), 401

        payload = verify_token(token)
        if 'error' in payload:
            return jsonify({'message': payload['error']}), 401

        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'message': 'User not found'}), 404

        new_token = create_token(user)
        return jsonify({'message': 'Token refreshed', 'token': new_token}), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'message': 'Email is required'}), 400

        email = data['email'].strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({'message': 'If an account exists with this email, an OTP has been sent'}), 200

        otp = generate_otp()
        otp_expires = datetime.utcnow() + timedelta(minutes=10)

        user.password_reset_otp = otp
        user.password_reset_otp_expires = otp_expires

        if not mail_credentials_configured():
            db.session.rollback()
            return jsonify({
                'message': (
                    'Password reset email is not configured on the server. '
                    'Set MAIL_USERNAME and MAIL_PASSWORD in Railway, then try again.'
                )
            }), 503

        if not send_otp_email(email, otp, user.name):
            db.session.rollback()
            return jsonify({
                'message': (
                    'Could not send reset email. Verify MAIL_SERVER, MAIL_PORT, '
                    'MAIL_USE_TLS or MAIL_USE_SSL (e.g. 465), and Gmail app password if using Gmail.'
                )
            }), 503

        db.session.commit()

        return jsonify({'message': 'OTP has been sent to your email', 'email': email}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['email', 'otp']):
            return jsonify({'message': 'Email and OTP are required'}), 400

        email = data['email'].strip().lower()
        otp = data['otp'].strip()

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        if not user.password_reset_otp:
            return jsonify({'message': 'No password reset request found'}), 400

        if user.password_reset_otp_expires < datetime.utcnow():
            return jsonify({'message': 'OTP has expired. Request a new one.'}), 400

        if user.password_reset_otp != otp:
            return jsonify({'message': 'Invalid OTP'}), 401

        reset_token = str(uuid.uuid4())
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()

        return jsonify({'message': 'OTP verified successfully', 'reset_token': reset_token}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['email', 'reset_token', 'new_password']):
            return jsonify({'message': 'Email, reset token, and new password are required'}), 400

        email = data['email'].strip().lower()
        reset_token = data['reset_token'].strip()
        new_password = data['new_password'].strip()

        if len(new_password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        if not user.password_reset_token or user.password_reset_token != reset_token:
            return jsonify({'message': 'Invalid or expired reset token'}), 401

        if user.password_reset_expires < datetime.utcnow():
            return jsonify({'message': 'Reset token has expired'}), 401

        user.set_password(new_password)
        user.password_reset_otp = None
        user.password_reset_otp_expires = None
        user.password_reset_token = None
        user.password_reset_expires = None
        db.session.commit()

        try:
            msg = Message(
                subject='CareerWays - Password Changed Successfully',
                recipients=[email],
                html=f"<p>Hi {user.name}, your password has been reset successfully.</p>"
            )
            mail.send(msg)
        except Exception as e:
            _log_mail_error("password-changed notification failed", e)

        return jsonify({'message': 'Password reset successful. Please log in with your new password.'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500