# Pandora Pro - Plataforma de Assistentes Virtuais

Sistema de gerenciamento para criação e administração de assistentes virtuais personalizados.

## Requisitos

- Python 3.8+
- PostgreSQL 12+
- pip (gerenciador de pacotes Python)

## Configuração Inicial

1. Clone o repositório:
```bash
git clone [url-do-repositorio]
cd formulario-ai-pandora-pro
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
- Copie o arquivo `.env.example` para `.env`
- Edite o arquivo `.env` com suas configurações:
  - SECRET_KEY: Chave secreta para a aplicação Flask
  - DATABASE_URL: URL de conexão com o PostgreSQL

5. Inicialize o banco de dados:
```bash
flask db upgrade
```

6. Execute a aplicação:
```bash
flask run
```

## Estrutura do Projeto

```
formulario-ai-pandora-pro/
├── app.py              # Aplicação principal
├── requirements.txt    # Dependências do projeto
├── .env               # Variáveis de ambiente
├── static/            # Arquivos estáticos (CSS, JS, imagens)
├── templates/         # Templates HTML
└── migrations/        # Migrações do banco de dados
```

## Funcionalidades

- Cadastro e autenticação de usuários
- Criação de assistentes virtuais personalizados
- Painel administrativo para gestão de cadastros
- Interface responsiva e moderna
- Integração com PostgreSQL
- Sistema de aprovação de cadastros

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE.md para detalhes.
