# Generated manually on 2026-02-09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_documentos'),
        ('ia', '0002_contextrag'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnaliseJurisprudencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('indice_risco', models.IntegerField()),
                ('classificacao', models.CharField(max_length=20)),
                ('erros_coerencia', models.JSONField(default=list)),
                ('riscos_juridicos', models.JSONField(default=list)),
                ('problemas_formatacao', models.JSONField(default=list)),
                ('red_flags', models.JSONField(default=list)),
                ('tempo_processamento', models.IntegerField(default=0)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('documento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analises', to='usuarios.documentos')),
            ],
            options={
                'ordering': ['-data_criacao'],
            },
        ),
    ]
