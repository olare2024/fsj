# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from django.contrib import messages
from .models import User, UserProfile, TwoFactorAuth, OTPToken, LoginHistory
from django.db.models import F
from django.utils import timezone
from datetime import timedelta


# ============================================================================
# INLINES
# ============================================================================

class UserProfileInline(admin.StackedInline):
    """Inline for UserProfile in User admin"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('User Profile')

    fields = (
        'bio', 'website', 'social_links', 'hobbies',
        'notifications_enabled', 'email_notifications',
        'sms_notifications', 'push_notifications',
        'language', 'timezone', 'profile_visibility',
        'contact_preference'
    )
    readonly_fields = ('achievements', 'skills', 'education_background')


class TwoFactorAuthInline(admin.TabularInline):
    """Inline for TwoFactorAuth in User admin"""
    model = TwoFactorAuth
    can_delete = False
    verbose_name_plural = _('Two-Factor Authentication')
    fields = ('is_enabled', 'primary_method', 'last_used', 'recovery_email')
    readonly_fields = ('last_used',)


# ============================================================================
# FILTERS
# ============================================================================

class RoleFilter(admin.SimpleListFilter):
    """Filter users by role"""
    title = _('Role')
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        return User.Role.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(role=self.value())
        return queryset


class ProfileCompletionFilter(admin.SimpleListFilter):
    """Filter users by profile completion status"""
    title = _('Profile Completion')
    parameter_name = 'profile_completed'

    def lookups(self, request, model_admin):
        return (
            ('completed', _('Completed')),
            ('incomplete', _('Incomplete')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'completed':
            return queryset.filter(profile_completed=True)
        elif self.value() == 'incomplete':
            return queryset.filter(profile_completed=False)
        return queryset


class VerificationStatusFilter(admin.SimpleListFilter):
    """Filter users by verification status"""
    title = _('Verification Status')
    parameter_name = 'verification_status'

    def lookups(self, request, model_admin):
        return (
            ('verified', _('Verified')),
            ('unverified', _('Unverified')),
            ('suspended', _('Suspended')),
            ('pending', _('Pending Approval')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'verified':
            return queryset.filter(is_verified=True, is_suspended=False)
        elif self.value() == 'unverified':
            return queryset.filter(is_verified=False, is_suspended=False)
        elif self.value() == 'suspended':
            return queryset.filter(is_suspended=True)
        elif self.value() == 'pending':
            return queryset.filter(is_approved=False, is_suspended=False)
        return queryset


# ============================================================================
# USER ADMIN
# ============================================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin with enhanced functionality"""
    
    inlines = [UserProfileInline, TwoFactorAuthInline]
    list_display = (
        'email', 'full_name', 'role_display', 'profile_completion_badge',
        'verification_status', 'last_login_display', 'actions'
    )
    list_filter = (
        RoleFilter,
        ProfileCompletionFilter,
        VerificationStatusFilter,
        'is_staff', 'is_active', 'is_superuser',
        'date_joined', 'last_login'
    )
    search_fields = ('email', 'first_name', 'last_name', 'admission_number', 'staff_id')
    ordering = ('-date_joined',)
    readonly_fields = (
        'date_joined', 'last_login', 'last_login_ip',
        'login_count', 'failed_login_attempts',
        'profile_completion_date', 'last_profile_update',
        'password_changed_at', 'last_activity',
        'profile_completion_percentage_display',
        'age_display', 'years_of_service_display',
        'online_status', 'identifier_display'
    )
    actions = [
        'activate_users', 'deactivate_users',
        'verify_users', 'unverify_users',
        'approve_users', 'suspend_users',
        'mark_profiles_completed', 'send_welcome_email'
    ]
    
    fieldsets = (
        (_('Authentication'), {
            'fields': ('email', 'password', 'date_joined', 'last_login')
        }),
        (_('Personal Information'), {
            'fields': (
                ('first_name', 'middle_name', 'last_name'),
                ('date_of_birth', 'gender', 'nationality'),
                ('phone_number', 'alternative_phone'),
                ('address', 'city', 'country'),
                'profile_picture',
                'id_number'
            )
        }),
        (_('Academy Information'), {
            'fields': (
                ('role', 'is_active', 'is_staff', 'is_superuser'),
                ('admission_number', 'staff_id'),
                ('grade_level', 'current_class', 'house'),
                ('primary_curriculum', 'academic_year'),
                ('enrollment_date', 'employment_date')
            )
        }),
        (_('Professional Information'), {
            'fields': (
                ('department', 'designation'),
                ('qualification', 'specialization'),
                'years_of_experience'
            )
        }),
        (_('Parent/Guardian Information'), {
            'fields': (
                ('parent_name', 'parent_email', 'parent_phone'),
                'parent_occupation'
            )
        }),
        (_('Emergency Contact'), {
            'fields': (
                ('emergency_contact_name', 'emergency_contact_relationship'),
                ('emergency_contact_phone', 'emergency_contact_address')
            )
        }),
        (_('Medical Information'), {
            'fields': (
                ('blood_group', 'medical_info'),
                ('allergies', 'chronic_conditions'),
                ('current_medications', 'doctor_name', 'doctor_phone')
            )
        }),
        (_('Documents'), {
            'fields': (
                'previous_school',
                ('transfer_certificate', 'birth_certificate', 'recommendation_letter')
            )
        }),
        (_('Status & Verification'), {
            'fields': (
                ('is_verified', 'is_approved', 'is_suspended', 'is_on_leave'),
                ('email_verified', 'phone_verified'),
                ('profile_completed', 'profile_completion_date'),
                'profile_requirements_met'
            )
        }),
        (_('Dashboard Preferences'), {
            'fields': (
                ('preferred_dashboard_view', 'theme_preference'),
                'dashboard_widgets'
            )
        }),
        (_('Security & Activity'), {
            'fields': (
                ('last_login_ip', 'last_login_user_agent'),
                ('login_count', 'failed_login_attempts'),
                ('account_locked_until', 'password_changed_at'),
                ('last_activity', 'last_profile_update')
            )
        }),
        (_('Calculated Fields'), {
            'fields': (
                'profile_completion_percentage_display',
                'age_display', 'years_of_service_display',
                'online_status', 'identifier_display'
            ),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'role',
                'password1', 'password2', 'is_staff', 'is_active'
            ),
        }),
    )
    
    # === Custom List Display Methods ===
    def full_name(self, obj):
        """Display full name"""
        return obj.get_full_name()
    full_name.short_description = _('Full Name')
    full_name.admin_order_field = 'last_name'
    
    def role_display(self, obj):
        """Display role with badge"""
        colors = {
            'admin': 'red',
            'head_teacher': 'purple',
            'teacher': 'blue',
            'student': 'green',
            'parent': 'orange',
            'accountant': 'teal',
        }
        color = colors.get(obj.role, 'gray')
        return format_html(
            '<span style="padding: 2px 6px; border-radius: 3px; '
            f'background-color: {color}; color: white; font-size: 0.9em;">'
            f'{obj.get_role_display()}'
            '</span>'
        )
    role_display.short_description = _('Role')
    
    def profile_completion_badge(self, obj):
        """Display profile completion as badge"""
        percentage = obj.profile_completion_percentage
        if percentage == 100:
            color = 'green'
            text = _('Complete')
        elif percentage >= 70:
            color = 'orange'
            text = f'{percentage}%'
        else:
            color = 'red'
            text = f'{percentage}%'
        
        return format_html(
            '<span style="padding: 2px 6px; border-radius: 3px; '
            f'background-color: {color}; color: white; font-size: 0.9em;">'
            f'{text}'
            '</span>'
        )
    profile_completion_badge.short_description = _('Profile')
    profile_completion_badge.admin_order_field = 'profile_completed'
    
    def verification_status(self, obj):
        """Display verification status"""
        if obj.is_suspended:
            color = 'red'
            text = _('Suspended')
        elif not obj.is_verified:
            color = 'orange'
            text = _('Unverified')
        elif not obj.is_approved:
            color = 'yellow'
            text = _('Pending')
        else:
            color = 'green'
            text = _('Verified')
        
        return format_html(
            '<span style="padding: 2px 6px; border-radius: 3px; '
            f'background-color: {color}; color: white; font-size: 0.9em;">'
            f'{text}'
            '</span>'
        )
    verification_status.short_description = _('Status')
    
    def last_login_display(self, obj):
        """Display last login in human-readable format"""
        if obj.last_login:
            from django.utils import timezone
            now = timezone.now()
            diff = now - obj.last_login
            
            if diff.days == 0:
                if diff.seconds < 60:
                    return _('Just now')
                elif diff.seconds < 3600:
                    minutes = diff.seconds // 60
                    return _('{} minutes ago').format(minutes)
                else:
                    hours = diff.seconds // 3600
                    return _('{} hours ago').format(hours)
            elif diff.days == 1:
                return _('Yesterday')
            elif diff.days < 7:
                return _('{} days ago').format(diff.days)
            else:
                return obj.last_login.strftime('%Y-%m-%d')
        return _('Never')
    last_login_display.short_description = _('Last Login')

    def user_actions(self, obj):
        """Display action buttons"""
        view_url = reverse('admin:accounts_user_change', args=[obj.id])
        login_history_url = reverse('admin:accounts_loginhistory_changelist') + f'?user__id__exact={obj.id}'
        otp_tokens_url = reverse('admin:accounts_otptoken_changelist') + f'?user__id__exact={obj.id}'
        
        return format_html(
            '<a href="{}" class="button" title="{}">👁️</a>&nbsp;'
            '<a href="{}" class="button" title="{}">📋</a>&nbsp;'
            '<a href="{}" class="button" title="{}">🔑</a>',
            view_url, _('Edit User'),
            login_history_url, _('View Login History'),
            otp_tokens_url, _('View OTP Tokens')
        )
    user_actions.short_description = _('Actions')
    
    # === Custom Readonly Fields ===
    def profile_completion_percentage_display(self, obj):
        """Display profile completion percentage"""
        percentage = obj.profile_completion_percentage
        return f'{percentage}%'
    profile_completion_percentage_display.short_description = _('Profile Completion')
    
    def age_display(self, obj):
        """Display age"""
        if obj.age:
            return f'{obj.age} years'
        return 'N/A'
    age_display.short_description = _('Age')
    
    def years_of_service_display(self, obj):
        """Display years of service"""
        if obj.years_of_service:
            return f'{obj.years_of_service} years'
        return 'N/A'
    years_of_service_display.short_description = _('Years of Service')
    
    def online_status(self, obj):
        """Display online status"""
        if obj.is_online:
            return format_html(
                '<span style="color: green;">● {}</span>',
                _('Online')
            )
        return format_html(
            '<span style="color: gray;">● {}</span>',
            _('Offline')
        )
    online_status.short_description = _('Status')
    
    def identifier_display(self, obj):
        """Display primary identifier"""
        return obj.identifier
    identifier_display.short_description = _('Identifier')
    
    # === Custom Actions ===
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            _('Successfully activated {} users.').format(updated),
            messages.SUCCESS
        )
    activate_users.short_description = _('Activate selected users')
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            _('Successfully deactivated {} users.').format(updated),
            messages.SUCCESS
        )
    deactivate_users.short_description = _('Deactivate selected users')
    
    def verify_users(self, request, queryset):
        """Verify selected users"""
        updated = queryset.update(is_verified=True, is_approved=True)
        self.message_user(
            request,
            _('Successfully verified {} users.').format(updated),
            messages.SUCCESS
        )
    verify_users.short_description = _('Verify selected users')
    
    def unverify_users(self, request, queryset):
        """Unverify selected users"""
        updated = queryset.update(is_verified=False)
        self.message_user(
            request,
            _('Successfully unverified {} users.').format(updated),
            messages.SUCCESS
        )
    unverify_users.short_description = _('Unverify selected users')
    
    def approve_users(self, request, queryset):
        """Approve selected users"""
        updated = queryset.update(is_approved=True)
        self.message_user(
            request,
            _('Successfully approved {} users.').format(updated),
            messages.SUCCESS
        )
    approve_users.short_description = _('Approve selected users')
    
    def suspend_users(self, request, queryset):
        """Suspend selected users"""
        updated = queryset.update(is_suspended=True, is_active=False)
        self.message_user(
            request,
            _('Successfully suspended {} users.').format(updated),
            messages.SUCCESS
        )
    suspend_users.short_description = _('Suspend selected users')
    
    def mark_profiles_completed(self, request, queryset):
        """Mark profiles as completed"""
        for user in queryset:
            user.mark_profile_completed()
        self.message_user(
            request,
            _('Successfully marked {} profiles as completed.').format(queryset.count()),
            messages.SUCCESS
        )
    mark_profiles_completed.short_description = _('Mark profiles as completed')
    
    def send_welcome_email(self, request, queryset):
        """Send welcome email to selected users"""
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        
        count = 0
        for user in queryset:
            if user.email:
                try:
                    subject = _("Welcome to Delvok Academy")
                    html_message = render_to_string('accounts/welcome_email.html', {
                        'user': user,
                        'admin': request.user
                    })
                    plain_message = strip_tags(html_message)
                    
                    user.email_user(subject, plain_message, html_message=html_message)
                    count += 1
                except Exception as e:
                    self.message_user(
                        request,
                        _('Failed to send email to {}: {}').format(user.email, str(e)),
                        messages.ERROR
                    )
        
        self.message_user(
            request,
            _('Successfully sent welcome emails to {} users.').format(count),
            messages.SUCCESS
        )
    send_welcome_email.short_description = _('Send welcome email')
    
    # === Override Methods ===
    def get_queryset(self, request):
        """Optimize queryset for admin"""
        qs = super().get_queryset(request)
        return qs.select_related('user_profile').prefetch_related('two_factor_auth')
    
    def get_inline_instances(self, request, obj=None):
        """Only show inlines when editing an existing object"""
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


# ============================================================================
# USER PROFILE ADMIN
# ============================================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model"""
    list_display = ('user_email', 'full_name', 'notifications_status', 'profile_visibility')
    list_filter = ('notifications_enabled', 'profile_visibility', 'contact_preference')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'bio')
    readonly_fields = ('user_link', 'achievements', 'skills', 'education_background')
    
    fieldsets = (
        (_('User Information'), {
            'fields': ('user_link',)
        }),
        (_('Profile Information'), {
            'fields': ('bio', 'website', 'social_links', 'hobbies')
        }),
        (_('Notifications'), {
            'fields': (
                'notifications_enabled',
                ('email_notifications', 'sms_notifications', 'push_notifications'),
                'contact_preference'
            )
        }),
        (_('Preferences'), {
            'fields': ('language', 'timezone', 'profile_visibility')
        }),
        (_('Additional Information'), {
            'fields': ('achievements', 'skills', 'education_background'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = _('Email')
    user_email.admin_order_field = 'user__email'
    
    def full_name(self, obj):
        """Display full name"""
        return obj.user.get_full_name()
    full_name.short_description = _('Full Name')
    full_name.admin_order_field = 'user__last_name'
    
    def user_link(self, obj):
        """Display link to user"""
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user)
    user_link.short_description = _('User')
    
    def notifications_status(self, obj):
        """Display notifications status"""
        if obj.notifications_enabled:
            enabled = []
            if obj.email_notifications:
                enabled.append('Email')
            if obj.sms_notifications:
                enabled.append('SMS')
            if obj.push_notifications:
                enabled.append('Push')
            
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                ', '.join(enabled) or _('None')
            )
        return format_html(
            '<span style="color: red;">✗ {}</span>',
            _('Disabled')
        )
    notifications_status.short_description = _('Notifications')
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user')


# ============================================================================
# TWO FACTOR AUTH ADMIN
# ============================================================================

@admin.register(TwoFactorAuth)
class TwoFactorAuthAdmin(admin.ModelAdmin):
    """Admin for TwoFactorAuth model"""
    list_display = ('user_email', 'full_name', 'is_enabled_badge', 'primary_method', 'last_used', 'backup_codes_count')
    list_filter = ('is_enabled', 'primary_method')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'recovery_email')
    readonly_fields = ('user_link', 'secret_key', 'last_used', 'backup_codes_list', 'qr_code_display')
    
    fieldsets = (
        (_('User Information'), {
            'fields': ('user_link',)
        }),
        (_('2FA Configuration'), {
            'fields': (
                'is_enabled', 'primary_method',
                ('recovery_email', 'recovery_phone'),
                'secret_key', 'qr_code_display'
            )
        }),
        (_('Usage'), {
            'fields': ('last_used', 'last_backup_code_generated')
        }),
        (_('Backup Codes'), {
            'fields': ('backup_codes_list',),
            'classes': ('collapse',)
        }),
        (_('Session Management'), {
            'fields': ('pending_session_token', 'pending_session_expiry', 'pending_redirect_url'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['enable_2fa', 'disable_2fa', 'regenerate_backup_codes']
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = _('Email')
    user_email.admin_order_field = 'user__email'
    
    def full_name(self, obj):
        """Display full name"""
        return obj.user.get_full_name()
    full_name.short_description = _('Full Name')
    full_name.admin_order_field = 'user__last_name'
    
    def is_enabled_badge(self, obj):
        """Display enabled status as badge"""
        if obj.is_enabled:
            return format_html(
                '<span style="padding: 2px 6px; border-radius: 3px; '
                'background-color: green; color: white; font-size: 0.9em;">'
                '✓ Enabled'
                '</span>'
            )
        return format_html(
            '<span style="padding: 2px 6px; border-radius: 3px; '
            'background-color: red; color: white; font-size: 0.9em;">'
            '✗ Disabled'
            '</span>'
        )
    is_enabled_badge.short_description = _('Status')
    
    def backup_codes_count(self, obj):
        """Count unused backup codes"""
        unused = obj.get_unused_backup_codes()
        return f'{len(unused)}/{len(obj.backup_codes)}'
    backup_codes_count.short_description = _('Backup Codes')
    
    def user_link(self, obj):
        """Display link to user"""
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user)
    user_link.short_description = _('User')
    
    def backup_codes_list(self, obj):
        """Display backup codes in readable format"""
        if not obj.backup_codes:
            return _('No backup codes generated')
        
        html = '<table style="width: 100%;">'
        html += '<tr><th>Code</th><th>Used</th><th>Generated At</th><th>Used At</th></tr>'
        
        for code in obj.backup_codes:
            used = '✓' if code.get('used') else '✗'
            used_at = code.get('used_at', 'N/A')
            generated_at = code.get('generated_at', 'N/A')
            
            html += f'<tr>'
            html += f'<td><code>{code.get("code")}</code></td>'
            html += f'<td style="text-align: center;">{used}</td>'
            html += f'<td>{generated_at}</td>'
            html += f'<td>{used_at}</td>'
            html += f'</tr>'
        
        html += '</table>'
        return format_html(html)
    backup_codes_list.short_description = _('Backup Codes')
    
    def qr_code_display(self, obj):
        """Display QR code for 2FA setup"""
        if obj.is_enabled and obj.primary_method == 'authenticator':
            qr_code = obj.generate_qr_code()
            if qr_code:
                return format_html(
                    '<img src="data:image/png;base64,{}" alt="QR Code" style="max-width: 200px;" />',
                    qr_code
                )
        return _('QR code available only for enabled authenticator 2FA')
    qr_code_display.short_description = _('QR Code')
    
    # === Custom Actions ===
    def enable_2fa(self, request, queryset):
        """Enable 2FA for selected users"""
        for two_fa in queryset:
            two_fa.is_enabled = True
            two_fa.save()
        
        self.message_user(
            request,
            _('Successfully enabled 2FA for {} users.').format(queryset.count()),
            messages.SUCCESS
        )
    enable_2fa.short_description = _('Enable 2FA')
    
    def disable_2fa(self, request, queryset):
        """Disable 2FA for selected users"""
        for two_fa in queryset:
            two_fa.disable_2fa()
        
        self.message_user(
            request,
            _('Successfully disabled 2FA for {} users.').format(queryset.count()),
            messages.SUCCESS
        )
    disable_2fa.short_description = _('Disable 2FA')
    
    def regenerate_backup_codes(self, request, queryset):
        """Regenerate backup codes for selected users"""
        for two_fa in queryset:
            two_fa.generate_backup_codes()
        
        self.message_user(
            request,
            _('Successfully regenerated backup codes for {} users.').format(queryset.count()),
            messages.SUCCESS
        )
    regenerate_backup_codes.short_description = _('Regenerate Backup Codes')


# ============================================================================
# OTP TOKEN ADMIN
# ============================================================================

@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
    """Admin for OTPToken model"""
    list_display = ('token', 'user_email', 'token_type_badge', 'purpose', 'is_used_badge', 'created_at', 'expires_at')
    list_filter = ('token_type', 'is_used', 'created_at')
    search_fields = ('token', 'user__email', 'purpose', 'ip_address')
    readonly_fields = ('user_link', 'token', 'created_at', 'expires_at', 'used_at', 'validity_status')
    list_per_page = 50
    
    fieldsets = (
        (_('Token Information'), {
            'fields': ('token', 'token_type', 'purpose')
        }),
        (_('User Information'), {
            'fields': ('user_link',)
        }),
        (_('Status'), {
            'fields': ('is_used', 'validity_status', ('created_at', 'expires_at', 'used_at'))
        }),
        (_('Request Information'), {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_used', 'mark_as_unused', 'delete_expired']
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = _('Email')
    user_email.admin_order_field = 'user__email'
    
    def token_type_badge(self, obj):
        """Display token type as badge"""
        colors = {
            'email_verification': 'blue',
            'password_reset': 'orange',
            'login_verification': 'green',
            'account_recovery': 'red',
        }
        color = colors.get(obj.token_type, 'gray')
        return format_html(
            '<span style="padding: 2px 6px; border-radius: 3px; '
            f'background-color: {color}; color: white; font-size: 0.9em;">'
            f'{obj.get_token_type_display()}'
            '</span>'
        )
    token_type_badge.short_description = _('Type')
    
    def is_used_badge(self, obj):
        """Display used status as badge"""
        if obj.is_used:
            return format_html(
                '<span style="padding: 2px 6px; border-radius: 3px; '
                'background-color: gray; color: white; font-size: 0.9em;">'
                'Used'
                '</span>'
            )
        
        if obj.is_valid():
            return format_html(
                '<span style="padding: 2px 6px; border-radius: 3px; '
                'background-color: green; color: white; font-size: 0.9em;">'
                'Valid'
                '</span>'
            )
        else:
            return format_html(
                '<span style="padding: 2px 6px; border-radius: 3px; '
                'background-color: red; color: white; font-size: 0.9em;">'
                'Expired'
                '</span>'
            )
    is_used_badge.short_description = _('Status')
    
    def user_link(self, obj):
        """Display link to user"""
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user)
    user_link.short_description = _('User')
    
    def validity_status(self, obj):
        """Display validity status"""
        from django.utils import timezone
        
        if obj.is_used:
            return _('Used at {}').format(obj.used_at.strftime('%Y-%m-%d %H:%M:%S'))
        
        if obj.expires_at > timezone.now():
            time_left = obj.expires_at - timezone.now()
            minutes = int(time_left.total_seconds() / 60)
            return _('Valid for {} minutes').format(minutes)
        else:
            return _('Expired')
    validity_status.short_description = _('Validity')
    
    # === Custom Actions ===
    def mark_as_used(self, request, queryset):
        """Mark selected tokens as used"""
        updated = queryset.update(is_used=True, used_at=timezone.now())
        self.message_user(
            request,
            _('Successfully marked {} tokens as used.').format(updated),
            messages.SUCCESS
        )
    mark_as_used.short_description = _('Mark as used')
    
    def mark_as_unused(self, request, queryset):
        """Mark selected tokens as unused"""
        updated = queryset.update(is_used=False, used_at=None)
        self.message_user(
            request,
            _('Successfully marked {} tokens as unused.').format(updated),
            messages.SUCCESS
        )
    mark_as_unused.short_description = _('Mark as unused')
    
    def delete_expired(self, request, queryset):
        """Delete expired tokens"""
        from django.utils import timezone
        expired = queryset.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        
        self.message_user(
            request,
            _('Successfully deleted {} expired tokens.').format(count),
            messages.SUCCESS
        )
    delete_expired.short_description = _('Delete expired tokens')
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user')


# ============================================================================
# LOGIN HISTORY ADMIN
# ============================================================================

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """Admin for LoginHistory model"""
    list_display = ('user_email', 'full_name', 'login_status_badge', 'ip_address', 'location', 'device_info', 'created_at', 'suspicious_flag')
    list_filter = ('login_status', 'is_suspicious', 'device_type', 'browser', 'country', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'ip_address', 'location', 'user_agent')
    readonly_fields = ('user_link', 'created_at', 'device_info_display', 'location_display', 'suspicious_reason')
    list_per_page = 50
    
    fieldsets = (
        (_('User Information'), {
            'fields': ('user_link',)
        }),
        (_('Login Details'), {
            'fields': ('login_status', 'failure_reason', 'created_at')
        }),
        (_('Device & Location'), {
            'fields': ('device_info_display', 'location_display')
        }),
        (_('Security'), {
            'fields': ('is_suspicious', 'suspicious_reason'),
            'classes': ('collapse',)
        }),
        (_('Technical Details'), {
            'fields': ('ip_address', 'user_agent', 'session_key', 'two_fa_method'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_suspicious', 'mark_as_normal', 'delete_old_records']
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = _('Email')
    user_email.admin_order_field = 'user__email'
    
    def full_name(self, obj):
        """Display full name"""
        return obj.user.get_full_name()
    full_name.short_description = _('Full Name')
    full_name.admin_order_field = 'user__last_name'
    
    def login_status_badge(self, obj):
        """Display login status as badge"""
        colors = {
            'success': 'green',
            'failed': 'red',
            'locked': 'orange',
            'two_factor_required': 'blue',
            'two_factor_verified': 'purple',
        }
        color = colors.get(obj.login_status, 'gray')
        return format_html(
            '<span style="padding: 2px 6px; border-radius: 3px; '
            f'background-color: {color}; color: white; font-size: 0.9em;">'
            f'{obj.get_login_status_display()}'
            '</span>'
        )
    login_status_badge.short_description = _('Status')
    
    def device_info(self, obj):
        """Display device information concisely"""
        return f"{obj.device_type} - {obj.browser}"
    device_info.short_description = _('Device')
    
    def suspicious_flag(self, obj):
        """Display suspicious flag"""
        if obj.is_suspicious:
            return format_html(
                '<span style="color: red;" title="{}">⚠️</span>',
                _('Suspicious activity detected')
            )
        return ''
    suspicious_flag.short_description = _('⚠')
    
    def user_link(self, obj):
        """Display link to user"""
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user)
    user_link.short_description = _('User')
    
    def device_info_display(self, obj):
        """Display detailed device information"""
        return format_html(
            '<strong>{}:</strong> {}<br>'
            '<strong>{}:</strong> {}<br>'
            '<strong>{}:</strong> {}',
            _('Device Type'), obj.device_type,
            _('Browser'), obj.browser,
            _('Platform'), obj.platform
        )
    device_info_display.short_description = _('Device Information')
    
    def location_display(self, obj):
        """Display location information"""
        location_parts = []
        if obj.city:
            location_parts.append(obj.city)
        if obj.country:
            location_parts.append(obj.country)
        
        location = ', '.join(location_parts) if location_parts else obj.location
        
        return format_html(
            '<strong>{}:</strong> {}<br>'
            '<strong>{}:</strong> {}',
            _('IP Address'), obj.ip_address,
            _('Location'), location
        )
    location_display.short_description = _('Location')
    
    def suspicious_reason(self, obj):
        """Explain why the login might be suspicious"""
        if not obj.is_suspicious:
            return _('No suspicious activity detected')
        
        reasons = []
        if obj.login_status == 'failed':
            reasons.append(_('Failed login attempt'))
        
        recent_logins = LoginHistory.objects.filter(
            user=obj.user,
            created_at__gte=obj.created_at - timedelta(days=1),
            created_at__lt=obj.created_at
        ).exclude(ip_address=obj.ip_address)
        
        if recent_logins.count() >= 3:
            reasons.append(_('Multiple IP addresses used in last 24 hours'))
        
        if obj.country and obj.country != 'Unknown':
            different_country_logins = LoginHistory.objects.filter(
                user=obj.user,
                country__isnull=False,
                country=obj.country,
                created_at__gte=obj.created_at - timedelta(days=30)
            ).exclude(ip_address=obj.ip_address)
            
            if not different_country_logins.exists():
                reasons.append(_('First login from this country'))
        
        return ', '.join(reasons) if reasons else _('Suspicious pattern detected')
    suspicious_reason.short_description = _('Suspicious Reason')
    
    # === Custom Actions ===
    def mark_as_suspicious(self, request, queryset):
        """Mark selected records as suspicious"""
        updated = queryset.update(is_suspicious=True)
        self.message_user(
            request,
            _('Successfully marked {} records as suspicious.').format(updated),
            messages.SUCCESS
        )
    mark_as_suspicious.short_description = _('Mark as suspicious')
    
    def mark_as_normal(self, request, queryset):
        """Mark selected records as normal"""
        updated = queryset.update(is_suspicious=False)
        self.message_user(
            request,
            _('Successfully marked {} records as normal.').format(updated),
            messages.SUCCESS
        )
    mark_as_normal.short_description = _('Mark as normal')
    
    def delete_old_records(self, request, queryset):
        """Delete records older than 90 days"""
        from django.utils import timezone
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=90)
        old_records = queryset.filter(created_at__lt=cutoff_date)
        count = old_records.count()
        old_records.delete()
        
        self.message_user(
            request,
            _('Successfully deleted {} old records.').format(count),
            messages.SUCCESS
        )
    delete_old_records.short_description = _('Delete records older than 90 days')
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user')


# ============================================================================
# ADMIN SITE CUSTOMIZATION
# ============================================================================

# Custom admin site header and title
admin.site.site_header = _('Delvok Academy Administration')
admin.site.site_title = _('Delvok Academy Admin Portal')
admin.site.index_title = _('Academy Management System')