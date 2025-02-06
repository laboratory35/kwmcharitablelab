from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
import csv
from io import StringIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
    static_url_path='',
    static_folder='static',
    template_folder='templates'
)

# Enable CORS for development
CORS(app)

# Configuration
app.config.update(
    SQLALCHEMY_DATABASE_URI='sqlite:///bookings.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY='your-secret-key-here',  # Change this to a secure secret key
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)
    preferred_date = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create initial admin user
def create_admin():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('admin123')  # Change this password
            db.session.add(admin)
            db.session.commit()
            logger.info("Admin user created")

# Routes
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # First try to serve from static folder
    try:
        return send_from_directory('static', path)
    except:
        # If not found in static, try serving from root
        return send_from_directory('.', path)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    try:
        # If user is already logged in, redirect to dashboard
        if current_user.is_authenticated:
            return redirect(url_for('admin_dashboard'))

        if request.method == 'GET':
            return render_template('admin/login.html')
        
        # Check if request is JSON
        if not request.is_json:
            logger.error("Login attempt failed: Content-Type is not application/json")
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        data = request.json
        logger.info(f"Login attempt for username: {data.get('username', 'not provided')}")

        # Validate request data
        if not data or 'username' not in data or 'password' not in data:
            logger.error("Login attempt failed: Missing required fields")
            return jsonify({'error': 'Username and password are required'}), 400

        # Find user
        user = User.query.filter_by(username=data.get('username')).first()
        
        if user and user.check_password(data.get('password')):
            login_user(user, remember=True)
            logger.info(f"Successful login for user: {user.username}")
            return jsonify({
                'message': 'Login successful',
                'redirect': url_for('admin_dashboard')
            })
        
        logger.warning(f"Failed login attempt for username: {data.get('username')}")
        return jsonify({'error': 'Invalid username or password'}), 401

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'An error occurred during login. Please try again.'}), 500

@app.route('/admin/logout')
@login_required
def admin_logout():
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    return redirect(url_for('serve_index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    try:
        return render_template('admin/dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        return jsonify({'error': 'Error loading dashboard'}), 500

@app.route('/admin/check-auth')
def check_auth():
    try:
        if current_user.is_authenticated:
            return jsonify({
                'authenticated': True,
                'username': current_user.username
            })
        return jsonify({'authenticated': False}), 401
    except Exception as e:
        logger.error(f"Error checking authentication: {str(e)}")
        return jsonify({'error': 'Error checking authentication status'}), 500

# API routes
@app.route('/api/book', methods=['POST'])
def book_test():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        data = request.json
        required_fields = ['name', 'email', 'phone', 'testType', 'preferredDate']
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        new_booking = Booking(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            test_type=data['testType'],
            preferred_date=data['preferredDate'],
            message=data.get('message', '')
        )
        
        db.session.add(new_booking)
        db.session.commit()
        
        logger.info(f"New booking created for {data['name']} ({data['email']})")
        return jsonify({'message': 'Booking submitted successfully!'}), 201
        
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request. Please try again.'}), 400

# Admin API routes
@app.route('/api/admin/stats')
@login_required
def get_stats():
    total_bookings = Booking.query.count()
    today_bookings = Booking.query.filter(
        db.func.date(Booking.created_at) == date.today()
    ).count()
    pending_tests = Booking.query.filter_by(status='pending').count()
    
    return jsonify({
        'total_bookings': total_bookings,
        'today_bookings': today_bookings,
        'pending_tests': pending_tests
    })

@app.route('/api/admin/recent-bookings')
@login_required
def get_recent_bookings():
    bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    return jsonify([{
        'id': b.id,
        'name': b.name,
        'email': b.email,
        'phone': b.phone,
        'test_type': b.test_type,
        'preferred_date': b.preferred_date,
        'status': b.status,
        'created_at': b.created_at.isoformat()
    } for b in bookings])

@app.route('/api/admin/booking/<int:id>')
@login_required
def get_booking(id):
    booking = Booking.query.get_or_404(id)
    return jsonify({
        'id': booking.id,
        'name': booking.name,
        'email': booking.email,
        'phone': booking.phone,
        'test_type': booking.test_type,
        'preferred_date': booking.preferred_date,
        'message': booking.message,
        'status': booking.status,
        'created_at': booking.created_at.isoformat()
    })

@app.route('/api/admin/booking/<int:id>/status', methods=['POST'])
@login_required
def update_booking_status(id):
    booking = Booking.query.get_or_404(id)
    data = request.json
    
    if 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
        
    booking.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Status updated successfully'})

@app.route('/api/admin/export')
@login_required
def export_bookings():
    si = StringIO()
    cw = csv.writer(si)
    
    # Write headers
    cw.writerow(['ID', 'Name', 'Email', 'Phone', 'Test Type', 'Preferred Date', 
                 'Message', 'Status', 'Created At'])
    
    # Write data
    bookings = Booking.query.all()
    for booking in bookings:
        cw.writerow([
            booking.id, booking.name, booking.email, booking.phone,
            booking.test_type, booking.preferred_date, booking.message,
            booking.status, booking.created_at
        ])
    
    output = si.getvalue()
    si.close()
    
    return output, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=bookings.csv'
    }

if __name__ == '__main__':
    create_admin()
    app.run(debug=True, port=5000)
