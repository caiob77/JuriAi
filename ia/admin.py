from django.contrib import admin
from usuarios.models import Documentos
from .models import (
    Pergunta, 
    ContextRag, 
    AnaliseJurisprudencia,
    ConversaWhatsApp,
    MensagemWhatsApp,
    AgendamentoWhatsApp
)

# Register your models here.
admin.site.register(Documentos)
admin.site.register(Pergunta)
admin.site.register(ContextRag)

@admin.register(AnaliseJurisprudencia)
class AnaliseJurisprudenciaAdmin(admin.ModelAdmin):
    list_display = ['id', 'documento', 'classificacao', 'indice_risco', 'tempo_processamento', 'data_criacao']
    list_filter = ['classificacao', 'data_criacao']
    search_fields = ['documento__tipo', 'classificacao']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('documento', 'indice_risco', 'classificacao', 'tempo_processamento')
        }),
        ('Análises Detalhadas', {
            'fields': ('erros_coerencia', 'riscos_juridicos', 'problemas_formatacao', 'red_flags'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

# Modelos WhatsApp
@admin.register(ConversaWhatsApp)
class ConversaWhatsAppAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone', 'nome_contato', 'cliente', 'ativo', 'data_inicio', 'data_ultima_mensagem']
    list_filter = ['ativo', 'data_inicio']
    search_fields = ['phone', 'nome_contato', 'cliente__nome']
    readonly_fields = ['session_id', 'data_inicio', 'data_ultima_mensagem']
    
    fieldsets = (
        ('Informações de Contato', {
            'fields': ('phone', 'nome_contato', 'cliente')
        }),
        ('Status', {
            'fields': ('ativo', 'session_id')
        }),
        ('Datas', {
            'fields': ('data_inicio', 'data_ultima_mensagem'),
        }),
    )

@admin.register(MensagemWhatsApp)
class MensagemWhatsAppAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversa', 'tipo', 'conteudo_resumido', 'timestamp', 'processada']
    list_filter = ['tipo', 'processada', 'timestamp']
    search_fields = ['conteudo', 'conversa__phone']
    readonly_fields = ['timestamp', 'message_id']
    
    def conteudo_resumido(self, obj):
        return obj.conteudo[:50] + '...' if len(obj.conteudo) > 50 else obj.conteudo
    conteudo_resumido.short_description = 'Conteúdo'

@admin.register(AgendamentoWhatsApp)
class AgendamentoWhatsAppAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversa', 'data_hora', 'status', 'data_criacao']
    list_filter = ['status', 'data_hora', 'data_criacao']
    search_fields = ['descricao', 'conversa__phone']
    readonly_fields = ['google_calendar_id', 'data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações do Agendamento', {
            'fields': ('conversa', 'data_hora', 'descricao', 'status')
        }),
        ('Google Calendar', {
            'fields': ('google_calendar_id',),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )