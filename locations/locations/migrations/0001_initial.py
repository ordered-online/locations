# Generated by Django 2.2.6 on 2019-10-22 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('name', models.TextField(max_length=100, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('name', models.TextField(max_length=100, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=100)),
                ('description', models.TextField(max_length=500)),
                ('address', models.TextField(max_length=200)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=8, max_digits=10, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=8, max_digits=10, null=True)),
                ('website', models.TextField(blank=True, max_length=100, null=True)),
                ('telephone', models.TextField(blank=True, max_length=100, null=True)),
                ('categories', models.ManyToManyField(to='locations.Category')),
                ('tags', models.ManyToManyField(to='locations.Tag')),
            ],
        ),
    ]