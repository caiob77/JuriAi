"""
Agente Secretária Virtual - Implementado com LangChain (compatível com Python 3.8)
"""
import datetime
import os
import json
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

logger = logging.getLogger(__name__)

# Armazenamento simples de histórico de conversas em memória
_conversation_history = {}


class SecretariaAI:
    """
    Agente de Secretária Virtual usando LangChain.
    Compatível com Python 3.8.
    """
    
    llm = ChatOpenAI(model_name='gpt-4o-mini', temperature=0.7)
    
    SYSTEM_PROMPT = """Você é um assistente virtual de secretaria especializado em atendimento ao cliente e agendamento de reuniões.
Atue como vendedor da empresa, você deve vender os produtos e serviços da empresa para o cliente.
Sempre que vir alguma dúvida sobre a empresa, responda as perguntas do cliente direcionando para algum produto e com foco em agendar uma reunião com o advogado, deixe a pessoa escolher entre os possíveis dias e horários disponíveis.

SUAS CAPACIDADES:

1. ATENDIMENTO AO CLIENTE:
   - Seja cordial, profissional e prestativo em todas as interações.
   - Responda perguntas sobre produtos, serviços, preços e políticas da empresa.
   - Forneça informações claras e objetivas.
   - Se não souber algo, ofereça-se para buscar mais informações ou conectar o cliente com o setor adequado.

2. AGENDAMENTO DE REUNIÕES:
   - IMPORTANTE: Reuniões devem ser agendadas APENAS entre 13h e 18h (horário local).
   - Se o cliente solicitar um horário fora desse intervalo, explique que os agendamentos são apenas entre 13h e 18h e ofereça alternativas dentro desse horário.
   - Ao sugerir agendamento, inclua:
     * Data e horário (entre 13h e 18h)
     * Duração sugerida (padrão: 1 hora)
   - Confirme o agendamento com o cliente antes de finalizar.

DIRETRIZES DE AGENDAMENTO:
- Horário permitido: 13:00 às 18:00 (horário local)
- Se não houver horário disponível no dia solicitado, ofereça alternativas nos próximos dias
- Confirme todas as informações antes de finalizar

FLUXO DE ATENDIMENTO:
1. Cumprimente o cliente de forma cordial
2. Identifique a necessidade (informação ou agendamento)
3. Para informações: responda de forma clara e direta
4. Para agendamento: sugira horários entre 13h-18h
5. Confirme todas as informações antes de finalizar

IMPORTANTE:
- Responda de forma concisa e objetiva (mensagens de WhatsApp devem ser curtas)
- Use emojis com moderação para tornar a conversa mais amigável
- Não use markdown ou formatação complexa (é WhatsApp)
- Quebre mensagens longas em parágrafos curtos

Data e hora atual: {data_hora}
"""
    
    @classmethod
    def _get_prompt(cls):
        return ChatPromptTemplate.from_messages([
            ('system', cls.SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name='history'),
            ('human', '{message}'),
        ])
    
    @classmethod
    def _get_history(cls, session_id):
        """Retorna o histórico de conversas para uma sessão (máx 10 mensagens)."""
        if session_id not in _conversation_history:
            _conversation_history[session_id] = []
        return _conversation_history[session_id][-10:]  # últimas 10 mensagens
    
    @classmethod
    def _save_to_history(cls, session_id, human_msg, ai_msg):
        """Salva mensagens no histórico."""
        if session_id not in _conversation_history:
            _conversation_history[session_id] = []
        _conversation_history[session_id].append(HumanMessage(content=human_msg))
        _conversation_history[session_id].append(AIMessage(content=ai_msg))
        
        # Limitar a 20 mensagens (10 trocas)
        if len(_conversation_history[session_id]) > 20:
            _conversation_history[session_id] = _conversation_history[session_id][-20:]
    
    @classmethod
    def build_agent(cls, knowledge_filters=None, session_id=1):
        """
        Retorna uma instância configurada do agente.
        Mantém interface compatível com o código existente.
        """
        return _SecretariaAgentRunner(cls, session_id)
    
    @classmethod
    def processar_mensagem(cls, mensagem, session_id=1, knowledge_filters=None):
        """
        Processa uma mensagem e retorna a resposta.
        """
        agent = cls.build_agent(session_id=session_id)
        response = agent.run(mensagem)
        return response.content


class _SecretariaAgentRunner:
    """
    Wrapper que mantém a interface compatível com o código que chama agent.run()
    """
    
    def __init__(self, agent_cls, session_id):
        self.agent_cls = agent_cls
        self.session_id = session_id
    
    def run(self, message):
        """Processa a mensagem e retorna um objeto com .content"""
        prompt = self.agent_cls._get_prompt()
        chain = prompt | self.agent_cls.llm
        
        history = self.agent_cls._get_history(self.session_id)
        
        now = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        
        response = chain.invoke({
            'message': message,
            'history': history,
            'data_hora': now,
        })
        
        # Salvar no histórico
        self.agent_cls._save_to_history(self.session_id, message, response.content)
        
        logger.info(f"[SecretariaAI] session={self.session_id} | resposta={response.content[:100]}...")
        
        return response