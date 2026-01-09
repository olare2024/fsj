# notes/management/commands/setup_notes.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from academics.models import Subject, Class
from notes.models import LearningModule

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup initial learning modules and content'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up initial learning modules...')
        
        # Get admin user
        try:
            admin = User.objects.get(email='admin@delvok.ac.ke')
        except User.DoesNotExist:
            admin = User.objects.filter(is_superuser=True).first()
        
        if not admin:
            self.stdout.write(self.style.ERROR('No admin user found'))
            return
        
        # Get sample subject and class
        try:
            subject = Subject.objects.first()
            class_field = Class.objects.first()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting subject/class: {e}'))
            return
        
        # Create sample module
        if subject and class_field:
            module, created = LearningModule.objects.get_or_create(
                title='Introduction to Learning',
                defaults={
                    'description': 'Introduction module for new students',
                    'subject': subject,
                    'class_field': class_field,
                    'curriculum': 'cbc',
                    'completion_threshold': 80,
                    'author': admin,
                    'is_published': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created module: {module.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Module already exists: {module.title}'))
        
        self.stdout.write(self.style.SUCCESS('Setup complete!'))