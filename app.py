from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo

load_dotenv()

app = Flask(__name__)

# Configurações do Flask
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sua-chave-secreta-aqui')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://postgres:Marcus1911!!Marcus@77.37.41.106:5432/postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() == 'true'

# Inicialização das extensões
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'register'

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

class AssistantForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    specialization = StringField('Especialização', validators=[DataRequired()])
    target_audience = TextAreaField('Público-Alvo', validators=[DataRequired()])
    personality = TextAreaField('Personalidade', validators=[DataRequired()])
    achievements = TextAreaField('Conquistas', validators=[DataRequired()])
    products_services = TextAreaField('Produtos/Serviços', validators=[DataRequired()])
    initial_question = TextAreaField('Pergunta Inicial', validators=[DataRequired()])
    client_pain_points = TextAreaField('Pontos de Dor do Cliente', validators=[DataRequired()])
    solutions = TextAreaField('Soluções', validators=[DataRequired()])
    differentials = TextAreaField('Diferenciais', validators=[DataRequired()])
    purchase_process = TextAreaField('Processo de Compra', validators=[DataRequired()])
    common_objections = TextAreaField('Objecções Comuns', validators=[DataRequired()])
    purchase_links = TextAreaField('Links de Compra', validators=[DataRequired()])
    urgency = TextAreaField('Urgência', validators=[DataRequired()])
    payment_methods = TextAreaField('Métodos de Pagamento', validators=[DataRequired()])

# Models
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Registration(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assistant = db.relationship('Assistant', backref='registration', uselist=False)

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

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
    # Primeiro tenta carregar um admin
    admin = Admin.query.get(int(user_id))
    if admin:
        return admin
    # Se não encontrar admin, tenta carregar um registro normal
    return Registration.query.get(int(user_id))

# Rotas públicas
@app.route('/')
def index():
    return render_template('register.html', form=RegistrationForm())

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Verificar se o email já existe
        existing_user = Registration.query.filter_by(email=form.email.data).first()
        if existing_user:
            # Se o usuário já existe, verificar a senha
            if check_password_hash(existing_user.password_hash, form.password.data):
                login_user(existing_user)
                return redirect(url_for('registration_success'))
            else:
                flash('Email já cadastrado. Por favor, use sua senha cadastrada.', 'danger')
                return render_template('register.html', form=form)
            
        # Se é um novo usuário, criar o registro
        registration = Registration(
            company_name=form.company_name.data,
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            password=form.password.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(registration)
        db.session.commit()
        
        # Fazer login automático após o registro
        login_user(registration)
        
        return redirect(url_for('registration_success'))
    return render_template('register.html', form=form)

@app.route('/ia-formulario', methods=['GET', 'POST'])
@login_required
def ia_formulario():
    if not isinstance(current_user, Registration):
        return redirect(url_for('index'))
        
    form = AssistantForm()
    if form.validate_on_submit():
        assistant = Assistant(
            registration_id=current_user.id,
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
        db.session.add(assistant)
        db.session.commit()
        return redirect(url_for('success'))
        
    return render_template('assistant_form.html', form=form)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/registration-success')
@login_required
def registration_success():
    return render_template('registration_success.html')

# Rotas administrativas
@app.route('/adm')
def admin_redirect():
    return redirect(url_for('admin_login'))

@app.route('/adm/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(email=email).first()
        
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Email ou senha inválidos', 'danger')
    
    return render_template('admin/login.html')

@app.route('/adm/dashboard')
@login_required
def admin_dashboard():
    if not isinstance(current_user, Admin):
        logout_user()
        return redirect(url_for('admin_login'))
        
    # Buscar todos os registros e suas senhas originais
    registrations = Registration.query.order_by(Registration.created_at.desc()).all()
    for reg in registrations:
        # Armazenar a senha sem hash no atributo temporário
        reg.plain_password = reg.password
    
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

@app.route('/adm/edit/<int:registration_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_registration(registration_id):
    if not isinstance(current_user, Admin):
        return redirect(url_for('admin_login'))
        
    registration = Registration.query.get_or_404(registration_id)
    
    if request.method == 'POST':
        registration.company_name = request.form.get('company_name')
        registration.name = request.form.get('name')
        registration.email = request.form.get('email')
        registration.phone = request.form.get('phone')
        
        # Se uma nova senha foi fornecida, atualize-a
        new_password = request.form.get('password')
        if new_password:
            registration.password = new_password
            registration.password_hash = generate_password_hash(new_password)
            
        db.session.commit()
        flash('Registro atualizado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_registration.html', registration=registration)

# Rota temporária para inicializar o banco de dados (remover após usar)
@app.route('/init-db')
def init_database():
    # Verificar se a requisição vem da Vercel
    if not request.headers.get('x-vercel-deployment-url'):
        return 'Acesso não autorizado', 403
        
    try:
        db.drop_all()
        db.create_all()
        
        # Criar admin padrão
        if not Admin.query.filter_by(email='admin@pandorapro.com').first():
            admin = Admin(
                email='admin@pandorapro.com',
                password=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
        
        return 'Banco de dados inicializado com sucesso!'
    except Exception as e:
        return f'Erro: {str(e)}', 500

if __name__ == '__main__':
    with app.app_context():
        # Força a recriação do banco de dados
        db.drop_all()
        db.create_all()
        
        # Criar admin padrão se não existir
        if not Admin.query.filter_by(email='admin@pandorapro.com').first():
            admin = Admin(
                email='admin@pandorapro.com',
                password=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
