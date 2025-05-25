from django.core.management.base import BaseCommand
from selftest.models import Symptom

class Command(BaseCommand):
    help = 'Create basic symptoms for testing'

    def handle(self, *args, **options):
        symptoms = [
            ('Fever', 'Elevated body temperature above normal range'),
            ('Headache', 'Pain in the head or upper neck'),
            ('Cough', 'Sudden expulsion of air from the lungs'),
            ('Sore Throat', 'Pain or irritation in the throat'),
            ('Fatigue', 'Extreme tiredness or lack of energy'),
            ('Nausea', 'Feeling sick to your stomach'),
            ('Stomach Pain', 'Pain in the abdominal area'),
            ('Muscle Aches', 'Pain or soreness in muscles'),
            ('Difficulty Breathing', 'Trouble breathing or shortness of breath'),
            ('Chest Pain', 'Pain or discomfort in the chest area'),
            ('Dizziness', 'Feeling lightheaded or unsteady'),
            ('Runny Nose', 'Nasal discharge or congestion'),
            ('Sneezing', 'Sudden expulsion of air through nose'),
            ('Vomiting', 'Forceful emptying of stomach contents'),
            ('Diarrhea', 'Loose or watery bowel movements'),
            ('Skin Rash', 'Red, irritated, or inflamed skin'),
            ('Itching', 'Urge to scratch the skin'),
            ('Swelling', 'Enlargement or puffiness of body parts'),
            ('Joint Pain', 'Pain in joints or connecting tissues'),
            ('Back Pain', 'Pain in the back or spine area'),
            ('Constipation', 'Difficulty passing stool'),
            ('Loss of Appetite', 'Reduced desire to eat'),
            ('Weight Loss', 'Unintentional decrease in body weight'),
            ('Blurred Vision', 'Unclear or fuzzy vision'),
            ('Ear Pain', 'Pain in or around the ear'),
            ('Rapid Heartbeat', 'Fast or irregular heart rate'),
            ('Sweating', 'Excessive perspiration'),
            ('Anxiety', 'Feelings of worry or nervousness'),
            ('Depression', 'Persistent sad or empty mood'),
            ('Insomnia', 'Difficulty falling or staying asleep'),
        ]
        
        created_count = 0
        for name, description in symptoms:
            symptom, created = Symptom.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created: {name}')
            else:
                self.stdout.write(f'Already exists: {name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} new symptoms. '
                f'Total symptoms in database: {Symptom.objects.count()}'
            )
        ) 