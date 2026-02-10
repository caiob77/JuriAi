"""
Wrapper para Evolution API - Envio de mensagens WhatsApp
"""

import requests
import os
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()


class SendMessage:
    """
    Classe para enviar mensagens via Evolution API
    """
    
    def __init__(self):
        self.base_url = os.getenv('EVOLUTION_API_URL', 'http://localhost:8080')
        self.api_key = os.getenv('EVOLUTION_API_KEY')
        
        if not self.api_key:
            raise ValueError("EVOLUTION_API_KEY não configurada no .env")
    
    def send_message(self, instance_name: str, data: dict) -> dict:
        """
        Envia uma mensagem de texto via WhatsApp
        
        Args:
            instance_name: Nome da instância (ex: 'secretaria-juriai')
            data: Dicionário com dados da mensagem
                {
                    "number": "5511999999999",
                    "textMessage": {
                        "text": "Mensagem a ser enviada"
                    }
                }
        
        Returns:
            dict: Resposta da API
        """
        url = f"{self.base_url}/message/sendText/{instance_name}"
        
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar mensagem: {e}")
            return {'error': str(e)}
    
    def send_text(self, instance_name: str, phone: str, text: str) -> dict:
        """
        Método simplificado para enviar texto
        
        Args:
            instance_name: Nome da instância
            phone: Número do telefone (ex: '5511999999999')
            text: Texto da mensagem
            
        Returns:
            dict: Resposta da API
        """
        data = {
            "number": phone,
            "textMessage": {
                "text": text
            }
        }
        return self.send_message(instance_name, data)
    
    def send_media(self, instance_name: str, phone: str, media_url: str, caption: str = "") -> dict:
        """
        Envia mídia (imagem, vídeo, documento)
        
        Args:
            instance_name: Nome da instância
            phone: Número do telefone
            media_url: URL da mídia
            caption: Legenda (opcional)
            
        Returns:
            dict: Resposta da API
        """
        url = f"{self.base_url}/message/sendMedia/{instance_name}"
        
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
        
        data = {
            "number": phone,
            "mediaMessage": {
                "mediaUrl": media_url,
                "caption": caption
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar mídia: {e}")
            return {'error': str(e)}


class EvolutionAPI:
    """
    Classe para gerenciar instâncias da Evolution API
    """
    
    def __init__(self):
        self.base_url = os.getenv('EVOLUTION_API_URL', 'http://localhost:8080')
        self.api_key = os.getenv('EVOLUTION_API_KEY')
        
        if not self.api_key:
            raise ValueError("EVOLUTION_API_KEY não configurada no .env")
    
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """
        Faz requisição para a API
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            return {'error': str(e)}
    
    def create_instance(self, instance_name: str, qrcode: bool = True) -> dict:
        """
        Cria uma nova instância
        """
        data = {
            "instanceName": instance_name,
            "qrcode": qrcode
        }
        return self._make_request('POST', '/instance/create', data)
    
    def get_instances(self) -> dict:
        """
        Lista todas as instâncias
        """
        return self._make_request('GET', '/instance/fetchInstances')
    
    def connect_instance(self, instance_name: str) -> dict:
        """
        Conecta uma instância (retorna QR Code)
        """
        return self._make_request('GET', f'/instance/connect/{instance_name}')
    
    def delete_instance(self, instance_name: str) -> dict:
        """
        Deleta uma instância
        """
        return self._make_request('DELETE', f'/instance/delete/{instance_name}')
    
    def get_instance_status(self, instance_name: str) -> dict:
        """
        Verifica status da instância
        """
        return self._make_request('GET', f'/instance/connectionState/{instance_name}')
