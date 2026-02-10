"""
Utilitários otimizados para processamento de OCR
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class OCROptimizado:
    """
    Classe para processamento otimizado de OCR usando RapidOCR
    """
    
    def __init__(self):
        """Inicializa o engine de OCR"""
        try:
            from rapidocr_onnxruntime import RapidOCR
            self.ocr = RapidOCR()
            logger.info("RapidOCR inicializado com sucesso")
        except ImportError:
            logger.warning("RapidOCR não disponível. Instale com: pip install rapidocr-onnxruntime")
            self.ocr = None
    
    def processar_imagem(self, image_path: str) -> str:
        """
        Processa uma imagem com RapidOCR
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            str: Texto extraído
        """
        if self.ocr is None:
            raise ImportError("RapidOCR não está instalado")
        
        try:
            result, elapse = self.ocr(image_path)
            
            if result is None:
                logger.warning(f"Nenhum texto encontrado em {image_path}")
                return ""
            
            # result é uma lista de [bbox, texto, confiança]
            textos = [item[1] for item in result]
            
            logger.info(f"OCR processado: {len(textos)} linhas de texto em {elapse:.2f}s")
            
            return "\n".join(textos)
            
        except Exception as e:
            logger.error(f"Erro ao processar imagem {image_path}: {str(e)}")
            raise
    
    def preprocessar_imagem(
        self, 
        image_path: str, 
        max_width: int = 2000,
        aplicar_threshold: bool = True,
        remover_ruido: bool = False
    ) -> str:
        """
        Pré-processa imagem antes do OCR para melhorar precisão e velocidade
        
        Args:
            image_path: Caminho para a imagem
            max_width: Largura máxima (redimensiona se maior)
            aplicar_threshold: Aplicar threshold binário
            remover_ruido: Aplicar remoção de ruído (mais lento)
            
        Returns:
            str: Texto extraído da imagem processada
        """
        try:
            # Carregar imagem
            img = cv2.imread(image_path)
            
            if img is None:
                raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
            
            # 1. Converter para escala de cinza
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 2. Redimensionar se muito grande (otimiza velocidade)
            height, width = gray.shape
            if width > max_width:
                scale = max_width / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                gray = cv2.resize(gray, (new_width, new_height))
                logger.debug(f"Imagem redimensionada de {width}x{height} para {new_width}x{new_height}")
            
            # 3. Aplicar threshold para melhorar contraste
            if aplicar_threshold:
                _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 4. Remover ruído (opcional, mais lento)
            if remover_ruido:
                gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # Salvar imagem processada temporariamente
            processed_path = image_path.replace('.', '_processed.')
            cv2.imwrite(processed_path, gray)
            
            # Processar com OCR
            resultado = self.processar_imagem(processed_path)
            
            # Limpar arquivo temporário
            import os
            try:
                os.remove(processed_path)
            except:
                pass
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao pré-processar imagem {image_path}: {str(e)}")
            # Fallback: tentar processar sem pré-processamento
            return self.processar_imagem(image_path)
    
    def processar_pdf_como_imagens(
        self, 
        pdf_path: str, 
        dpi: int = 150,
        preprocessar: bool = True
    ) -> str:
        """
        Converte PDF em imagens e processa com OCR
        
        Args:
            pdf_path: Caminho para o PDF
            dpi: Resolução para conversão (150-300, maior = melhor qualidade mas mais lento)
            preprocessar: Aplicar pré-processamento nas imagens
            
        Returns:
            str: Texto extraído de todas as páginas
        """
        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise ImportError("pdf2image não está instalado. Instale com: pip install pdf2image")
        
        import os
        
        try:
            logger.info(f"Convertendo PDF para imagens: {pdf_path} (DPI: {dpi})")
            
            # Converter PDF em imagens
            images = convert_from_path(pdf_path, dpi=dpi)
            
            logger.info(f"PDF convertido: {len(images)} páginas")
            
            textos = []
            for i, img in enumerate(images):
                # Salvar temporariamente
                temp_path = f"/tmp/page_{os.getpid()}_{i}.jpg"
                img.save(temp_path, 'JPEG', quality=85)
                
                # Processar OCR
                if preprocessar:
                    texto = self.preprocessar_imagem(temp_path)
                else:
                    texto = self.processar_imagem(temp_path)
                
                textos.append(f"--- Página {i+1} ---\n{texto}")
                
                # Limpar arquivo temporário
                try:
                    os.remove(temp_path)
                except:
                    pass
            
            logger.info(f"OCR concluído: {len(textos)} páginas processadas")
            
            return "\n\n".join(textos)
            
        except Exception as e:
            logger.error(f"Erro ao processar PDF {pdf_path}: {str(e)}")
            raise


class ImagePreprocessor:
    """
    Classe auxiliar para pré-processamento avançado de imagens
    """
    
    @staticmethod
    def remover_bordas(img: np.ndarray) -> np.ndarray:
        """Remove bordas pretas da imagem"""
        # Encontrar contornos
        _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Pegar maior contorno
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            return img[y:y+h, x:x+w]
        
        return img
    
    @staticmethod
    def corrigir_inclinacao(img: np.ndarray) -> np.ndarray:
        """Corrige inclinação do texto (deskew)"""
        # Detectar ângulo
        coords = np.column_stack(np.where(img > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = 90 + angle
        
        # Rotacionar
        if abs(angle) > 0.5:  # Só rotacionar se inclinação significativa
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, 
                                    borderMode=cv2.BORDER_REPLICATE)
            return rotated
        
        return img
    
    @staticmethod
    def aumentar_contraste(img: np.ndarray) -> np.ndarray:
        """Aumenta o contraste da imagem usando CLAHE"""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(img)


def processar_documento_completo(
    file_path: str,
    usar_cache: bool = True,
    preprocessar: bool = True,
    dpi: int = 150
) -> str:
    """
    Função de conveniência para processar qualquer documento (imagem ou PDF)
    
    Args:
        file_path: Caminho para o arquivo
        usar_cache: Usar cache se disponível
        preprocessar: Aplicar pré-processamento
        dpi: DPI para conversão de PDF
        
    Returns:
        str: Texto extraído
    """
    import hashlib
    import os
    from django.core.cache import cache
    
    # Verificar cache se habilitado
    if usar_cache:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        cache_key = f'ocr_{file_hash}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            logger.info(f"Resultado obtido do cache: {file_path}")
            return cached_result
    
    # Processar documento
    ocr = OCROptimizado()
    
    if file_path.lower().endswith('.pdf'):
        texto = ocr.processar_pdf_como_imagens(file_path, dpi=dpi, preprocessar=preprocessar)
    else:
        if preprocessar:
            texto = ocr.preprocessar_imagem(file_path)
        else:
            texto = ocr.processar_imagem(file_path)
    
    # Salvar em cache
    if usar_cache:
        cache.set(cache_key, texto, 60 * 60 * 24 * 7)  # 7 dias
    
    return texto
