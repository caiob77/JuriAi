from django.db import models

from usuarios.models import Cliente, Documentos

class Pergunta(models.Model):
    pergunta = models.TextField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    def __str__(self):
        return self.pergunta

class ContextRag(models.Model):
    content = models.JSONField()
    tool_name = models.CharField(max_length=255)
    tool_args = models.JSONField(null=True, blank=True)
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)

    def __str__(self):
        return self.tool_name

class AnaliseJurisprudencia(models.Model):
    documento = models.ForeignKey(Documentos, on_delete=models.CASCADE, related_name='analises')
    indice_risco = models.IntegerField()
    classificacao = models.CharField(max_length=20)  # Baixo, Médio, Alto, Crítico
    erros_coerencia = models.JSONField(default=list)
    riscos_juridicos = models.JSONField(default=list)
    problemas_formatacao = models.JSONField(default=list)
    red_flags = models.JSONField(default=list)
    tempo_processamento = models.IntegerField(default=0)  # em segundos
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Análise - {self.documento.get_tipo_display()} - {self.data_criacao.strftime('%d/%m/%Y %H:%M')}"

# Modelos WhatsApp
class ConversaWhatsApp(models.Model):
    """
    Modelo para armazenar conversas do WhatsApp
    """
    phone = models.CharField(max_length=20, db_index=True)
    nome_contato = models.CharField(max_length=255, blank=True, null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.BigIntegerField()
    ativo = models.BooleanField(default=True)
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_ultima_mensagem = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_ultima_mensagem']
        verbose_name = 'Conversa WhatsApp'
        verbose_name_plural = 'Conversas WhatsApp'
    
    def __str__(self):
        return f"{self.phone} - {self.nome_contato or 'Sem nome'}"

class MensagemWhatsApp(models.Model):
    """
    Modelo para armazenar mensagens individuais
    """
    TIPO_CHOICES = [
        ('recebida', 'Recebida'),
        ('enviada', 'Enviada'),
    ]
    
    conversa = models.ForeignKey(ConversaWhatsApp, on_delete=models.CASCADE, related_name='mensagens')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    conteudo = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    message_id = models.CharField(max_length=255, blank=True, null=True)
    processada = models.BooleanField(default=False)
    erro = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Mensagem WhatsApp'
        verbose_name_plural = 'Mensagens WhatsApp'
    
    def __str__(self):
        return f"{self.tipo} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"

class AgendamentoWhatsApp(models.Model):
    """
    Modelo para armazenar agendamentos feitos via WhatsApp
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
        ('realizado', 'Realizado'),
    ]
    
    conversa = models.ForeignKey(ConversaWhatsApp, on_delete=models.CASCADE, related_name='agendamentos')
    data_hora = models.DateTimeField()
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    google_calendar_id = models.CharField(max_length=255, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['data_hora']
        verbose_name = 'Agendamento WhatsApp'
        verbose_name_plural = 'Agendamentos WhatsApp'
    
    def __str__(self):
        return f"{self.conversa.phone} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
