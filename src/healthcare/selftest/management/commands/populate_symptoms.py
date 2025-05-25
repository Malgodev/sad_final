from django.core.management.base import BaseCommand
from django.db import transaction
from selftest.models import Symptom
from selftest.ai_engine import HealthAIEngine


class Command(BaseCommand):
    help = 'Populate the database with symptoms from JSON data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing symptoms before populating',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting symptom population...'))
        
        # Clear existing symptoms if requested
        if options['clear']:
            self.stdout.write('Clearing existing symptoms...')
            Symptom.objects.all().delete()
            self.stdout.write(self.style.WARNING('Existing symptoms cleared.'))
        
        # Load symptoms from AI engine
        ai_engine = HealthAIEngine()
        symptoms_data = ai_engine.symptoms_data.get('symptoms', [])
        
        if not symptoms_data:
            self.stdout.write(self.style.ERROR('No symptoms data found in JSON file.'))
            return
        
        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            for symptom_data in symptoms_data:
                symptom, created = Symptom.objects.get_or_create(
                    name=symptom_data['name'],
                    defaults={
                        'description': symptom_data.get('description', ''),
                        'category': symptom_data.get('category', 'General'),
                        'severity_scale': '1-10'
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'Created: {symptom.name}')
                else:
                    # Update existing symptom
                    symptom.description = symptom_data.get('description', '')
                    symptom.category = symptom_data.get('category', 'General')
                    symptom.save()
                    updated_count += 1
                    self.stdout.write(f'Updated: {symptom.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated symptoms: {created_count} created, {updated_count} updated'
            )
        )
        
        # Display summary
        total_symptoms = Symptom.objects.count()
        categories = Symptom.objects.values_list('category', flat=True).distinct()
        
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'Total symptoms in database: {total_symptoms}')
        self.stdout.write(f'Categories: {", ".join(categories)}')
        
        # Show category breakdown
        self.stdout.write('\nCategory breakdown:')
        for category in categories:
            count = Symptom.objects.filter(category=category).count()
            self.stdout.write(f'  {category}: {count} symptoms')
        
        self.stdout.write(self.style.SUCCESS('\nSymptom population completed successfully!')) 