# Generated by Django 4.0.6 on 2022-07-09 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='comments',
        ),
        migrations.AddField(
            model_name='post',
            name='comments',
            field=models.ManyToManyField(related_name='comments', to='blog.comment'),
        ),
    ]
