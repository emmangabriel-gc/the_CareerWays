"""
Authentication Routes for CareerWays
"""

from flask import Blueprint, request, jsonify
from app import db, mail
from models import User
from flask_mail import Message
import jwt
import os
from datetime import datetime, timedelta
import uuid
import random
import string

auth_bp = Blueprint('auth', __name__)

JWT_SECRET = os.getenv(
    'JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 30  # days


def create_token(user):
    """Create JWT token for user"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(days=JWT_EXPIRATION)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate input
        if not data or not all(k in data for k in ['name', 'email', 'password']):
            return jsonify({'message': 'Missing required fields'}), 400

        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']

        # Validate password
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400

        # Check if user exists
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered'}), 409

        # Create new user
        user = User(name=name, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Create token
        token = create_token(user)

        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({'message': 'Missing email or password'}), 400

        email = data['email'].strip().lower()
        password = data['password']

        # Find user
        user = User.query.filter_by(email=email).first()

        print(
            f"Email: {email}, User found: {user is not None}, Password check: {user.check_password(password) if user else 'N/A'}")

        if not user or not user.check_password(password):
            return jsonify({'message': 'Invalid email or password'}), 401

        # Create token
        token = create_token(user)

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/verify', methods=['POST'])
def verify():
    """Verify token"""
    try:
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'message': 'Missing authorization header'}), 401

        # Extract token
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'message': 'Invalid authorization header'}), 401

        payload = verify_token(token)

        if 'error' in payload:
            return jsonify({'message': payload['error']}), 401

        # Get user
        user = User.query.get(payload['user_id'])

        if not user:
            return jsonify({'message': 'User not found'}), 404

        return jsonify({
            'message': 'Token valid',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh JWT token"""
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

        # Get user and create new token
        user = User.query.get(payload['user_id'])

        if not user:
            return jsonify({'message': 'User not found'}), 404

        new_token = create_token(user)

        return jsonify({
            'message': 'Token refreshed',
            'token': new_token
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    # Token invalidation would require a token blacklist in production
    return jsonify({'message': 'Logged out successfully'}), 200


def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(email, otp, user_name):
    """Send OTP to user's email"""
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
                    <p style="color: #666;">If you didn't request a password reset, please ignore this email and your password will remain unchanged.</p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #999; font-size: 12px;">CareerWays - AI-Powered Course Guidance</p>
                </div>
            </body>
        </html>
        """

        msg = Message(
            subject=subject,
            recipients=[email],
            html=html
        )

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset - sends OTP to email"""
    try:
        data = request.get_json()

        if not data or 'email' not in data:
            return jsonify({'message': 'Email is required'}), 400

        email = data['email'].strip().lower()

        # Find user
        user = User.query.filter_by(email=email).first()

        if not user:
            # Don't reveal if email exists (security best practice)
            return jsonify({'message': 'If an account exists with this email, an OTP has been sent'}), 200

        # Generate OTP
        otp = generate_otp()
        otp_expires = datetime.utcnow() + timedelta(minutes=10)

        # Save OTP to user
        user.password_reset_otp = otp
        user.password_reset_otp_expires = otp_expires

        db.session.commit()

        # Send email
        if not send_otp_email(email, otp, user.name):
            return jsonify({'message': 'Error sending OTP. Please try again.'}), 500

        return jsonify({
            'message': 'OTP has been sent to your email',
            'email': email
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP for password reset"""
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ['email', 'otp']):
            return jsonify({'message': 'Email and OTP are required'}), 400

        email = data['email'].strip().lower()
        otp = data['otp'].strip()

        # Find user
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Check if OTP exists and not expired
        if not user.password_reset_otp:
            return jsonify({'message': 'No password reset request found'}), 400

        if user.password_reset_otp_expires < datetime.utcnow():
            return jsonify({'message': 'OTP has expired. Request a new one.'}), 400

        if user.password_reset_otp != otp:
            return jsonify({'message': 'Invalid OTP'}), 401

        # Generate a temporary token for password reset
        reset_token = str(uuid.uuid4())
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(minutes=15)

        db.session.commit()

        return jsonify({
            'message': 'OTP verified successfully',
            'reset_token': reset_token
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with valid reset token"""
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ['email', 'reset_token', 'new_password']):
            return jsonify({'message': 'Email, reset token, and new password are required'}), 400

        email = data['email'].strip().lower()
        reset_token = data['reset_token'].strip()
        new_password = data['new_password'].strip()

        # Validate password
        if len(new_password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400

        # Find user
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Verify reset token
        if not user.password_reset_token or user.password_reset_token != reset_token:
            return jsonify({'message': 'Invalid or expired reset token'}), 401

        if user.password_reset_expires < datetime.utcnow():
            return jsonify({'message': 'Reset token has expired'}), 401

        # Update password
        user.set_password(new_password)

        # Clear reset tokens
        user.password_reset_otp = None
        user.password_reset_otp_expires = None
        user.password_reset_token = None
        user.password_reset_expires = None

        db.session.commit()

        # Send confirmation email
        try:
            subject = 'CareerWays - Password Changed Successfully'
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                    <div style="background-color: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto;">
                        <h2 style="color: #333;">Password Changed Successfully</h2>
                        <p>Hi {user.name},</p>
                        <p>Your password has been reset successfully. You can now log in with your new password.</p>
                        <p style="color: #666;">If you didn't make this change, please contact support immediately.</p>
                        
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="color: #999; font-size: 12px;">CareerWays - AI-Powered Course Guidance</p>
                    </div>
                </body>
            </html>
            """
            msg = Message(
                subject=subject,
                recipients=[email],
                html=html
            )
            mail.send(msg)
        except Exception as e:
            print(f"Error sending confirmation email: {str(e)}")

        return jsonify({'message': 'Password reset successful. Please log in with your new password.'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500
