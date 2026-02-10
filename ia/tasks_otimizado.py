"""
Versão otimizada das tasks com processamento paralelo e cache
"""
from usuarios.models import Documentos
from django.shortcuts import get_object_or_404
from .agents import JuriAI
import logging
import time
import hashlib
from django.core.cache import cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
import os

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


def ocr_paralelo_multipaginas(instance_id, num_workers: int = 4):
    """
    Versão com processamento paralelo de páginas
    Ideal para PDFs com muitas páginas
    """
    from pdf2image import convert_from_path
    from .ocr_utils import OCROptimizado
    
    start_time = time.time()
    
    try:
        documentos = get_object_or_404(Documentos, id=instance_id)
        
        logger.info(f"Iniciando OCR paralelo para documento {instance_id}: {documentos.arquivo.name}")
        
        # Gerar hash do arquivo para cache
        with open(documentos.arquivo.path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        cache_key = f'ocr_paralelo_{file_hash}'
        
        # Verificar cache
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Resultado paralelo obtido do cache para documento {instance_id}")
            documentos.content = cached_result
            documentos.save()
            return
        
        # Converter PDF em imagens
        logger.info(f"Convertendo PDF em imagens...")
        images = convert_from_path(documentos.arquivo.path, dpi=150)
        logger.info(f"{len(images)} páginas para processar")
        
        # Criar instância OCR
        ocr = OCROptimizado()
        
        def processar_pagina(img_data):
            idx, img = img_data
            temp_path = f"/tmp/doc_{instance_id}_page_{idx}_{os.getpid()}.jpg"
            img.save(temp_path, 'JPEG', quality=85)
            texto = ocr.preprocessar_imagem(temp_path)
            try:
                os.remove(temp_path)
            except:
                pass
            return idx, texto
        
        # Processar páginas em paralelo
        resultados = {}
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {executor.submit(processar_pagina, (i, img)): i 
                      for i, img in enumerate(images)}
            
            for future in as_completed(futures):
                try:
                    idx, texto = future.result()
                    resultados[idx] = texto
                    logger.info(f"Página {idx+1}/{len(images)} processada")
                except Exception as e:
                    logger.error(f"Erro ao processar página: {str(e)}")
        
        # Ordenar e juntar textos
        texto_final = "\n\n".join([
            f"--- Página {i+1} ---\n{resultados[i]}" 
            for i in sorted(resultados.keys())
        ])
        
        # Salvar em cache por 7 dias
        cache.set(cache_key, texto_final, 60 * 60 * 24 * 7)
        
        documentos.content = texto_final
        documentos.save()
        
        elapsed = time.time() - start_time
        logger.info(f"OCR paralelo concluído para documento {instance_id} em {elapsed:.2f}s ({len(images)} páginas)")
        
    except Exception as e:
        logger.error(f"Erro no OCR paralelo do documento {instance_id}: {str(e)}", exc_info=True)
        raise


def rag_documentos(instance_id):
    """
    Mantido como está, mas com logging adicional
    """
    start_time = time.time()
    
    try:
        documentos = get_object_or_404(Documentos, id=instance_id)
        
        logger.info(f"Iniciando indexação RAG para documento {instance_id}")
        
        JuriAI.knowledge.insert(
            name=documentos.arquivo.name,
            text_content=documentos.content,
            metadata={
                "cliente_id": documentos.cliente.id,
                "name": documentos.arquivo.name,
            },
        )
        
        elapsed = time.time() - start_time
        logger.info(f"RAG concluído para documento {instance_id} em {elapsed:.2f}s")
        
    except Exception as e:
        logger.error(f"Erro na indexação RAG do documento {instance_id}: {str(e)}", exc_info=True)
        raise


def rag_dados_empresa(instance_id):
    """
    Placeholder mantido
    """
    pass
