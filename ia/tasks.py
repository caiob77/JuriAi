import asyncio
import logging

from usuarios.models import Documentos
from django.shortcuts import get_object_or_404

# NÃO importar agno/agents no topo - causa TypeError no Python 3.8
# Usar lazy imports dentro de cada função

logger = logging.getLogger(__name__)


def ocr_and_markdown_file_otimizado(instance_id):
    """
    Versão otimizada com cache e logging
    """
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
    
    start_time = time.time()
    
    try:
        documentos = get_object_or_404(Documentos, id=instance_id)
        
        logger.info(f"Iniciando OCR para documento {instance_id}: {documentos.arquivo.name}")
        
        # Gerar hash do arquivo para cache
        with open(documentos.arquivo.path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        cache_key = f'ocr_{file_hash}'
        
        # Verificar cache
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Resultado obtido do cache para documento {instance_id}")
            documentos.content = cached_result
            documentos.save()
            return
        
        # Configuração otimizada do Docling
        pipeline_options = PdfFormatOption(
            backend=PyPdfiumDocumentBackend,
            do_ocr=True,
            do_table_structure=True,
            images_scale=1.5,  # Reduzido para melhor performance
            generate_page_images=False,
            generate_picture_images=False,
        )
        
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: pipeline_options,
            }
        )
        
        result = converter.convert(documentos.arquivo.path)
        doc = result.document
        texto = doc.export_to_markdown()
        
        # Salvar em cache por 7 dias
        cache.set(cache_key, texto, 60 * 60 * 24 * 7)
        
        documentos.content = texto
        documentos.save()
        
        elapsed = time.time() - start_time
        logger.info(f"OCR concluído para documento {instance_id} em {elapsed:.2f}s")
        
    except Exception as e:
        logger.error(f"Erro no OCR do documento {instance_id}: {str(e)}", exc_info=True)
        raise

def ocr_and_markdown_file_rapidocr(instance_id):
    """
    Versão usando RapidOCR (mais rápido)
    """
    from .ocr_utils import OCROptimizado
    
    start_time = time.time()
    
    try:
        documentos = get_object_or_404(Documentos, id=instance_id)
        
        logger.info(f"Iniciando RapidOCR para documento {instance_id}: {documentos.arquivo.name}")
        
        # Gerar hash do arquivo para cache
        with open(documentos.arquivo.path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        cache_key = f'rapidocr_{file_hash}'
        
        # Verificar cache
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Resultado RapidOCR obtido do cache para documento {instance_id}")
            documentos.content = cached_result
            documentos.save()
            return
        
        # Processar com RapidOCR
        ocr = OCROptimizado()
        
        if documentos.arquivo.path.lower().endswith('.pdf'):
            texto = ocr.processar_pdf_como_imagens(
                documentos.arquivo.path, 
                dpi=150,  # 150 para velocidade, 300 para qualidade
                preprocessar=True
            )
        else:
            texto = ocr.preprocessar_imagem(documentos.arquivo.path)
        
        # Salvar em cache por 7 dias
        cache.set(cache_key, texto, 60 * 60 * 24 * 7)
        
        documentos.content = texto
        documentos.save()
        
        elapsed = time.time() - start_time
        logger.info(f"RapidOCR concluído para documento {instance_id} em {elapsed:.2f}s")
        
    except Exception as e:
        logger.error(f"Erro no RapidOCR do documento {instance_id}: {str(e)}", exc_info=True)
        raise


def rag_documentos(instance_id):
    from .agents import JuriAI  # lazy import
    
    documentos = get_object_or_404(Documentos, id=instance_id)
    JuriAI.knowledge.insert(
        name=documentos.arquivo.name,
        text_content=documentos.content,
        metadata={
            "cliente_id": documentos.cliente.id,
            "name": documentos.arquivo.name,
        },
    )

def rag_dados_empresa(instance_id):
    ...


def processar_mensagem_whatsapp(phone, message, session_id):
    """
    Task para processar mensagens do WhatsApp via Django-Q.
    Roda no cluster com event loop próprio, sem bloquear o webhook.
    """
    # Garantir event loop na thread do worker
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    try:
        from .agente_secretaria import SecretariaAI
        from usuarios.wrapper_evolutionapi import SendMessage

        logger.info(f"[WhatsApp] Processando mensagem de {phone}: {message}")

        # Construir agente e processar mensagem
        agent = SecretariaAI.build_agent(session_id=session_id)
        response = agent.run(message)

        logger.info(f"[WhatsApp] Resposta do agente para {phone}: {response.content}")

        # Enviar resposta de volta para o WhatsApp
        instance_name = 'secretaria-juriai'
        sender = SendMessage()
        send_result = sender.send_text(
            instance_name=instance_name,
            phone=phone,
            text=response.content
        )

        logger.info(f"[WhatsApp] Mensagem enviada para {phone}: {send_result}")

        return {
            'status': 'success',
            'phone': phone,
            'response': response.content,
            'send_result': send_result
        }

    except Exception as e:
        logger.error(f"[WhatsApp] Erro ao processar mensagem de {phone}: {e}", exc_info=True)

        # Tentar enviar mensagem de erro ao usuário
        try:
            from usuarios.wrapper_evolutionapi import SendMessage
            sender = SendMessage()
            sender.send_text(
                instance_name='secretaria-juriai',
                phone=phone,
                text="Desculpe, tive um problema ao processar sua mensagem. Por favor, tente novamente em alguns instantes."
            )
        except Exception:
            pass

        return {'status': 'error', 'phone': phone, 'error': str(e)}