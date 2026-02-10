# Generated manually on 2026-02-09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_documentos'),
        ('ia', '0003_analisejurisprudencia'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConversaWhatsApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(db_index=True, max_length=20)),
                ('nome_contato', models.CharField(blank=True, max_length=255, null=True)),
                ('session_id', models.BigIntegerField()),
                ('ativo', models.BooleanField(default=True)),
                ('data_inicio', models.DateTimeField(auto_now_add=True)),
                ('data_ultima_mensagem', models.DateTimeField(auto_now=True)),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='usuarios.cliente')),
            ],
            options={
                'verbose_name': 'Conversa WhatsApp',
                'verbose_name_plural': 'Conversas WhatsApp',
                'ordering': ['-data_ultima_mensagem'],
            },
        ),
        migrations.CreateModel(
            name='MensagemWhatsApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('recebida', 'Recebida'), ('enviada', 'Enviada')], max_length=10)),
                ('conteudo', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('message_id', models.CharField(blank=True, max_length=255, null=True)),
                ('processada', models.BooleanField(default=False)),
                ('erro', models.TextField(blank=True, null=True)),
                ('conversa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensagens', to='ia.conversawhatsapp')),
            ],
            options={
                'verbose_name': 'Mensagem WhatsApp',
                'verbose_name_plural': 'Mensagens WhatsApp',
                'ordering': ['timestamp'],
            },
        ),
        migrations.CreateModel(
            name='AgendamentoWhatsApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_hora', models.DateTimeField()),
                ('descricao', models.TextField()),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('confirmado', 'Confirmado'), ('cancelado', 'Cancelado'), ('realizado', 'Realizado')], default='pendente', max_length=20)),
                ('google_calendar_id', models.CharField(blank=True, max_length=255, null=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('conversa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agendamentos', to='ia.conversawhatsapp')),
            ],
            options={
                'verbose_name': 'Agendamento WhatsApp',
                'verbose_name_plural': 'Agendamentos WhatsApp',
                'ordering': ['data_hora'],
            },
        ),
    ]
