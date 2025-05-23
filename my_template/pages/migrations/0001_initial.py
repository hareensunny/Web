# Generated by Django 5.1.6 on 2025-04-23 11:01

import django.core.validators
import django.db.models.deletion
import pages.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BU',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ContractData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract', models.CharField(max_length=255, unique=True)),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
                ('effective_date', models.DateField(blank=True, null=True)),
                ('termination_date', models.DateField(blank=True, null=True)),
                ('lot_turns', models.FloatField(blank=True, null=True)),
                ('euv3400', models.FloatField(blank=True, null=True)),
                ('exe5000', models.FloatField(blank=True, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Factory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Integrator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Litho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='LotStatusData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.CharField(blank=True, max_length=255, null=True)),
                ('factory', models.CharField(blank=True, max_length=255, null=True)),
                ('lot_id', models.CharField(blank=True, max_length=255, null=True)),
                ('hold_code', models.CharField(blank=True, max_length=255, null=True)),
                ('priority', models.IntegerField(blank=True, null=True)),
                ('current_operation', models.CharField(blank=True, max_length=255, null=True)),
                ('oper1', models.CharField(blank=True, max_length=255, null=True)),
                ('oper2', models.CharField(blank=True, max_length=255, null=True)),
                ('oper3', models.CharField(blank=True, max_length=255, null=True)),
                ('oper4', models.CharField(blank=True, max_length=255, null=True)),
                ('oper5', models.CharField(blank=True, max_length=255, null=True)),
                ('oper6', models.CharField(blank=True, max_length=255, null=True)),
                ('oper7', models.CharField(blank=True, max_length=255, null=True)),
                ('oper8', models.CharField(blank=True, max_length=255, null=True)),
                ('oper9', models.CharField(blank=True, max_length=255, null=True)),
                ('oper10', models.CharField(blank=True, max_length=255, null=True)),
                ('oper11', models.CharField(blank=True, max_length=255, null=True)),
                ('oper12', models.CharField(blank=True, max_length=255, null=True)),
                ('oper13', models.CharField(blank=True, max_length=255, null=True)),
                ('oper14', models.CharField(blank=True, max_length=255, null=True)),
                ('oper15', models.CharField(blank=True, max_length=255, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='RequestType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Reticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='UploadRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('file_type', models.CharField(max_length=50)),
                ('uploader', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='WBS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('bu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.bu')),
            ],
        ),
        migrations.AddField(
            model_name='bu',
            name='factory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.factory'),
        ),
        migrations.CreateModel(
            name='ProjectGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('factory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.factory')),
            ],
        ),
        migrations.CreateModel(
            name='Requestor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('factory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.factory')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=pages.models.upload_to)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('folder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pages.folder')),
            ],
        ),
        migrations.CreateModel(
            name='upload_data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tmp_lot_id', models.CharField(max_length=255)),
                ('lot_turns', models.FloatField(blank=True, null=True)),
                ('EUV_3300', models.FloatField(blank=True, null=True)),
                ('EUV_3400', models.FloatField(blank=True, null=True)),
                ('EXE_5000', models.FloatField(blank=True, null=True)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('month', models.IntegerField(blank=True, null=True)),
                ('jpn_ytd', models.CharField(max_length=255)),
                ('no_of_samples', models.FloatField(blank=True, null=True)),
                ('bu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pages.bu')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pages.department')),
                ('factory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pages.factory')),
                ('wbs', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pages.wbs')),
            ],
            options={
                'db_table': 'upload_data',
            },
        ),
        migrations.CreateModel(
            name='Lot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=100)),
                ('special_focus', models.CharField(max_length=100)),
                ('estimated_end_date', models.DateField()),
                ('no_of_samples', models.IntegerField(help_text='Enter a number between 1 and 23', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(23)])),
                ('current_number', models.CharField(default='0000000T', editable=False, max_length=20)),
                ('tmp_lot_id', models.CharField(default='TMP0000000000', editable=False, max_length=20)),
                ('project_factory_date_code', models.CharField(default='DEFAULT_CODE', editable=False, max_length=50)),
                ('es_number', models.CharField(blank=True, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('waiting', 'Waiting'), ('active', 'Active'), ('completed', 'Completed')], default='waiting', max_length=20)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('development', models.FloatField(default='0.0')),
                ('metrology', models.FloatField(default='0.0')),
                ('duplo', models.FloatField(default='0.0')),
                ('other', models.FloatField(default='0.0')),
                ('created_at', models.DateField(blank=True, null=True)),
                ('url', models.CharField(blank=True, max_length=100, null=True)),
                ('bu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.bu')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.department')),
                ('factory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.factory')),
                ('integrator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.integrator')),
                ('litho', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.litho')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.location')),
                ('project_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.projectgroup')),
                ('requestor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.requestor')),
                ('request_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.requesttype')),
                ('reticle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.reticle')),
                ('wbs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.wbs')),
            ],
        ),
        migrations.AddField(
            model_name='factory',
            name='wbs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.wbs'),
        ),
        migrations.CreateModel(
            name='CompletedForm_Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=100)),
                ('special_focus', models.CharField(max_length=100)),
                ('estimated_end_date', models.DateField()),
                ('no_of_samples', models.IntegerField()),
                ('is_active', models.BooleanField(default=False)),
                ('current_number', models.CharField(default='0000000T', editable=False, max_length=20)),
                ('tmp_lot_id', models.CharField(default='TMP0000000000', editable=False, max_length=20)),
                ('project_factory_date_code', models.CharField(default='DEFAULT_CODE', editable=False, max_length=50)),
                ('es_number', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(default='Completed', max_length=50)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('development', models.FloatField(default='0.0')),
                ('metrology', models.FloatField(default='0.0')),
                ('duplo', models.FloatField(default='0.0')),
                ('other', models.FloatField(default='0.0')),
                ('created_at', models.DateField(blank=True, null=True)),
                ('url', models.CharField(blank=True, max_length=100, null=True)),
                ('bu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.bu')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.department')),
                ('factory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.factory')),
                ('integrator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.integrator')),
                ('litho', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.litho')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.location')),
                ('project_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.projectgroup')),
                ('requestor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.requestor')),
                ('request_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.requesttype')),
                ('reticle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.reticle')),
                ('wbs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.wbs')),
            ],
        ),
        migrations.CreateModel(
            name='BudgetData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lot_turns_budget', models.FloatField(blank=True, null=True)),
                ('euv3400_budget', models.FloatField(blank=True, null=True)),
                ('exe5000_budget', models.FloatField(blank=True, null=True)),
                ('bu', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.bu')),
                ('factory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.factory')),
                ('wbs', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.wbs')),
            ],
        ),
        migrations.CreateModel(
            name='ActiveForm_Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=100)),
                ('special_focus', models.CharField(max_length=100)),
                ('estimated_end_date', models.DateField()),
                ('no_of_samples', models.IntegerField()),
                ('is_active', models.BooleanField(default=False)),
                ('current_number', models.CharField(default='0000000T', editable=False, max_length=20)),
                ('tmp_lot_id', models.CharField(default='TMP0000000000', editable=False, max_length=20)),
                ('project_factory_date_code', models.CharField(default='DEFAULT_CODE', editable=False, max_length=50)),
                ('es_number', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(default='Active', max_length=50)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('development', models.FloatField(default='0.0')),
                ('metrology', models.FloatField(default='0.0')),
                ('duplo', models.FloatField(default='0.0')),
                ('other', models.FloatField(default='0.0')),
                ('created_at', models.DateField(blank=True, null=True)),
                ('url', models.CharField(blank=True, max_length=100, null=True)),
                ('bu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.bu')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.department')),
                ('factory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.factory')),
                ('integrator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.integrator')),
                ('litho', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.litho')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.location')),
                ('project_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.projectgroup')),
                ('requestor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.requestor')),
                ('request_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.requesttype')),
                ('reticle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.reticle')),
                ('wbs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.wbs')),
            ],
        ),
    ]
