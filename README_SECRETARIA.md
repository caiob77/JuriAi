# 🤖 Secretária Virtual - JuriAI

## 📋 Descrição

Agente de IA para atendimento ao cliente via WhatsApp com capacidades de:
- 💬 Atendimento automático
- 📅 Agendamento no Google Calendar
- 📚 Consulta à base de conhecimento (RAG)
- 🧠 Memória de conversas

## 🚀 Configuração

### 1. Credenciais do Google Calendar

**✅ JÁ CONFIGURADO!**

As credenciais são lidas automaticamente do arquivo `.env`:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_PROJECT_ID`
- `GOOGLE_CLIENT_SECRET_JSON` (JSON completo)

**Para autorizar o acesso:**

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar configuração (abrirá navegador para autorizar)
python google_calendar_config.py
```

Isso irá:
1. Abrir seu navegador
2. Pedir para fazer login no Google
3. Autorizar acesso ao Calendar
4. Salvar token automaticamente

### 2. Variáveis de Ambiente

Adicione no arquivo `.env`:

```bash
# Evolution API
EVOLUTION_API_KEY=sua_chave_api_super_secreta
EVOLUTION_API_URL=http://localhost:8080
WEBHOOK_URL=http://localhost:8000/ia/webhook_whatsapp

# OpenAI (já configurado)
OPENAI_API_KEY=sua_openai_key
```

### 3. Iniciar Evolution API

```bash
# Iniciar com Docker Compose
docker-compose up -d

# Verificar logs
docker-compose logs -f evolution-api
```

A API estará disponível em: `http://localhost:8080`

### 4. Criar Instância WhatsApp

Acesse a documentação da Evolution API ou use:

```bash
# Criar instância
curl -X POST http://localhost:8080/instance/create \
  -H "apikey: sua_chave_api" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "secretaria-juriai",
    "qrcode": true
  }'
```

## 📚 Base de Conhecimento

O agente utiliza RAG (Retrieval Augmented Generation) com LanceDB.

### Adicionar Documentos

```python
from ia.agente_secretaria import SecretariaAI

# Adicionar documentos à base
knowledge = SecretariaAI.knowledge
knowledge.load_documents([
    "caminho/para/documento1.pdf",
    "caminho/para/documento2.txt"
])
```

## 🎯 Funcionalidades

### Horário de Agendamento
- ⏰ **Apenas entre 13h e 18h**
- 📅 Duração padrão: 1 hora
- ✅ Verificação automática de disponibilidade

### Atendimento
- Consulta à base de conhecimento
- Respostas personalizadas
- Memória de 5 conversas anteriores
- Contexto temporal (data/hora atual)

## 🔧 Uso no Código

```python
from ia.agente_secretaria import SecretariaAI

# Criar agente
agent = SecretariaAI.build_agent(session_id=123)

# Processar mensagem simples
resposta = SecretariaAI.processar_mensagem(
    mensagem="Olá, gostaria de agendar uma reunião",
    session_id=123
)
print(resposta)
```

## 📡 Webhook WhatsApp

O webhook está configurado em:
- URL: `/ia/webhook_whatsapp`
- Método: POST
- Recebe mensagens do WhatsApp
- Processa com o agente
- Envia resposta automaticamente

## 🐛 Troubleshooting

### Erro de autenticação Google
- Verifique se o arquivo de credenciais está na raiz
- Execute a primeira vez localmente para autorizar

### Evolution API não conecta
- Verifique se o Docker está rodando: `docker ps`
- Verifique logs: `docker-compose logs evolution-api`
- Teste conexão: `curl http://localhost:8080`

### Mensagens não chegam
- Verifique webhook configurado no Evolution API
- Confira logs do Django
- Teste endpoint: `/ia/webhook_whatsapp`

## 📖 Documentação

- [Evolution API Docs](https://doc.evolution-api.com/)
- [Agno Documentation](https://docs.agno.io/)
- [Google Calendar API](https://developers.google.com/calendar)

## 🎓 Exemplos de Conversas

**Cliente**: "Olá, gostaria de saber sobre os serviços"
**Bot**: *Consulta RAG e responde sobre serviços*

**Cliente**: "Quero agendar uma reunião amanhã às 15h"
**Bot**: *Verifica calendário e agenda se disponível*

**Cliente**: "Qual o preço da consultoria?"
**Bot**: *Consulta base de conhecimento e informa*
