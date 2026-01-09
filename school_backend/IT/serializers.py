# backend/apps/it/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import (
    SystemComponent, ComponentStatusLog, SupportTicket, TicketComment,
    TimeEntry, SystemAlert, AlertLog, MaintenanceTask, BackupJob,
    PerformanceMetric, KnowledgeBaseArticle, ArticleRating, ITResource,
    ResourceLog, ITProject, ITDashboard
)
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user display"""
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'department']


class SystemComponentSerializer(serializers.ModelSerializer):
    """Serializer for system components"""
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    component_type_display = serializers.CharField(source='get_component_type_display', read_only=True)
    criticality_display = serializers.CharField(source='get_criticality_display', read_only=True)
    is_under_warranty = serializers.BooleanField(read_only=True)
    age_in_months = serializers.IntegerField(read_only=True)
    requires_maintenance = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SystemComponent
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'component_code', 'last_check']
    
    def validate(self, data):
        """Custom validation"""
        # Validate IP address if provided
        if data.get('ip_address'):
            # Check for duplicate IP addresses
            queryset = SystemComponent.objects.filter(ip_address=data['ip_address'])
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({'ip_address': 'This IP address is already in use.'})
        
        # Validate purchase date
        if data.get('purchase_date') and data['purchase_date'] > timezone.now().date():
            raise serializers.ValidationError({'purchase_date': 'Purchase date cannot be in the future.'})
        
        # Validate warranty expiry
        if data.get('warranty_expiry') and data.get('purchase_date'):
            if data['warranty_expiry'] < data['purchase_date']:
                raise serializers.ValidationError({'warranty_expiry': 'Warranty expiry must be after purchase date.'})
        
        return data
    
    def create(self, validated_data):
        """Create component with current user as creator"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ComponentStatusLogSerializer(serializers.ModelSerializer):
    """Serializer for component status logs"""
    changed_by_details = UserSerializer(source='changed_by', read_only=True)
    component_name = serializers.CharField(source='component.name', read_only=True)
    old_status_display = serializers.CharField(source='get_old_status_display', read_only=True)
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)
    
    class Meta:
        model = ComponentStatusLog
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SupportTicketSerializer(serializers.ModelSerializer):
    """Serializer for support tickets"""
    created_by_details = UserSerializer(source='created_by', read_only=True)
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sla_status_display = serializers.CharField(source='get_sla_status_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    age_in_days = serializers.IntegerField(read_only=True)
    time_to_first_response = serializers.DurationField(read_only=True)
    affected_components_details = SystemComponentSerializer(
        source='affected_components', many=True, read_only=True
    )
    
    class Meta:
        model = SupportTicket
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'ticket_number', 'created_by',
            'first_response_at', 'resolved_at', 'closed_at', 'sla_status'
        ]
    
    def create(self, validated_data):
        """Create ticket with current user as creator"""
        request = self.context['request']
        validated_data['created_by'] = request.user
        
        # Auto-assign to IT support if not specified
        if not validated_data.get('assigned_to'):
            it_staff = User.objects.filter(
                role=User.Role.IT_SUPPORT,
                is_active=True
            ).first()
            if it_staff:
                validated_data['assigned_to'] = it_staff
        
        # Set reported by information
        if not validated_data.get('reported_by_name'):
            validated_data['reported_by_name'] = request.user.get_full_name()
            validated_data['reported_by_email'] = request.user.email
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update ticket with status change handling"""
        # Track status changes
        if 'status' in validated_data and validated_data['status'] != instance.status:
            old_status = instance.status
            new_status = validated_data['status']
            
            # Handle status-specific actions
            if new_status == SupportTicket.TicketStatus.IN_PROGRESS and not instance.assigned_to:
                # Auto-assign to current user if not assigned
                validated_data['assigned_to'] = self.context['request'].user
            
            elif new_status == SupportTicket.TicketStatus.RESOLVED:
                validated_data['resolved_at'] = timezone.now()
                
            elif new_status == SupportTicket.TicketStatus.CLOSED:
                validated_data['closed_at'] = timezone.now()
        
        return super().update(instance, validated_data)


class TicketCommentSerializer(serializers.ModelSerializer):
    """Serializer for ticket comments"""
    user_details = UserSerializer(source='user', read_only=True)
    ticket_number = serializers.CharField(source='ticket.ticket_number', read_only=True)
    mentions_details = UserSerializer(source='mentions', many=True, read_only=True)
    
    class Meta:
        model = TicketComment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'user']
    
    def create(self, validated_data):
        """Create comment with current user"""
        validated_data['user'] = self.context['request'].user
        
        # Update ticket's first response time if needed
        ticket = validated_data['ticket']
        if not ticket.first_response_at and validated_data['user'] != ticket.created_by:
            ticket.first_response_at = timezone.now()
            ticket.save()
        
        return super().create(validated_data)


class TimeEntrySerializer(serializers.ModelSerializer):
    """Serializer for time entries"""
    user_details = UserSerializer(source='user', read_only=True)
    ticket_number = serializers.CharField(source='ticket.ticket_number', read_only=True)
    
    class Meta:
        model = TimeEntry
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'user']
    
    def validate(self, data):
        """Validate time entry"""
        if data['hours'] <= 0:
            raise serializers.ValidationError({'hours': 'Hours must be greater than 0.'})
        
        if data['date_worked'] > timezone.now().date():
            raise serializers.ValidationError({'date_worked': 'Date cannot be in the future.'})
        
        return data
    
    def create(self, validated_data):
        """Create time entry with current user"""
        validated_data['user'] = self.context['request'].user
        
        # Update ticket time spent
        ticket = validated_data['ticket']
        if not ticket.time_spent:
            ticket.time_spent = timezone.timedelta()
        
        ticket.time_spent += timezone.timedelta(hours=float(validated_data['hours']))
        ticket.save()
        
        return super().create(validated_data)


class SystemAlertSerializer(serializers.ModelSerializer):
    """Serializer for system alerts"""
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    component_details = SystemComponentSerializer(source='component', read_only=True)
    ticket_details = SupportTicketSerializer(source='ticket', read_only=True)
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    duration = serializers.DurationField(read_only=True)
    requires_action = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SystemAlert
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'detected_at',
            'acknowledged_at', 'resolved_at', 'created_by'
        ]
    
    def create(self, validated_data):
        """Create alert with current user as creator"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AlertLogSerializer(serializers.ModelSerializer):
    """Serializer for alert logs"""
    user_details = UserSerializer(source='user', read_only=True)
    alert_title = serializers.CharField(source='alert.title', read_only=True)
    
    class Meta:
        model = AlertLog
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class MaintenanceTaskSerializer(serializers.ModelSerializer):
    """Serializer for maintenance tasks"""
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    impact_level_display = serializers.CharField(source='get_impact_level_display', read_only=True)
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    approved_by_details = UserSerializer(source='approved_by', read_only=True)
    team_members_details = UserSerializer(source='team_members', many=True, read_only=True)
    affected_components_details = SystemComponentSerializer(
        source='affected_components', many=True, read_only=True
    )
    duration = serializers.DurationField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = MaintenanceTask
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'task_number',
            'notification_sent_at', 'approved_at', 'actual_start',
            'actual_end', 'created_by'
        ]
    
    def validate(self, data):
        """Validate maintenance task"""
        if data.get('scheduled_start') and data.get('scheduled_end'):
            if data['scheduled_start'] >= data['scheduled_end']:
                raise serializers.ValidationError({
                    'scheduled_end': 'End time must be after start time.'
                })
        
        return data
    
    def create(self, validated_data):
        """Create maintenance task with current user as creator"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class BackupJobSerializer(serializers.ModelSerializer):
    """Serializer for backup jobs"""
    backup_type_display = serializers.CharField(source='get_backup_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    components_details = SystemComponentSerializer(source='components', many=True, read_only=True)
    formatted_size = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = BackupJob
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'started_at',
            'completed_at', 'success', 'duration',
            'backup_size', 'logs'
        ]
    
    def create(self, validated_data):
        """Create backup job with current user as creator"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class PerformanceMetricSerializer(serializers.ModelSerializer):
    """Serializer for performance metrics"""
    component_details = SystemComponentSerializer(source='component', read_only=True)
    is_healthy = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PerformanceMetric
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class KnowledgeBaseArticleSerializer(serializers.ModelSerializer):
    """Serializer for knowledge base articles"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    author_details = UserSerializer(source='author', read_only=True)
    reviewers_details = UserSerializer(source='reviewers', many=True, read_only=True)
    last_reviewed_by_details = UserSerializer(source='last_reviewed_by', read_only=True)
    last_updated_by_details = UserSerializer(source='last_updated_by', read_only=True)
    related_tickets_details = SupportTicketSerializer(source='related_tickets', many=True, read_only=True)
    related_components_details = SystemComponentSerializer(
        source='related_components', many=True, read_only=True
    )
    view_count_formatted = serializers.CharField(read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = KnowledgeBaseArticle
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'slug', 'views',
            'rating', 'helpful_count', 'not_helpful_count',
            'published_at', 'last_reviewed_at'
        ]
    
    def create(self, validated_data):
        """Create article with current user as author"""
        validated_data['author'] = self.context['request'].user
        validated_data['last_updated_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update article and track last updated by"""
        validated_data['last_updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class ArticleRatingSerializer(serializers.ModelSerializer):
    """Serializer for article ratings"""
    user_details = UserSerializer(source='user', read_only=True)
    article_title = serializers.CharField(source='article.title', read_only=True)
    
    class Meta:
        model = ArticleRating
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'user']
    
    def create(self, validated_data):
        """Create rating with current user"""
        validated_data['user'] = self.context['request'].user
        
        # Update article rating
        article = validated_data['article']
        if validated_data['helpful']:
            article.helpful_count += 1
        else:
            article.not_helpful_count += 1
        
        # Recalculate rating
        total_votes = article.helpful_count + article.not_helpful_count
        if total_votes > 0:
            article.rating = (article.helpful_count / total_votes) * 5
        
        article.save()
        
        return super().create(validated_data)


class ITResourceSerializer(serializers.ModelSerializer):
    """Serializer for IT resources"""
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    installed_on_details = SystemComponentSerializer(source='installed_on', read_only=True)
    is_under_warranty = serializers.BooleanField(read_only=True)
    age_in_months = serializers.IntegerField(read_only=True)
    requires_reorder = serializers.BooleanField(read_only=True)
    needs_maintenance = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ITResource
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'resource_code',
            'assigned_date', 'created_by'
        ]
    
    def create(self, validated_data):
        """Create resource with current user as creator"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ResourceLogSerializer(serializers.ModelSerializer):
    """Serializer for resource logs"""
    user_details = UserSerializer(source='user', read_only=True)
    resource_name = serializers.CharField(source='resource.name', read_only=True)
    
    class Meta:
        model = ResourceLog
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ITProjectSerializer(serializers.ModelSerializer):
    """Serializer for IT projects"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    project_manager_details = UserSerializer(source='project_manager', read_only=True)
    team_members_details = UserSerializer(source='team_members', many=True, read_only=True)
    stakeholders_details = UserSerializer(source='stakeholders', many=True, read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    resources_details = ITResourceSerializer(source='resources', many=True, read_only=True)
    components_details = SystemComponentSerializer(source='components', many=True, read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    budget_variance = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)
    
    class Meta:
        model = ITProject
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'project_code',
            'actual_start_date', 'actual_end_date', 'created_by'
        ]
    
    def create(self, validated_data):
        """Create project with current user as creator"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ITDashboardSerializer(serializers.ModelSerializer):
    """Serializer for IT dashboards"""
    dashboard_type_display = serializers.CharField(source='get_dashboard_type_display', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    allowed_users_details = UserSerializer(source='allowed_users', many=True, read_only=True)
    
    class Meta:
        model = ITDashboard
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'last_viewed', 'view_count']
    
    def create(self, validated_data):
        """Create dashboard with current user as creator"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)