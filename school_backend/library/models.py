from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
import os
from django.core.validators import MinValueValidator, MaxValueValidator

from academics.models import Subject, Class
from accounts.models import User


class BaseLibraryModel(models.Model):
    """Abstract base model for all library models"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


# ==================== BOOK CATEGORIES ====================
class BookCategory(BaseLibraryModel):
    """Book categories for organization"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='subcategories'
    )
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Icon class for UI")
    color = models.CharField(max_length=7, blank=True, null=True, help_text="Hex color code")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Book Category"
        verbose_name_plural = "Book Categories"
    
    def __str__(self):
        return self.name
    
    @property
    def book_count(self):
        """Count of books in this category"""
        return self.books.count()
    
    @property
    def subcategory_count(self):
        """Count of subcategories"""
        return self.subcategories.count()


# ==================== AUTHORS AND PUBLISHERS ====================
class Author(BaseLibraryModel):
    """Book author information"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='authors/%Y/%m/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        unique_together = ['first_name', 'last_name', 'middle_name']
        verbose_name = "Author"
        verbose_name_plural = "Authors"
    
    def __str__(self):
        if self.middle_name:
            return f"{self.last_name}, {self.first_name} {self.middle_name}"
        return f"{self.last_name}, {self.first_name}"
    
    @property
    def full_name(self):
        """Get author's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def book_count(self):
        """Count of books by this author"""
        return self.books.count()


class Publisher(BaseLibraryModel):
    """Book publisher information"""
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    logo = models.ImageField(upload_to='publishers/%Y/%m/', blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Publisher"
        verbose_name_plural = "Publishers"
    
    def __str__(self):
        return self.name
    
    @property
    def book_count(self):
        """Count of books published by this publisher"""
        return self.books.count()


# ==================== BOOKS ====================
class Book(BaseLibraryModel):
    """Enhanced book model with comprehensive details"""
    BOOK_TYPES = [
        ('textbook', 'Textbook'),
        ('reference', 'Reference'),
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('biography', 'Biography'),
        ('magazine', 'Magazine'),
        ('journal', 'Journal'),
        ('research', 'Research Paper'),
        ('thesis', 'Thesis/Dissertation'),
        ('periodical', 'Periodical'),
    ]
    
    BOOK_FORMATS = [
        ('hardcover', 'Hardcover'),
        ('paperback', 'Paperback'),
        ('spiral', 'Spiral-bound'),
        ('ebook', 'E-Book'),
        ('audiobook', 'Audiobook'),
    ]
    
    LANGUAGES = [
        ('en', 'English'),
        ('sw', 'Kiswahili'),
        ('fr', 'French'),
        ('ar', 'Arabic'),
        ('other', 'Other'),
    ]
    
    CURRICULUM_CHOICES = [
        ('cbc', 'CBC'),
        ('8-4-4', '8-4-4'),
        ('igcse', 'IGCSE'),
        ('ib', 'International Baccalaureate'),
    ]
    
    # Basic information
    title = models.CharField(max_length=500)
    subtitle = models.CharField(max_length=500, blank=True, null=True)
    isbn = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        unique=True,
        verbose_name="ISBN"
    )
    book_type = models.CharField(max_length=20, choices=BOOK_TYPES, default='textbook')
    format = models.CharField(max_length=20, choices=BOOK_FORMATS, default='paperback')
    language = models.CharField(max_length=10, choices=LANGUAGES, default='en')
    
    # Academic associations
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='books'
    )
    curriculum = models.CharField(max_length=20, choices=CURRICULUM_CHOICES, blank=True, null=True)
    grade_level = models.CharField(max_length=20, blank=True, null=True)
    
    # Author and publisher
    authors = models.ManyToManyField(Author, related_name='books', blank=True)
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='books'
    )
    publication_year = models.PositiveIntegerField(blank=True, null=True)
    edition = models.CharField(max_length=50, blank=True, null=True)
    
    # Categories and subjects
    categories = models.ManyToManyField(BookCategory, related_name='books', blank=True)
    
    # Physical details
    pages = models.PositiveIntegerField(blank=True, null=True)
    dimensions = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 8.5 x 11 inches")
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="Weight in grams")
    
    # Inventory details
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    shelf_location = models.CharField(max_length=100, blank=True, null=True, help_text="Shelf/Location in library")
    accession_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)
    
    # Content details
    description = models.TextField(blank=True, null=True)
    table_of_contents = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True, help_text="Comma-separated keywords")
    
    # Media
    cover_image = models.ImageField(upload_to='book_covers/%Y/%m/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='ebooks/%Y/%m/', blank=True, null=True, help_text="E-book PDF")
    preview_file = models.FileField(upload_to='book_previews/%Y/%m/', blank=True, null=True)
    
    # Pricing (if applicable)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, default='KES', help_text="Currency code")
    
    # Metadata
    date_added = models.DateField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_reference = models.BooleanField(default=False, help_text="Reference books cannot be borrowed")
    is_digital = models.BooleanField(default=False, help_text="Digital-only book")
    
    class Meta:
        ordering = ['title']
        verbose_name = "Book"
        verbose_name_plural = "Books"
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn']),
            models.Index(fields=['book_type', 'curriculum']),
            models.Index(fields=['available_copies']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Set available copies if not set"""
        if not self.available_copies and self.total_copies:
            self.available_copies = self.total_copies
        
        # Generate barcode if not provided
        if not self.barcode:
            self.barcode = f"BOOK-{uuid.uuid4().hex[:10].upper()}"
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate book data"""
        if self.total_copies < 0:
            raise ValidationError("Total copies cannot be negative.")
        
        if self.available_copies > self.total_copies:
            raise ValidationError("Available copies cannot exceed total copies.")
    
    @property
    def is_available(self):
        """Check if book is available for borrowing"""
        return self.available_copies > 0 and not self.is_reference
    
    @property
    def is_popular(self):
        """Check if book is popular (based on borrow count)"""
        return self.borrow_records.filter(
            returned=False
        ).count() > 10  # Arbitrary threshold
    
    @property
    def current_borrowers(self):
        """Get current borrowers of this book"""
        return self.borrow_records.filter(returned=False).select_related('borrower')
    
    @property
    def borrow_count(self):
        """Total number of times book has been borrowed"""
        return self.borrow_records.count()
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        from django.db.models import Avg
        result = self.reviews.aggregate(avg_rating=Avg('rating'))
        return result['avg_rating'] or 0
    
    def update_availability(self):
        """Update available copies based on current borrows"""
        borrowed_count = self.borrow_records.filter(returned=False).count()
        self.available_copies = max(0, self.total_copies - borrowed_count)
        self.save()


# ==================== BOOK COPIES ====================
class BookCopy(BaseLibraryModel):
    """Individual book copy tracking"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    copy_number = models.PositiveIntegerField(default=1)
    barcode = models.CharField(max_length=100, unique=True)
    condition = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('damaged', 'Damaged'),
        ],
        default='good'
    )
    notes = models.TextField(blank=True, null=True, help_text="Specific notes about this copy")
    acquisition_date = models.DateField(default=timezone.now)
    acquisition_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    supplier = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        ordering = ['book', 'copy_number']
        unique_together = ['book', 'copy_number']
        verbose_name = "Book Copy"
        verbose_name_plural = "Book Copies"
    
    def __str__(self):
        return f"{self.book.title} - Copy {self.copy_number}"
    
    @property
    def is_available(self):
        """Check if this copy is available"""
        return not self.borrow_records.filter(returned=False).exists()
    
    @property
    def current_borrower(self):
        """Get current borrower of this copy"""
        current_borrow = self.borrow_records.filter(returned=False).first()
        return current_borrow.borrower if current_borrow else None


# ==================== BORROWING SYSTEM ====================
class BorrowRecord(BaseLibraryModel):
    """Enhanced book borrowing record"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('issued', 'Issued'),
        ('overdue', 'Overdue'),
        ('returned', 'Returned'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]
    
    borrower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='borrow_records',
        limit_choices_to={'role__in': ['student', 'teacher', 'staff']}
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    copy = models.ForeignKey(
        BookCopy,
        on_delete=models.CASCADE,
        related_name='borrow_records',
        blank=True,
        null=True
    )
    
    # Borrowing details
    borrow_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(blank=True, null=True)
    
    # Renewal information
    renewals = models.PositiveIntegerField(default=0)
    max_renewals = models.PositiveIntegerField(default=2)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    returned = models.BooleanField(default=False)
    returned_condition = models.CharField(
        max_length=20,
        choices=BookCopy._meta.get_field('condition').choices,
        blank=True,
        null=True
    )
    
    # Fines and penalties
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine_paid = models.BooleanField(default=False)
    damage_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Approval and processing
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='approved_borrows',
        limit_choices_to={'role': 'librarian'}
    )
    issued_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='issued_borrows',
        limit_choices_to={'role': 'librarian'}
    )
    received_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='received_returns',
        limit_choices_to={'role': 'librarian'}
    )
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-borrow_date']
        verbose_name = "Borrow Record"
        verbose_name_plural = "Borrow Records"
        indexes = [
            models.Index(fields=['borrower', 'returned']),
            models.Index(fields=['due_date', 'returned']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.borrower.get_full_name()} - {self.book.title}"
    
    def clean(self):
        """Validate borrow record"""
        if self.due_date <= self.borrow_date:
            raise ValidationError("Due date must be after borrow date.")
        
        if self.return_date and self.return_date < self.borrow_date:
            raise ValidationError("Return date cannot be before borrow date.")
    
    def save(self, *args, **kwargs):
        """Handle borrow logic"""
        is_new = self.pk is None
        
        if is_new:
            # Set initial due date (14 days from borrow)
            if not self.due_date:
                self.due_date = timezone.now() + timedelta(days=14)
        
        # Update status based on dates
        if not self.returned:
            if timezone.now() > self.due_date and self.status != 'overdue':
                self.status = 'overdue'
            elif self.status == 'pending':
                self.status = 'approved'
        
        super().save(*args, **kwargs)
        
        # Update book availability if needed
        if is_new or self.returned:
            self.book.update_availability()
    
    @property
    def is_overdue(self):
        """Check if book is overdue"""
        if self.returned:
            return False
        return timezone.now() > self.due_date
    
    @property
    def overdue_days(self):
        """Calculate number of overdue days"""
        if self.is_overdue:
            return (timezone.now() - self.due_date).days
        return 0
    
    @property
    def calculated_fine(self):
        """Calculate fine amount"""
        if self.is_overdue and not self.fine_paid:
            # Example: 10 KES per day
            daily_fine = 10
            return self.overdue_days * daily_fine
        return 0
    
    def renew(self, user):
        """Renew the book"""
        if self.renewals >= self.max_renewals:
            raise ValidationError("Maximum renewals reached.")
        
        if self.is_overdue:
            raise ValidationError("Cannot renew overdue books.")
        
        # Extend due date by 14 days
        self.due_date = self.due_date + timedelta(days=14)
        self.renewals += 1
        self.save()
    
    def return_book(self, condition=None, received_by=None):
        """Return the borrowed book"""
        if self.returned:
            raise ValidationError("Book already returned.")
        
        self.returned = True
        self.return_date = timezone.now()
        self.status = 'returned'
        
        if condition:
            self.returned_condition = condition
        
        if received_by:
            self.received_by = received_by
        
        # Update fine if overdue
        if self.is_overdue:
            self.fine_amount = self.calculated_fine
        
        self.save()


# ==================== BOOK REVIEWS AND RATINGS ====================
class BookReview(BaseLibraryModel):
    """Book reviews and ratings"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True, null=True)
    review = models.TextField()
    is_approved = models.BooleanField(default=False)
    helpful_votes = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['book', 'user']
        ordering = ['-created_at']
        verbose_name = "Book Review"
        verbose_name_plural = "Book Reviews"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.book.title} - {self.rating}★"
    
    def vote_helpful(self):
        """Increment helpful votes"""
        self.helpful_votes += 1
        self.save()


class ReadingList(BaseLibraryModel):
    """Personal reading lists for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_lists')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    books = models.ManyToManyField(Book, through='ReadingListItem', related_name='reading_lists')
    is_public = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['-created_at']
        verbose_name = "Reading List"
        verbose_name_plural = "Reading Lists"
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s {self.name}"


class ReadingListItem(BaseLibraryModel):
    """Items in a reading list"""
    reading_list = models.ForeignKey(ReadingList, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    priority = models.PositiveIntegerField(default=1, help_text="1 = Highest priority")
    notes = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    completed_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['priority', 'added_date']
        unique_together = ['reading_list', 'book']
        verbose_name = "Reading List Item"
        verbose_name_plural = "Reading List Items"
    
    def __str__(self):
        return f"{self.book.title} in {self.reading_list.name}"


# ==================== RESERVATIONS ====================
class BookReservation(BaseLibraryModel):
    """Book reservations system"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('ready', 'Ready for Pickup'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    requested_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.PositiveIntegerField(default=1)
    
    # Fulfillment
    fulfilled_date = models.DateTimeField(blank=True, null=True)
    fulfilled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='fulfilled_reservations',
        limit_choices_to={'role': 'librarian'}
    )
    
    class Meta:
        ordering = ['priority', 'requested_date']
        verbose_name = "Book Reservation"
        verbose_name_plural = "Book Reservations"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.book.title}"
    
    def save(self, *args, **kwargs):
        """Set expiry date if not set"""
        if not self.expiry_date and self.pk is None:
            self.expiry_date = timezone.now() + timedelta(days=7)  # 7 days reservation
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if reservation has expired"""
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False
    
    def fulfill(self, user):
        """Fulfill the reservation"""
        if self.is_expired:
            raise ValidationError("Reservation has expired.")
        
        self.status = 'ready'
        self.fulfilled_date = timezone.now()
        self.fulfilled_by = user
        self.save()


# ==================== DIGITAL RESOURCES ====================
class DigitalResource(BaseLibraryModel):
    """Digital resources (e-books, articles, videos, etc.)"""
    RESOURCE_TYPES = [
        ('ebook', 'E-Book'),
        ('audiobook', 'Audiobook'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('presentation', 'Presentation'),
        ('website', 'Website Link'),
        ('database', 'Database'),
    ]
    
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='ebook')
    file = models.FileField(upload_to='digital_resources/%Y/%m/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='resource_thumbs/%Y/%m/', blank=True, null=True)
    
    # Academic associations
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, blank=True, null=True, related_name='digital_resources')
    curriculum = models.CharField(max_length=20, choices=Book.CURRICULUM_CHOICES, blank=True, null=True)
    grade_level = models.CharField(max_length=20, blank=True, null=True)
    
    # Metadata
    author = models.CharField(max_length=200, blank=True, null=True)
    publisher = models.CharField(max_length=200, blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    file_size = models.PositiveIntegerField(blank=True, null=True, help_text="Size in bytes")
    duration = models.PositiveIntegerField(blank=True, null=True, help_text="Duration in seconds (for audio/video)")
    
    # Categories
    categories = models.ManyToManyField(BookCategory, blank=True, related_name='digital_resources')
    
    # Access control
    is_public = models.BooleanField(default=True)
    access_groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        help_text="User groups that can access this resource"
    )
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Digital Resource"
        verbose_name_plural = "Digital Resources"
    
    def __str__(self):
        return self.title
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    @property
    def duration_formatted(self):
        """Format duration as HH:MM:SS"""
        if self.duration:
            hours = self.duration // 3600
            minutes = (self.duration % 3600) // 60
            seconds = self.duration % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return None
    
    def increment_download(self):
        """Increment download count"""
        self.download_count += 1
        self.save()
    
    def increment_view(self):
        """Increment view count"""
        self.view_count += 1
        self.save()


# ==================== TEACHER RESOURCES ====================
class TeacherResource(BaseLibraryModel):
    """Resources specifically for teachers"""
    RESOURCE_TYPES = [
        ('lesson_plan', 'Lesson Plan'),
        ('worksheet', 'Worksheet'),
        ('assessment', 'Assessment'),
        ('curriculum_guide', 'Curriculum Guide'),
        ('teaching_aid', 'Teaching Aid'),
        ('professional_development', 'Professional Development'),
    ]
    
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    resource_type = models.CharField(max_length=30, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to='teacher_resources/%Y/%m/')
    thumbnail = models.ImageField(upload_to='teacher_thumbs/%Y/%m/', blank=True, null=True)
    
    # Academic associations
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, blank=True, null=True)
    grade_level = models.CharField(max_length=20, blank=True, null=True)
    curriculum = models.CharField(max_length=20, choices=Book.CURRICULUM_CHOICES, blank=True, null=True)
    
    # Metadata
    author = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_teacher_resources')
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    # Access control
    is_public = models.BooleanField(default=True)
    access_groups = models.ManyToManyField('auth.Group', blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Teacher Resource"
        verbose_name_plural = "Teacher Resources"
    
    def __str__(self):
        return self.title
    
    def increment_download(self):
        self.download_count += 1
        self.save()
    
    def increment_view(self):
        self.view_count += 1
        self.save()

# ==================== LIBRARY STATISTICS ====================
class LibraryStats(BaseLibraryModel):
    """Library statistics and analytics"""
    date = models.DateField(unique=True)
    
    # Book statistics
    total_books = models.PositiveIntegerField(default=0)
    total_copies = models.PositiveIntegerField(default=0)
    available_copies = models.PositiveIntegerField(default=0)
    borrowed_copies = models.PositiveIntegerField(default=0)
    
    # Digital resources
    digital_resources = models.PositiveIntegerField(default=0)
    digital_downloads = models.PositiveIntegerField(default=0)
    
    # Activity statistics
    daily_borrows = models.PositiveIntegerField(default=0)
    daily_returns = models.PositiveIntegerField(default=0)
    daily_reservations = models.PositiveIntegerField(default=0)
    active_borrowers = models.PositiveIntegerField(default=0)
    
    # Fines
    total_fines = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fines_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Library Statistics"
        verbose_name_plural = "Library Statistics"
    
    def __str__(self):
        return f"Library Stats - {self.date}"


# ==================== SIGNALS ====================
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=BorrowRecord)
def update_book_availability(sender, instance, created, **kwargs):
    """Update book availability when borrow record changes"""
    if not instance.returned:
        instance.book.update_availability()

@receiver(post_save, sender=Book)
def create_book_copies(sender, instance, created, **kwargs):
    """Create individual copies when a new book is added"""
    if created and instance.total_copies > 0:
        for i in range(1, instance.total_copies + 1):
            BookCopy.objects.create(
                book=instance,
                copy_number=i,
                barcode=f"{instance.barcode}-{i:03d}",
                condition='new'
            )

@receiver(post_save, sender=BookReview)
def update_book_rating(sender, instance, created, **kwargs):
    """Update book average rating when review is saved"""
    # Trigger save to recalculate average_rating property
    instance.book.save()