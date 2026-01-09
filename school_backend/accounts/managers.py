from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils import timezone
import random
import string

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        
        # Generate admission number for students
        if extra_fields.get('role') == 'student' and not extra_fields.get('admission_number'):
            extra_fields['admission_number'] = self.generate_admission_number()
        
        # Generate staff ID for staff members
        if extra_fields.get('role') in ['teacher', 'admin', 'office_staff', 'head_teacher', 'curriculum_coordinator'] and not extra_fields.get('staff_id'):
            extra_fields['staff_id'] = self.generate_staff_id(extra_fields.get('role'))
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')
        
        return self.create_user(email, password, **extra_fields)

    def generate_admission_number(self):
        """
        Generate unique admission number for students: DEL-YYYY-XXXX
        """
        year = timezone.now().year
        last_student = self.filter(role='student', admission_number__isnull=False).last()
        
        if last_student and last_student.admission_number:
            try:
                last_num = int(last_student.admission_number.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1
        
        return f"DEL-{year}-{new_num:04d}"

    def generate_staff_id(self, role):
        """
        Generate unique staff ID based on role
        """
        role_prefixes = {
            'teacher': 'DEL-TCH',
            'admin': 'DEL-ADM',
            'head_teacher': 'DEL-HTR',
            'office_staff': 'DEL-OFF',
            'curriculum_coordinator': 'DEL-CCD'
        }
        
        prefix = role_prefixes.get(role, 'DEL-STA')
        year = timezone.now().year
        
        last_staff = self.filter(role=role, staff_id__isnull=False).last()
        if last_staff and last_staff.staff_id:
            try:
                last_num = int(last_staff.staff_id.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1
        
        return f"{prefix}-{year}-{new_num:04d}"