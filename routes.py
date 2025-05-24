from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app import app, csrf
from extensions import db, limiter
from forms import LoginForm, RegistrationForm, TransferForm, ResetPasswordRequestForm, ResetPasswordForm, DepositForm, UserEditForm, ConfirmTransferForm, ChangePasswordForm, SetPinForm, ResetPinForm
from models import User, Transaction
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os
from functools import wraps
import psgc_api
import datetime
import uuid

# Context processor to provide current year to all templates
@app.context_processor
def inject_year():
    return {'current_year': datetime.datetime.now().year}

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need to be an admin to access this page.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Manager required decorator
def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_manager:
            flash('You need to be a manager to access this page.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# First login check decorator
def first_login_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            # Check if user needs to set PIN (first time login)
            if not current_user.pin_hash:
                flash('Please set up your 6-digit PIN before continuing.', 'warning')
                return redirect(url_for('set_pin'))
            # Check if user needs to change password (admin-created account)
            if current_user.force_password_change:
                flash('You must change your password before continuing.', 'warning')
                return redirect(url_for('change_password'))
        return f(*args, **kwargs)
    return decorated_function

# Email functionality (simulated for this example)
def send_password_reset_email(user):
    # In a real app, this would send an actual email with a reset token
    # For simplicity, we're just creating the token and displaying it
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = serializer.dumps(user.email, salt='password-reset')
    reset_url = url_for('reset_password', token=token, _external=True)
    flash(f'Password reset link (would be emailed): {reset_url}')

# Session timeout checker
@app.before_request
def check_session_timeout():
    if current_user.is_authenticated:
        # Skip check for change_password route if user has force_password_change flag
        if current_user.force_password_change and request.endpoint == 'change_password':
            return
            
        # Skip for static files
        if request.path.startswith('/static'):
            return
            
        # Check if session is permanent (should always be for logged in users)
        if not session.permanent:
            session.permanent = True  # Make it permanent if it's not
            
        # Check last activity time
        last_active = session.get('last_active_time', None)
        now = datetime.datetime.utcnow()
        
        if last_active:
            last_active = datetime.datetime.fromisoformat(last_active)
            # If inactive for more than the permanent session lifetime, log them out
            timeout = app.config.get('PERMANENT_SESSION_LIFETIME', datetime.timedelta(minutes=30))
            if now - last_active > timeout:
                logout_user()
                flash('Your session has expired due to inactivity. Please log in again.')
                return redirect(url_for('login'))
        
        # Update last activity time
        session['last_active_time'] = now.isoformat()

@app.route('/')
@app.route('/index')
@login_required
@first_login_check
def index():
    if current_user.status != 'active' and not current_user.is_admin and not current_user.is_manager:
        flash('Your account is awaiting approval from an administrator.')
        logout_user()
        return redirect(url_for('login'))
    return render_template('index.html', title='Home')

@app.route('/about')
def about():
    return render_template('about.html', title='About Us')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.status == 'pending':
                flash('Your account is pending approval. Please contact an administrator.', 'warning')
                return redirect(url_for('login'))
            elif user.status == 'deactivated':
                flash('Your account has been deactivated. Please contact an administrator.', 'danger')
                return redirect(url_for('login'))
            
            login_user(user)
            session.permanent = True
            session['last_activity'] = datetime.datetime.utcnow().isoformat()
            
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                # Check if user needs to set PIN or change password
                if not user.pin_hash:
                    next_page = url_for('set_pin')
                elif user.force_password_change:
                    next_page = url_for('change_password')
                else:
                    next_page = url_for('index')
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, status='pending')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been registered and is awaiting admin approval.')
        flash('Please set your 6-digit PIN.')
        return redirect(url_for('set_pin', username=user.username))
    return render_template('register.html', title='Register', form=form)

@app.route('/set_pin', methods=['GET', 'POST'])
@login_required
def set_pin():
    # If user already has a PIN and is not forced to change it, redirect to account
    if current_user.pin_hash and not request.args.get('reset'):
        flash('You already have a PIN set. Use the reset PIN option to change it.', 'info')
        return redirect(url_for('account'))
    
    form = SetPinForm()
    if form.validate_on_submit():
        current_user.set_pin(form.pin.data)
        db.session.commit()
        flash('Your PIN has been set successfully!', 'success')
        
        # If this was a forced PIN setup, redirect to account page
        return redirect(url_for('account'))
    
    return render_template('set_pin.html', title='Set PIN', form=form)

@app.route('/account')
@login_required
@first_login_check
def account():
    if current_user.status != 'active' and not current_user.is_admin and not current_user.is_manager:
        flash('Your account is awaiting approval from an administrator.')
        logout_user()
        return redirect(url_for('login'))
    transactions = current_user.get_recent_transactions()
    return render_template('account.html', title='Account', transactions=transactions)

@app.route('/transfer', methods=['GET', 'POST'])
@login_required
@limiter.limit("20 per hour")
@first_login_check
def transfer():
    if current_user.status != 'active' and not current_user.is_admin and not current_user.is_manager:
        flash('Your account is awaiting approval from an administrator.')
        return redirect(url_for('index'))
        
    form = TransferForm()
    # Initialize or increment PIN attempt counter
    if 'pin_attempts' not in session:
        session['pin_attempts'] = 0

    if form.validate_on_submit():

        if not current_user.check_pin(form.pin.data):
            session['pin_attempts'] += 1
            form.pin.errors.append("Incorrect PIN.")
            if session['pin_attempts'] >= 3:
                flash('You have entered an incorrect PIN 3 times. Please reset your PIN.', 'danger')
                session['pin_attempts'] = 0  # Reset counter after lockout
                return redirect(url_for('reset_pin'))  # Or your PIN reset route
            else:
                flash(f'Incorrect PIN. Attempt {session["pin_attempts"]}/3.', 'warning')
            return render_template('transfer.html', title='Transfer Money', form=form)
        # Reset counter on successful PIN entry
        session['pin_attempts'] = 0

        # Find recipient based on transfer type
        recipient = None
        if form.transfer_type.data == 'username':
            recipient = User.query.filter_by(username=form.recipient_username.data).first()
        else:  # account
            recipient = User.query.filter_by(account_number=form.recipient_account.data).first()
            
        amount = form.amount.data
        
        # Check for self-transfer
        if recipient and recipient.id == current_user.id:
            flash('You cannot transfer money to yourself.')
            return redirect(url_for('transfer'))
            
        if current_user.balance < amount:
            flash('Insufficient funds for this transfer.')
            return redirect(url_for('transfer'))
        
        # Check if recipient account is active
        if recipient.status != 'active' and not recipient.is_admin and not recipient.is_manager:
            flash('The recipient account is not active.')
            return redirect(url_for('transfer'))
        
        # Create confirm transfer form with pre-populated data
        confirm_form = ConfirmTransferForm(
            recipient_username=recipient.username,
            recipient_account=recipient.account_number,
            amount=amount,
            transfer_type=form.transfer_type.data
        )
        
        # Show confirmation page before completing transfer
        return render_template('confirm_transfer.html', 
                              recipient=recipient,
                              amount=amount,
                              form=confirm_form)
    
    return render_template('transfer.html', title='Transfer Money', form=form)

@app.route('/reset_pin', methods=['GET', 'POST'])
@login_required
def reset_pin():
    form = ResetPinForm()
    if form.validate_on_submit():
        # Verify current PIN
        if not current_user.check_pin(form.current_pin.data):
            flash('Current PIN is incorrect. Please try again.', 'danger')
            return render_template('reset_pin.html', title='Reset PIN', form=form)
        
        # Set new PIN
        current_user.set_pin(form.pin.data)
        db.session.commit()
        flash('Your PIN has been reset successfully!', 'success')
        return redirect(url_for('account'))
    
    return render_template('reset_pin.html', title='Reset PIN', form=form)

@app.route('/execute_transfer', methods=['POST'])
@login_required
@limiter.limit("20 per hour")
def execute_transfer():
    if current_user.status != 'active' and not current_user.is_admin and not current_user.is_manager:
        flash('Your account is awaiting approval from an administrator.')
        return redirect(url_for('index'))
    
    form = ConfirmTransferForm()
    if form.validate_on_submit():
        amount = float(form.amount.data)
        
        # Find recipient based on transfer type
        recipient = None
        if form.transfer_type.data == 'username':
            recipient = User.query.filter_by(username=form.recipient_username.data).first()
        else:  # account
            recipient = User.query.filter_by(account_number=form.recipient_account.data).first()
        
        if recipient is None:
            flash('Recipient not found.')
            return redirect(url_for('transfer'))
        
        # Check if recipient account is active
        if recipient.status != 'active' and not recipient.is_admin and not recipient.is_manager:
            flash('The recipient account is not active.')
            return redirect(url_for('transfer'))
        
        if current_user.transfer_money(recipient, amount):
            db.session.commit()
            flash(f'Successfully transferred ₱{amount:.2f} to {recipient.username}')
            return redirect(url_for('account'))
        else:
            flash('Transfer failed. Please check your balance.')
            return redirect(url_for('transfer'))
    
    return redirect(url_for('transfer'))

@app.route('/reset_password_request', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    try:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='password-reset', max_age=3600)
        user = User.query.filter_by(email=email).first()
        if not user:
            return redirect(url_for('index'))
    except SignatureExpired:
        flash('The password reset link has expired.')
        return redirect(url_for('reset_password_request'))
    except:
        flash('Invalid reset link')
        return redirect(url_for('reset_password_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Verify current password
        if current_user.check_password(form.current_password.data):
            # Set new password
            current_user.set_password(form.new_password.data)
            # Clear force_password_change flag
            current_user.force_password_change = False
            db.session.commit()
            flash('Your password has been changed successfully.')
            return redirect(url_for('index'))
        else:
            flash('Current password is incorrect.')
    
    return render_template('change_password.html', title='Change Password', form=form)

# Admin routes
@app.route('/admin')
@login_required
@admin_required
@limiter.limit("60 per hour")
def admin_dashboard():
    # Regular admins can only see regular users
    if current_user.is_manager:
        # Managers can see all regular users
        users = User.query.filter(User.is_admin.is_(False)).all()
    else:
        # Regular admins can only see regular users (not managers or other admins)
        users = User.query.filter(User.is_admin.is_(False), User.is_manager.is_(False)).all()
    
    return render_template('admin/dashboard.html', title='Admin Dashboard', users=users)

@app.route('/admin/activate_user/<int:user_id>')
@login_required
@admin_required
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Ensure admin can only activate/deactivate users they can manage
    if not current_user.can_manage_user(user):
        flash('You do not have permission to manage this user.')
        return redirect(url_for('admin_dashboard'))
        
    user.status = 'active'
    db.session.commit()
    flash(f'Account {user.username} has been activated.')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/deactivate_user/<int:user_id>')
@login_required
@admin_required
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Ensure admin can only activate/deactivate users they can manage
    if not current_user.can_manage_user(user):
        flash('You do not have permission to manage this user.')
        return redirect(url_for('admin_dashboard'))
        
    user.status = 'deactivated'
    db.session.commit()
    flash(f'Account {user.username} has been deactivated.')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/create_account', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("20 per hour")
def create_account():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, status='active', force_password_change=True)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User account has been created. User will be required to change password on first login.')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/create_account.html', title='Create User Account', form=form)

@app.route('/admin/deposit', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("30 per hour")
def admin_deposit():
    form = DepositForm()
    
    # Initialize or increment PIN attempt counter
    if 'admin_pin_attempts' not in session:
        session['admin_pin_attempts'] = 0
    
    # Handle account lookup from query parameters (for the lookup button)
    account_details = None
    if request.args.get('account_number'):
        account_number = request.args.get('account_number')
        account_details = User.query.filter_by(account_number=account_number).first()
    
    if form.validate_on_submit():
        # Verify admin PIN first
        if not current_user.check_pin(form.pin.data):
            session['admin_pin_attempts'] += 1
            form.pin.errors.append("Incorrect PIN.")
            if session['admin_pin_attempts'] >= 3:
                flash('You have entered an incorrect PIN 3 times. Please reset your PIN.', 'danger')
                session['admin_pin_attempts'] = 0  # Reset counter after lockout
                return redirect(url_for('reset_pin'))
            else:
                flash(f'Incorrect PIN. Attempt {session["admin_pin_attempts"]}/3.', 'warning')
            return render_template('admin/deposit.html', title='Deposit Funds', form=form, account_details=account_details)
        
        # Reset counter on successful PIN entry
        session['admin_pin_attempts'] = 0
        
        user = User.query.filter_by(account_number=form.account_number.data).first()
        if not user:
            flash('User not found')
            return redirect(url_for('admin_deposit'))
        
        # Admin can only deposit to active accounts (or admin/manager accounts)
        if user.status != 'active' and not user.is_admin and not user.is_manager:
            flash('Cannot deposit to inactive account.')
            return redirect(url_for('admin_deposit'))
        
        amount = form.amount.data
        
        # Call deposit method
        if user.deposit(amount, current_user):
            db.session.commit()
            flash(f'Successfully deposited ₱{amount:.2f} to {user.username}')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Deposit failed.')
            return redirect(url_for('admin_deposit'))
    
    return render_template('admin/deposit.html', title='Deposit Funds', form=form, account_details=account_details)

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    from forms import UserEditForm  # Import here to avoid circular imports
    
    user = User.query.get_or_404(user_id)
    
    # Ensure admin can only edit users they can manage
    if not current_user.can_manage_user(user):
        flash('You do not have permission to edit this user.')
        return redirect(url_for('admin_dashboard'))
    
    form = UserEditForm(original_email=user.email)
    
    # Load region choices for dropdown (always needed)
    regions = psgc_api.get_regions()
    form.region_name.choices = [('', '-- Select Region --')] + [(r['code'], r['name']) for r in regions]
    
    # Always populate form on both GET and POST to maintain choices
    form.email.data = user.email if form.email.data is None else form.email.data
    form.firstname.data = user.firstname if form.firstname.data is None else form.firstname.data
    form.lastname.data = user.lastname if form.lastname.data is None else form.lastname.data
    form.address_line.data = user.address_line if form.address_line.data is None else form.address_line.data
    form.postal_code.data = user.postal_code if form.postal_code.data is None else form.postal_code.data
    form.phone.data = user.phone if form.phone.data is None else form.phone.data
    form.status.data = user.status if form.status.data is None else form.status.data
    
    # CRITICAL: We need to populate the dependent dropdown choices
    # for both GET and POST requests to avoid validation errors
    
    # Load existing region selection
    region_code = user.region_code
    if form.region_name.data:
        region_code = form.region_name.data
    
    # If we have a region, load provinces
    if region_code:
        provinces = psgc_api.get_provinces(region_code)
        form.province_name.choices = [('', '-- Select Province --')] + [(p['code'], p['name']) for p in provinces]
        
        # Load existing province selection
        province_code = user.province_code
        if form.province_name.data:
            province_code = form.province_name.data
        
        # If we have a province, load cities/municipalities
        if province_code:
            cities = psgc_api.get_cities(province_code)
            municipalities = psgc_api.get_municipalities(province_code)
            city_choices = [('', '-- Select City/Municipality --')]
            
            # Add cities
            for city in cities:
                city_choices.append((city['code'], f"{city['name']} (City)"))
            
            # Add municipalities
            for municipality in municipalities:
                city_choices.append((municipality['code'], municipality['name']))
            
            form.city_name.choices = city_choices
            
            # Load existing city selection
            city_code = user.city_code
            if form.city_name.data:
                city_code = form.city_name.data
            
            # If we have a city, load barangays
            if city_code:
                barangays = []
                # Check if it's a city or municipality
                city_info = psgc_api.get_city_by_code(city_code)
                if city_info:
                    barangays = psgc_api.get_barangays(city_code=city_code)
                else:
                    barangays = psgc_api.get_barangays(municipality_code=city_code)
                
                form.barangay_name.choices = [('', '-- Select Barangay --')] + [(b['code'], b['name']) for b in barangays]
    else:
        # If no region selected, provide empty choices for dependent fields
        form.province_name.choices = [('', '-- Select Province --')]
        form.city_name.choices = [('', '-- Select City/Municipality --')]
        form.barangay_name.choices = [('', '-- Select Barangay --')]
    
    # Only on GET request, set the selected values
    if request.method == 'GET':
        if user.region_code:
            form.region_code.data = user.region_code
            form.region_name.data = user.region_code
            
        if user.province_code:
            form.province_code.data = user.province_code
            form.province_name.data = user.province_code
            
        if user.city_code:
            form.city_code.data = user.city_code
            form.city_name.data = user.city_code
            
        if user.barangay_code:
            form.barangay_code.data = user.barangay_code
            form.barangay_name.data = user.barangay_code
    
    if form.validate_on_submit():
        # Track changes to create an audit record
        changes = []
        if user.email != form.email.data:
            changes.append(f"Email: {user.email} → {form.email.data}")
        if user.firstname != form.firstname.data:
            changes.append(f"First Name: {user.firstname or 'None'} → {form.firstname.data or 'None'}")
        if user.lastname != form.lastname.data:
            changes.append(f"Last Name: {user.lastname or 'None'} → {form.lastname.data or 'None'}")
        if user.address_line != form.address_line.data:
            changes.append(f"Address Line: {user.address_line or 'None'} → {form.address_line.data or 'None'}")
        if user.phone != form.phone.data:
            changes.append(f"Phone: {user.phone or 'None'} → {form.phone.data or 'None'}")
        if user.status != form.status.data:
            changes.append(f"Status: {user.status} → {form.status.data}")
            
        # Address fields changes
        if form.region_name.data and form.region_name.data != '' and form.region_name.data != user.region_code:
            region = psgc_api.get_region_by_code(form.region_name.data)
            region_name = region['name'] if region else form.region_name.data
            changes.append(f"Region: {user.region_name or 'None'} → {region_name}")
            
        if form.province_name.data and form.province_name.data != '' and form.province_name.data != user.province_code:
            province = psgc_api.get_province_by_code(form.province_name.data)
            province_name = province['name'] if province else form.province_name.data
            changes.append(f"Province: {user.province_name or 'None'} → {province_name}")
            
        if form.city_name.data and form.city_name.data != '' and form.city_name.data != user.city_code:
            city = psgc_api.get_city_by_code(form.city_name.data)
            municipality = None if city else psgc_api.get_municipality_by_code(form.city_name.data)
            city_name = city['name'] if city else (municipality['name'] if municipality else form.city_name.data)
            changes.append(f"City/Municipality: {user.city_name or 'None'} → {city_name}")
            
        if form.barangay_name.data and form.barangay_name.data != '' and form.barangay_name.data != user.barangay_code:
            barangay = psgc_api.get_barangay_by_code(form.barangay_name.data)
            barangay_name = barangay['name'] if barangay else form.barangay_name.data
            changes.append(f"Barangay: {user.barangay_name or 'None'} → {barangay_name}")
            
        if user.postal_code != form.postal_code.data:
            changes.append(f"Postal Code: {user.postal_code or 'None'} → {form.postal_code.data or 'None'}")
        
        # Update user information
        user.email = form.email.data
        user.firstname = form.firstname.data
        user.lastname = form.lastname.data
        user.address_line = form.address_line.data
        user.postal_code = form.postal_code.data
        user.phone = form.phone.data
        user.status = form.status.data
        
        # Update address data with names and codes
        if form.region_name.data and form.region_name.data != '':
            user.region_code = form.region_name.data
            region = psgc_api.get_region_by_code(form.region_name.data)
            if region:
                user.region_name = region['name']
        else:
            user.region_code = None
            user.region_name = None
            
        if form.province_name.data and form.province_name.data != '':
            user.province_code = form.province_name.data
            province = psgc_api.get_province_by_code(form.province_name.data)
            if province:
                user.province_name = province['name']
        else:
            user.province_code = None
            user.province_name = None
            
        if form.city_name.data and form.city_name.data != '':
            user.city_code = form.city_name.data
            # Check if it's a city
            city = psgc_api.get_city_by_code(form.city_name.data)
            if city:
                user.city_name = city['name']
            else:
                # Must be a municipality
                municipality = psgc_api.get_municipality_by_code(form.city_name.data)
                if municipality:
                    user.city_name = municipality['name']
        else:
            user.city_code = None
            user.city_name = None
            
        if form.barangay_name.data and form.barangay_name.data != '':
            user.barangay_code = form.barangay_name.data
            barangay = psgc_api.get_barangay_by_code(form.barangay_name.data)
            if barangay:
                user.barangay_name = barangay['name']
        else:
            user.barangay_code = None
            user.barangay_name = None
        
        # Create audit record if there were changes
        if changes:
            # Create a transaction record for the user edit
            transaction = Transaction(
                transaction_id=str(uuid.uuid4()),
                sender_id=current_user.id,
                receiver_id=user.id,
                amount=0.0,  # Changed from None to 0.0
                transaction_type='user_edit',
                details="\n".join(changes),
                timestamp=datetime.datetime.utcnow()
            )
            db.session.add(transaction)
        
        db.session.commit()
        flash('User information updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('admin/edit_user.html', form=form, user=user)

# Apply rate limiting to API endpoints
@app.route('/api/provinces/<region_code>')
@login_required
@admin_required
@limiter.limit("30 per minute")
def get_provinces(region_code):
    provinces = psgc_api.get_provinces(region_code)
    return jsonify([{'code': p['code'], 'name': p['name']} for p in provinces])

@app.route('/api/cities/<province_code>')
@login_required
@admin_required
@limiter.limit("30 per minute")
def get_cities_and_municipalities(province_code):
    # Check if it's a city or municipality
    cities = psgc_api.get_cities(province_code)
    municipalities = psgc_api.get_municipalities(province_code)
    
    result = []
    
    # Add cities
    for city in cities:
        result.append({'code': city['code'], 'name': f"{city['name']} (City)"})
    
    # Add municipalities
    for municipality in municipalities:
        result.append({'code': municipality['code'], 'name': municipality['name']})
        
    return jsonify(result)

@app.route('/api/barangays/<city_code>')
@login_required
@admin_required
@limiter.limit("30 per minute")
def get_barangays(city_code):
    # Check if it's a city or municipality
    city_info = psgc_api.get_city_by_code(city_code)
    
    barangays = []
    if city_info:
        barangays = psgc_api.get_barangays(city_code=city_code)
    else:
        # Must be a municipality
        barangays = psgc_api.get_barangays(municipality_code=city_code)
        
    return jsonify([{'code': b['code'], 'name': b['name']} for b in barangays])

# Manager routes
@app.route('/manager')
@login_required
@manager_required
@limiter.limit("60 per hour")
def manager_dashboard():
    # Managers can see all admins and regular users, but not other managers
    admins = User.query.filter_by(is_admin=True, is_manager=False).all()
    regular_users = User.query.filter_by(is_admin=False, is_manager=False).all()
    
    return render_template('manager/dashboard.html', title='Manager Dashboard', admins=admins, regular_users=regular_users)

@app.route('/manager/create_admin', methods=['GET', 'POST'])
@login_required
@manager_required
@limiter.limit("10 per hour")
def create_admin():
    from forms import CreateAdminForm  # Import the new form
    
    form = CreateAdminForm()
    
    # Initialize or increment PIN attempt counter
    if 'manager_pin_attempts' not in session:
        session['manager_pin_attempts'] = 0

    if form.validate_on_submit():
        # Verify manager PIN first
        if not current_user.check_pin(form.pin.data):
            session['manager_pin_attempts'] += 1
            form.pin.errors.append("Incorrect PIN.")
            if session['manager_pin_attempts'] >= 3:
                flash('Too many incorrect PIN attempts. Please try again later.', 'danger')
                return redirect(url_for('manager_dashboard'))
            else:
                flash(f'Incorrect PIN. {3 - session["manager_pin_attempts"]} attempts remaining.', 'warning')
            return render_template('manager/create_admin.html', title='Create Admin Account', form=form)

        # Reset counter on successful PIN entry
        session['manager_pin_attempts'] = 0

        admin = User(username=form.username.data, email=form.email.data, status='active', is_admin=True, force_password_change=True)
        admin.set_password(form.password.data)
        db.session.add(admin)
        db.session.commit()
        flash('Admin account has been created successfully!', 'success')
        return redirect(url_for('admin_list'))
    
    return render_template('manager/create_admin.html', title='Create Admin Account', form=form)

@app.route('/manager/toggle_admin_with_pin', methods=['POST'])
@login_required
@manager_required
def toggle_admin_with_pin():
    # Create a form instance to handle CSRF validation
    from forms import ToggleAdminForm
    form = ToggleAdminForm()
    
    if not form.validate_on_submit():
        flash('Invalid form submission. Please try again.', 'danger')
        return redirect(request.referrer or url_for('manager_dashboard'))
    
    user_id = form.user_id.data
    action = form.action.data
    pin = form.pin.data
    
    if not user_id or not action or not pin:
        flash('Missing required information.', 'danger')
        return redirect(url_for('manager_dashboard'))
    
    # Initialize or increment PIN attempt counter
    if 'manager_pin_attempts' not in session:
        session['manager_pin_attempts'] = 0

    # Verify manager PIN
    if not current_user.check_pin(pin):
        session['manager_pin_attempts'] += 1
        if session['manager_pin_attempts'] >= 3:
            flash('Too many incorrect PIN attempts. Access temporarily restricted.', 'danger')
            return redirect(url_for('manager_dashboard'))
        else:
            flash(f'Incorrect PIN. {3 - session["manager_pin_attempts"]} attempts remaining.', 'warning')
        return redirect(request.referrer or url_for('manager_dashboard'))

    # Reset counter on successful PIN entry
    session['manager_pin_attempts'] = 0

    user = User.query.get_or_404(user_id)
    
    # Managers can only modify admins, not other managers
    if user.is_manager:
        flash('You cannot modify another manager account.', 'danger')
        return redirect(url_for('manager_dashboard'))
    
    if action == 'promote_admin':
        user.is_admin = True
        user.status = 'active'  # Set status to active when promoting to admin
        flash(f'User {user.username} has been promoted to admin.', 'success')
        
        # Create audit record
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            sender_id=current_user.id,
            receiver_id=user.id,
            amount=0.0,
            transaction_type='admin_promotion',
            details=f'Manager {current_user.username} promoted user {user.username} to admin',
            timestamp=datetime.datetime.utcnow()
        )
        db.session.add(transaction)
        
    elif action == 'remove_admin':
        user.is_admin = False
        flash(f'User {user.username} has been demoted from admin.', 'success')
        
        # Create audit record
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            sender_id=current_user.id,
            receiver_id=user.id,
            amount=0.0,
            transaction_type='admin_demotion',
            details=f'Manager {current_user.username} removed admin privileges from {user.username}',
            timestamp=datetime.datetime.utcnow()
        )
        db.session.add(transaction)
    
    db.session.commit()
    return redirect(request.referrer or url_for('manager_dashboard'))

@app.route('/manager/toggle_admin/<int:user_id>')
@login_required
@manager_required
def toggle_admin(user_id):
    # This route now just redirects to the appropriate list page
    # The actual toggle action is handled by toggle_admin_with_pin
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        return redirect(url_for('admin_list'))
    else:
        return redirect(url_for('user_list'))

@app.route('/manager/user_list')
@login_required
@manager_required
def user_list():
    from forms import ToggleAdminForm
    # Get all users except admins and managers
    users = User.query.filter(User.is_admin.is_(False), User.is_manager.is_(False)).all()
    form = ToggleAdminForm()  # Create form instance for CSRF
    return render_template('manager/user_list.html', title='All Users', users=users, form=form)

@app.route('/manager/admin_list')
@login_required
@manager_required
def admin_list():
    # Get all admin users except managers
    admins = User.query.filter(User.is_admin.is_(True), User.is_manager.is_(False)).all()
    return render_template('manager/admin_list.html', title='All Admin Users', admins=admins)

@app.route('/manager/admin_transactions')
@login_required
@manager_required
def admin_transactions():
    # Get all admin users except managers
    admins = User.query.filter(User.is_admin.is_(True), User.is_manager.is_(False)).all()
    
    # Get all transactions where any admin is either a sender or receiver
    admin_ids = [admin.id for admin in admins]
    
    # Base query
    query = Transaction.query.filter(
        db.or_(
            Transaction.sender_id.in_(admin_ids),
            Transaction.receiver_id.in_(admin_ids)
        )
    )
    
    # Apply search if provided
    search_term = request.args.get('search', '').strip()
    if search_term:
        # Build list of transaction IDs that match search criteria
        matching_transaction_ids = []
        
        # If search term is a number, check transaction ID
        if search_term.isdigit():
            matching_transaction_ids.extend([t.id for t in Transaction.query.filter(Transaction.id == int(search_term)).all()])
        
        # Search by sender username
        sender_matches = Transaction.query.join(
            User, Transaction.sender_id == User.id
        ).filter(
            User.username.ilike(f'%{search_term}%')
        ).all()
        matching_transaction_ids.extend([t.id for t in sender_matches])
        
        # Search by receiver username
        receiver_matches = Transaction.query.join(
            User, Transaction.receiver_id == User.id
        ).filter(
            User.username.ilike(f'%{search_term}%')
        ).all()
        matching_transaction_ids.extend([t.id for t in receiver_matches])
        
        # Search in transaction details
        detail_matches = Transaction.query.filter(
            Transaction.details.ilike(f'%{search_term}%')
        ).all()
        matching_transaction_ids.extend([t.id for t in detail_matches])
        
        # Filter original query to only include matching transactions
        if matching_transaction_ids:
            query = query.filter(Transaction.id.in_(set(matching_transaction_ids)))
        else:
            # If no matches, return empty result
            query = query.filter(Transaction.id == -1)  # Impossible condition to return empty set
    
    # Apply filters
    transaction_type = request.args.get('type')
    admin_role = request.args.get('role')
    admin_id = request.args.get('admin_id')
    
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    
    if admin_role == 'sender':
        query = query.filter(Transaction.sender_id.in_(admin_ids))
    elif admin_role == 'receiver':
        query = query.filter(Transaction.receiver_id.in_(admin_ids))
    
    if admin_id and admin_id.isdigit():
        admin_id = int(admin_id)
        query = query.filter(
            db.or_(
                Transaction.sender_id == admin_id,
                Transaction.receiver_id == admin_id
            )
        )
    
    # Get sorted results
    transactions = query.order_by(Transaction.timestamp.desc()).all()
    
    return render_template('manager/admin_transactions.html', 
                         title='Admin Transactions', 
                         transactions=transactions,
                         admins=admins)

@app.route('/manager/transfers')
@login_required
@manager_required
def manager_transfers():
    # Base query - only get transfer transactions
    query = Transaction.query.filter(Transaction.transaction_type == 'transfer')
    
    # Apply search if provided
    search_term = request.args.get('search', '').strip()
    if search_term:
        # Build list of transaction IDs that match search criteria
        matching_transaction_ids = []
        
        # If search term is a number, check transaction ID
        if search_term.isdigit():
            matching_transaction_ids.extend([t.id for t in Transaction.query.filter(Transaction.id == int(search_term)).all()])
        
        # Search by sender username
        sender_matches = Transaction.query.join(
            User, Transaction.sender_id == User.id
        ).filter(
            User.username.ilike(f'%{search_term}%')
        ).all()
        matching_transaction_ids.extend([t.id for t in sender_matches])
        
        # Search by receiver username
        receiver_matches = Transaction.query.join(
            User, Transaction.receiver_id == User.id
        ).filter(
            User.username.ilike(f'%{search_term}%')
        ).all()
        matching_transaction_ids.extend([t.id for t in receiver_matches])
        
        # Search by sender account number
        sender_account_matches = Transaction.query.join(
            User, Transaction.sender_id == User.id
        ).filter(
            User.account_number.ilike(f'%{search_term}%')
        ).all()
        matching_transaction_ids.extend([t.id for t in sender_account_matches])
        
        # Search by receiver account number
        receiver_account_matches = Transaction.query.join(
            User, Transaction.receiver_id == User.id
        ).filter(
            User.account_number.ilike(f'%{search_term}%')
        ).all()
        matching_transaction_ids.extend([t.id for t in receiver_account_matches])
        
        # Search by amount (if search term can be converted to float)
        try:
            amount = float(search_term)
            amount_matches = Transaction.query.filter(Transaction.amount == amount).all()
            matching_transaction_ids.extend([t.id for t in amount_matches])
        except ValueError:
            pass
            
        # Filter original query to only include matching transactions
        if matching_transaction_ids:
            query = query.filter(Transaction.id.in_(set(matching_transaction_ids)))
        else:
            # If no matches, return empty result
            query = query.filter(Transaction.id == -1)  # Impossible condition to return empty set
    
    # Apply date range filter if provided
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    if from_date:
        try:
            from_datetime = datetime.datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(Transaction.timestamp >= from_datetime)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_datetime = datetime.datetime.strptime(to_date, '%Y-%m-%d')
            # Add one day to include the entire end date
            to_datetime = to_datetime + datetime.timedelta(days=1)
            query = query.filter(Transaction.timestamp < to_datetime)
        except ValueError:
            pass
    
    # Apply amount range filter if provided
    min_amount = request.args.get('min_amount')
    max_amount = request.args.get('max_amount')
    
    if min_amount:
        try:
            min_amount_value = float(min_amount)
            query = query.filter(Transaction.amount >= min_amount_value)
        except ValueError:
            pass
    
    if max_amount:
        try:
            max_amount_value = float(max_amount)
            query = query.filter(Transaction.amount <= max_amount_value)
        except ValueError:
            pass
    
    # Apply user filter if provided
    user_id = request.args.get('user_id')
    user_role = request.args.get('user_role')
    
    if user_id and user_id.isdigit():
        user_id = int(user_id)
        if user_role == 'sender':
            query = query.filter(Transaction.sender_id == user_id)
        elif user_role == 'receiver':
            query = query.filter(Transaction.receiver_id == user_id)
        else:
            # Both sender and receiver
            query = query.filter(
                db.or_(
                    Transaction.sender_id == user_id,
                    Transaction.receiver_id == user_id
                )
            )
    
    # Get all users for filter dropdown
    users = User.query.all()
    
    # Get sorted results
    transactions = query.order_by(Transaction.timestamp.desc()).all()
    
    return render_template('manager/transfers.html', 
                         title='Transfer Transactions', 
                         transactions=transactions,
                         users=users)