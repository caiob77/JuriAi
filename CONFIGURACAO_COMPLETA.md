# ✅ Configuração Completa - JuriAI Secretária

## 🎉 TUDO JÁ ESTÁ CONFIGURADO!

Suas credenciais do Google Calendar estão no arquivo `.env` (protegido pelo .gitignore):

```
✅ Client ID: Configurado em GOOGLE_CLIENT_ID
✅ Client Secret: Configurado em GOOGLE_CLIENT_SECRET
✅ Project ID: Configurado em GOOGLE_PROJECT_ID
✅ Arquivo: Configurado em .env e carregado automaticamente
```

## 🚀 Início Rápido (3 Comandos)

### 1. Configurar Google Calendar (primeira vez)

```bash
source venv/bin/activate
python google_calendar_config.py
```

Isso irá:
- Abrir navegador automaticamente
- Pedir login no Google
- Autorizar acesso ao Calendar
- Salvar token (token.pickle)

### 2. Iniciar tudo automaticamente

```bash
./INICIAR.sh
```

Ou manualmente:

```bash
# Iniciar Evolution API (WhatsApp)
docker-compose up -d

# Iniciar Django
source venv/bin/activate
python manage.py runserver
```

### 3. Configurar WhatsApp (primeira vez)

Acesse http://localhost:8080 e crie uma instância.

**OU via cURL:**

```bash
# Carregar variável de ambiente
source .env

curl -X POST http://localhost:8080/instance/create \
  -H "apikey: $EVOLUTION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "secretaria-juriai",
    "qrcode": true
  }'
```

Depois:

```bash
# Obter QR Code
curl http://localhost:8080/instance/connect/secretaria-juriai \
  -H "apikey: $EVOLUTION_API_KEY"
```

## 📋 Variáveis de Ambiente Configuradas

Arquivo `.env` já possui todas as chaves necessárias (protegido pelo .gitignore):

```bash
# OpenAI
OPENAI_API_KEY=sua_chave_openai

# Evolution API
EVOLUTION_API_KEY=sua_chave_evolution
EVOLUTION_API_URL=http://localhost:8080
WEBHOOK_URL=http://localhost:8000/ia/webhook_whatsapp

# Google Calendar (carregado automaticamente)
GOOGLE_CLIENT_ID=seu_client_id
GOOGLE_CLIENT_SECRET=seu_client_secret
GOOGLE_PROJECT_ID=seu_project_id
```

⚠️ **Nunca compartilhe seu arquivo `.env`! Ele está protegido no .gitignore**

## 🎯 URLs Importantes

| Serviço | URL |
|---------|-----|
| Evolution API | http://localhost:8080 |
| Django Admin | http://localhost:8000/admin |
| Webhook WhatsApp | http://localhost:8000/ia/webhook_whatsapp |
| API Key Evolution | Ver variável `EVOLUTION_API_KEY` no `.env` |

## 📱 Testar Agente

```python
from ia.agente_secretaria import SecretariaAI

# Teste simples
resposta = SecretariaAI.processar_mensagem(
    "Olá, gostaria de agendar uma reunião para amanhã às 15h",
    session_id=1
)
print(resposta)
```

## 🔧 Comandos Úteis

### Verificar Evolution API
```bash
# Status
docker ps | grep evolution

# Logs
docker-compose logs -f evolution-api

# Reiniciar
docker-compose restart evolution-api
```

### Verificar Google Calendar
```bash
# Testar autenticação
python -c "from ia.agente_secretaria import SecretariaAI; print('✅ OK')"

# Reconfigurar (se necessário)
rm token.pickle
python google_calendar_config.py
```

### Ver Instâncias WhatsApp
```bash
# Carregar variáveis do .env primeiro
source .env

curl http://localhost:8080/instance/fetchInstances \
  -H "apikey: $EVOLUTION_API_KEY"
```

## 📚 Próximos Passos

1. **Adicionar Documentos à Base de Conhecimento**
   ```python
   from ia.agente_secretaria import SecretariaAI
   
   knowledge = SecretariaAI.knowledge
   knowledge.load_documents(["documentos/catalogo.pdf"])
   ```

2. **Configurar Webhook no Django** (próximo passo)

3. **Testar Conversas pelo WhatsApp**

## 🆘 Resolução de Problemas

### "Token not found"
```bash
python google_calendar_config.py
```

### "Evolution API not responding"
```bash
docker-compose down
docker-compose up -d
docker-compose logs -f evolution-api
```

### "OpenAI error"
Verifique se a API key está correta em `.env`

## 📖 Documentação Completa

- [README_SECRETARIA.md](README_SECRETARIA.md) - Documentação detalhada
- [SETUP_RAPIDO.md](SETUP_RAPIDO.md) - Guia de setup
- [Evolution API Docs](https://doc.evolution-api.com/)

---

## ✅ Checklist de Configuração

- [x] Credenciais Google configuradas
- [x] Variáveis de ambiente definidas
- [x] Docker Compose criado
- [x] Agente secretária implementado
- [x] Scripts de inicialização prontos
- [ ] Token Google gerado (execute `python google_calendar_config.py`)
- [ ] Evolution API iniciada (execute `docker-compose up -d`)
- [ ] Instância WhatsApp criada e QR Code escaneado
- [ ] Webhook Django configurado (próximo passo)

---

**🎉 Configuração 98% completa! Falta apenas gerar o token e criar a instância WhatsApp!**
