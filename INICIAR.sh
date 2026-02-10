#!/bin/bash

echo "=================================="
echo "🚀 Iniciando JuriAI Secretária"
echo "=================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Verificar ambiente virtual
echo -e "${YELLOW}[1/5]${NC} Verificando ambiente virtual..."
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Ambiente virtual não encontrado!${NC}"
    echo "Execute: python3 -m venv venv"
    exit 1
fi
source venv/bin/activate
echo -e "${GREEN}✅ Ambiente virtual ativado${NC}"
echo ""

# 2. Verificar Google Calendar
echo -e "${YELLOW}[2/5]${NC} Verificando Google Calendar..."
if [ ! -f "token.pickle" ]; then
    echo -e "${YELLOW}⚠️  Token do Google não encontrado${NC}"
    echo "Execute: python google_calendar_config.py"
    read -p "Deseja configurar agora? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        python google_calendar_config.py
    fi
else
    echo -e "${GREEN}✅ Google Calendar configurado${NC}"
fi
echo ""

# 3. Iniciar Evolution API
echo -e "${YELLOW}[3/5]${NC} Iniciando Evolution API (WhatsApp)..."
docker-compose up -d
sleep 3
if docker ps | grep -q evolution_api; then
    echo -e "${GREEN}✅ Evolution API rodando${NC}"
    echo "   Acesse: http://localhost:8080"
else
    echo -e "${RED}❌ Erro ao iniciar Evolution API${NC}"
fi
echo ""

# 4. Executar migrações
echo -e "${YELLOW}[4/5]${NC} Executando migrações do banco..."
python manage.py migrate --noinput
echo -e "${GREEN}✅ Migrações concluídas${NC}"
echo ""

# 5. Iniciar Django
echo -e "${YELLOW}[5/5]${NC} Iniciando servidor Django..."
echo ""
echo "=================================="
echo -e "${GREEN}✅ Sistema iniciado com sucesso!${NC}"
echo "=================================="
echo ""
echo "📱 Evolution API: http://localhost:8080"
echo "🌐 Django Admin: http://localhost:8000/admin"
echo "🤖 API Webhook: http://localhost:8000/ia/webhook_whatsapp"
echo ""
echo "Para parar: Ctrl+C e depois: docker-compose down"
echo ""

python manage.py runserver
