from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import StudentGrade, SubjectGrade, Assessment

@receiver(post_save, sender=StudentGrade)
def update_subject_grade_on_student_grade_save(sender, instance, created, **kwargs):
    """Update subject grade when student grade is saved"""
    if instance.marks_obtained is not None:
        try:
            # Get or create subject grade
            subject_grade, created = SubjectGrade.objects.get_or_create(
                student=instance.student,
                subject=instance.assessment.subject,
                class_level=instance.assessment.class_level,
                grading_period=instance.assessment.grading_period,
                defaults={
                    'total_marks': 0,
                    'marks_obtained': 0
                }
            )
            
            # Recalculate overall grade
            subject_grade.calculate_overall_grade()
            subject_grade.save()
        except Exception as e:
            # Log error but don't crash
            pass

@receiver(post_delete, sender=StudentGrade)
def update_subject_grade_on_student_grade_delete(sender, instance, **kwargs):
    """Update subject grade when student grade is deleted"""
    try:
        # Find the subject grade
        subject_grade = SubjectGrade.objects.get(
            student=instance.student,
            subject=instance.assessment.subject,
            class_level=instance.assessment.class_level,
            grading_period=instance.assessment.grading_period
        )
        
        # Recalculate overall grade
        subject_grade.calculate_overall_grade()
        subject_grade.save()
    except SubjectGrade.DoesNotExist:
        pass
    except Exception as e:
        # Log error but don't crash
        pass

@receiver(post_save, sender=Assessment)
def create_gradebook_on_assessment_save(sender, instance, created, **kwargs):
    """Create gradebook if it doesn't exist when assessment is created"""
    if created:
        try:
            Gradebook.objects.get_or_create(
                teacher=instance.created_by,
                subject=instance.subject,
                class_level=instance.class_level,
                grading_period=instance.grading_period
            )
        except Exception as e:
            # Log error but don't crash
            pass