# Generated by Django 4.2.21 on 2025-05-25 12:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0002_doctor_approval_status_doctor_approved_at_and_more'),
        ('patient', '0001_initial'),
        ('appointment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='duration_minutes',
            field=models.IntegerField(default=90),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='patient.patient'),
        ),
        migrations.CreateModel(
            name='AppointmentSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('slot_type', models.CharField(choices=[('morning_1', 'Morning 8:00 - 9:30'), ('morning_2', 'Morning 10:00 - 11:30'), ('afternoon_1', 'Afternoon 1:30 - 3:00'), ('afternoon_2', 'Afternoon 3:30 - 5:00')], max_length=20)),
                ('is_available', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointment_slots', to='doctor.doctor')),
            ],
            options={
                'verbose_name': 'Appointment Slot',
                'verbose_name_plural': 'Appointment Slots',
                'ordering': ['date', 'slot_type'],
                'unique_together': {('doctor', 'date', 'slot_type')},
            },
        ),
        migrations.AddField(
            model_name='appointment',
            name='appointment_slot',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment', to='appointment.appointmentslot'),
        ),
    ]
