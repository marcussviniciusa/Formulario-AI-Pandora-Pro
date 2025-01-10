import os
from app import app, db, Admin, generate_password_hash

def init_db():
    with app.app_context():
        # Criar todas as tabelas
        db.drop_all()  # Primeiro remove todas as tabelas existentes
        db.create_all()  # Cria todas as tabelas novamente
        
        # Criar admin padrão
        if not Admin.query.filter_by(email='admin@pandorapro.com').first():
            admin = Admin(
                email='admin@pandorapro.com',
                password=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin criado com sucesso!")
        
        print("Banco de dados inicializado com sucesso!")

if __name__ == '__main__':
    init_db()
