# backend/apps/it/models.py
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from datetime import timedelta
from accounts.models import User


class BaseModel(models.Model):
    """Abstract base model with common fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class SystemComponent(BaseModel):
    """Model for tracking IT system components"""
    
    class ComponentType(models.TextChoices):
        SERVER = 'server', _('Server')
        DATABASE = 'database', _('Database')
        NETWORK = 'network', _('Network Device')
        STORAGE = 'storage', _('Storage System')
        SECURITY = 'security', _('Security System')
        WEB = 'web', _('Web Server')
        EMAIL = 'email', _('Email Server')
        BACKUP = 'backup', _('Backup System')
        VIRTUALIZATION = 'virtualization', _('Virtualization')
        MONITORING = 'monitoring', _('Monitoring System')
        WORKSTATION = 'workstation', _('Workstation')
        PRINTER = 'printer', _('Printer')
        SCANNER = 'scanner', _('Scanner')
        PROJECTOR = 'projector', _('Projector')
        UPS = 'ups', _('UPS')
        FIREWALL = 'firewall', _('Firewall')
        SWITCH = 'switch', _('Network Switch')
        ROUTER = 'router', _('Router')
        ACCESS_POINT = 'access_point', _('Wireless Access Point')
    
    class ComponentStatus(models.TextChoices):
        ONLINE = 'online', _('Online')
        OFFLINE = 'offline', _('Offline')
        DEGRADED = 'degraded', _('Degraded Performance')
        MAINTENANCE = 'maintenance', _('Under Maintenance')
        ERROR = 'error', _('Error')
        RETIRED = 'retired', _('Retired')
    
    class CriticalityLevel(models.TextChoices):
        CRITICAL = 'critical', _('Critical')
        HIGH = 'high', _('High')
        MEDIUM = 'medium', _('Medium')
        LOW = 'low', _('Low')

    # Basic Information
    name = models.CharField(max_length=100, verbose_name=_("Component Name"))
    component_code = models.CharField(max_length=50, unique=True, verbose_name=_("Component Code"))
    component_type = models.CharField(
        max_length=30, 
        choices=ComponentType.choices,
        verbose_name=_("Component Type")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    # Technical Specifications
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("IP Address"))
    hostname = models.CharField(max_length=100, blank=True, verbose_name=_("Hostname"))
    mac_address = models.CharField(max_length=17, blank=True, verbose_name=_("MAC Address"))
    serial_number = models.CharField(max_length=100, blank=True, verbose_name=_("Serial Number"))
    asset_tag = models.CharField(max_length=50, blank=True, verbose_name=_("Asset Tag"))
    
    manufacturer = models.CharField(max_length=100, blank=True, verbose_name=_("Manufacturer"))
    model = models.CharField(max_length=100, blank=True, verbose_name=_("Model"))
    os = models.CharField(max_length=100, blank=True, verbose_name=_("Operating System"))
    firmware_version = models.CharField(max_length=50, blank=True, verbose_name=_("Firmware Version"))
    
    # Hardware Specifications
    cpu_cores = models.IntegerField(default=1, verbose_name=_("CPU Cores"))
    memory_gb = models.IntegerField(default=1, verbose_name=_("Memory (GB)"))
    storage_gb = models.IntegerField(default=1, verbose_name=_("Storage (GB)"))
    processor = models.CharField(max_length=100, blank=True, verbose_name=_("Processor"))
    
    # Status and Monitoring
    status = models.CharField(
        max_length=20,
        choices=ComponentStatus.choices,
        default=ComponentStatus.ONLINE,
        verbose_name=_("Current Status")
    )
    criticality = models.CharField(
        max_length=20,
        choices=CriticalityLevel.choices,
        default=CriticalityLevel.MEDIUM,
        verbose_name=_("Criticality Level")
    )
    is_monitored = models.BooleanField(default=True, verbose_name=_("Is Monitored"))
    last_check = models.DateTimeField(default=timezone.now, verbose_name=_("Last Status Check"))
    uptime = models.DurationField(null=True, blank=True, verbose_name=_("Uptime"))
    
    # Location Information
    location = models.CharField(max_length=200, blank=True, verbose_name=_("Location"))
    building = models.CharField(max_length=100, blank=True, verbose_name=_("Building"))
    room = models.CharField(max_length=50, blank=True, verbose_name=_("Room"))
    rack = models.CharField(max_length=50, blank=True, verbose_name=_("Rack"))
    rack_unit = models.IntegerField(null=True, blank=True, verbose_name=_("Rack Unit"))
    
    # Ownership and Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_components',
        verbose_name=_("Assigned To")
    )
    department = models.CharField(max_length=100, blank=True, verbose_name=_("Department"))
    
    # Purchase Information
    purchase_date = models.DateField(null=True, blank=True, verbose_name=_("Purchase Date"))
    warranty_expiry = models.DateField(null=True, blank=True, verbose_name=_("Warranty Expiry"))
    purchase_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name=_("Purchase Price")
    )
    vendor = models.CharField(max_length=100, blank=True, verbose_name=_("Vendor"))
    
    # Maintenance Information
    last_maintenance = models.DateField(null=True, blank=True, verbose_name=_("Last Maintenance"))
    next_maintenance = models.DateField(null=True, blank=True, verbose_name=_("Next Maintenance"))
    maintenance_schedule = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('weekly', _('Weekly')),
            ('monthly', _('Monthly')),
            ('quarterly', _('Quarterly')),
            ('biannual', _('Biannual')),
            ('annual', _('Annual')),
        ],
        verbose_name=_("Maintenance Schedule")
    )
    
    # Monitoring URLs
    monitoring_url = models.URLField(blank=True, verbose_name=_("Monitoring URL"))
    management_url = models.URLField(blank=True, verbose_name=_("Management URL"))
    documentation_url = models.URLField(blank=True, verbose_name=_("Documentation URL"))
    
    # Alert Configuration
    alert_email = models.EmailField(blank=True, verbose_name=_("Alert Email"))
    alert_threshold_cpu = models.IntegerField(default=80, verbose_name=_("CPU Alert Threshold (%)"))
    alert_threshold_memory = models.IntegerField(default=85, verbose_name=_("Memory Alert Threshold (%)"))
    alert_threshold_disk = models.IntegerField(default=90, verbose_name=_("Disk Alert Threshold (%)"))
    
    # Dependencies
    dependencies = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='dependents',
        verbose_name=_("Dependencies")
    )
    
    # Custom fields
    custom_fields = models.JSONField(default=dict, blank=True, verbose_name=_("Custom Fields"))
    tags = models.JSONField(default=list, blank=True, verbose_name=_("Tags"))
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_components',
        verbose_name=_("Created By")
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    class Meta:
        verbose_name = _("System Component")
        verbose_name_plural = _("System Components")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['component_type']),
            models.Index(fields=['status']),
            models.Index(fields=['criticality']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['hostname']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['department']),
            models.Index(fields=['location']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_component_type_display()})"

    def save(self, *args, **kwargs):
        """Auto-generate component code if not provided"""
        if not self.component_code:
            prefix = {
                'server': 'SRV',
                'workstation': 'WS',
                'printer': 'PRT',
                'network': 'NET',
                'storage': 'STR',
                'security': 'SEC',
                'database': 'DB',
                'web': 'WEB',
                'email': 'EML',
                'backup': 'BKP',
            }.get(self.component_type, 'CMP')
            
            year = timezone.now().year
            last_component = SystemComponent.objects.filter(
                component_code__startswith=f'{prefix}-{year}-'
            ).order_by('-component_code').first()
            
            next_number = 1
            if last_component:
                try:
                    last_number = int(last_component.component_code.split('-')[-1])
                    next_number = last_number + 1
                except (ValueError, IndexError):
                    pass
            
            self.component_code = f"{prefix}-{year}-{next_number:04d}"
        
        super().save(*args, **kwargs)

    def update_status(self, status, notes=''):
        """Update component status"""
        old_status = self.status
        self.status = status
        self.last_check = timezone.now()
        self.save(update_fields=['status', 'last_check', 'updated_at'])
        
        # Log the status change
        ComponentStatusLog.objects.create(
            component=self,
            old_status=old_status,
            new_status=status,
            changed_by=self.assigned_to,
            notes=notes
        )
        
        # Create alert for status changes to offline or error
        if status in [self.ComponentStatus.OFFLINE, self.ComponentStatus.ERROR]:
            SystemAlert.objects.create(
                title=f"Component Status Changed: {self.name}",
                message=f"Component {self.name} changed from {old_status} to {status}",
                severity=SystemAlert.AlertSeverity.CRITICAL if status == self.ComponentStatus.OFFLINE else SystemAlert.AlertSeverity.ERROR,
                component=self,
                source='status_monitor',
                detected_at=timezone.now()
            )

    @property
    def is_healthy(self):
        """Check if component is healthy"""
        return self.status == self.ComponentStatus.ONLINE

    @property
    def is_under_warranty(self):
        """Check if component is under warranty"""
        if not self.warranty_expiry:
            return False
        return self.warranty_expiry >= timezone.now().date()

    @property
    def age_in_months(self):
        """Calculate component age in months"""
        if not self.purchase_date:
            return 0
        today = timezone.now().date()
        months = (today.year - self.purchase_date.year) * 12 + today.month - self.purchase_date.month
        return max(0, months)

    @property
    def requires_maintenance(self):
        """Check if maintenance is due"""
        if not self.next_maintenance:
            return False
        return self.next_maintenance <= timezone.now().date()

    def schedule_maintenance(self, date, notes=''):
        """Schedule next maintenance"""
        self.next_maintenance = date
        if notes:
            self.notes = f"{self.notes}\nMaintenance scheduled for {date}: {notes}"
        self.save()
        
        MaintenanceTask.objects.create(
            title=f"Scheduled Maintenance for {self.name}",
            description=f"Routine maintenance for {self.name}",
            task_type=MaintenanceTask.TaskType.SCHEDULED,
            scheduled_start=date,
            scheduled_end=date + timedelta(hours=2),
            priority='medium',
            affected_components=[self],
            notes=notes
        )


class ComponentStatusLog(BaseModel):
    """Log of component status changes"""
    component = models.ForeignKey(
        SystemComponent, 
        on_delete=models.CASCADE,
        related_name='status_logs'
    )
    old_status = models.CharField(max_length=20, verbose_name=_("Old Status"))
    new_status = models.CharField(max_length=20, verbose_name=_("New Status"))
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='component_status_changes'
    )
    notes = models.TextField(blank=True)
    checked_at = models.DateTimeField(default=timezone.now)
    response_time = models.FloatField(null=True, blank=True, verbose_name=_("Response Time (ms)"))

    class Meta:
        verbose_name = _("Component Status Log")
        verbose_name_plural = _("Component Status Logs")
        ordering = ['-checked_at']
        indexes = [
            models.Index(fields=['component', 'checked_at']),
            models.Index(fields=['new_status']),
        ]

    def __str__(self):
        return f"{self.component.name}: {self.old_status} → {self.new_status} at {self.checked_at}"


class SupportTicket(BaseModel):
    """Model for IT support tickets"""
    
    class TicketCategory(models.TextChoices):
        HARDWARE = 'hardware', _('Hardware')
        SOFTWARE = 'software', _('Software')
        NETWORK = 'network', _('Network')
        SECURITY = 'security', _('Security')
        DATABASE = 'database', _('Database')
        EMAIL = 'email', _('Email')
        BACKUP = 'backup', _('Backup')
        PRINTING = 'printing', _('Printing')
        ACCOUNT = 'account', _('Account')
        PERMISSIONS = 'permissions', _('Permissions')
        ACCESS = 'access', _('Access')
        OTHER = 'other', _('Other')
    
    class TicketPriority(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')
        CRITICAL = 'critical', _('Critical')
    
    class TicketStatus(models.TextChoices):
        OPEN = 'open', _('Open')
        IN_PROGRESS = 'in-progress', _('In Progress')
        ON_HOLD = 'on-hold', _('On Hold')
        RESOLVED = 'resolved', _('Resolved')
        CLOSED = 'closed', _('Closed')
        CANCELLED = 'cancelled', _('Cancelled')

    # Ticket Information
    ticket_number = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name=_("Ticket Number")
    )
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    
    # Classification
    category = models.CharField(
        max_length=20,
        choices=TicketCategory.choices,
        verbose_name=_("Category")
    )
    priority = models.CharField(
        max_length=20,
        choices=TicketPriority.choices,
        default=TicketPriority.MEDIUM,
        verbose_name=_("Priority")
    )
    status = models.CharField(
        max_length=20,
        choices=TicketStatus.choices,
        default=TicketStatus.OPEN,
        verbose_name=_("Status")
    )
    
    # People Involved
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tickets',
        verbose_name=_("Created By")
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name=_("Assigned To")
    )
    reported_by_name = models.CharField(max_length=100, blank=True, verbose_name=_("Reported By Name"))
    reported_by_email = models.EmailField(blank=True, verbose_name=_("Reported By Email"))
    reported_by_phone = models.CharField(max_length=20, blank=True, verbose_name=_("Reported By Phone"))
    
    # Dates
    due_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Due Date"))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Resolved At"))
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Closed At"))
    first_response_at = models.DateTimeField(null=True, blank=True, verbose_name=_("First Response At"))
    
    # SLA Information
    sla_target = models.DurationField(null=True, blank=True, verbose_name=_("SLA Target"))
    sla_status = models.CharField(
        max_length=20,
        choices=[
            ('within_sla', _('Within SLA')),
            ('breached', _('SLA Breached')),
            ('warning', _('SLA Warning')),
        ],
        default='within_sla',
        verbose_name=_("SLA Status")
    )
    
    # Related Items
    affected_components = models.ManyToManyField(
        SystemComponent,
        blank=True,
        related_name='tickets',
        verbose_name=_("Affected Components")
    )
    related_tickets = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name=_("Related Tickets")
    )
    
    # Time Tracking
    estimated_time = models.DurationField(null=True, blank=True, verbose_name=_("Estimated Resolution Time"))
    actual_time = models.DurationField(null=True, blank=True, verbose_name=_("Actual Resolution Time"))
    time_spent = models.DurationField(null=True, blank=True, verbose_name=_("Time Spent"))
    
    # Additional Information
    attachments = models.JSONField(default=list, blank=True, verbose_name=_("Attachments"))
    tags = models.JSONField(default=list, blank=True, verbose_name=_("Tags"))
    impact = models.TextField(blank=True, verbose_name=_("Impact"))
    resolution = models.TextField(blank=True, verbose_name=_("Resolution"))
    resolution_notes = models.TextField(blank=True, verbose_name=_("Resolution Notes"))
    feedback_score = models.IntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Feedback Score")
    )
    feedback_comments = models.TextField(blank=True, verbose_name=_("Feedback Comments"))

    class Meta:
        verbose_name = _("Support Ticket")
        verbose_name_plural = _("Support Tickets")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ticket_number']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['category']),
            models.Index(fields=['created_by']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['due_date']),
            models.Index(fields=['sla_status']),
        ]

    def __str__(self):
        return f"{self.ticket_number}: {self.title}"

    def save(self, *args, **kwargs):
        # Generate ticket number if not set
        if not self.ticket_number:
            year = timezone.now().year
            last_ticket = SupportTicket.objects.filter(
                ticket_number__startswith=f'TKT-{year}-'
            ).order_by('-ticket_number').first()
            
            next_number = 1
            if last_ticket:
                try:
                    last_number = int(last_ticket.ticket_number.split('-')[-1])
                    next_number = last_number + 1
                except (ValueError, IndexError):
                    pass
            
            self.ticket_number = f"TKT-{year}-{next_number:04d}"
        
        # Update timestamps based on status changes
        if self.pk:
            original = SupportTicket.objects.get(pk=self.pk)
            
            if original.status != self.status:
                if self.status == self.TicketStatus.IN_PROGRESS and not self.assigned_to:
                    # Auto-assign to IT support staff
                    it_staff = User.objects.filter(
                        role=User.Role.IT_SUPPORT,
                        is_active=True
                    ).first()
                    if it_staff:
                        self.assigned_to = it_staff
                
                if self.status == self.TicketStatus.RESOLVED and not self.resolved_at:
                    self.resolved_at = timezone.now()
                    if self.time_spent and self.estimated_time:
                        # Calculate SLA status
                        self.update_sla_status()
                
                elif self.status == self.TicketStatus.CLOSED and not self.closed_at:
                    self.closed_at = timezone.now()
        
        # Update due date based on priority if not set
        if not self.due_date and self.priority:
            due_days = {
                'critical': 1,  # 1 day
                'high': 3,      # 3 days
                'medium': 7,    # 1 week
                'low': 14,      # 2 weeks
            }
            days = due_days.get(self.priority, 7)
            self.due_date = timezone.now() + timedelta(days=days)
        
        super().save(*args, **kwargs)

    def update_sla_status(self):
        """Update SLA status based on resolution time"""
        if not self.resolved_at or not self.sla_target:
            return
        
        resolution_time = self.resolved_at - self.created_at
        
        if resolution_time <= self.sla_target:
            self.sla_status = 'within_sla'
        elif resolution_time <= self.sla_target * 1.5:
            self.sla_status = 'warning'
        else:
            self.sla_status = 'breached'
        
        self.save(update_fields=['sla_status'])

    @property
    def is_overdue(self):
        """Check if ticket is overdue"""
        if self.due_date and self.status not in [self.TicketStatus.RESOLVED, self.TicketStatus.CLOSED, self.TicketStatus.CANCELLED]:
            return timezone.now() > self.due_date
        return False

    @property
    def age_in_days(self):
        """Calculate ticket age in days"""
        return (timezone.now() - self.created_at).days

    @property
    def time_to_first_response(self):
        """Calculate time to first response"""
        if self.first_response_at:
            return self.first_response_at - self.created_at
        return None

    def assign_to_user(self, user):
        """Assign ticket to specific user"""
        self.assigned_to = user
        self.status = self.TicketStatus.IN_PROGRESS
        self.save()
        
        # Add comment about assignment
        TicketComment.objects.create(
            ticket=self,
            user=user,
            comment=f"Ticket assigned to {user.get_full_name()}",
            is_internal=True
        )

    def add_time_entry(self, user, hours, description):
        """Add time entry to ticket"""
        if not self.time_spent:
            self.time_spent = timedelta()
        
        self.time_spent += timedelta(hours=hours)
        self.save()
        
        # Create time entry record
        TimeEntry.objects.create(
            ticket=self,
            user=user,
            hours=hours,
            description=description
        )


class TicketComment(BaseModel):
    """Comments on support tickets"""
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ticket_comments'
    )
    comment = models.TextField(verbose_name=_("Comment"))
    is_internal = models.BooleanField(default=False, verbose_name=_("Internal Note"))
    attachments = models.JSONField(default=list, blank=True, verbose_name=_("Attachments"))
    mentions = models.ManyToManyField(
        User,
        blank=True,
        related_name='mentioned_in_comments',
        verbose_name=_("Mentioned Users")
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = _("Ticket Comment")
        verbose_name_plural = _("Ticket Comments")
        indexes = [
            models.Index(fields=['ticket', 'created_at']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Comment on {self.ticket.ticket_number} by {self.user}"

    def save(self, *args, **kwargs):
        # Update ticket's first response timestamp if this is the first comment
        if not self.ticket.first_response_at and self.user != self.ticket.created_by:
            self.ticket.first_response_at = timezone.now()
            self.ticket.save(update_fields=['first_response_at'])
        
        super().save(*args, **kwargs)


class TimeEntry(BaseModel):
    """Time entries for ticket work"""
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='time_entries'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='time_entries'
    )
    hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        verbose_name=_("Hours")
    )
    description = models.TextField(verbose_name=_("Description"))
    date_worked = models.DateField(default=timezone.now, verbose_name=_("Date Worked"))
    billable = models.BooleanField(default=True, verbose_name=_("Billable"))

    class Meta:
        verbose_name = _("Time Entry")
        verbose_name_plural = _("Time Entries")
        ordering = ['-date_worked']
        indexes = [
            models.Index(fields=['ticket', 'date_worked']),
            models.Index(fields=['user', 'date_worked']),
        ]

    def __str__(self):
        return f"{self.hours}h on {self.ticket.ticket_number} by {self.user}"


class SystemAlert(BaseModel):
    """System alerts and notifications"""
    
    class AlertSeverity(models.TextChoices):
        INFO = 'info', _('Information')
        WARNING = 'warning', _('Warning')
        ERROR = 'error', _('Error')
        CRITICAL = 'critical', _('Critical')
    
    class AlertStatus(models.TextChoices):
        ACTIVE = 'active', _('Active')
        ACKNOWLEDGED = 'acknowledged', _('Acknowledged')
        RESOLVED = 'resolved', _('Resolved')
        DISMISSED = 'dismissed', _('Dismissed')

    # Alert Information
    title = models.CharField(max_length=200, verbose_name=_("Alert Title"))
    message = models.TextField(verbose_name=_("Alert Message"))
    
    # Alert Details
    severity = models.CharField(
        max_length=20,
        choices=AlertSeverity.choices,
        default=AlertSeverity.INFO,
        verbose_name=_("Severity")
    )
    status = models.CharField(
        max_length=20,
        choices=AlertStatus.choices,
        default=AlertStatus.ACTIVE,
        verbose_name=_("Status")
    )
    
    # Source Information
    source = models.CharField(max_length=100, verbose_name=_("Alert Source"))
    component = models.ForeignKey(
        SystemComponent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    
    # Timing Information
    detected_at = models.DateTimeField(default=timezone.now, verbose_name=_("Detected At"))
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Acknowledged At"))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Resolved At"))
    
    # Alert Data
    alert_data = models.JSONField(default=dict, blank=True, verbose_name=_("Alert Data"))
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_alerts'
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_alerts'
    )

    class Meta:
        verbose_name = _("System Alert")
        verbose_name_plural = _("System Alerts")
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['severity']),
            models.Index(fields=['status']),
            models.Index(fields=['detected_at']),
            models.Index(fields=['component']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"{self.get_severity_display()}: {self.title}"

    def acknowledge(self, user=None, notes=''):
        """Acknowledge the alert"""
        self.status = self.AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = timezone.now()
        self.assigned_to = user or self.assigned_to
        self.save()
        
        # Log the acknowledgment
        AlertLog.objects.create(
            alert=self,
            action='acknowledged',
            user=user,
            notes=notes
        )
        
        # Create support ticket for critical alerts
        if self.severity in [self.AlertSeverity.ERROR, self.AlertSeverity.CRITICAL] and not self.ticket:
            ticket = SupportTicket.objects.create(
                title=f"Alert: {self.title}",
                description=self.message,
                category=SupportTicket.TicketCategory.SECURITY if 'security' in self.source.lower() else SupportTicket.TicketCategory.HARDWARE,
                priority=SupportTicket.TicketPriority.HIGH if self.severity == self.AlertSeverity.CRITICAL else SupportTicket.TicketPriority.MEDIUM,
                created_by=user,
                assigned_to=user,
                status=SupportTicket.TicketStatus.IN_PROGRESS
            )
            self.ticket = ticket
            self.save()

    def resolve(self, resolution_notes='', user=None):
        """Resolve the alert"""
        self.status = self.AlertStatus.RESOLVED
        self.resolved_at = timezone.now()
        self.save()
        
        # Log the resolution
        AlertLog.objects.create(
            alert=self,
            action='resolved',
            notes=resolution_notes,
            user=user
        )
        
        # Resolve associated ticket if exists
        if self.ticket and self.ticket.status not in [SupportTicket.TicketStatus.RESOLVED, SupportTicket.TicketStatus.CLOSED]:
            self.ticket.status = SupportTicket.TicketStatus.RESOLVED
            self.ticket.resolution_notes = f"Alert resolved: {resolution_notes}"
            self.ticket.save()

    def dismiss(self, user=None, notes=''):
        """Dismiss the alert"""
        self.status = self.AlertStatus.DISMISSED
        self.resolved_at = timezone.now()
        self.save()
        
        AlertLog.objects.create(
            alert=self,
            action='dismissed',
            notes=notes,
            user=user
        )

    @property
    def duration(self):
        """Calculate alert duration"""
        end_time = self.resolved_at or timezone.now()
        return end_time - self.detected_at

    @property
    def requires_action(self):
        """Check if alert requires action"""
        return self.status == self.AlertStatus.ACTIVE and self.severity in [self.AlertSeverity.ERROR, self.AlertSeverity.CRITICAL]


class AlertLog(BaseModel):
    """Log of alert actions"""
    alert = models.ForeignKey(
        SystemAlert,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=50, verbose_name=_("Action"))
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("Alert Log")
        verbose_name_plural = _("Alert Logs")
        indexes = [
            models.Index(fields=['alert', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.action} on {self.alert.title} at {self.timestamp}"


class MaintenanceTask(BaseModel):  # Changed from models.Model
    """Scheduled maintenance tasks"""
    
    class TaskType(models.TextChoices):
        SCHEDULED = 'scheduled', _('Scheduled Maintenance')
        EMERGENCY = 'emergency', _('Emergency Maintenance')
        UPGRADE = 'upgrade', _('System Upgrade')
        PATCH = 'patch', _('Security Patch')
        BACKUP = 'backup', _('Backup Maintenance')
        CLEANUP = 'cleanup', _('System Cleanup')
        REPAIR = 'repair', _('Repair')
        INSTALLATION = 'installation', _('Installation')
    
    class TaskStatus(models.TextChoices):
        SCHEDULED = 'scheduled', _('Scheduled')
        IN_PROGRESS = 'in-progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
        FAILED = 'failed', _('Failed')
    
    class ImpactLevel(models.TextChoices):
        LOW = 'low', _('Low (No downtime)')
        MEDIUM = 'medium', _('Medium (Limited downtime)')
        HIGH = 'high', _('High (Service interruption)')
        CRITICAL = 'critical', _('Critical (Extended downtime)')

    # Task Information
    task_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Task Number")
    )
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    
    # Classification
    task_type = models.CharField(
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.SCHEDULED,
        verbose_name=_("Task Type")
    )
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.SCHEDULED,
        verbose_name=_("Status")
    )
    impact_level = models.CharField(
        max_length=20,
        choices=ImpactLevel.choices,
        default=ImpactLevel.MEDIUM,
        verbose_name=_("Impact Level")
    )
    
    # Scheduling
    scheduled_start = models.DateTimeField(verbose_name=_("Scheduled Start"))
    scheduled_end = models.DateTimeField(verbose_name=_("Scheduled End"))
    actual_start = models.DateTimeField(null=True, blank=True, verbose_name=_("Actual Start"))
    actual_end = models.DateTimeField(null=True, blank=True, verbose_name=_("Actual End"))
    
    # Related Components
    affected_components = models.ManyToManyField(
        'SystemComponent',
        related_name='maintenance_tasks',
        verbose_name=_("Affected Components")
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_tasks'
    )
    team_members = models.ManyToManyField(
        User,
        blank=True,
        related_name='team_maintenance_tasks',
        verbose_name=_("Team Members")
    )
    
    # Planning Information
    prerequisites = models.TextField(blank=True, verbose_name=_("Prerequisites"))
    steps = models.JSONField(default=list, blank=True, verbose_name=_("Steps"))
    rollback_plan = models.TextField(blank=True, verbose_name=_("Rollback Plan"))
    risk_assessment = models.TextField(blank=True, verbose_name=_("Risk Assessment"))
    
    # Communication
    notify_users = models.BooleanField(default=True, verbose_name=_("Notify Users"))
    notification_sent = models.BooleanField(default=False, verbose_name=_("Notification Sent"))
    notification_sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Notification Sent At"))
    
    # Results
    outcome = models.TextField(blank=True, verbose_name=_("Outcome"))
    issues_encountered = models.TextField(blank=True, verbose_name=_("Issues Encountered"))
    lessons_learned = models.TextField(blank=True, verbose_name=_("Lessons Learned"))
    
    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_maintenance_tasks'
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved At"))
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_maintenance_tasks'
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    class Meta:
        verbose_name = _("Maintenance Task")
        verbose_name_plural = _("Maintenance Tasks")
        ordering = ['-scheduled_start']
        indexes = [
            models.Index(fields=['task_number']),
            models.Index(fields=['status']),
            models.Index(fields=['task_type']),
            models.Index(fields=['scheduled_start']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"{self.task_number}: {self.title}"

    def save(self, *args, **kwargs):
        # Generate task number if not set
        if not self.task_number:
            year = timezone.now().year
            last_task = MaintenanceTask.objects.filter(
                task_number__startswith=f'MT-{year}-'
            ).order_by('-task_number').first()
            
            next_number = 1
            if last_task:
                try:
                    last_number = int(last_task.task_number.split('-')[-1])
                    next_number = last_number + 1
                except (ValueError, IndexError):
                    pass
            
            self.task_number = f"MT-{year}-{next_number:04d}"
        
        super().save(*args, **kwargs)

    def start_task(self, user=None):
        """Start the maintenance task"""
        self.status = self.TaskStatus.IN_PROGRESS
        self.actual_start = timezone.now()
        if user:
            self.assigned_to = user
        self.save()

    def complete_task(self, outcome='', issues='', lessons_learned=''):
        """Complete the maintenance task"""
        self.status = self.TaskStatus.COMPLETED
        self.actual_end = timezone.now()
        self.outcome = outcome
        self.issues_encountered = issues
        self.lessons_learned = lessons_learned
        self.save()
        
        # Update affected components' maintenance dates
        for component in self.affected_components.all():
            component.last_maintenance = timezone.now().date()
            component.save()

    def cancel_task(self, reason=''):
        """Cancel the maintenance task"""
        self.status = self.TaskStatus.CANCELLED
        self.notes = f"{self.notes}\nCancelled: {reason}"
        self.save()

    @property
    def duration(self):
        """Calculate task duration"""
        if self.actual_start and self.actual_end:
            return self.actual_end - self.actual_start
        elif self.actual_start:
            return timezone.now() - self.actual_start
        return self.scheduled_end - self.scheduled_start

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.status == self.TaskStatus.SCHEDULED:
            return timezone.now() > self.scheduled_start
        return False

    @property
    def is_active(self):
        """Check if task is currently active"""
        if self.status == self.TaskStatus.IN_PROGRESS:
            return True
        if self.status == self.TaskStatus.SCHEDULED:
            now = timezone.now()
            return self.scheduled_start <= now <= self.scheduled_end
        return False

    def send_notification(self):
        """Send notification about maintenance"""
        if not self.notify_users or self.notification_sent:
            return
        
        # In production, this would send actual notifications
        self.notification_sent = True
        self.notification_sent_at = timezone.now()
        self.save()


class BackupJob(BaseModel):
    """Backup job tracking"""
    
    class BackupType(models.TextChoices):
        FULL = 'full', _('Full Backup')
        INCREMENTAL = 'incremental', _('Incremental Backup')
        DIFFERENTIAL = 'differential', _('Differential Backup')
        DATABASE = 'database', _('Database Backup')
        CONFIGURATION = 'configuration', _('Configuration Backup')
        FILE = 'file', _('File Backup')
    
    class BackupStatus(models.TextChoices):
        SCHEDULED = 'scheduled', _('Scheduled')
        RUNNING = 'running', _('Running')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        CANCELLED = 'cancelled', _('Cancelled')
        VERIFYING = 'verifying', _('Verifying')

    # Job Information
    job_name = models.CharField(max_length=200, verbose_name=_("Job Name"))
    backup_type = models.CharField(
        max_length=20,
        choices=BackupType.choices,
        default=BackupType.FULL,
        verbose_name=_("Backup Type")
    )
    status = models.CharField(
        max_length=20,
        choices=BackupStatus.choices,
        default=BackupStatus.SCHEDULED,
        verbose_name=_("Status")
    )
    
    # Source and Destination
    source_path = models.TextField(verbose_name=_("Source Path"))
    destination_path = models.TextField(verbose_name=_("Destination Path"))
    source_type = models.CharField(
        max_length=50,
        choices=[
            ('filesystem', _('File System')),
            ('database', _('Database')),
            ('virtual_machine', _('Virtual Machine')),
            ('configuration', _('Configuration')),
        ],
        default='filesystem',
        verbose_name=_("Source Type")
    )
    
    # Scheduling
    scheduled_time = models.DateTimeField(verbose_name=_("Scheduled Time"))
    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Started At"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed At"))
    
    # Results
    backup_size = models.BigIntegerField(null=True, blank=True, verbose_name=_("Backup Size (bytes)"))
    duration = models.DurationField(null=True, blank=True, verbose_name=_("Duration"))
    success = models.BooleanField(default=False, verbose_name=_("Success"))
    
    # Verification
    verification_status = models.BooleanField(null=True, blank=True, verbose_name=_("Verification Status"))
    verification_notes = models.TextField(blank=True, verbose_name=_("Verification Notes"))
    checksum = models.CharField(max_length=100, blank=True, verbose_name=_("Checksum"))
    
    # Error Handling
    error_message = models.TextField(blank=True, verbose_name=_("Error Message"))
    retry_count = models.IntegerField(default=0, verbose_name=_("Retry Count"))
    max_retries = models.IntegerField(default=3, verbose_name=_("Max Retries"))
    
    # Retention
    retention_days = models.IntegerField(default=30, verbose_name=_("Retention Days"))
    
    # Related Components
    components = models.ManyToManyField(
        SystemComponent,
        related_name='backup_jobs',
        blank=True,
        verbose_name=_("Components")
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_backup_jobs'
    )
    logs = models.TextField(blank=True, verbose_name=_("Logs"))

    class Meta:
        verbose_name = _("Backup Job")
        verbose_name_plural = _("Backup Jobs")
        ordering = ['-scheduled_time']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['backup_type']),
            models.Index(fields=['scheduled_time']),
            models.Index(fields=['success']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.job_name} ({self.get_backup_type_display()})"

    def start_backup(self, user=None):
        """Start the backup job"""
        self.status = self.BackupStatus.RUNNING
        self.started_at = timezone.now()
        if user:
            self.created_by = user
        self.save()
        
        # Log the start
        self.logs = f"{self.logs}\n[{timezone.now()}] Backup started by {user if user else 'System'}\n"
        self.save(update_fields=['logs'])

    def complete_backup(self, success=True, error_message='', backup_size=None, duration=None, checksum=''):
        """Complete the backup job"""
        self.status = self.BackupStatus.VERIFYING if success else self.BackupStatus.FAILED
        self.completed_at = timezone.now()
        self.success = success
        self.error_message = error_message
        self.backup_size = backup_size
        self.duration = duration
        self.checksum = checksum
        
        if success:
            self.logs = f"{self.logs}\n[{timezone.now()}] Backup completed successfully"
        else:
            self.logs = f"{self.logs}\n[{timezone.now()}] Backup failed: {error_message}"
        
        self.save()

    def verify_backup(self, status=True, notes=''):
        """Verify backup completion"""
        self.verification_status = status
        self.verification_notes = notes
        
        if status:
            self.status = self.BackupStatus.COMPLETED
            self.logs = f"{self.logs}\n[{timezone.now()}] Backup verified: {notes}"
        else:
            self.status = self.BackupStatus.FAILED
            self.logs = f"{self.logs}\n[{timezone.now()}] Backup verification failed: {notes}"
        
        self.save()

    def retry_backup(self):
        """Retry failed backup"""
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            self.status = self.BackupStatus.SCHEDULED
            self.scheduled_time = timezone.now() + timedelta(minutes=30)  # Retry in 30 minutes
            self.save()
            return True
        return False

    @property
    def is_overdue(self):
        """Check if backup is overdue"""
        if self.status == self.BackupStatus.SCHEDULED:
            return timezone.now() > self.scheduled_time
        return False

    @property
    def formatted_size(self):
        """Format backup size in human-readable format"""
        if not self.backup_size:
            return "N/A"
        
        size = self.backup_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    @property
    def is_expired(self):
        """Check if backup should be expired based on retention policy"""
        if not self.completed_at:
            return False
        return timezone.now() > self.completed_at + timedelta(days=self.retention_days)


class PerformanceMetric(BaseModel):
    """System performance metrics"""
    component = models.ForeignKey(
        SystemComponent,
        on_delete=models.CASCADE,
        related_name='performance_metrics'
    )
    
    # Metrics
    cpu_usage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("CPU Usage (%)")
    )
    memory_usage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Memory Usage (%)")
    )
    disk_usage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Disk Usage (%)")
    )
    network_in = models.FloatField(verbose_name=_("Network In (Mbps)"))
    network_out = models.FloatField(verbose_name=_("Network Out (Mbps)"))
    
    # Response times
    response_time = models.FloatField(verbose_name=_("Response Time (ms)"))
    uptime = models.FloatField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Uptime (%)")
    )
    
    # Timestamp
    timestamp = models.DateTimeField(default=timezone.now, verbose_name=_("Timestamp"))
    
    # Additional data
    processes = models.IntegerField(default=0, verbose_name=_("Running Processes"))
    connections = models.IntegerField(default=0, verbose_name=_("Active Connections"))
    disk_read = models.FloatField(default=0, verbose_name=_("Disk Read (MB/s)"))
    disk_write = models.FloatField(default=0, verbose_name=_("Disk Write (MB/s)"))
    
    # Temperature (for servers)
    temperature = models.FloatField(null=True, blank=True, verbose_name=_("Temperature (°C)"))
    
    # Power consumption
    power_usage = models.FloatField(null=True, blank=True, verbose_name=_("Power Usage (W)"))

    class Meta:
        verbose_name = _("Performance Metric")
        verbose_name_plural = _("Performance Metrics")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['component', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['cpu_usage']),
            models.Index(fields=['memory_usage']),
        ]

    def __str__(self):
        return f"Metrics for {self.component.name} at {self.timestamp}"

    @property
    def is_healthy(self):
        """Check if metrics indicate healthy system"""
        return (
            self.cpu_usage < self.component.alert_threshold_cpu and
            self.memory_usage < self.component.alert_threshold_memory and
            self.disk_usage < self.component.alert_threshold_disk and
            self.uptime > 99.5
        )

    @classmethod
    def get_daily_average(cls, component, date):
        """Get daily average metrics for a component"""
        metrics = cls.objects.filter(
            component=component,
            timestamp__date=date
        )
        
        if not metrics.exists():
            return None
        
        avg_data = {
            'cpu_usage': metrics.aggregate(avg=models.Avg('cpu_usage'))['avg'],
            'memory_usage': metrics.aggregate(avg=models.Avg('memory_usage'))['avg'],
            'disk_usage': metrics.aggregate(avg=models.Avg('disk_usage'))['avg'],
            'network_in': metrics.aggregate(avg=models.Avg('network_in'))['avg'],
            'network_out': metrics.aggregate(avg=models.Avg('network_out'))['avg'],
            'response_time': metrics.aggregate(avg=models.Avg('response_time'))['avg'],
            'count': metrics.count()
        }
        
        return avg_data


class KnowledgeBaseArticle(BaseModel):
    """IT knowledge base articles"""
    
    class ArticleCategory(models.TextChoices):
        TROUBLESHOOTING = 'troubleshooting', _('Troubleshooting')
        HOW_TO = 'how_to', _('How-to Guides')
        BEST_PRACTICES = 'best_practices', _('Best Practices')
        REFERENCE = 'reference', _('Reference')
        FAQ = 'faq', _('FAQ')
        POLICY = 'policy', _('Policy')
        PROCEDURE = 'procedure', _('Procedure')
        SECURITY = 'security', _('Security')
        NETWORK = 'network', _('Network')
        SERVER = 'server', _('Server')
    
    class ArticleStatus(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        REVIEW = 'review', _('Under Review')
        PUBLISHED = 'published', _('Published')
        ARCHIVED = 'archived', _('Archived')
        DEPRECATED = 'deprecated', _('Deprecated')

    # Article Information
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_("Slug"))
    content = models.TextField(verbose_name=_("Content"))
    summary = models.TextField(blank=True, verbose_name=_("Summary"))
    
    # Classification
    category = models.CharField(
        max_length=20,
        choices=ArticleCategory.choices,
        verbose_name=_("Category")
    )
    status = models.CharField(
        max_length=20,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT,
        verbose_name=_("Status")
    )
    
    # Metadata
    tags = models.JSONField(default=list, blank=True, verbose_name=_("Tags"))
    views = models.IntegerField(default=0, verbose_name=_("Views"))
    rating = models.FloatField(default=0, verbose_name=_("Rating"))
    helpful_count = models.IntegerField(default=0, verbose_name=_("Helpful Count"))
    not_helpful_count = models.IntegerField(default=0, verbose_name=_("Not Helpful Count"))
    
    # Related Items
    related_tickets = models.ManyToManyField(
        SupportTicket,
        blank=True,
        related_name='knowledge_base_articles'
    )
    related_components = models.ManyToManyField(
        SystemComponent,
        blank=True,
        related_name='knowledge_base_articles'
    )
    
    # Authorship
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='authored_articles'
    )
    reviewers = models.ManyToManyField(
        User,
        blank=True,
        related_name='reviewed_articles'
    )
    last_reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='last_reviewed_articles'
    )
    
    # Dates
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Published At"))
    last_reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Last Reviewed At"))
    last_updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_articles'
    )
    
    # Attachments
    attachments = models.JSONField(default=list, blank=True, verbose_name=_("Attachments"))

    class Meta:
        verbose_name = _("Knowledge Base Article")
        verbose_name_plural = _("Knowledge Base Articles")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['slug']),
            models.Index(fields=['author']),
            models.Index(fields=['views']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
            
            # Ensure slug uniqueness
            original_slug = self.slug
            counter = 1
            while KnowledgeBaseArticle.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)

    def publish(self, reviewed_by=None):
        """Publish the article"""
        self.status = self.ArticleStatus.PUBLISHED
        self.published_at = timezone.now()
        if reviewed_by:
            self.last_reviewed_by = reviewed_by
            self.last_reviewed_at = timezone.now()
        self.save()

    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])

    def rate_article(self, helpful=True, user=None):
        """Rate article as helpful or not helpful"""
        if helpful:
            self.helpful_count += 1
        else:
            self.not_helpful_count += 1
        
        # Recalculate rating
        total_votes = self.helpful_count + self.not_helpful_count
        if total_votes > 0:
            self.rating = (self.helpful_count / total_votes) * 5
        
        self.save()
        
        # Record rating
        ArticleRating.objects.create(
            article=self,
            user=user,
            helpful=helpful
        )

    @property
    def is_published(self):
        """Check if article is published"""
        return self.status == self.ArticleStatus.PUBLISHED

    @property
    def view_count_formatted(self):
        """Format view count with K/M suffixes"""
        if self.views >= 1000000:
            return f"{self.views/1000000:.1f}M"
        elif self.views >= 1000:
            return f"{self.views/1000:.1f}K"
        return str(self.views)


class ArticleRating(BaseModel):
    """Article ratings by users"""
    article = models.ForeignKey(
        KnowledgeBaseArticle,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='article_ratings'
    )
    helpful = models.BooleanField(default=True, verbose_name=_("Helpful"))
    comment = models.TextField(blank=True, verbose_name=_("Comment"))
    
    class Meta:
        unique_together = ['article', 'user']
        verbose_name = _("Article Rating")
        verbose_name_plural = _("Article Ratings")

    def __str__(self):
        return f"{'Helpful' if self.helpful else 'Not Helpful'} rating for {self.article.title} by {self.user}"


class ITResource(BaseModel):
    """IT resources and inventory"""
    
    class ResourceType(models.TextChoices):
        HARDWARE = 'hardware', _('Hardware')
        SOFTWARE = 'software', _('Software')
        LICENSE = 'license', _('License')
        CONSUMABLE = 'consumable', _('Consumable')
        PERIPHERAL = 'peripheral', _('Peripheral')
        NETWORK = 'network', _('Network Equipment')
        SERVER = 'server', _('Server')
        STORAGE = 'storage', _('Storage')
        MOBILE = 'mobile', _('Mobile Device')
    
    class ResourceStatus(models.TextChoices):
        AVAILABLE = 'available', _('Available')
        IN_USE = 'in_use', _('In Use')
        MAINTENANCE = 'maintenance', _('Under Maintenance')
        RETIRED = 'retired', _('Retired')
        RESERVED = 'reserved', _('Reserved')
        LOST = 'lost', _('Lost')
        DAMAGED = 'damaged', _('Damaged')

    # Basic Information
    name = models.CharField(max_length=200, verbose_name=_("Resource Name"))
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
        verbose_name=_("Resource Type")
    )
    status = models.CharField(
        max_length=20,
        choices=ResourceStatus.choices,
        default=ResourceStatus.AVAILABLE,
        verbose_name=_("Status")
    )
    resource_code = models.CharField(max_length=50, unique=True, verbose_name=_("Resource Code"))
    
    # Details
    description = models.TextField(blank=True, verbose_name=_("Description"))
    manufacturer = models.CharField(max_length=100, blank=True, verbose_name=_("Manufacturer"))
    model = models.CharField(max_length=100, blank=True, verbose_name=_("Model"))
    serial_number = models.CharField(max_length=100, blank=True, verbose_name=_("Serial Number"))
    asset_tag = models.CharField(max_length=50, blank=True, verbose_name=_("Asset Tag"))
    
    # Specifications
    specifications = models.JSONField(default=dict, blank=True, verbose_name=_("Specifications"))
    
    # Purchase Information
    purchase_date = models.DateField(null=True, blank=True, verbose_name=_("Purchase Date"))
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Purchase Price")
    )
    vendor = models.CharField(max_length=100, blank=True, verbose_name=_("Vendor"))
    warranty_expiry = models.DateField(null=True, blank=True, verbose_name=_("Warranty Expiry"))
    warranty_details = models.TextField(blank=True, verbose_name=_("Warranty Details"))
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_resources'
    )
    assigned_date = models.DateField(null=True, blank=True, verbose_name=_("Assigned Date"))
    location = models.CharField(max_length=200, blank=True, verbose_name=_("Location"))
    department = models.CharField(max_length=100, blank=True, verbose_name=_("Department"))
    
    # Maintenance
    last_maintenance = models.DateField(null=True, blank=True, verbose_name=_("Last Maintenance"))
    next_maintenance = models.DateField(null=True, blank=True, verbose_name=_("Next Maintenance"))
    maintenance_notes = models.TextField(blank=True, verbose_name=_("Maintenance Notes"))
    maintenance_schedule = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('monthly', _('Monthly')),
            ('quarterly', _('Quarterly')),
            ('biannual', _('Biannual')),
            ('annual', _('Annual')),
            ('as_needed', _('As Needed')),
        ],
        verbose_name=_("Maintenance Schedule")
    )
    
    # Software specific fields
    version = models.CharField(max_length=50, blank=True, verbose_name=_("Version"))
    license_key = models.CharField(max_length=200, blank=True, verbose_name=_("License Key"))
    license_expiry = models.DateField(null=True, blank=True, verbose_name=_("License Expiry"))
    license_count = models.IntegerField(default=1, verbose_name=_("License Count"))
    installed_on = models.ForeignKey(
        SystemComponent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='installed_software'
    )
    
    # Consumable specific fields
    quantity = models.IntegerField(default=1, verbose_name=_("Quantity"))
    minimum_quantity = models.IntegerField(default=1, verbose_name=_("Minimum Quantity"))
    reorder_level = models.IntegerField(default=5, verbose_name=_("Reorder Level"))
    
    # Metadata
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    tags = models.JSONField(default=list, blank=True, verbose_name=_("Tags"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_resources'
    )

    class Meta:
        verbose_name = _("IT Resource")
        verbose_name_plural = _("IT Resources")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['resource_type']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['location']),
            models.Index(fields=['department']),
            models.Index(fields=['resource_code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_resource_type_display()})"

    def save(self, *args, **kwargs):
        # Generate resource code if not provided
        if not self.resource_code:
            prefix = {
                'hardware': 'HW',
                'software': 'SW',
                'license': 'LIC',
                'consumable': 'CON',
                'peripheral': 'PER',
                'network': 'NET',
                'server': 'SRV',
                'storage': 'STR',
                'mobile': 'MOB',
            }.get(self.resource_type, 'RES')
            
            year = timezone.now().year
            last_resource = ITResource.objects.filter(
                resource_code__startswith=f'{prefix}-{year}-'
            ).order_by('-resource_code').first()
            
            next_number = 1
            if last_resource:
                try:
                    last_number = int(last_resource.resource_code.split('-')[-1])
                    next_number = last_number + 1
                except (ValueError, IndexError):
                    pass
            
            self.resource_code = f"{prefix}-{year}-{next_number:04d}"
        
        super().save(*args, **kwargs)

    def assign(self, user, location='', department=''):
        """Assign resource to user"""
        self.assigned_to = user
        self.status = self.ResourceStatus.IN_USE
        self.assigned_date = timezone.now().date()
        
        if location:
            self.location = location
        if department:
            self.department = department
        
        self.save()
        
        # Log the assignment
        ResourceLog.objects.create(
            resource=self,
            action='assigned',
            user=user,
            notes=f"Assigned to {user.get_full_name()}"
        )

    def unassign(self):
        """Unassign resource"""
        previous_user = self.assigned_to
        self.assigned_to = None
        self.status = self.ResourceStatus.AVAILABLE
        self.assigned_date = None
        self.save()
        
        ResourceLog.objects.create(
            resource=self,
            action='unassigned',
            user=previous_user,
            notes=f"Resource unassigned from {previous_user.get_full_name() if previous_user else 'unknown'}"
        )

    def schedule_maintenance(self, date, notes=''):
        """Schedule maintenance"""
        self.next_maintenance = date
        if notes:
            self.maintenance_notes = f"{self.maintenance_notes}\nMaintenance scheduled for {date}: {notes}"
        self.save()
        
        ResourceLog.objects.create(
            resource=self,
            action='maintenance_scheduled',
            notes=f"Maintenance scheduled for {date}"
        )

    def perform_maintenance(self, notes=''):
        """Record maintenance performed"""
        self.last_maintenance = timezone.now().date()
        self.next_maintenance = None
        if notes:
            self.maintenance_notes = f"{self.maintenance_notes}\nMaintenance performed on {timezone.now().date()}: {notes}"
        self.save()
        
        ResourceLog.objects.create(
            resource=self,
            action='maintenance_performed',
            notes=notes
        )

    @property
    def is_under_warranty(self):
        """Check if resource is under warranty"""
        if not self.warranty_expiry:
            return False
        return self.warranty_expiry >= timezone.now().date()

    @property
    def age_in_months(self):
        """Calculate resource age in months"""
        if not self.purchase_date:
            return 0
        today = timezone.now().date()
        months = (today.year - self.purchase_date.year) * 12 + today.month - self.purchase_date.month
        return max(0, months)

    @property
    def requires_reorder(self):
        """Check if consumable needs reorder"""
        if self.resource_type == self.ResourceType.CONSUMABLE:
            return self.quantity <= self.reorder_level
        return False

    @property
    def needs_maintenance(self):
        """Check if maintenance is due"""
        if not self.next_maintenance:
            return False
        return self.next_maintenance <= timezone.now().date()


class ResourceLog(BaseModel):
    """Log of resource actions"""
    resource = models.ForeignKey(
        ITResource,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=50, verbose_name=_("Action"))
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    timestamp = models.DateTimeField(default=timezone.now)
    details = models.JSONField(default=dict, blank=True, verbose_name=_("Details"))

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("Resource Log")
        verbose_name_plural = _("Resource Logs")
        indexes = [
            models.Index(fields=['resource', 'timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.action} on {self.resource.name} at {self.timestamp}"


class ITProject(BaseModel):
    """IT projects management"""
    
    class ProjectStatus(models.TextChoices):
        PLANNING = 'planning', _('Planning')
        IN_PROGRESS = 'in_progress', _('In Progress')
        ON_HOLD = 'on_hold', _('On Hold')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
    
    class ProjectPriority(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')
        CRITICAL = 'critical', _('Critical')

    # Project Information
    name = models.CharField(max_length=200, verbose_name=_("Project Name"))
    project_code = models.CharField(max_length=50, unique=True, verbose_name=_("Project Code"))
    description = models.TextField(verbose_name=_("Description"))
    objectives = models.TextField(blank=True, verbose_name=_("Objectives"))
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.PLANNING,
        verbose_name=_("Status")
    )
    priority = models.CharField(
        max_length=20,
        choices=ProjectPriority.choices,
        default=ProjectPriority.MEDIUM,
        verbose_name=_("Priority")
    )
    
    # Timeline
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    actual_start_date = models.DateField(null=True, blank=True, verbose_name=_("Actual Start Date"))
    actual_end_date = models.DateField(null=True, blank=True, verbose_name=_("Actual End Date"))
    
    # Team
    project_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_projects',
        verbose_name=_("Project Manager")
    )
    team_members = models.ManyToManyField(
        User,
        related_name='it_projects',
        verbose_name=_("Team Members")
    )
    stakeholders = models.ManyToManyField(
        User,
        blank=True,
        related_name='stakeholder_projects',
        verbose_name=_("Stakeholders")
    )
    
    # Budget
    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Budget")
    )
    actual_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Actual Cost")
    )
    
    # Resources
    resources = models.ManyToManyField(
        ITResource,
        blank=True,
        related_name='projects',
        verbose_name=_("Resources")
    )
    components = models.ManyToManyField(
        SystemComponent,
        blank=True,
        related_name='projects',
        verbose_name=_("Components")
    )
    
    # Documentation
    scope = models.TextField(blank=True, verbose_name=_("Scope"))
    deliverables = models.JSONField(default=list, blank=True, verbose_name=_("Deliverables"))
    risks = models.TextField(blank=True, verbose_name=_("Risks"))
    constraints = models.TextField(blank=True, verbose_name=_("Constraints"))
    
    # Results
    outcomes = models.TextField(blank=True, verbose_name=_("Outcomes"))
    lessons_learned = models.TextField(blank=True, verbose_name=_("Lessons Learned"))
    success_metrics = models.JSONField(default=list, blank=True, verbose_name=_("Success Metrics"))
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_it_projects'
    )
    tags = models.JSONField(default=list, blank=True, verbose_name=_("Tags"))

    class Meta:
        verbose_name = _("IT Project")
        verbose_name_plural = _("IT Projects")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_code']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['project_manager']),
        ]

    def __str__(self):
        return f"{self.project_code}: {self.name}"

    def save(self, *args, **kwargs):
        # Generate project code if not provided
        if not self.project_code:
            year = timezone.now().year
            last_project = ITProject.objects.filter(
                project_code__startswith=f'PRJ-{year}-'
            ).order_by('-project_code').first()
            
            next_number = 1
            if last_project:
                try:
                    last_number = int(last_project.project_code.split('-')[-1])
                    next_number = last_number + 1
                except (ValueError, IndexError):
                    pass
            
            self.project_code = f"PRJ-{year}-{next_number:04d}"
        
        super().save(*args, **kwargs)

    @property
    def progress_percentage(self):
        """Calculate project progress percentage"""
        if self.status == self.ProjectStatus.COMPLETED:
            return 100
        elif self.status == self.ProjectStatus.CANCELLED:
            return 0
        
        if self.actual_start_date:
            total_duration = (self.end_date - self.actual_start_date).days
            days_passed = (timezone.now().date() - self.actual_start_date).days
            
            if total_duration > 0:
                progress = min(99, int((days_passed / total_duration) * 100))
                return progress
        
        return 0

    @property
    def is_overdue(self):
        """Check if project is overdue"""
        if self.status in [self.ProjectStatus.IN_PROGRESS, self.ProjectStatus.PLANNING]:
            return timezone.now().date() > self.end_date
        return False

    @property
    def budget_variance(self):
        """Calculate budget variance"""
        if self.budget and self.actual_cost:
            return self.actual_cost - self.budget
        return None

    def start_project(self):
        """Mark project as started"""
        self.status = self.ProjectStatus.IN_PROGRESS
        self.actual_start_date = timezone.now().date()
        self.save()

    def complete_project(self, outcomes='', lessons_learned=''):
        """Mark project as completed"""
        self.status = self.ProjectStatus.COMPLETED
        self.actual_end_date = timezone.now().date()
        self.outcomes = outcomes
        self.lessons_learned = lessons_learned
        self.save()


class ITDashboard(BaseModel):
    """IT Dashboard for metrics and reporting"""
    
    class DashboardType(models.TextChoices):
        SYSTEM_HEALTH = 'system_health', _('System Health')
        TICKETS = 'tickets', _('Tickets')
        ALERTS = 'alerts', _('Alerts')
        PERFORMANCE = 'performance', _('Performance')
        RESOURCES = 'resources', _('Resources')
        PROJECTS = 'projects', _('Projects')
        CUSTOM = 'custom', _('Custom')
    
    name = models.CharField(max_length=100, verbose_name=_("Dashboard Name"))
    dashboard_type = models.CharField(
        max_length=20,
        choices=DashboardType.choices,
        verbose_name=_("Dashboard Type")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    # Configuration
    layout = models.JSONField(default=dict, blank=True, verbose_name=_("Layout"))
    widgets = models.JSONField(default=list, blank=True, verbose_name=_("Widgets"))
    filters = models.JSONField(default=dict, blank=True, verbose_name=_("Filters"))
    refresh_interval = models.IntegerField(default=300, verbose_name=_("Refresh Interval (seconds)"))
    
    # Access Control
    is_public = models.BooleanField(default=False, verbose_name=_("Is Public"))
    allowed_users = models.ManyToManyField(
        User,
        blank=True,
        related_name='accessible_dashboards',
        verbose_name=_("Allowed Users")
    )
    allowed_roles = models.JSONField(default=list, blank=True, verbose_name=_("Allowed Roles"))
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_dashboards'
    )
    last_viewed = models.DateTimeField(null=True, blank=True, verbose_name=_("Last Viewed"))
    view_count = models.IntegerField(default=0, verbose_name=_("View Count"))

    class Meta:
        verbose_name = _("IT Dashboard")
        verbose_name_plural = _("IT Dashboards")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dashboard_type']),
            models.Index(fields=['is_public']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_dashboard_type_display()})"

    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.last_viewed = timezone.now()
        self.save(update_fields=['view_count', 'last_viewed'])

    def can_access(self, user):
        """Check if user can access this dashboard"""
        if self.is_public:
            return True
        
        if self.allowed_users.filter(pk=user.pk).exists():
            return True
        
        if user.role in self.allowed_roles:
            return True
        
        return False

    def get_dashboard_data(self):
        """Get dashboard data based on type"""
        data = {
            'name': self.name,
            'type': self.dashboard_type,
            'widgets': self.widgets,
            'last_updated': timezone.now()
        }
        
        if self.dashboard_type == self.DashboardType.SYSTEM_HEALTH:
            data['metrics'] = self.get_system_health_metrics()
        elif self.dashboard_type == self.DashboardType.TICKETS:
            data['metrics'] = self.get_ticket_metrics()
        elif self.dashboard_type == self.DashboardType.ALERTS:
            data['metrics'] = self.get_alert_metrics()
        
        return data

    def get_system_health_metrics(self):
        """Get system health metrics"""
        components = SystemComponent.objects.filter(is_active=True, is_monitored=True)
        
        metrics = {
            'total_components': components.count(),
            'online_components': components.filter(status=SystemComponent.ComponentStatus.ONLINE).count(),
            'offline_components': components.filter(status=SystemComponent.ComponentStatus.OFFLINE).count(),
            'degraded_components': components.filter(status=SystemComponent.ComponentStatus.DEGRADED).count(),
            'maintenance_components': components.filter(status=SystemComponent.ComponentStatus.MAINTENANCE).count(),
            'uptime_percentage': self.calculate_average_uptime(components),
        }
        
        return metrics

    def calculate_average_uptime(self, components):
        """Calculate average uptime percentage for components"""
        if not components.exists():
            return 0
        
        total_uptime = 0
        count = 0
        
        for component in components:
            # Get latest performance metric
            latest_metric = PerformanceMetric.objects.filter(
                component=component
            ).order_by('-timestamp').first()
            
            if latest_metric:
                total_uptime += latest_metric.uptime
                count += 1
        
        return round(total_uptime / count, 2) if count > 0 else 0

    def get_ticket_metrics(self):
        """Get ticket metrics"""
        tickets = SupportTicket.objects.filter(is_active=True)
        
        metrics = {
            'total_tickets': tickets.count(),
            'open_tickets': tickets.filter(status=SupportTicket.TicketStatus.OPEN).count(),
            'in_progress_tickets': tickets.filter(status=SupportTicket.TicketStatus.IN_PROGRESS).count(),
            'resolved_tickets': tickets.filter(status=SupportTicket.TicketStatus.RESOLVED).count(),
            'closed_tickets': tickets.filter(status=SupportTicket.TicketStatus.CLOSED).count(),
            'overdue_tickets': sum(1 for ticket in tickets if ticket.is_overdue),
            'average_resolution_time': self.calculate_average_resolution_time(tickets),
        }
        
        return metrics

    def calculate_average_resolution_time(self, tickets):
        """Calculate average resolution time for resolved tickets"""
        resolved_tickets = tickets.filter(
            status=SupportTicket.TicketStatus.RESOLVED,
            resolved_at__isnull=False
        )
        
        if not resolved_tickets.exists():
            return 0
        
        total_seconds = 0
        for ticket in resolved_tickets:
            resolution_time = ticket.resolved_at - ticket.created_at
            total_seconds += resolution_time.total_seconds()
        
        avg_seconds = total_seconds / resolved_tickets.count()
        
        # Convert to hours
        return round(avg_seconds / 3600, 2)

    def get_alert_metrics(self):
        """Get alert metrics"""
        alerts = SystemAlert.objects.filter(is_active=True)
        
        metrics = {
            'total_alerts': alerts.count(),
            'active_alerts': alerts.filter(status=SystemAlert.AlertStatus.ACTIVE).count(),
            'acknowledged_alerts': alerts.filter(status=SystemAlert.AlertStatus.ACKNOWLEDGED).count(),
            'resolved_alerts': alerts.filter(status=SystemAlert.AlertStatus.RESOLVED).count(),
            'critical_alerts': alerts.filter(severity=SystemAlert.AlertSeverity.CRITICAL).count(),
            'error_alerts': alerts.filter(severity=SystemAlert.AlertSeverity.ERROR).count(),
            'warning_alerts': alerts.filter(severity=SystemAlert.AlertSeverity.WARNING).count(),
            'info_alerts': alerts.filter(severity=SystemAlert.AlertSeverity.INFO).count(),
        }
        
        return metrics