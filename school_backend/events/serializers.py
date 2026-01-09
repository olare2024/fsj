# serializers.py
from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Event, EventCategory, EventRegistration, EventFeedback, EventReminder, EventAttachment


User = get_user_model()

class EventCategorySerializer(serializers.ModelSerializer):
    event_count = serializers.SerializerMethodField()

    class Meta:
        model = EventCategory
        fields = '__all__'

    def get_event_count(self, obj):
        return obj.events.count()


class UserSimpleSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name']


class EventAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = EventAttachment
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'download_count']

    def get_file_size(self, obj):
        if obj.file:
            return obj.file.size
        return 0


class EventListSerializer(serializers.ModelSerializer):
    category_names = serializers.SerializerMethodField()
    coordinator_name = serializers.CharField(source='coordinator.get_full_name', read_only=True)
    registered_count = serializers.ReadOnlyField()
    available_slots = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    can_register = serializers.ReadOnlyField()
    current_fee = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'event_code', 'event_type', 'start_date', 'end_date',
            'location', 'is_online', 'image', 'coordinator_name', 'target_audience',
            'requires_registration', 'has_fee', 'current_fee', 'is_published',
            'is_featured', 'is_cancelled', 'registered_count', 'available_slots',
            'is_upcoming', 'is_ongoing', 'is_past', 'can_register', 'category_names'
        ]

    def get_category_names(self, obj):
        return [category.name for category in obj.categories.all()]


class EventDetailSerializer(serializers.ModelSerializer):
    categories = EventCategorySerializer(many=True, read_only=True)
    coordinator_details = UserSimpleSerializer(source='coordinator', read_only=True)
    created_by_details = UserSimpleSerializer(source='created_by', read_only=True)
    approved_by_details = UserSimpleSerializer(source='approved_by', read_only=True)
    attachments = EventAttachmentSerializer(many=True, read_only=True)
    
    # Computed fields
    registered_count = serializers.ReadOnlyField()
    waitlist_count = serializers.ReadOnlyField()
    available_slots = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    can_register = serializers.ReadOnlyField()
    current_fee = serializers.ReadOnlyField()
    is_fully_booked = serializers.ReadOnlyField()
    
    # Statistics
    feedback_stats = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'published_at', 'approved_at',
            'views_count', 'event_code', 'slug'
        ]

    def get_feedback_stats(self, obj):
        feedbacks = obj.feedbacks.all()
        if not feedbacks:
            return None
        
        ratings = [fb.rating for fb in feedbacks]
        return {
            'total_feedbacks': len(feedbacks),
            'average_rating': sum(ratings) / len(ratings),
            'rating_distribution': {
                '1': ratings.count(1),
                '2': ratings.count(2),
                '3': ratings.count(3),
                '4': ratings.count(4),
                '5': ratings.count(5),
            }
        }

    def validate(self, data):
        start_date = data.get('start_date', self.instance.start_date if self.instance else None)
        end_date = data.get('end_date', self.instance.end_date if self.instance else None)
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date")
        
        return data


class EventRegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    display_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    balance_due = serializers.ReadOnlyField()
    is_fully_paid = serializers.ReadOnlyField()

    class Meta:
        model = EventRegistration
        fields = '__all__'
        read_only_fields = [
            'registration_date', 'payment_amount', 'confirmation_sent',
            'reminder_sent'
        ]

    def validate(self, data):
        event = data.get('event', self.instance.event if self.instance else None)
        user = data.get('user', self.instance.user if self.instance else None)
        student = data.get('student')
        
        if event and user:
            # Check for duplicate registration
            existing_registration = EventRegistration.objects.filter(
                event=event, user=user, student=student
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_registration.exists():
                raise serializers.ValidationError("You are already registered for this event")
            
            # Check if registration is allowed
            if not event.can_register:
                raise serializers.ValidationError("Registration is not available for this event")
            
            # Check guest count
            guest_count = data.get('guest_count', 1)
            if guest_count > event.max_guests_per_registration:
                raise serializers.ValidationError(
                    f"Maximum {event.max_guests_per_registration} guests allowed per registration"
                )
        
        return data

    def create(self, validated_data):
        event = validated_data['event']
        
        # Set payment amount if not provided
        if event.has_fee and not validated_data.get('payment_amount'):
            validated_data['payment_amount'] = event.current_fee * validated_data.get('guest_count', 1)
        
        # Handle waitlist
        if event.is_fully_booked and event.waitlist_enabled:
            validated_data['status'] = 'waiting'
        
        return super().create(validated_data)


class EventFeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = EventFeedback
        fields = '__all__'
        read_only_fields = ['submitted_at', 'helpful_count']

    def validate(self, data):
        event = data.get('event', self.instance.event if self.instance else None)
        user = data.get('user', self.instance.user if self.instance else None)
        
        if event and user:
            # Check if user has attended the event
            if not EventRegistration.objects.filter(
                event=event, user=user, status='attended'
            ).exists():
                raise serializers.ValidationError("You must have attended the event to provide feedback")
            
            # Check for existing feedback
            existing_feedback = EventFeedback.objects.filter(
                event=event, user=user
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_feedback.exists():
                raise serializers.ValidationError("You have already submitted feedback for this event")
        
        return data


class EventReminderSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = EventReminder
        fields = '__all__'
        read_only_fields = ['sent', 'sent_at', 'send_attempts']

    def validate_reminder_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Reminder time cannot be in the past")
        return value


class EventRegistrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = ['event', 'student', 'dietary_restrictions', 'special_requirements', 
                 'emergency_contact', 'emergency_phone', 'medical_conditions', 'allergies',
                 'guest_count', 'guest_name', 'guest_email']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)