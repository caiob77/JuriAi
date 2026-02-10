from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.messages import constants
from usuarios.models import Cliente, Documentos
from .models import Pergunta, ContextRag, AnaliseJurisprudencia
import time
import json
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Importações do agno movidas para dentro das funções para evitar erro de import em Python 3.8
# from .agents import JuriAI
# from typing import Iterator
# from agno.agent import RunOutputEvent, RunEvent

@csrf_exempt
def chat(request, id):
    cliente = Cliente.objects.get(id=id)
    if request.method == 'GET':
        return render(request, 'chat.html', {'cliente': cliente})
    elif request.method == 'POST':
        pergunta = request.POST.get('pergunta')
        pergunta_model = Pergunta(pergunta=pergunta, cliente=cliente)
        pergunta_model.save()
        return JsonResponse({'id': pergunta_model.id})

def ver_referencias(request, id):
    """
    View para exibir as referências e contextos usados em uma pergunta específica.
    """
    pergunta = get_object_or_404(Pergunta, id=id)
    contextos = ContextRag.objects.filter(pergunta=pergunta)
    
    return render(request, 'ver_referencias.html', {
        'pergunta': pergunta,
        'contextos': contextos
    })

@csrf_exempt
def stream_resposta(request):
    # Importar apenas quando a função for chamada (lazy import)
    from .agents import JuriAI
    from typing import Iterator
    from agno.agent import RunOutputEvent, RunEvent
    from .models import ContextRag
    
    id_pergunta = request.POST.get('id_pergunta')

    pergunta = get_object_or_404(Pergunta, id=id_pergunta)

    def gerar_resposta():
        
        agent = JuriAI.build_agent(knowledge_filters={'cliente_id': pergunta.cliente.id})
        
        stream: Iterator[RunOutputEvent] = agent.run(pergunta.pergunta, stream=True, stream_events=True)
        for chunk in stream:
            if chunk.event == RunEvent.run_content:
                yield str(chunk.content)
            elif chunk.event == RunEvent.tool_call_completed:
                context = ContextRag(
                    content=chunk.tool.result, 
                    tool_name=chunk.tool.tool_name, 
                    tool_args=chunk.tool.tool_args, 
                    pergunta=pergunta
                )
                context.save()

    response = StreamingHttpResponse(
        gerar_resposta(),
        content_type='text/plain; charset=utf-8'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    
    return response

def analise_jurisprudencia(request, id):
    """
    View para exibir análise jurídica de documentos.
    """
    documento = get_object_or_404(Documentos, id=id)
    analise = AnaliseJurisprudencia.objects.filter(documento=documento).first()
    
    return render(request, 'analise_jurisprudencia.html', {
        'documento': documento,
        'analise': analise
    })

@csrf_exempt
def processar_analise(request, id):
    """
    View para processar análise jurídica de documentos usando IA.
    """
    if request.method != 'POST':
        messages.add_message(request, constants.ERROR, 'Método não permitido.')
        return redirect('analise_jurisprudencia', id=id)
    
    try:
        documento = get_object_or_404(Documentos, id=id)
        start_time = time.time()
        
        # Importar agente (lazy import para evitar erros)
        from .agente_langchain import JurisprudenciaAI
        
        agent = JurisprudenciaAI()
        response = agent.run(documento.content)
        
        processing_time = int(time.time() - start_time)
        
        indice = response.indice_risco
        if indice <= 30:
            classificacao = "Baixo"
        elif indice <= 60:
            classificacao = "Médio"
        elif indice <= 80:
            classificacao = "Alto"
        else:
            classificacao = "Crítico"
        
        analise, created = AnaliseJurisprudencia.objects.update_or_create(
            documento=documento,
            defaults={
                'indice_risco': indice,
                'classificacao': classificacao,
                'erros_coerencia': response.erros_coerencia,
                'riscos_juridicos': response.riscos_juridicos,
                'problemas_formatacao': response.problemas_formatacao,
                'red_flags': response.red_flags,
                'tempo_processamento': processing_time
            }
        )
        
        if created:
            messages.add_message(request, constants.SUCCESS, 'Análise realizada e salva com sucesso!')
        else:
            messages.add_message(request, constants.SUCCESS, 'Análise atualizada com sucesso!')
        
        return redirect('analise_jurisprudencia', id=id)
    except Exception as e:
        messages.add_message(request, constants.ERROR, f'Erro ao processar análise: {str(e)}')
        return redirect('analise_jurisprudencia', id=id)

@csrf_exempt
def qrcode_whatsapp(request):
    """
    View para exibir o QR Code de conexão do WhatsApp.
    Busca o QR Code da Evolution API e renderiza para o usuário escanear.
    """
    from usuarios.wrapper_evolutionapi import EvolutionAPI
    
    instance_name = 'secretaria-juriai'
    api = EvolutionAPI()
    
    context = {
        'instance_name': instance_name,
        'connected': False,
        'qrcode_base64': None,
        'error': None,
        'status': None,
    }
    
    try:
        # Verificar status da conexão
        status_data = api.get_instance_status(instance_name)
        state = status_data.get('instance', {}).get('state', status_data.get('state', ''))
        context['status'] = state
        
        if state == 'open':
            # Já está conectado
            context['connected'] = True
        else:
            # Buscar QR Code para conexão
            qr_data = api.connect_instance(instance_name)
            
            if 'base64' in qr_data:
                context['qrcode_base64'] = qr_data['base64']
            elif 'code' in qr_data:
                context['qrcode_base64'] = qr_data.get('base64')
            else:
                context['error'] = 'Não foi possível gerar o QR Code. Tente novamente.'
                
    except Exception as e:
        logger.error(f"Erro ao buscar QR Code: {e}", exc_info=True)
        context['error'] = f'Erro ao conectar com a Evolution API: {str(e)}'
    
    return render(request, 'qrcode_whatsapp.html', context)


@csrf_exempt
def webhook_whatsapp(request):
    """
    Webhook para receber mensagens do WhatsApp via Evolution API.
    Extrai os dados da mensagem e despacha para o Django-Q cluster processar.
    Responde imediatamente ao webhook (não bloqueia).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        # Parse do JSON recebido
        data = json.loads(request.body)
        
        # Log para debug
        logger.info(f"Webhook recebido: {json.dumps(data, indent=2)}")
        
        # Extrair informações da mensagem
        try:
            # Número do telefone
            phone = data.get('data', {}).get('key', {}).get('remoteJid', '').split('@')[0]
            
            # Tentar diferentes estruturas de mensagem
            message_data = data.get('data', {}).get('message', {})
            
            # Texto pode vir em diferentes formatos
            message = None
            if 'extendedTextMessage' in message_data:
                message = message_data.get('extendedTextMessage', {}).get('text')
            elif 'conversation' in message_data:
                message = message_data.get('conversation')
            elif 'text' in message_data:
                message = message_data.get('text')
            
            # Validar dados extraídos
            if not phone or not message:
                logger.warning(f"Dados incompletos: phone={phone}, message={message}")
                return JsonResponse({
                    'status': 'ignored',
                    'reason': 'Dados incompletos ou mensagem não textual'
                })
            
            # Ignorar mensagens do próprio bot
            if data.get('data', {}).get('key', {}).get('fromMe'):
                return JsonResponse({'status': 'ignored', 'reason': 'Mensagem do bot'})
            
            logger.info(f"Mensagem de {phone}: {message}")
            
            # Calcular session_id a partir do telefone
            session_id = int(phone) if phone.isdigit() else hash(phone)
            
            # Despachar para o Django-Q cluster (não bloqueia o webhook)
            from django_q.tasks import async_task
            
            task_id = async_task(
                'ia.tasks.processar_mensagem_whatsapp',
                phone,
                message,
                session_id,
                task_name=f'whatsapp_{phone}',
            )
            
            logger.info(f"Task despachada para o cluster: {task_id} (phone={phone})")
            
            return JsonResponse({
                'status': 'queued',
                'phone': phone,
                'task_id': task_id,
                'message': 'Mensagem recebida e sendo processada'
            })
            
        except KeyError as e:
            logger.error(f"Erro ao extrair dados: {e}")
            logger.error(f"Estrutura do payload: {json.dumps(data, indent=2)}")
            return JsonResponse({
                'status': 'error',
                'error': f'Estrutura de dados inválida: {str(e)}',
                'payload_received': data
            }, status=400)
    
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {e}")
        return JsonResponse({'status': 'error', 'error': 'JSON inválido'}, status=400)
    
    except Exception as e:
        logger.error(f"Erro no webhook: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)
