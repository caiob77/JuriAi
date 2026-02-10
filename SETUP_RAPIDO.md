# 🚀 Setup Rápido - Secretária WhatsApp

## 📋 Pré-requisitos

- ✅ Python 3.8+
- ✅ Docker e Docker Compose
- ✅ Conta Google (para Calendar)
- ✅ OpenAI API Key

## ⚡ Configuração em 5 Passos

### 1️⃣ Instalar Dependências

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar pacotes
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client tzlocal
```

### 2️⃣ Configurar Google Calendar

```bash
# Executar script de configuração
python google_calendar_config.py
```

Isso irá:
- ✅ Abrir navegador automaticamente
- ✅ Pedir login no Google
- ✅ Autorizar acesso ao Calendar
- ✅ Salvar token (token.pickle)

### 3️⃣ Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar e adicionar suas chaves reais
nano .env  # ou vim, code, etc
```

Configure no `.env`:
- `OPENAI_API_KEY` - Sua chave da OpenAI
- `EVOLUTION_API_KEY` - Crie uma chave segura aleatória
- `GOOGLE_CLIENT_ID` - Do Google Cloud Console
- `GOOGLE_CLIENT_SECRET` - Do Google Cloud Console
- `GOOGLE_PROJECT_ID` - Do Google Cloud Console

⚠️ **Nunca compartilhe o arquivo `.env`!**

### 4️⃣ Iniciar Evolution API (WhatsApp)

```bash
# Iniciar container Docker
docker-compose up -d

# Verificar se está rodando
docker ps

# Ver logs (opcional)
docker-compose logs -f evolution-api
```

Acesse: http://localhost:8080 para verificar

### 5️⃣ Criar Instância WhatsApp

**Opção A: Via cURL**

```bash
# Carregar variáveis do .env
source .env

curl -X POST http://localhost:8080/instance/create \
  -H "apikey: $EVOLUTION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "secretaria-juriai",
    "qrcode": true,
    "webhook": "http://localhost:8000/ia/webhook_whatsapp"
  }'
```

**Opção B: Via Interface Web**

1. Acesse http://localhost:8080
2. Crie nova instância
3. Escaneie QR Code com WhatsApp
4. Configure webhook: `http://localhost:8000/ia/webhook_whatsapp`

## ✅ Verificação

### Testar Google Calendar

```bash
python -c "from ia.agente_secretaria import SecretariaAI; print('✅ Google Calendar OK')"
```

### Testar Evolution API

```bash
# Carregar variáveis do .env
source .env

curl http://localhost:8080/instance/fetchInstances \
  -H "apikey: $EVOLUTION_API_KEY"
```

### Testar Agente

```python
from ia.agente_secretaria import SecretariaAI

# Processar mensagem de teste
resposta = SecretariaAI.processar_mensagem(
    "Olá, gostaria de informações sobre os serviços",
    session_id=1
)
print(resposta)
```

## 🎯 Próximos Passos

1. ✅ Adicionar documentos à base de conhecimento
2. ✅ Configurar webhook no Django
3. ✅ Testar conversas pelo WhatsApp
4. ✅ Monitorar logs

## 🐛 Problemas Comuns

### Erro: "credentials not found"
```bash
# Execute novamente a configuração
python google_calendar_config.py
```

### Erro: Evolution API não conecta
```bash
# Verificar se Docker está rodando
docker ps

# Reiniciar container
docker-compose restart
```

### Erro: "OpenAI API key not found"
```bash
# Verificar .env
cat .env | grep OPENAI_API_KEY
```

## 📞 Suporte

- Evolution API: https://doc.evolution-api.com/
- Agno Framework: https://docs.agno.io/
- Google Calendar API: https://developers.google.com/calendar

---

**🎉 Configuração concluída! Sua secretária virtual está pronta!**
