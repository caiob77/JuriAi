import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Documentos
from django_q.tasks import Chain
from ia.tasks_otimizado import (
    ocr_and_markdown_file_otimizado,
    ocr_and_markdown_file_rapidocr,
    ocr_paralelo_multipaginas,
    rag_documentos,
)

# Extensões tratadas como imagem → RapidOCR (mais rápido)
EXTENSOES_IMAGEM = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}
# A partir de quantas páginas usar OCR paralelo
LIMIAR_PAGINAS_PDF_PARALELO = 20


def _escolher_task_ocr(instance):
    """
    Decide qual task de OCR usar: otimizado (Docling), RapidOCR ou paralelo.
    Retorna (função, lista_args, dict_kwargs) para chain.append(fn, *args, **kwargs).
    """
    path = instance.arquivo.path
    ext = os.path.splitext(path)[1].lower()

    if ext in EXTENSOES_IMAGEM:
        return ocr_and_markdown_file_rapidocr, [instance.id], {}

    if ext == '.pdf':
        try:
            from pdf2image import pdfinfo_from_path
            info = pdfinfo_from_path(path)
            num_paginas = int(info.get('Pages', 1))
            if num_paginas > LIMIAR_PAGINAS_PDF_PARALELO:
                return ocr_paralelo_multipaginas, [instance.id, 4], {}
        except Exception:
            pass
        return ocr_and_markdown_file_otimizado, [instance.id], {}

    # Fallback (outros tipos): Docling otimizado
    return ocr_and_markdown_file_otimizado, [instance.id], {}


@receiver(post_save, sender=Documentos)
def post_save_documentos(sender, instance, created, **kwargs):
    if created:
        chain = Chain()
        fn, args, kws = _escolher_task_ocr(instance)
        chain.append(fn, *args, **kws)
        chain.append(rag_documentos, instance.id)
        chain.run() 