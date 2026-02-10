# 🧪 Testando Webhook WhatsApp

## 📋 Estrutura do Payload

O Evolution API envia diferentes estruturas dependendo do tipo de mensagem. Aqui estão exemplos:

### 1. Mensagem de Texto Simples

```json
{
  "event": "messages.upsert",
  "data": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "ABC123"
    },
    "message": {
      "conversation": "Olá, gostaria de agendar uma reunião"
    }
  }
}
```

### 2. Mensagem de Texto Estendida (reply/quote)

```json
{
  "event": "messages.upsert",
  "data": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false
    },
    "message": {
      "extendedTextMessage": {
        "text": "Sim, confirmo o agendamento"
      }
    }
  }
}
```

## 🧪 Testar Webhook Localmente

### 1. Testar com cURL

```bash
# Carregar variáveis
source .env

# Enviar mensagem de teste
curl -X POST http://localhost:8000/ia/webhook_whatsapp/ \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net",
        "fromMe": false,
        "id": "TEST123"
      },
      "message": {
        "conversation": "Olá, quero saber sobre os serviços"
      }
    }
  }'
```

### 2. Testar com Python

```python
import requests
import json

url = "http://localhost:8000/ia/webhook_whatsapp/"

payload = {
    "event": "messages.upsert",
    "data": {
        "key": {
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": False,
            "id": "TEST123"
        },
        "message": {
            "conversation": "Olá, preciso de ajuda"
        }
    }
}

response = requests.post(url, json=payload)
print(response.json())
```

### 3. Ver Logs

```bash
# Ver logs em tempo real
tail -f logs/juriai.log

# Ver últimas 50 linhas
tail -n 50 logs/juriai.log

# Buscar por palavra
grep "webhook" logs/juriai.log
```

## 🔍 Debugging

### Payload não reconhecido?

Adicione log temporário na view:

```python
# No início da view webhook_whatsapp
print("=" * 60)
print("PAYLOAD RECEBIDO:")
print(json.dumps(data, indent=2))
print("=" * 60)
```

### Agente não responde?

Verifique:
1. Google Calendar configurado? `ls token.pickle`
2. OpenAI API Key válida? Teste no console
3. Base de conhecimento existe? Verifique `lancedb/`

### Mensagem não é enviada?

```python
# Testar wrapper diretamente
from usuarios.wrapper_evolutionapi import SendMessage

sender = SendMessage()
result = sender.send_text(
    instance_name='secretaria-juriai',
    phone='5511999999999',
    text='Teste'
)
print(result)
```

## 🌐 Webhook Público (Produção)

Para receber webhooks em produção, você precisa de uma URL pública.

### Opção 1: ngrok (teste rápido)

```bash
# Instalar ngrok
npm install -g ngrok

# Criar túnel
ngrok http 8000

# Use a URL fornecida no webhook
# Ex: https://abc123.ngrok.io/ia/webhook_whatsapp/
```

### Opção 2: Deploy em servidor

Configure no Evolution API:

```bash
curl -X POST http://localhost:8080/webhook/set/secretaria-juriai \
  -H "apikey: $EVOLUTION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://seu-dominio.com/ia/webhook_whatsapp/",
    "webhook_by_events": true,
    "events": ["MESSAGES_UPSERT"]
  }'
```

## 📊 Monitoramento

### Ver todas as conversas

```bash
python manage.py shell

>>> from ia.models_whatsapp import ConversaWhatsApp
>>> ConversaWhatsApp.objects.all()
```

### Ver mensagens de uma conversa

```bash
python manage.py shell

>>> from ia.models_whatsapp import ConversaWhatsApp, MensagemWhatsApp
>>> conversa = ConversaWhatsApp.objects.first()
>>> conversa.mensagens.all()
```

### Estatísticas

```bash
python manage.py shell

>>> from ia.models_whatsapp import ConversaWhatsApp, MensagemWhatsApp
>>> print(f"Total conversas: {ConversaWhatsApp.objects.count()}")
>>> print(f"Total mensagens: {MensagemWhatsApp.objects.count()}")
>>> print(f"Conversas ativas: {ConversaWhatsApp.objects.filter(ativo=True).count()}")
```

## 🚨 Troubleshooting

### Erro: "instance_name not found"

Configure o nome correto da instância:
```python
# Em ia/views.py, linha ~195
instance_name = 'secretaria-juriai'  # Use o nome da SUA instância
```

### Erro: "EVOLUTION_API_KEY not found"

```bash
# Verificar .env
cat .env | grep EVOLUTION_API_KEY

# Se não existir, adicione
echo "EVOLUTION_API_KEY=sua_chave_aqui" >> .env
```

### Webhook não recebe mensagens

1. Verificar se instância está conectada
2. Verificar se webhook está configurado
3. Verificar logs do Evolution API: `docker-compose logs -f`

## ✅ Checklist

Antes de testar:

- [ ] Django rodando (`python manage.py runserver`)
- [ ] Evolution API rodando (`docker-compose ps`)
- [ ] Instância WhatsApp conectada
- [ ] Webhook configurado na instância
- [ ] `.env` com todas as chaves
- [ ] Google Calendar autorizado

---

**Pronto para testar! Envie uma mensagem no WhatsApp e veja a mágica acontecer! 🎉**
