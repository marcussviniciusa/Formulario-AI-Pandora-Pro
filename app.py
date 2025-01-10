from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Forms
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    company_name = StringField('Nome da Empresa', validators=[DataRequired()])
    name = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Telefone', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[
        DataRequired(),
        Length(min=6, message='A senha deve ter pelo menos 6 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Senha', validators=[
        DataRequired(),
        EqualTo('password', message='As senhas devem ser iguais')
    ])

# Models
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assistant = db.relationship('Assistant', backref='registration', uselist=False)

class Assistant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(200))
    target_audience = db.Column(db.Text)
    personality = db.Column(db.Text)
    achievements = db.Column(db.Text)
    products_services = db.Column(db.Text)
    initial_question = db.Column(db.Text)
    client_pain_points = db.Column(db.Text)
    solutions = db.Column(db.Text)
    differentials = db.Column(db.Text)
    purchase_process = db.Column(db.Text)
    common_objections = db.Column(db.Text)
    purchase_links = db.Column(db.Text)
    urgency = db.Column(db.Text)
    payment_methods = db.Column(db.Text)
    registration_id = db.Column(db.Integer, db.ForeignKey('registration.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Rotas públicas
@app.route('/')
def index():
    return render_template('register.html', form=RegistrationForm())

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Verificar se o email já existe
        if Registration.query.filter_by(email=form.email.data).first():
            flash('Este email já está cadastrado.', 'danger')
            return render_template('register.html', form=form)
            
        registration = Registration(
            company_name=form.company_name.data,
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(registration)
        db.session.commit()
        
        # Fazer login automático após o registro
        login_user(registration)
        
        return redirect(url_for('assistant_form', registration_id=registration.id))
    return render_template('register.html', form=form)

@app.route('/assistant/<int:registration_id>', methods=['GET', 'POST'])
def assistant_form(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    if request.method == 'POST':
        assistant = Assistant(
            name=request.form.get('name'),
            specialization=request.form.get('specialization'),
            target_audience=request.form.get('target_audience'),
            personality=request.form.get('personality'),
            achievements=request.form.get('achievements'),
            products_services=request.form.get('products_services'),
            initial_question=request.form.get('initial_question'),
            client_pain_points=request.form.get('client_pain_points'),
            solutions=request.form.get('solutions'),
            differentials=request.form.get('differentials'),
            purchase_process=request.form.get('purchase_process'),
            common_objections=request.form.get('common_objections'),
            purchase_links=request.form.get('purchase_links'),
            urgency=request.form.get('urgency'),
            payment_methods=request.form.get('payment_methods'),
            registration_id=registration_id
        )
        db.session.add(assistant)
        db.session.commit()
        flash('Assistente virtual configurado com sucesso!', 'success')
        return redirect(url_for('success'))
    return render_template('assistant_form.html', registration=registration)

@app.route('/success')
def success():
    return render_template('success.html')

# Rotas administrativas
@app.route('/adm', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin and check_password_hash(admin.password_hash, form.password.data):
            login_user(admin)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Email ou senha inválidos.', 'danger')
    
    return render_template('admin/login.html', form=form)

@app.route('/adm/dashboard')
@login_required
def admin_dashboard():
    registrations = Registration.query.all()
    return render_template('admin/dashboard.html', registrations=registrations)

@app.route('/adm/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/adm/assistant/<int:registration_id>')
@login_required
def admin_view_assistant(registration_id):
    assistant = Assistant.query.filter_by(registration_id=registration_id).first()
    if assistant:
        return jsonify({
            'assistant': {
                'name': assistant.name,
                'specialization': assistant.specialization,
                'target_audience': assistant.target_audience,
                'personality': assistant.personality,
                'achievements': assistant.achievements,
                'products_services': assistant.products_services,
                'initial_question': assistant.initial_question,
                'client_pain_points': assistant.client_pain_points,
                'solutions': assistant.solutions,
                'differentials': assistant.differentials,
                'purchase_process': assistant.purchase_process,
                'common_objections': assistant.common_objections,
                'purchase_links': assistant.purchase_links,
                'urgency': assistant.urgency,
                'payment_methods': assistant.payment_methods
            }
        })
    return jsonify({'assistant': None})

@app.route('/adm/registration/<int:registration_id>', methods=['DELETE'])
@login_required
def admin_delete_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    if registration.assistant:
        db.session.delete(registration.assistant)
    db.session.delete(registration)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/adm/registration/<int:registration_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    form = RegistrationForm(obj=registration)
    
    if form.validate_on_submit():
        registration.company_name = form.company_name.data
        registration.name = form.name.data
        registration.email = form.email.data
        registration.phone = form.phone.data
        db.session.commit()
        flash('Registro atualizado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_registration.html', form=form, registration=registration)

if __name__ == '__main__':
    with app.app_context():
        # Força a recriação do banco de dados
        db.drop_all()
        db.create_all()
        
        # Criar admin padrão se não existir
        if not Admin.query.filter_by(email='admin@pandorapro.com').first():
            admin = Admin(
                email='admin@pandorapro.com',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
