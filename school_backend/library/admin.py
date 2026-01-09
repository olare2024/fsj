from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    BookCategory, Author, Publisher, Book, BookCopy, 
    BorrowRecord, BookReview, ReadingList, ReadingListItem,
    BookReservation, DigitalResource, LibraryStats, TeacherResource
)


# ==================== INLINES ====================
class BookCopyInline(admin.TabularInline):
    """Inline for book copies"""
    model = BookCopy
    extra = 0
    readonly_fields = ['barcode', 'acquisition_date']
    fields = ['copy_number', 'barcode', 'condition', 'acquisition_date', 'notes']
    show_change_link = True


class BorrowRecordInline(admin.TabularInline):
    """Inline for borrow records"""
    model = BorrowRecord
    extra = 0
    readonly_fields = ['borrow_date', 'due_date', 'status']
    fields = ['borrower', 'borrow_date', 'due_date', 'status', 'returned']
    raw_id_fields = ['borrower']
    show_change_link = True
    max_num = 5


class BookReviewInline(admin.TabularInline):
    """Inline for book reviews"""
    model = BookReview
    extra = 0
    readonly_fields = ['created_at', 'helpful_votes']
    fields = ['user', 'rating', 'title', 'is_approved', 'helpful_votes']
    raw_id_fields = ['user']


class ReadingListItemInline(admin.TabularInline):
    """Inline for reading list items"""
    model = ReadingListItem
    extra = 1
    fields = ['book', 'priority', 'completed', 'completed_date', 'notes']
    raw_id_fields = ['book']


# ==================== CUSTOM FILTERS ====================
class IsAvailableFilter(admin.SimpleListFilter):
    """Filter for available books"""
    title = 'availability'
    parameter_name = 'available'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Available'),
            ('no', 'Not Available'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(available_copies__gt=0)
        if self.value() == 'no':
            return queryset.filter(available_copies=0)


class IsOverdueFilter(admin.SimpleListFilter):
    """Filter for overdue borrows"""
    title = 'overdue status'
    parameter_name = 'overdue'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Overdue'),
            ('no', 'Not Overdue'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'yes':
            return queryset.filter(returned=False, due_date__lt=now)
        if self.value() == 'no':
            return queryset.filter(returned=False, due_date__gte=now)


class BookTypeFilter(admin.SimpleListFilter):
    """Filter by book type"""
    title = 'book type'
    parameter_name = 'book_type'

    def lookups(self, request, model_admin):
        from .models import Book
        return Book.BOOK_TYPES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(book_type=self.value())


# ==================== ADMIN CLASSES ====================
@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    """Admin for book categories"""
    list_display = ['name', 'parent', 'book_count', 'subcategory_count', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'name': ('name',)}
    readonly_fields = ['book_count', 'subcategory_count']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'parent', 'is_active')
        }),
        ('Display', {
            'fields': ('icon', 'color'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin for authors"""
    list_display = ['full_name', 'nationality', 'book_count', 'is_active']
    list_filter = ['nationality', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'middle_name', 'biography']
    readonly_fields = ['book_count', 'full_name']
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'nationality')
        }),
        ('Biographical Information', {
            'fields': ('birth_date', 'death_date', 'biography'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('email', 'website'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('photo',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(TeacherResource)
class TeacherResourceAdmin(admin.ModelAdmin):
    """Admin for teacher resources"""
    list_display = [
        'title', 'resource_type', 'subject', 'grade_level', 
        'download_count', 'view_count', 'is_public', 'created_by'
    ]
    list_filter = ['resource_type', 'is_public', 'curriculum', 'grade_level', 'created_at']
    search_fields = ['title', 'description', 'author__username']
    readonly_fields = ['download_count', 'view_count', 'created_by']
    raw_id_fields = ['subject', 'author', 'created_by']
    filter_horizontal = ['access_groups']
    actions = ['make_public', 'make_private', 'reset_download_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'resource_type')
        }),
        ('File Information', {
            'fields': ('file', 'thumbnail')
        }),
        ('Academic Information', {
            'fields': ('subject', 'grade_level', 'curriculum')
        }),
        ('Author Information', {
            'fields': ('author', 'created_by'),
            'classes': ('collapse',)
        }),
        ('Access Control', {
            'fields': ('is_public', 'access_groups', 'download_count', 'view_count')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def make_public(self, request, queryset):
        """Make selected resources public"""
        queryset.update(is_public=True)
        self.message_user(request, f"{queryset.count()} teacher resources made public.")
    make_public.short_description = "Make public"
    
    def make_private(self, request, queryset):
        """Make selected resources private"""
        queryset.update(is_public=False)
        self.message_user(request, f"{queryset.count()} teacher resources made private.")
    make_private.short_description = "Make private"
    
    def reset_download_count(self, request, queryset):
        """Reset download count for selected resources"""
        queryset.update(download_count=0)
        self.message_user(request, f"Download count reset for {queryset.count()} resources.")
    reset_download_count.short_description = "Reset download count"
    
    def get_queryset(self, request):
        """Optimize queryset for admin"""
        return super().get_queryset(request).select_related(
            'subject', 'author', 'created_by'
        )

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """Admin for publishers"""
    list_display = ['name', 'city', 'country', 'book_count', 'is_active']
    list_filter = ['country', 'city', 'is_active']
    search_fields = ['name', 'address', 'email']
    readonly_fields = ['book_count']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'logo')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'country', 'phone', 'email', 'website')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin for books"""
    list_display = [
        'title', 'book_type', 'format', 'available_copies', 
        'total_copies', 'is_reference', 'is_available', 'average_rating'
    ]
    list_filter = [
        IsAvailableFilter, 'book_type', 'format', 'language', 
        'curriculum', 'is_reference', 'is_digital', 'created_at'
    ]
    search_fields = ['title', 'isbn', 'description', 'keywords']
    readonly_fields = [
        'available_copies', 'borrow_count', 'average_rating', 
        'date_added', 'last_updated', 'is_available'
    ]
    raw_id_fields = ['authors', 'publisher', 'subject']
    filter_horizontal = ['categories']
    inlines = [BookCopyInline, BorrowRecordInline, BookReviewInline]
    actions = ['mark_as_reference', 'mark_as_digital', 'update_availability']
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'isbn', 'description')
        }),
        ('Classification', {
            'fields': ('book_type', 'format', 'language', 'categories', 'keywords')
        }),
        ('Academic Information', {
            'fields': ('subject', 'curriculum', 'grade_level'),
            'classes': ('collapse',)
        }),
        ('Author & Publisher', {
            'fields': ('authors', 'publisher', 'publication_year', 'edition'),
            'classes': ('collapse',)
        }),
        ('Physical Details', {
            'fields': ('pages', 'dimensions', 'weight'),
            'classes': ('collapse',)
        }),
        ('Inventory', {
            'fields': ('total_copies', 'available_copies', 'shelf_location', 
                      'accession_number', 'barcode')
        }),
        ('Media & Files', {
            'fields': ('cover_image', 'pdf_file', 'preview_file'),
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': ('price', 'currency'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_reference', 'is_digital', 'is_available', 
                      'borrow_count', 'average_rating')
        }),
    )
    
    def mark_as_reference(self, request, queryset):
        """Mark selected books as reference books"""
        queryset.update(is_reference=True)
        self.message_user(request, f"{queryset.count()} books marked as reference.")
    mark_as_reference.short_description = "Mark as reference books"
    
    def mark_as_digital(self, request, queryset):
        """Mark selected books as digital"""
        queryset.update(is_digital=True)
        self.message_user(request, f"{queryset.count()} books marked as digital.")
    mark_as_digital.short_description = "Mark as digital books"
    
    def update_availability(self, request, queryset):
        """Update availability for selected books"""
        for book in queryset:
            book.update_availability()
        self.message_user(request, f"Availability updated for {queryset.count()} books.")
    update_availability.short_description = "Update availability"
    
    def get_queryset(self, request):
        """Optimize queryset for admin"""
        return super().get_queryset(request).select_related(
            'publisher', 'subject'
        ).prefetch_related('authors', 'categories')


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    """Admin for book copies"""
    list_display = ['book', 'copy_number', 'barcode', 'condition', 'is_available', 'acquisition_date']
    list_filter = ['condition', 'acquisition_date', 'is_active']
    search_fields = ['book__title', 'barcode', 'notes']
    readonly_fields = ['is_available', 'current_borrower']
    raw_id_fields = ['book']
    fieldsets = (
        ('Copy Information', {
            'fields': ('book', 'copy_number', 'barcode', 'condition')
        }),
        ('Acquisition Details', {
            'fields': ('acquisition_date', 'acquisition_price', 'supplier'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Availability', {
            'fields': ('is_available', 'current_borrower')
        }),
    )
    
    def is_available(self, obj):
        """Display availability status with color"""
        if obj.is_available:
            return format_html('<span style="color: green;">✓ Available</span>')
        return format_html('<span style="color: red;">✗ Borrowed</span>')
    is_available.short_description = 'Availability'


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    """Admin for borrow records"""
    list_display = [
        'book', 'borrower', 'borrow_date', 'due_date', 
        'return_date', 'status', 'is_overdue', 'fine_amount'
    ]
    list_filter = [IsOverdueFilter, 'status', 'returned', 'borrow_date', 'due_date']
    search_fields = ['book__title', 'borrower__username', 'borrower__email']
    readonly_fields = [
        'is_overdue', 'overdue_days', 'calculated_fine', 
        'borrow_date', 'due_date', 'return_date'
    ]
    raw_id_fields = ['borrower', 'book', 'copy']
    list_select_related = ['book', 'borrower']
    actions = ['mark_as_returned', 'calculate_fines', 'send_overdue_notices']
    date_hierarchy = 'borrow_date'
    
    fieldsets = (
        ('Borrow Information', {
            'fields': ('borrower', 'book', 'copy', 'borrow_date', 'due_date')
        }),
        ('Return Information', {
            'fields': ('returned', 'return_date', 'returned_condition')
        }),
        ('Renewals', {
            'fields': ('renewals', 'max_renewals'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'is_overdue', 'overdue_days')
        }),
        ('Fines & Fees', {
            'fields': ('fine_amount', 'calculated_fine', 'fine_paid', 'damage_fee')
        }),
        ('Approval', {
            'fields': ('approved_by', 'issued_by', 'received_by'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    def is_overdue(self, obj):
        """Display overdue status with color"""
        if obj.is_overdue:
            return format_html('<span style="color: red;">Yes ({0} days)</span>', obj.overdue_days)
        return format_html('<span style="color: green;">No</span>')
    is_overdue.short_description = 'Overdue'
    
    def mark_as_returned(self, request, queryset):
        """Mark selected records as returned"""
        count = 0
        for record in queryset.filter(returned=False):
            record.return_book()
            count += 1
        self.message_user(request, f"{count} records marked as returned.")
    mark_as_returned.short_description = "Mark as returned"
    
    def calculate_fines(self, request, queryset):
        """Calculate fines for selected overdue records"""
        overdue_records = queryset.filter(returned=False, due_date__lt=timezone.now())
        for record in overdue_records:
            record.fine_amount = record.calculated_fine
            record.save()
        self.message_user(request, f"Fines calculated for {overdue_records.count()} records.")
    calculate_fines.short_description = "Calculate fines"
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related(
            'book', 'borrower', 'copy'
        )


@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    """Admin for book reviews"""
    list_display = ['book', 'user', 'rating', 'is_approved', 'helpful_votes', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['book__title', 'user__username', 'title', 'review']
    raw_id_fields = ['book', 'user']
    actions = ['approve_reviews', 'disapprove_reviews']
    list_per_page = 50
    
    def approve_reviews(self, request, queryset):
        """Approve selected reviews"""
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} reviews approved.")
    approve_reviews.short_description = "Approve selected reviews"
    
    def disapprove_reviews(self, request, queryset):
        """Disapprove selected reviews"""
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} reviews disapproved.")
    disapprove_reviews.short_description = "Disapprove selected reviews"


@admin.register(ReadingList)
class ReadingListAdmin(admin.ModelAdmin):
    """Admin for reading lists"""
    list_display = ['name', 'user', 'is_public', 'book_count', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    raw_id_fields = ['user']
    inlines = [ReadingListItemInline]
    readonly_fields = ['book_count']
    
    def book_count(self, obj):
        """Count of books in reading list"""
        return obj.books.count()
    book_count.short_description = 'Books'


@admin.register(ReadingListItem)
class ReadingListItemAdmin(admin.ModelAdmin):
    """Admin for reading list items"""
    list_display = ['reading_list', 'book', 'priority', 'completed', 'added_date']
    list_filter = ['completed', 'priority', 'added_date']
    search_fields = ['reading_list__name', 'book__title', 'notes']
    raw_id_fields = ['reading_list', 'book']
    list_select_related = ['reading_list', 'book']


@admin.register(BookReservation)
class BookReservationAdmin(admin.ModelAdmin):
    """Admin for book reservations"""
    list_display = [
        'book', 'user', 'requested_date', 'expiry_date', 
        'status', 'is_expired', 'priority'
    ]
    list_filter = ['status', 'requested_date', 'expiry_date']
    search_fields = ['book__title', 'user__username']
    readonly_fields = ['is_expired', 'requested_date']
    raw_id_fields = ['user', 'book', 'fulfilled_by']
    actions = ['mark_as_confirmed', 'mark_as_ready', 'cancel_reservations']
    
    def is_expired(self, obj):
        """Display expiration status"""
        if obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Active</span>')
    is_expired.short_description = 'Expiration'
    
    def mark_as_confirmed(self, request, queryset):
        """Mark selected reservations as confirmed"""
        queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f"{queryset.count()} reservations confirmed.")
    mark_as_confirmed.short_description = "Mark as confirmed"
    
    def mark_as_ready(self, request, queryset):
        """Mark selected reservations as ready for pickup"""
        queryset.filter(status__in=['pending', 'confirmed']).update(status='ready')
        self.message_user(request, f"{queryset.count()} reservations marked as ready.")
    mark_as_ready.short_description = "Mark as ready for pickup"
    
    def cancel_reservations(self, request, queryset):
        """Cancel selected reservations"""
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} reservations cancelled.")
    cancel_reservations.short_description = "Cancel reservations"


@admin.register(DigitalResource)
class DigitalResourceAdmin(admin.ModelAdmin):
    """Admin for digital resources"""
    list_display = [
        'title', 'resource_type', 'file_size_mb', 
        'download_count', 'view_count', 'is_public'
    ]
    list_filter = ['resource_type', 'is_public', 'curriculum', 'created_at']
    search_fields = ['title', 'description', 'author', 'keywords']
    readonly_fields = ['file_size_mb', 'duration_formatted', 'download_count', 'view_count']
    filter_horizontal = ['categories', 'access_groups']
    raw_id_fields = ['subject']
    actions = ['make_public', 'make_private']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'resource_type')
        }),
        ('File Information', {
            'fields': ('file', 'url', 'thumbnail', 'file_size', 'duration')
        }),
        ('Metadata', {
            'fields': ('author', 'publisher', 'publication_date')
        }),
        ('Academic Information', {
            'fields': ('subject', 'curriculum', 'grade_level', 'categories')
        }),
        ('Access Control', {
            'fields': ('is_public', 'access_groups', 'download_count', 'view_count')
        }),
    )
    
    def make_public(self, request, queryset):
        """Make selected resources public"""
        queryset.update(is_public=True)
        self.message_user(request, f"{queryset.count()} resources made public.")
    make_public.short_description = "Make public"
    
    def make_private(self, request, queryset):
        """Make selected resources private"""
        queryset.update(is_public=False)
        self.message_user(request, f"{queryset.count()} resources made private.")
    make_private.short_description = "Make private"


@admin.register(LibraryStats)
class LibraryStatsAdmin(admin.ModelAdmin):
    """Admin for library statistics"""
    list_display = [
        'date', 'total_books', 'available_copies', 
        'borrowed_copies', 'daily_borrows', 'total_fines'
    ]
    list_filter = ['date']
    readonly_fields = ['date', 'total_books', 'total_copies', 'available_copies', 
                      'borrowed_copies', 'digital_resources', 'digital_downloads',
                      'daily_borrows', 'daily_returns', 'daily_reservations',
                      'active_borrowers', 'total_fines', 'fines_collected']
    date_hierarchy = 'date'
    
    def has_add_permission(self, request):
        """Prevent manual addition of stats"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of stats"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing of stats"""
        return False


# ==================== ADMIN CUSTOMIZATION ====================
class LibraryAdminSite(admin.AdminSite):
    """Custom admin site for library management"""
    site_header = "School Library Management System"
    site_title = "Library Admin"
    index_title = "Library Administration"
    
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request, app_label)
        
        # Sort the apps alphabetically
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        
        # Sort the models alphabetically within each app
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
        
        return app_list


# Create custom admin site instance
library_admin_site = LibraryAdminSite(name='library_admin')

# Register all models with custom admin site
library_admin_site.register(BookCategory, BookCategoryAdmin)
library_admin_site.register(Author, AuthorAdmin)
library_admin_site.register(Publisher, PublisherAdmin)
library_admin_site.register(Book, BookAdmin)
library_admin_site.register(BookCopy, BookCopyAdmin)
library_admin_site.register(BorrowRecord, BorrowRecordAdmin)
library_admin_site.register(BookReview, BookReviewAdmin)
library_admin_site.register(ReadingList, ReadingListAdmin)
library_admin_site.register(ReadingListItem, ReadingListItemAdmin)
library_admin_site.register(BookReservation, BookReservationAdmin)
library_admin_site.register(DigitalResource, DigitalResourceAdmin)
library_admin_site.register(LibraryStats, LibraryStatsAdmin)
library_admin_site.register(TeacherResource, TeacherResourceAdmin)