# 🤖 JuriAI - Sistema Jurídico com IA

Sistema completo de gestão jurídica com inteligência artificial, incluindo chat, análise de documentos e secretária virtual via WhatsApp.

## 🚀 Funcionalidades

- 💬 **Chat com IA** - Assistente jurídico com RAG
- 📄 **Análise de Documentos** - Análise automática de petições e contratos
- 📱 **Secretária WhatsApp** - Atendimento automatizado com agendamento
- 📅 **Google Calendar** - Integração para agendamentos
- 🔍 **Base de Conhecimento** - RAG para consultas especializadas

## 📋 Pré-requisitos

- Python 3.8+
- Docker e Docker Compose
- Conta Google (para Calendar)
- OpenAI API Key
- Git

## ⚡ Instalação Rápida

### 1. Clone o Repositório

```bash
git clone <seu-repositorio>
cd juriAi
```

### 2. Configure o Ambiente

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configure Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas chaves (NUNCA COMMITE O .env!)
nano .env
```

Preencha as seguintes variáveis no `.env`:
- `OPENAI_API_KEY` - Chave da OpenAI
- `EVOLUTION_API_KEY` - Chave para Evolution API (crie uma aleatória segura)
- `GOOGLE_CLIENT_ID` - Do Google Cloud Console
- `GOOGLE_CLIENT_SECRET` - Do Google Cloud Console
- `GOOGLE_PROJECT_ID` - Do Google Cloud Console

### 4. Execute a Configuração

```bash
# Configurar Google Calendar (primeira vez)
python google_calendar_config.py

# Executar migrações
python manage.py migrate

# Criar superusuário (opcional)
python manage.py createsuperuser
```

### 5. Inicie os Serviços

```bash
# Opção A: Script automatizado
./INICIAR.sh

# Opção B: Manual
docker-compose up -d  # Evolution API
python manage.py runserver  # Django
```

## 📚 Documentação

- **[CONFIGURACAO_COMPLETA.md](CONFIGURACAO_COMPLETA.md)** - Guia completo de configuração
- **[SETUP_RAPIDO.md](SETUP_RAPIDO.md)** - Setup em 5 minutos
- **[README_SECRETARIA.md](README_SECRETARIA.md)** - Secretária WhatsApp
- **[SEGURANCA.md](SEGURANCA.md)** - ⚠️ **IMPORTANTE**: Guia de segurança

## 🔒 Segurança

⚠️ **ATENÇÃO**: Este projeto usa APIs que requerem chaves de acesso.

**NUNCA commite:**
- `.env` - Variáveis de ambiente
- `client_secret_*.json` - Credenciais Google
- `token.pickle` - Tokens de autenticação

Leia o **[SEGURANCA.md](SEGURANCA.md)** antes de fazer qualquer commit!

## 🛠️ Tecnologias

- **Backend**: Django 4.2
- **IA**: OpenAI GPT-4, Agno Framework
- **WhatsApp**: Evolution API
- **Banco de Dados**: SQLite (dev), PostgreSQL (prod)
- **Vector DB**: LanceDB
- **Calendar**: Google Calendar API
- **Frontend**: TailwindCSS

## 📱 Módulos

### 1. Chat Jurídico
- Assistente com base de conhecimento
- Histórico de conversas
- Referências às fontes consultadas

### 2. Análise de Documentos
- Análise automática de petições
- Identificação de riscos jurídicos
- Índice de risco (0-100)
- Sugestões de melhorias

### 3. Secretária WhatsApp
- Atendimento automático 24/7
- Agendamento via Google Calendar
- Consulta à base de conhecimento
- Memória de conversas

## 🚀 Deploy

### Heroku

```bash
# Login
heroku login

# Criar app
heroku create juriai-app

# Configurar variáveis
heroku config:set OPENAI_API_KEY=sua_chave
heroku config:set EVOLUTION_API_KEY=sua_chave

# Deploy
git push heroku main
```

### Docker

```bash
# Build
docker build -t juriai .

# Run
docker run -p 8000:8000 --env-file .env juriai
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

**⚠️ IMPORTANTE**: Nunca commite chaves de API! Verifique o `.gitignore`.

## 📄 Licença

Este projeto está sob a licença MIT para uso privado. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

- **Issues**: Use GitHub Issues para reportar bugs
- **Documentação**: Veja pasta `/docs`
- **Email**: seu-email@dominio.com

## 📊 Status do Projeto

🟢 Em desenvolvimento ativo

## ✅ Checklist de Segurança

Antes de fazer qualquer commit:

- [ ] Verificou se `.env` não está sendo commitado
- [ ] Removeu qualquer chave hardcoded do código
- [ ] Atualizou `.env.example` se necessário
- [ ] Não há credenciais Google no código
- [ ] Rodou `git status` e conferiu os arquivos

## 🔗 Links Úteis

- [OpenAI API](https://platform.openai.com/)
- [Evolution API](https://doc.evolution-api.com/)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Agno Framework](https://docs.agno.io/)
- [Django Documentation](https://docs.djangoproject.com/)

---

**Desenvolvido com ❤️ para advocacia moderna**
