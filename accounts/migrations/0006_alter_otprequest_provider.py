# Generated by Django 4.0.6 on 2022-07-08 01:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otprequest',
            name='provider',
            field=models.CharField(choices=[('p', 'phone'), ('e', 'email'), ('r', 'reset password')], default='p', max_length=1),
        ),
    ]
