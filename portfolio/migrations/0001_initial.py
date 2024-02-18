# Generated by Django 4.2.10 on 2024-02-18 18:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ticker', models.CharField(default='', max_length=64)),
                ('operation', models.CharField(choices=[('sell', 'sell'), ('buy', 'buy')], max_length=150)),
                ('operation_date', models.DateField()),
                ('n_stock', models.FloatField()),
                ('price', models.FloatField()),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ticker', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=150)),
                ('n_stock', models.FloatField()),
                ('avg_price', models.FloatField()),
                ('industry', models.CharField(max_length=150)),
                ('n_stock_next_exdiv_payment', models.FloatField()),
                ('next_exdiv_payment', models.DateField()),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DividendPayment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ticker', models.CharField(max_length=64)),
                ('payment_date', models.DateField()),
                ('amount', models.FloatField()),
                ('n_stock', models.FloatField()),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
