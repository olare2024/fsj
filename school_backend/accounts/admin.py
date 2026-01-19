# accounts/admin.py - REFACTORED AND ORGANIZED VERSION

import csv
import logging
from datetime import timedelta

from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.db import models
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    LoginHistory, OTPToken, TwoFactorAuth, User, UserProfile,
    EmailVerification, LoginSession, GenderChoices, UserRole,
    CurriculumChoices, HouseChoices, BloodGroupChoices,
    TwoFAMethodChoices, TokenTypeChoices, LoginStatusChoices,
    SessionStatusChoices
)

logger = logging.getLogger(__name__)


# ============================================================================
# CUSTOM FORMS
# ============================================================================

class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form for admin"""
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role')
    
    def clean(self):
        """Clean form data - skip admission_number and staff_id validation"""
        cleaned_data = super().clean()
        return cleaned_data
    
    def save(self, commit=True):
        """Save the user - admission_number and staff_id will be auto-generated"""
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """Custom user change form for admin"""
    class Meta:
        model = User
        fields = '__all__'
    
    def clean(self):
        """Clean form - skip admission_number and staff_id validation"""
        cleaned_data = super().clean()
        return cleaned_data


# ============================================================================
# INLINE ADMIN CLASSES
# ============================================================================

class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile"""
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
    readonly_fields = ('skills', 'achievements', 'education_background')


class TwoFactorAuthInline(admin.StackedInline):
    """Inline admin for TwoFactorAuth"""
    model = TwoFactorAuth
    can_delete = False
    verbose_name_plural = _('Two Factor Authentication')
    fields = (
        'is_enabled', 'primary_method', 'last_used',
        'recovery_email', 'recovery_phone', 'last_backup_code_generated'
    )
    readonly_fields = ('secret_key', 'backup_codes')


# ============================================================================
# CUSTOM FILTERS
# ============================================================================

class RoleFilter(admin.SimpleListFilter):
    """Filter users by role"""
    title = _('Role')
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        return UserRole.choices

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
        if self.value() == 'incomplete':
            return queryset.filter(profile_completed=False)
        return queryset


class AccountStatusFilter(admin.SimpleListFilter):
    """Filter users by account status"""
    title = _('Account Status')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('active', _('Active')),
            ('suspended', _('Suspended')),
            ('pending_approval', _('Pending Approval')),
            ('on_leave', _('On Leave')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True, is_suspended=False)
        if self.value() == 'suspended':
            return queryset.filter(is_suspended=True)
        if self.value() == 'pending_approval':
            return queryset.filter(is_approved=False, is_active=True)
        if self.value() == 'on_leave':
            return queryset.filter(is_on_leave=True)
        return queryset


class LastLoginFilter(admin.SimpleListFilter):
    """Filter users by last login time"""
    title = _('Last Login')
    parameter_name = 'last_login'

    def lookups(self, request, model_admin):
        return (
            ('today', _('Today')),
            ('week', _('This Week')),
            ('month', _('This Month')),
            ('year', _('This Year')),
            ('never', _('Never Logged In')),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'today':
            today = now.date()
            return queryset.filter(last_login__date=today)
        if self.value() == 'week':
            week_ago = now - timedelta(days=7)
            return queryset.filter(last_login__gte=week_ago)
        if self.value() == 'month':
            month_ago = now - timedelta(days=30)
            return queryset.filter(last_login__gte=month_ago)
        if self.value() == 'year':
            year_ago = now - timedelta(days=365)
            return queryset.filter(last_login__gte=year_ago)
        if self.value() == 'never':
            return queryset.filter(last_login__isnull=True)
        return queryset


# ============================================================================
# ADMIN ACTIONS
# ============================================================================

@admin.action(description=_("Approve selected users"))
def approve_users(modeladmin, request, queryset):
    """Approve selected users"""
    updated = queryset.update(is_approved=True, is_verified=True)
    modeladmin.message_user(
        request,
        _("Successfully approved %(count)d user(s)") % {'count': updated},
        messages.SUCCESS
    )


@admin.action(description=_("Suspend selected users"))
def suspend_users(modeladmin, request, queryset):
    """Suspend selected users"""
    updated = queryset.update(is_suspended=True)
    modeladmin.message_user(
        request,
        _("Successfully suspended %(count)d user(s)") % {'count': updated},
        messages.SUCCESS
    )


@admin.action(description=_("Unsuspend selected users"))
def unsuspend_users(modeladmin, request, queryset):
    """Unsuspend selected users"""
    updated = queryset.update(is_suspended=False)
    modeladmin.message_user(
        request,
        _("Successfully unsuspended %(count)d user(s)") % {'count': updated},
        messages.SUCCESS
    )


@admin.action(description=_("Mark as verified"))
def verify_users(modeladmin, request, queryset):
    """Mark selected users as verified"""
    updated = queryset.update(is_verified=True, email_verified=True)
    modeladmin.message_user(
        request,
        _("Successfully verified %(count)d user(s)") % {'count': updated},
        messages.SUCCESS
    )


@admin.action(description=_("Send verification email"))
def send_verification_email(modeladmin, request, queryset):
    """Send verification email to selected users"""
    success_count = 0
    for user in queryset:
        try:
            user.send_verification_email(request)
            success_count += 1
        except Exception as e:
            modeladmin.message_user(
                request,
                _("Failed to send verification email to %(email)s: %(error)s") % {
                    'email': user.email,
                    'error': str(e)
                },
                messages.ERROR
            )
    
    if success_count > 0:
        modeladmin.message_user(
            request,
            _("Verification emails sent to %(count)d user(s)") % {'count': success_count},
            messages.SUCCESS
        )


@admin.action(description=_("Reset password"))
def reset_password(modeladmin, request, queryset):
    """Initiate password reset for selected users"""
    success_count = 0
    for user in queryset:
        try:
            user.initiate_password_reset(request)
            success_count += 1
        except Exception as e:
            modeladmin.message_user(
                request,
                _("Failed to reset password for %(email)s: %(error)s") % {
                    'email': user.email,
                    'error': str(e)
                },
                messages.ERROR
            )
    
    if success_count > 0:
        modeladmin.message_user(
            request,
            _("Password reset emails sent to %(count)d user(s)") % {'count': success_count},
            messages.SUCCESS
        )


@admin.action(description=_("Export user data (GDPR)"))
def export_user_data(modeladmin, request, queryset):
    """Export user data for GDPR compliance"""
    data = []
    for user in queryset:
        user_data = user.export_data(include_sensitive=True)
        data.append(user_data)
    
    response = JsonResponse(data, safe=False)
    response['Content-Disposition'] = 'attachment; filename="user_data_export.json"'
    return response


@admin.action(description=_("Bulk activate users"))
def bulk_activate_users(modeladmin, request, queryset):
    """Activate selected users"""
    updated = queryset.update(is_active=True)
    modeladmin.message_user(
        request,
        _("Activated %(count)d user(s)") % {'count': updated},
        messages.SUCCESS
    )


@admin.action(description=_("Bulk deactivate users"))
def bulk_deactivate_users(modeladmin, request, queryset):
    """Deactivate selected users"""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(
        request,
        _("Deactivated %(count)d user(s)") % {'count': updated},
        messages.SUCCESS
    )


@admin.action(description=_("Force profile completion check"))
def force_profile_check(modeladmin, request, queryset):
    """Force profile completion check for selected users"""
    checked_count = 0
    for user in queryset:
        user.check_profile_completion(force_check=True)
        checked_count += 1
    
    modeladmin.message_user(
        request,
        _("Forced profile completion check for %(count)d user(s)") % {'count': checked_count},
        messages.SUCCESS
    )


# ============================================================================
# USER ADMIN
# ============================================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin interface"""
    
    # Use custom forms
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Fix the ordering field
    ordering = ('email',)
    
    # Inline configurations
    inlines = [UserProfileInline, TwoFactorAuthInline]
    
    # List display configuration
    list_display = (
        'email', 'get_full_name', 'role', 'is_active', 
        'is_verified', 'is_approved', 'is_suspended',
        'last_login', 'profile_completion_badge', 'action_buttons'
    )
    
    list_display_links = ('email', 'get_full_name')
    
    # List filters
    list_filter = (
        RoleFilter,
        ProfileCompletionFilter,
        AccountStatusFilter,
        LastLoginFilter,
        'is_staff', 
        'is_superuser',
        'email_verified',
        'phone_verified',
        'created_at'
    )
    
    # Search fields
    search_fields = (
        'email', 'first_name', 'last_name', 'middle_name',
        'admission_number', 'staff_id', 'phone_number',
        'id_number', 'parent_email'
    )
    
    # Fieldsets for add/edit form
    fieldsets = (
        (_('Authentication'), {
            'fields': ('email', 'password', 'role')
        }),
        (_('Personal Information'), {
            'fields': (
                ('first_name', 'middle_name', 'last_name'),
                'date_of_birth', 'gender', 'nationality',
                'id_number', 'profile_picture'
            )
        }),
        (_('Academy Information'), {
            'fields': (
                'admission_number', 'staff_id',
                'grade_level', 'current_class', 'house',
                'primary_curriculum', 'academic_year'
            )
        }),
        (_('Contact Information'), {
            'fields': (
                'phone_number', 'alternative_phone',
                'address', 'city', 'country'
            )
        }),
        (_('Emergency Contact'), {
            'fields': (
                'emergency_contact_name',
                'emergency_contact_phone',
                'emergency_contact_relationship',
                'emergency_contact_address'
            )
        }),
        (_('Medical Information'), {
            'fields': (
                'blood_group', 'medical_info',
                'allergies', 'chronic_conditions',
                'current_medications',
                'doctor_name', 'doctor_phone'
            )
        }),
        (_('Student Information'), {
            'fields': (
                'parent_name', 'parent_email',
                'parent_phone', 'parent_occupation',
                'previous_school'
            ),
            'classes': ('collapse',)
        }),
        (_('Professional Information'), {
            'fields': (
                'department', 'qualification',
                'specialization', 'designation',
                'years_of_experience', 'employment_date'
            ),
            'classes': ('collapse',)
        }),
        (_('Documents'), {
            'fields': (
                'transfer_certificate',
                'birth_certificate',
                'recommendation_letter'
            ),
            'classes': ('collapse',)
        }),
        (_('Status & Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'is_verified', 'is_approved', 'is_suspended',
                'is_on_leave', 'email_verified', 'phone_verified',
                'groups', 'user_permissions'
            )
        }),
        (_('Profile & Settings'), {
            'fields': (
                'profile_completed', 'profile_completion_date',
                'preferred_dashboard_view', 'dashboard_widgets',
                'theme_preference'
            )
        }),
        (_('Login Information'), {
            'fields': (
                'last_login', 'last_login_ip',
                'login_count', 'failed_login_attempts',
                'account_locked_until',
                'password_changed_at'
            ),
            'classes': ('collapse',)
        }),
        (_('Important Dates'), {
            'fields': ('date_joined', 'enrollment_date', 'last_profile_update'),
            'classes': ('collapse',)
        }),
    )
    
    # Add form fieldsets - simplified for new user creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'role',
                'password1', 'password2'
            ),
        }),
    )
    
    # Admin actions
    actions = [
        approve_users,
        suspend_users,
        unsuspend_users,
        verify_users,
        send_verification_email,
        reset_password,
        bulk_activate_users,
        bulk_deactivate_users,
        force_profile_check,
        export_user_data
    ]
    
    # Readonly fields for viewing
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:  # editing an existing object
            readonly_fields.extend([
                'last_login', 'last_login_ip', 'login_count',
                'failed_login_attempts', 'password_changed_at',
                'date_joined', 'profile_completion_date',
                'last_profile_update', 'admission_number', 'staff_id'
            ])
        return readonly_fields
    
    # Formfield overrides
    formfield_overrides = {
        models.JSONField: {'widget': admin.widgets.AdminTextareaWidget},
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget},
    }
    
    # ====================
    # CUSTOM LIST DISPLAY METHODS
    # ====================
    
    def get_full_name(self, obj):
        """Display full name in admin"""
        return obj.get_full_name()
    get_full_name.short_description = _('Full Name')
    get_full_name.admin_order_field = 'first_name'
    
    def profile_completion_badge(self, obj):
        """Display profile completion as colored badge"""
        percentage = obj.profile_completion_percentage
        if percentage >= 100:
            color = 'green'
        elif percentage >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, percentage
        )
    profile_completion_badge.short_description = _('Profile Complete')
    
    def action_buttons(self, obj):
        """Display quick action buttons"""
        return format_html(
            '<div class="action-buttons">'
            '<a href="{}" class="button" title="{}">🔐</a> '
            '<a href="{}" class="button" title="{}">📧</a> '
            '<a href="{}" class="button" title="{}">👁️</a>'
            '</div>',
            reverse('admin:auth_user_password_change', args=[obj.id]),
            _('Change Password'),
            reverse('admin:accounts_user_send_verification', args=[obj.id]),
            _('Send Verification Email'),
            reverse('admin:accounts_user_view_logins', args=[obj.id]),
            _('View Login History')
        )
    action_buttons.short_description = _('Actions')
    
    # ====================
    # CUSTOM URLS AND VIEWS
    # ====================
    
    def get_urls(self):
        """Add custom URLs to user admin"""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/send-verification/',
                self.admin_site.admin_view(self.send_verification_view),
                name='accounts_user_send_verification'
            ),
            path(
                '<path:object_id>/view-logins/',
                self.admin_site.admin_view(self.view_logins_view),
                name='accounts_user_view_logins'
            ),
        ]
        return custom_urls + urls
    
    def send_verification_view(self, request, object_id):
        """Custom view to send verification email"""
        try:
            user = User.objects.get(id=object_id)
            user.send_verification_email(request)
            self.message_user(
                request,
                _('Verification email sent to %(email)s') % {'email': user.email},
                messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request,
                _('Failed to send verification email: %(error)s') % {'error': str(e)},
                messages.ERROR
            )
        
        return redirect(reverse('admin:accounts_user_change', args=[object_id]))
    
    def view_logins_view(self, request, object_id):
        """Custom view to display user login history"""
        try:
            user = User.objects.get(id=object_id)
            login_history = LoginHistory.objects.filter(user=user).order_by('-created_at')[:50]
            
            context = {
                'title': _('Login History for %s') % user.email,
                'user': user,
                'login_history': login_history,
                'opts': self.model._meta,
                'app_label': self.model._meta.app_label,
                'media': self.media,
                'has_view_permission': True,
                'has_add_permission': False,
                'has_change_permission': False,
                'has_delete_permission': False,
            }
            
            return render(request, 'admin/accounts/user/view_logins.html', context)
            
        except User.DoesNotExist:
            self.message_user(request, _('User not found'), messages.ERROR)
            return redirect(reverse('admin:accounts_user_changelist'))
    
    # ====================
    # CUSTOM VIEWS AND STATISTICS
    # ====================
    
    def changelist_view(self, request, extra_context=None):
        """Add statistics to changelist view"""
        response = super().changelist_view(request, extra_context=extra_context)
        
        try:
            # Get statistics
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            staff_users = User.objects.filter(is_staff=True).count()
            verified_users = User.objects.filter(is_verified=True).count()
            
            # Role statistics
            role_stats = User.objects.values('role').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Profile completion statistics
            completed_profiles = User.objects.filter(profile_completed=True).count()
            incomplete_profiles = total_users - completed_profiles
            
            # Login statistics
            recent_logins = User.objects.filter(
                last_login__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            statistics = {
                'total_users': total_users,
                'active_users': active_users,
                'staff_users': staff_users,
                'verified_users': verified_users,
                'role_stats': role_stats,
                'completed_profiles': completed_profiles,
                'incomplete_profiles': incomplete_profiles,
                'recent_logins': recent_logins,
            }
            
            if extra_context is None:
                extra_context = {}
            extra_context.update(statistics)
            
            response.context_data.update(extra_context)
            
        except Exception as e:
            logger.error(f"Error loading statistics: {e}")
            self.message_user(request, f"Error loading statistics: {e}", messages.ERROR)
        
        return response
    
    # ====================
    # SAVE AND QUERYSET METHODS
    # ====================
    
    def save_model(self, request, obj, form, change):
        """Custom save model to handle password and logging"""
        if not change:  # New user
            if 'password' in form.cleaned_data and form.cleaned_data['password']:
                obj.set_password(form.cleaned_data['password'])
        
        super().save_model(request, obj, form, change)
        
        # Log the action
        if change:
            action = _('updated')
        else:
            action = _('created')
        
        self.log_change(request, obj, [{'changed': {'fields': list(form.changed_data)}}])
    
    def get_queryset(self, request):
        """Custom queryset to optimize performance"""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'user_profile', 'two_factor_auth'
        ).prefetch_related(
            'groups', 'user_permissions'
        )


# ============================================================================
# USER PROFILE ADMIN
# ============================================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile"""
    
    list_display = ('user', 'language', 'timezone', 'notifications_enabled')
    list_filter = ('language', 'timezone', 'notifications_enabled', 'profile_visibility')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'bio')
    raw_id_fields = ('user',)
    
    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        (_('Profile Information'), {
            'fields': ('bio', 'website', 'social_links', 'hobbies')
        }),
        (_('Settings'), {
            'fields': (
                'language', 'timezone', 'profile_visibility',
                'contact_preference'
            )
        }),
        (_('Notifications'), {
            'fields': (
                'notifications_enabled',
                'email_notifications',
                'sms_notifications',
                'push_notifications'
            )
        }),
        (_('Skills & Achievements'), {
            'fields': ('skills', 'achievements', 'education_background'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['user'] + list(super().get_readonly_fields(request, obj))
        return super().get_readonly_fields(request, obj)


# ============================================================================
# TWO FACTOR AUTH ADMIN
# ============================================================================

@admin.register(TwoFactorAuth)
class TwoFactorAuthAdmin(admin.ModelAdmin):
    """Admin for TwoFactorAuth"""
    
    list_display = ('user', 'is_enabled', 'primary_method', 'last_used')
    list_filter = ('is_enabled', 'primary_method', 'last_used')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)
    readonly_fields = ('secret_key', 'backup_codes', 'last_backup_code_generated')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'is_enabled', 'primary_method')
        }),
        (_('Security Information'), {
            'fields': ('secret_key', 'backup_codes'),
            'classes': ('collapse',)
        }),
        (_('Recovery Options'), {
            'fields': ('recovery_email', 'recovery_phone')
        }),
        (_('Activity'), {
            'fields': ('last_used', 'last_backup_code_generated')
        }),
        (_('Session Management'), {
            'fields': (
                'pending_session_token',
                'pending_session_expiry',
                'pending_redirect_url'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['enable_2fa', 'disable_2fa', 'generate_backup_codes']
    
    @admin.action(description=_("Enable 2FA for selected users"))
    def enable_2fa(self, request, queryset):
        """Enable 2FA for selected users"""
        updated = queryset.update(is_enabled=True)
        self.message_user(
            request,
            _("Enabled 2FA for %(count)d user(s)") % {'count': updated},
            messages.SUCCESS
        )
    
    @admin.action(description=_("Disable 2FA for selected users"))
    def disable_2fa(self, request, queryset):
        """Disable 2FA for selected users"""
        for obj in queryset:
            obj.disable_2fa()
        self.message_user(
            request,
            _("Disabled 2FA for %(count)d user(s)") % {'count': queryset.count()},
            messages.SUCCESS
        )
    
    @admin.action(description=_("Generate backup codes"))
    def generate_backup_codes(self, request, queryset):
        """Generate backup codes for selected users"""
        for obj in queryset:
            if obj.is_enabled:
                backup_codes = obj.generate_backup_codes()
                self.message_user(
                    request,
                    _("Generated backup codes for %(email)s") % {'email': obj.user.email},
                    messages.SUCCESS
                )
            else:
                self.message_user(
                    request,
                    _("2FA is not enabled for %(email)s") % {'email': obj.user.email},
                    messages.WARNING
                )


# ============================================================================
# OTP TOKEN ADMIN
# ============================================================================

@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
    """Admin for OTPToken"""
    
    list_display = ('user', 'token', 'token_type', 'is_used', 'created_at', 'expires_at')
    list_filter = ('token_type', 'is_used', 'created_at')
    search_fields = ('user__email', 'token', 'purpose')
    raw_id_fields = ('user',)
    readonly_fields = ('token', 'ip_address', 'user_agent')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'token', 'token_type', 'purpose')
        }),
        (_('Status'), {
            'fields': ('is_used', 'used_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'expires_at')
        }),
        (_('Request Information'), {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    # Don't allow adding new tokens via admin
    def has_add_permission(self, request):
        return False
    
    # Don't allow changing existing tokens
    def has_change_permission(self, request, obj=None):
        return False if obj else True
    
    # Actions
    actions = ['mark_as_used', 'mark_as_unused', 'cleanup_expired_tokens']
    
    @admin.action(description=_("Mark selected tokens as used"))
    def mark_as_used(self, request, queryset):
        """Mark selected tokens as used"""
        updated = queryset.update(is_used=True, used_at=timezone.now())
        self.message_user(
            request,
            _("Marked %(count)d token(s) as used") % {'count': updated},
            messages.SUCCESS
        )
    
    @admin.action(description=_("Mark selected tokens as unused"))
    def mark_as_unused(self, request, queryset):
        """Mark selected tokens as unused"""
        updated = queryset.update(is_used=False, used_at=None)
        self.message_user(
            request,
            _("Marked %(count)d token(s) as unused") % {'count': updated},
            messages.SUCCESS
        )
    
    @admin.action(description=_("Cleanup expired tokens"))
    def cleanup_expired_tokens(self, request, queryset=None):
        """Cleanup expired tokens"""
        if queryset is None:
            expired_tokens = OTPToken.objects.filter(expires_at__lt=timezone.now())
        else:
            expired_tokens = queryset.filter(expires_at__lt=timezone.now())
        
        count, _ = expired_tokens.delete()
        self.message_user(
            request,
            _("Deleted %(count)d expired token(s)") % {'count': count},
            messages.SUCCESS
        )
    
    def get_queryset(self, request):
        """Show only recent tokens by default"""
        qs = super().get_queryset(request)
        return qs.filter(created_at__gte=timezone.now() - timedelta(days=30))


# ============================================================================
# LOGIN HISTORY ADMIN
# ============================================================================

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """Admin for LoginHistory"""
    
    list_display = ('user', 'ip_address', 'login_status', 'created_at', 'is_suspicious')
    list_filter = ('login_status', 'is_suspicious', 'created_at', 'device_type', 'browser')
    search_fields = ('user__email', 'ip_address', 'location', 'user_agent')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'login_status', 'failure_reason')
        }),
        (_('Device Information'), {
            'fields': ('device_type', 'browser', 'platform', 'user_agent')
        }),
        (_('Location Information'), {
            'fields': ('ip_address', 'country', 'city', 'location')
        }),
        (_('Security'), {
            'fields': ('is_suspicious', 'two_fa_method', 'session_key')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    # Don't allow adding new login history via admin
    def has_add_permission(self, request):
        return False
    
    # Don't allow changing login history
    def has_change_permission(self, request, obj=None):
        return False
    
    # Actions
    actions = ['mark_as_suspicious', 'mark_as_not_suspicious', 'export_to_csv']
    
    @admin.action(description=_("Mark selected entries as suspicious"))
    def mark_as_suspicious(self, request, queryset):
        """Mark selected entries as suspicious"""
        updated = queryset.update(is_suspicious=True)
        self.message_user(
            request,
            _("Marked %(count)d entry(s) as suspicious") % {'count': updated},
            messages.SUCCESS
        )
    
    @admin.action(description=_("Mark selected entries as not suspicious"))
    def mark_as_not_suspicious(self, request, queryset):
        """Mark selected entries as not suspicious"""
        updated = queryset.update(is_suspicious=False)
        self.message_user(
            request,
            _("Marked %(count)d entry(s) as not suspicious") % {'count': updated},
            messages.SUCCESS
        )
    
    @admin.action(description=_("Export to CSV"))
    def export_to_csv(self, request, queryset):
        """Export selected login history to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="login_history.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'User', 'IP Address', 'Status', 'Device', 'Browser',
            'Country', 'City', 'Date', 'Suspicious'
        ])
        
        for entry in queryset:
            writer.writerow([
                entry.user.email,
                entry.ip_address,
                entry.get_login_status_display(),
                entry.device_type,
                entry.browser,
                entry.country,
                entry.city,
                entry.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Yes' if entry.is_suspicious else 'No'
            ])
        
        return response
    
    def get_queryset(self, request):
        """Show only recent login history by default"""
        qs = super().get_queryset(request)
        return qs.filter(created_at__gte=timezone.now() - timedelta(days=7))
    
    # Custom changelist view with statistics
    def changelist_view(self, request, extra_context=None):
        """Add statistics to changelist view"""
        response = super().changelist_view(request, extra_context=extra_context)
        
        try:
            # Get statistics for the last 7 days
            week_ago = timezone.now() - timedelta(days=7)
            
            total_logins = LoginHistory.objects.filter(created_at__gte=week_ago).count()
            successful_logins = LoginHistory.objects.filter(
                login_status=LoginStatusChoices.SUCCESS,
                created_at__gte=week_ago
            ).count()
            failed_logins = LoginHistory.objects.filter(
                login_status=LoginStatusChoices.FAILED,
                created_at__gte=week_ago
            ).count()
            suspicious_activity = LoginHistory.objects.filter(
                is_suspicious=True,
                created_at__gte=week_ago
            ).count()
            
            # Top countries
            top_countries = LoginHistory.objects.filter(
                created_at__gte=week_ago
            ).exclude(country='').values('country').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
            
            # Top browsers
            top_browsers = LoginHistory.objects.filter(
                created_at__gte=week_ago
            ).exclude(browser='').values('browser').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
            
            statistics = {
                'total_logins': total_logins,
                'successful_logins': successful_logins,
                'failed_logins': failed_logins,
                'suspicious_activity': suspicious_activity,
                'top_countries': top_countries,
                'top_browsers': top_browsers,
            }
            
            if extra_context is None:
                extra_context = {}
            extra_context.update(statistics)
            
            response.context_data.update(extra_context)
            
        except Exception as e:
            logger.error(f"Error loading statistics: {e}")
            self.message_user(request, f"Error loading statistics: {e}", messages.ERROR)
        
        return response


# ============================================================================
# EMAIL VERIFICATION ADMIN
# ============================================================================

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """Admin for EmailVerification"""
    
    list_display = ('user', 'token', 'is_used', 'created_at', 'expires_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'token')
    raw_id_fields = ('user',)
    readonly_fields = ('token', 'used_at')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'token')
        }),
        (_('Status'), {
            'fields': ('is_used', 'used_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'expires_at')
        }),
    )
    
    # Don't allow adding new tokens via admin
    def has_add_permission(self, request):
        return False
    
    # Don't allow changing existing tokens
    def has_change_permission(self, request, obj=None):
        return False if obj else True
    
    # Actions
    actions = ['mark_as_used', 'mark_as_unused', 'cleanup_expired_tokens']
    
    @admin.action(description=_("Mark selected tokens as used"))
    def mark_as_used(self, request, queryset):
        """Mark selected tokens as used"""
        updated = queryset.update(is_used=True, used_at=timezone.now())
        self.message_user(
            request,
            _("Marked %(count)d token(s) as used") % {'count': updated},
            messages.SUCCESS
        )
    
    @admin.action(description=_("Mark selected tokens as unused"))
    def mark_as_unused(self, request, queryset):
        """Mark selected tokens as unused"""
        updated = queryset.update(is_used=False, used_at=None)
        self.message_user(
            request,
            _("Marked %(count)d token(s) as unused") % {'count': updated},
            messages.SUCCESS
        )
    
    @admin.action(description=_("Cleanup expired tokens"))
    def cleanup_expired_tokens(self, request, queryset=None):
        """Cleanup expired tokens"""
        if queryset is None:
            expired_tokens = EmailVerification.objects.filter(expires_at__lt=timezone.now())
        else:
            expired_tokens = queryset.filter(expires_at__lt=timezone.now())
        
        count, _ = expired_tokens.delete()
        self.message_user(
            request,
            _("Deleted %(count)d expired token(s)") % {'count': count},
            messages.SUCCESS
        )
    
    def get_queryset(self, request):
        """Show only recent tokens by default"""
        qs = super().get_queryset(request)
        return qs.filter(created_at__gte=timezone.now() - timedelta(days=30))


# ============================================================================
# LOGIN SESSION ADMIN
# ============================================================================

@admin.register(LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    """Admin for LoginSession"""
    
    list_display = ('user', 'session_token', 'status', 'ip_address', 'created_at', 'expires_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'session_token', 'ip_address')
    raw_id_fields = ('user',)
    readonly_fields = ('session_token', 'jwt_access_token', 'jwt_refresh_token')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'session_token', 'status')
        }),
        (_('Device Information'), {
            'fields': ('ip_address', 'user_agent', 'device_info')
        }),
        (_('OTP Verification'), {
            'fields': ('otp_sent_at', 'otp_verified_at')
        }),
        (_('JWT Tokens'), {
            'fields': ('jwt_access_token', 'jwt_refresh_token'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'expires_at', 'last_activity')
        }),
    )
    
    # Don't allow adding new sessions via admin
    def has_add_permission(self, request):
        return False
    
    # Don't allow changing sessions
    def has_change_permission(self, request, obj=None):
        return False
    
    # Actions
    actions = ['revoke_sessions', 'cleanup_expired_sessions']
    
    @admin.action(description=_("Revoke selected sessions"))
    def revoke_sessions(self, request, queryset):
        """Revoke selected login sessions"""
        revoked_count = 0
        for session in queryset:
            session.revoke()
            revoked_count += 1
        
        self.message_user(
            request,
            _("Revoked %(count)d session(s)") % {'count': revoked_count},
            messages.SUCCESS
        )
    
    @admin.action(description=_("Cleanup expired sessions"))
    def cleanup_expired_sessions(self, request, queryset=None):
        """Cleanup expired sessions"""
        if queryset is None:
            expired_sessions = LoginSession.objects.filter(expires_at__lt=timezone.now())
        else:
            expired_sessions = queryset.filter(expires_at__lt=timezone.now())
        
        count, _ = expired_sessions.delete()
        self.message_user(
            request,
            _("Deleted %(count)d expired session(s)") % {'count': count},
            messages.SUCCESS
        )
    
    def get_queryset(self, request):
        """Show only recent sessions by default"""
        qs = super().get_queryset(request)
        return qs.filter(created_at__gte=timezone.now() - timedelta(days=7))


# ============================================================================
# ADMIN SITE CONFIGURATION
# ============================================================================

# Configure the default admin site
admin.site.site_header = _("Delvok Academy Management System")
admin.site.site_title = _("Delvok Academy Admin Portal")
admin.site.index_title = _("System Administration")


# ============================================================================
# TEMPLATE CUSTOMIZATIONS
# ============================================================================

class DelvokAdminSite(admin.AdminSite):
    """Custom admin site for Delvok Academy"""
    
    site_header = _("Delvok Academy Management System")
    site_title = _("Delvok Academy Admin")
    index_title = _("System Administration")
    
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_list = super().get_app_list(request)
        
        # Custom ordering of apps
        app_ordering = {
            'accounts': 1,
            'auth': 2,
            # Add other apps here
        }
        
        # Sort apps by custom ordering
        app_list.sort(key=lambda x: app_ordering.get(x['app_label'], 999))
        
        return app_list


# Uncomment to use custom admin site
# admin_site = DelvokAdminSite(name='delvok_admin')
# Then register models with admin_site instead of admin.site


# ============================================================================
# ADMIN CSS CUSTOMIZATION
# ============================================================================

class Media:
    """Custom CSS for admin interface"""
    css = {
        'all': ('admin/css/custom.css',)
    }


# Add custom CSS class to action buttons
admin.site.enable_nav_sidebar = True