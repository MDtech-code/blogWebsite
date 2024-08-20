# Generated by Django 5.0.8 on 2024-08-11 17:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_alter_comment_author_alter_comment_post'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.RenameField(
            model_name='category',
            old_name='parent_id',
            new_name='parent',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='parent_id',
            new_name='parent',
        ),
        migrations.AddField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='blog.comment'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='bookmark',
            unique_together={('user', 'post')},
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together={('user', 'post')},
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['slug'], name='blog_post_slug_cdb902_idx'),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['created_at'], name='blog_post_created_b20a1e_idx'),
        ),
    ]
