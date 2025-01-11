from flask import Flask, render_template, url_for, redirect, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

# Database configuration
if os.environ.get('VERCEL_ENV') == 'production':
    # Use PostgreSQL in production (Vercel)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # Use SQLite for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, value):
        self.password_hash = value

class IARequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    target_audience = db.Column(db.Text, nullable=False)
    personality = db.Column(db.Text, nullable=False)
    achievements = db.Column(db.Text, nullable=False)
    products_services = db.Column(db.Text, nullable=False)
    initial_question = db.Column(db.Text, nullable=False)
    client_pain_points = db.Column(db.Text, nullable=False)
    solutions = db.Column(db.Text, nullable=False)
    differentials = db.Column(db.Text, nullable=False)
    purchase_process = db.Column(db.Text, nullable=False)
    common_objections = db.Column(db.Text, nullable=False)
    purchase_links = db.Column(db.Text, nullable=False)
    urgency = db.Column(db.Text, nullable=False)
    payment_methods = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserRegistrationForm(FlaskForm):
    company_name = StringField('Nome da Empresa', validators=[DataRequired(), Length(min=2, max=100)])
    name = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[
        DataRequired(),
        Length(min=6, message='A senha deve ter pelo menos 6 caracteres')
    ])
    confirm_password = PasswordField('Confirme a Senha', validators=[
        DataRequired(),
        EqualTo('password', message='As senhas devem ser iguais')
    ])

    def validate_email(self, email):
        user = Registration.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está cadastrado.')

class IACreationForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    name = StringField('Nome da IA', validators=[DataRequired(), Length(min=2, max=100)])
    specialization = StringField('Especialização', validators=[DataRequired(), Length(min=2, max=100)])
    target_audience = TextAreaField('Público-Alvo', validators=[DataRequired()])
    personality = TextAreaField('Personalidade da IA', validators=[DataRequired()])
    achievements = TextAreaField('Conquistas da Empresa', validators=[DataRequired()])
    products_services = TextAreaField('Produtos e Serviços', validators=[DataRequired()])
    initial_question = TextAreaField('Pergunta Inicial', validators=[DataRequired()])
    client_pain_points = TextAreaField('Dores dos Clientes', validators=[DataRequired()])
    solutions = TextAreaField('Soluções', validators=[DataRequired()])
    differentials = TextAreaField('Diferenciais', validators=[DataRequired()])
    purchase_process = TextAreaField('Processo de Compra', validators=[DataRequired()])
    common_objections = TextAreaField('Objeções Comuns', validators=[DataRequired()])
    purchase_links = TextAreaField('Links de Compra', validators=[DataRequired()])
    urgency = TextAreaField('Motivos de Urgência', validators=[DataRequired()])
    payment_methods = TextAreaField('Formas de Pagamento', validators=[DataRequired()])

class AdminLoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserRegistrationForm()
    if form.validate_on_submit():
        registration = Registration(
            company_name=form.company_name.data,
            name=form.name.data,
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(registration)
        try:
            db.session.commit()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('success'))
        except:
            db.session.rollback()
            flash('Erro ao realizar cadastro. Tente novamente.', 'danger')
    return render_template('register.html', form=form)

@app.route('/check_email', methods=['POST'])
def check_email():
    email = request.form.get('email')
    if not email:
        return jsonify({'valid': False, 'message': 'Email é obrigatório'})
    
    try:
        from email_validator import validate_email, EmailNotValidError
        validate_email(email)
    except EmailNotValidError:
        return jsonify({'valid': False, 'message': 'Email inválido'})
    
    return jsonify({'valid': True})

@app.route('/create_ia', methods=['GET', 'POST'])
def create_ia():
    form = IACreationForm()
    if request.args.get('email'):
        form.email.data = request.args.get('email')
    
    if form.validate_on_submit():
        ia_request = IARequest(
            email=form.email.data,
            name=form.name.data,
            specialization=form.specialization.data,
            target_audience=form.target_audience.data,
            personality=form.personality.data,
            achievements=form.achievements.data,
            products_services=form.products_services.data,
            initial_question=form.initial_question.data,
            client_pain_points=form.client_pain_points.data,
            solutions=form.solutions.data,
            differentials=form.differentials.data,
            purchase_process=form.purchase_process.data,
            common_objections=form.common_objections.data,
            purchase_links=form.purchase_links.data,
            urgency=form.urgency.data,
            payment_methods=form.payment_methods.data
        )
        db.session.add(ia_request)
        try:
            db.session.commit()
            flash('Solicitação de IA enviada com sucesso!', 'success')
            return redirect(url_for('success'))
        except:
            db.session.rollback()
            flash('Erro ao enviar solicitação. Tente novamente.', 'danger')
    return render_template('create_ia.html', form=form)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Email ou senha inválidos', 'danger')
    return render_template('admin/login.html', form=form)

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    registrations = Registration.query.order_by(Registration.created_at.desc()).all()
    ia_requests = IARequest.query.order_by(IARequest.created_at.desc()).all()
    return render_template('admin/dashboard.html', registrations=registrations, ia_requests=ia_requests)

@app.route('/admin/edit_registration/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_registration(id):
    registration = Registration.query.get_or_404(id)
    if request.method == 'POST':
        registration.company_name = request.form['company_name']
        registration.name = request.form['name']
        registration.email = request.form['email']
        try:
            db.session.commit()
            flash('Registro atualizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        except:
            db.session.rollback()
            flash('Erro ao atualizar registro', 'danger')
    return render_template('admin/edit_registration.html', registration=registration)

@app.route('/admin/delete_registration/<int:id>', methods=['POST'])
@login_required
def delete_registration(id):
    registration = Registration.query.get_or_404(id)
    
    # Primeiro exclui a IA associada (se existir)
    ia_request = IARequest.query.filter_by(email=registration.email).first()
    if ia_request:
        db.session.delete(ia_request)
    
    # Depois exclui o registro
    db.session.delete(registration)
    
    try:
        db.session.commit()
        flash('Registro excluído com sucesso!', 'success')
    except:
        db.session.rollback()
        flash('Erro ao excluir registro.', 'danger')
    
    return redirect(url_for('admin_dashboard'))

with app.app_context():
    db.create_all()
    # Criar usuário admin se não existir
    admin = User.query.filter_by(email='admin@pandorapro.com').first()
    if not admin:
        admin = User(
            email='admin@pandorapro.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
