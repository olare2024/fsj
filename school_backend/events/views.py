# views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Avg
from .models import Event, EventCategory, EventRegistration, EventFeedback, EventReminder, EventAttachment
from .serializers import *
from .filters import EventFilter
from .permissions import IsEventCoordinator, IsEventCreator, CanApproveEvents


class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.filter(is_active=True)
    serializer_class = EventCategorySerializer
    
    # FIXED: Proper permission configuration
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]  # FIXED: Added parentheses


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'description', 'location', 'organizer']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'priority']
    ordering = ['-start_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        return EventDetailSerializer

    # FIXED: Proper permission configuration with parentheses
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        elif self.action in ['approve', 'publish', 'cancel']:
            return [IsAdminUser() | CanApproveEvents()]
        return [AllowAny()]  # FIXED: Added parentheses for list/retrieve actions

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter based on user type and permissions
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return queryset
            else:
                # Use the manager method to filter events for user audience
                return Event.objects.for_user_audience(self.request.user)
        else:
            # Public events for unauthenticated users
            return queryset.filter(is_published=True, target_audience='all')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Increment view count
        if request.user.is_authenticated:
            instance.views_count += 1
            instance.save(update_fields=['views_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming events"""
        queryset = self.get_queryset().upcoming()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ongoing(self, request):
        """Get ongoing events"""
        queryset = self.get_queryset().ongoing()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self, request):
        """Get past events"""
        queryset = self.get_queryset().past()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured events"""
        queryset = self.get_queryset().filter(is_featured=True, is_published=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        """Register for an event"""
        event = self.get_object()
        
        if not event.can_register:
            return Response(
                {'error': 'Registration is not available for this event'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = EventRegistrationCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            registration = serializer.save()
            response_serializer = EventRegistrationSerializer(registration)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an event (admin only)"""
        event = self.get_object()
        event.approved_by = request.user
        event.approved_at = timezone.now()
        event.requires_approval = False
        event.save()
        
        return Response({'status': 'Event approved'})

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish an event"""
        event = self.get_object()
        event.is_published = True
        event.save()
        
        return Response({'status': 'Event published'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an event"""
        event = self.get_object()
        event.is_cancelled = True
        event.cancellation_reason = request.data.get('reason', '')
        event.save()
        
        return Response({'status': 'Event cancelled'})

    @action(detail=True, methods=['get'])
    def registrations(self, request, pk=None):
        """Get event registrations"""
        event = self.get_object()
        registrations = event.registrations.all()
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def feedback(self, request, pk=None):
        """Get event feedback"""
        event = self.get_object()
        feedback = event.feedbacks.filter(approved=True)
        serializer = EventFeedbackSerializer(feedback, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EventRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]  # FIXED: All registration actions require auth
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'status', 'payment_status', 'checked_in']
    ordering_fields = ['registration_date', 'payment_date']
    ordering = ['-registration_date']

    def get_queryset(self):
        if self.request.user.is_staff:
            return EventRegistration.objects.all()
        return EventRegistration.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Check in a participant"""
        registration = self.get_object()
        
        if registration.checked_in:
            return Response(
                {'error': 'Participant already checked in'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        registration.checked_in = True
        registration.check_in_time = timezone.now()
        registration.checked_in_by = request.user
        registration.save()
        
        return Response({'status': 'Checked in successfully'})

    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        """Record payment for registration"""
        registration = self.get_object()
        amount = request.data.get('amount', registration.balance_due)
        
        registration.amount_paid += float(amount)
        registration.payment_date = timezone.now()
        registration.payment_method = request.data.get('payment_method', '')
        registration.payment_reference = request.data.get('reference', '')
        registration.save()
        
        return Response({
            'status': 'Payment recorded',
            'amount_paid': registration.amount_paid,
            'balance_due': registration.balance_due
        })


class EventFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = EventFeedbackSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'rating', 'approved']
    ordering_fields = ['submitted_at', 'rating']
    ordering = ['-submitted_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return EventFeedback.objects.all()
        return EventFeedback.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """Mark feedback as helpful"""
        feedback = self.get_object()
        feedback.helpful_count += 1
        feedback.save()
        
        return Response({'helpful_count': feedback.helpful_count})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser()])
    def approve(self, request, pk=None):
        """Approve feedback (admin only)"""
        feedback = self.get_object()
        feedback.approved = True
        feedback.save()
        
        return Response({'status': 'Feedback approved'})


class EventReminderViewSet(viewsets.ModelViewSet):
    queryset = EventReminder.objects.all()
    serializer_class = EventReminderSerializer
    permission_classes = [IsAdminUser()]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'reminder_type', 'sent']
    ordering_fields = ['reminder_time', 'created_at']
    ordering = ['reminder_time']


class EventAttachmentViewSet(viewsets.ModelViewSet):
    queryset = EventAttachment.objects.all()
    serializer_class = EventAttachmentSerializer
    permission_classes = [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Increment download count"""
        attachment = self.get_object()
        attachment.download_count += 1
        attachment.save()
        
        return Response({'download_count': attachment.download_count})