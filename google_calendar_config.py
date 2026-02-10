"""
Script de configuração inicial do Google Calendar.
Execute este script para autenticar e gerar o token de acesso.
Lê as credenciais do arquivo .env
"""

import os
import json
import tempfile
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv
import pickle

# Carregar variáveis de ambiente
load_dotenv()

# Escopos necessários para o Google Calendar
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]


def _build_client_secret_json():
    """
    Constrói o JSON de credenciais a partir das variáveis de ambiente.
    Usa formato 'installed' (desktop app) para OAuth com localhost.
    """
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    project_id = os.getenv('GOOGLE_PROJECT_ID', '')
    auth_uri = os.getenv('GOOGLE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth')
    token_uri = os.getenv('GOOGLE_TOKEN_URI', 'https://oauth2.googleapis.com/token')
    cert_url = os.getenv('GOOGLE_AUTH_PROVIDER_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs')
    
    if not client_id or not client_secret:
        raise ValueError(
            "Credenciais Google não encontradas no .env!\n"
            "Configure GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET no arquivo .env"
        )
    
    return {
        "installed": {
            "client_id": client_id,
            "project_id": project_id,
            "auth_uri": auth_uri,
            "token_uri": token_uri,
            "auth_provider_x509_cert_url": cert_url,
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost"]
        }
    }


def setup_google_calendar():
    """
    Configura a autenticação do Google Calendar.
    Gera o token de acesso necessário para o agente funcionar.
    Lê credenciais do .env (não depende mais de arquivo JSON externo).
    """
    base_dir = Path(__file__).resolve().parent
    token_file = base_dir / "token.pickle"
    
    creds = None
    
    # Verificar se já existe token salvo
    if token_file.exists():
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # Se não há credenciais válidas, fazer login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Atualizando token expirado...")
            creds.refresh(Request())
        else:
            print("🔐 Iniciando processo de autenticação...")
            print("📁 Lendo credenciais do .env...")
            
            try:
                client_config = _build_client_secret_json()
            except ValueError as e:
                print(f"❌ Erro: {e}")
                return False
            
            # Criar arquivo temporário com as credenciais
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                json.dump(client_config, tmp)
                tmp_path = tmp.name
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    tmp_path, 
                    SCOPES
                )
                
                # Executar servidor local para OAuth
                creds = flow.run_local_server(port=0)
                print("✅ Autenticação concluída!")
            finally:
                # Remover arquivo temporário
                os.unlink(tmp_path)
        
        # Salvar token para uso futuro
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
        print(f"💾 Token salvo em: {token_file}")
    
    print("✅ Google Calendar configurado com sucesso!")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🗓️  Configuração do Google Calendar - JuriAI")
    print("=" * 60)
    print()
    
    success = setup_google_calendar()
    
    if success:
        print()
        print("=" * 60)
        print("✅ Configuração concluída!")
        print("=" * 60)
        print()
        print("Próximos passos:")
        print("1. O agente agora pode acessar seu Google Calendar")
        print("2. Execute o Django: python manage.py runserver")
        print("3. Inicie a Evolution API: docker-compose up -d")
        print("4. Configure a instância do WhatsApp")
    else:
        print()
        print("=" * 60)
        print("❌ Erro na configuração")
        print("=" * 60)
        print()
        print("Verifique:")
        print("1. Arquivo de credenciais existe")
        print("2. Credenciais estão corretas no Google Cloud Console")
        print("3. Google Calendar API está ativada")
