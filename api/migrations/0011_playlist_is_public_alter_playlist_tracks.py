# Generated by Django 4.2 on 2023-04-09 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_track_album_alter_track_audio_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='is_public',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='playlist',
            name='tracks',
            field=models.ManyToManyField(blank=True, null=True, related_name='playlists', to='api.track'),
        ),
    ]
