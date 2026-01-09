from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import StudentGrade, SubjectGrade, Assessment, Gradebook, ReportCard, GradingPeriod
import logging

logger = logging.getLogger(__name__)

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
            
            logger.info(f"Updated SubjectGrade for student {instance.student.id} in {instance.assessment.subject.name}")
        except Exception as e:
            logger.error(f"Error updating SubjectGrade: {str(e)}")

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
        
        logger.info(f"Recalculated SubjectGrade after deletion for student {instance.student.id}")
    except SubjectGrade.DoesNotExist:
        logger.warning(f"No SubjectGrade found for student {instance.student.id}")
    except Exception as e:
        logger.error(f"Error updating SubjectGrade after deletion: {str(e)}")

@receiver(post_save, sender=Assessment)
def create_gradebook_on_assessment_save(sender, instance, created, **kwargs):
    """Create gradebook if it doesn't exist when assessment is created"""
    if created and instance.created_by:
        try:
            Gradebook.objects.get_or_create(
                teacher=instance.created_by,
                subject=instance.subject,
                class_level=instance.class_level,
                grading_period=instance.grading_period
            )
            logger.info(f"Created/updated Gradebook for {instance.created_by.username}")
        except Exception as e:
            logger.error(f"Error creating Gradebook: {str(e)}")

@receiver(post_save, sender=SubjectGrade)
def update_report_card_on_subject_grade_save(sender, instance, created, **kwargs):
    """Update report card when subject grade is saved or finalized"""
    if instance.is_finalized:
        try:
            report_card, created = ReportCard.objects.get_or_create(
                student=instance.student,
                grading_period=instance.grading_period,
                class_level=instance.class_level
            )
            
            # Recalculate overall performance
            report_card.calculate_overall()
            report_card.save()
            
            logger.info(f"Updated ReportCard for student {instance.student.id}")
        except Exception as e:
            logger.error(f"Error updating ReportCard: {str(e)}")

@receiver(post_save, sender=GradingPeriod)
def mark_report_cards_draft_on_period_change(sender, instance, **kwargs):
    """Mark report cards as draft when grading period is changed"""
    if instance.pk:
        try:
            # If grading period is no longer active or finalized, mark report cards as draft
            if not instance.is_active or not instance.is_finalized:
                ReportCard.objects.filter(grading_period=instance, status='published').update(status='draft')
                logger.info(f"Marked report cards as draft for grading period {instance.name}")
        except Exception as e:
            logger.error(f"Error updating report cards: {str(e)}")