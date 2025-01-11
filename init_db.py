from app import app, db, User, generate_password_hash

def init_db():
    with app.app_context():
        # Criar todas as tabelas
        db.drop_all()  # Primeiro remove todas as tabelas existentes
        db.create_all()  # Cria todas as tabelas novamente
        
        # Criar admin padrão
        admin = User(
            email='admin@pandorapro.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin criado com sucesso!")
        print("Banco de dados PostgreSQL inicializado com sucesso!")

if __name__ == '__main__':
    init_db()
