# Generated by Django 2.1.1 on 2018-10-17 01:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('course', '0001_initial'),
        ('action', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseaction',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Course'),
        ),
        migrations.AddField(
            model_name='actionyaolingtu',
            name='action',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='action.ActionLibrary'),
        ),
        migrations.AddField(
            model_name='actionmusclepicture',
            name='action',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='action.ActionLibrary'),
        ),
        migrations.AddField(
            model_name='actionlibrary',
            name='level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='action.ActionLevel'),
        ),
        migrations.AddField(
            model_name='actionlibrary',
            name='machine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Machine'),
        ),
        migrations.AddField(
            model_name='actionlibrary',
            name='muscle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='action.Muscle'),
        ),
    ]
