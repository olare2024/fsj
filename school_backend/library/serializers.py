from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from library.models import (
    BookCategory, Author, Publisher, Book, BookCopy,
    BorrowRecord, BookReview, ReadingList, ReadingListItem,
    BookReservation, DigitalResource, LibraryStats, TeacherResource
)
#from academics.models import Lerani
from accounts.models import User

User = get_user_model()




# ==================== UTILITY MIXINS ====================
class DynamicFieldsSerializer(serializers.ModelSerializer):
    """Serializer that can dynamically include/exclude fields"""
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)
        super().__init__(*args, **kwargs)
        
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        
        if exclude is not None:
            for field_name in exclude:
                self.fields.pop(field_name, None)


class TimestampMixin:
    """Add timestamp fields to serializer"""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(default=True)


# ==================== CATEGORIES ====================
class BookCategorySerializer(DynamicFieldsSerializer, TimestampMixin):
    """Serializer for BookCategory"""
    book_count = serializers.IntegerField(read_only=True)
    subcategory_count = serializers.IntegerField(read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    
    class Meta:
        model = BookCategory
        fields = [
            'id', 'name', 'description', 'parent', 'parent_name',
            'icon', 'color', 'book_count', 'subcategory_count',
            'created_at', 'updated_at', 'is_active'
        ]


class BookCategoryTreeSerializer(BookCategorySerializer):
    """Serializer for category tree structure"""
    subcategories = BookCategorySerializer(many=True, read_only=True)
    
    class Meta(BookCategorySerializer.Meta):
        fields = BookCategorySerializer.Meta.fields + ['subcategories']


# ==================== AUTHORS AND PUBLISHERS ====================
class AuthorSerializer(DynamicFieldsSerializer, TimestampMixin):
    """Serializer for Author"""
    full_name = serializers.CharField(read_only=True)
    book_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Author
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'full_name',
            'biography', 'nationality', 'birth_date', 'death_date',
            'photo', 'website', 'email', 'book_count',
            'created_at', 'updated_at', 'is_active'
        ]


class PublisherSerializer(DynamicFieldsSerializer, TimestampMixin):
    """Serializer for Publisher"""
    book_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Publisher
        fields = [
            'id', 'name', 'address', 'city', 'country',
            'website', 'email', 'phone', 'logo', 'book_count',
            'created_at', 'updated_at', 'is_active'
        ]


# ==================== BOOKS ====================
class BookSummarySerializer(DynamicFieldsSerializer, TimestampMixin):
    """Lightweight serializer for book lists"""
    subject_name = serializers.CharField(source='subject.name', read_only=True, allow_null=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True, allow_null=True)
    is_available = serializers.BooleanField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    borrow_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'subtitle', 'isbn', 'book_type', 'format',
            'language', 'subject', 'subject_name', 'curriculum', 'grade_level',
            'publisher', 'publisher_name', 'publication_year', 'edition',
            'cover_image', 'pages', 'total_copies', 'available_copies',
            'is_available', 'average_rating', 'borrow_count', 'is_reference',
            'is_digital', 'created_at', 'updated_at', 'is_active'
        ]


class BookDetailSerializer(DynamicFieldsSerializer, TimestampMixin):
    """Detailed serializer for Book model"""
    subject_name = serializers.CharField(source='subject.name', read_only=True, allow_null=True)
    publisher_details = PublisherSerializer(source='publisher', read_only=True)
    authors = AuthorSerializer(many=True, read_only=True)
    categories = BookCategorySerializer(many=True, read_only=True)
    
    # Computed fields
    is_available = serializers.BooleanField(read_only=True)
    is_popular = serializers.BooleanField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    borrow_count = serializers.IntegerField(read_only=True)
    current_borrowers = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'subtitle', 'isbn', 'book_type', 'format', 'language',
            'subject', 'subject_name', 'curriculum', 'grade_level',
            'authors', 'publisher', 'publisher_details', 'publication_year', 'edition',
            'categories', 'pages', 'dimensions', 'weight',
            'total_copies', 'available_copies', 'shelf_location',
            'accession_number', 'barcode', 'description', 'table_of_contents',
            'keywords', 'cover_image', 'pdf_file', 'preview_file',
            'price', 'currency', 'date_added', 'last_updated',
            'is_reference', 'is_digital', 'is_available', 'is_popular',
            'average_rating', 'borrow_count', 'current_borrowers',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['date_added', 'last_updated']
    
    def get_current_borrowers(self, obj):
        """Get current borrowers for this book"""
        current_borrows = obj.borrow_records.filter(returned=False)[:5]  # Limit to 5
        return [
            {
                'id': borrow.borrower.id,
                'name': borrow.borrower.get_full_name(),
                'borrow_date': borrow.borrow_date,
                'due_date': borrow.due_date
            }
            for borrow in current_borrows
        ]
    
    def validate(self, data):
        """Validate book data"""
        if 'total_copies' in data and 'available_copies' in data:
            if data['available_copies'] > data['total_copies']:
                raise serializers.ValidationError({
                    'available_copies': 'Available copies cannot exceed total copies.'
                })
        
        if 'publication_year' in data:
            current_year = timezone.now().year
            if data['publication_year'] > current_year:
                raise serializers.ValidationError({
                    'publication_year': f'Publication year cannot be in the future (max {current_year}).'
                })
        
        return data


class BookCreateSerializer(DynamicFieldsSerializer):
    """Serializer for creating books"""
    class Meta:
        model = Book
        fields = [
            'title', 'subtitle', 'isbn', 'book_type', 'format', 'language',
            'subject', 'curriculum', 'grade_level',
            'authors', 'publisher', 'publication_year', 'edition',
            'categories', 'pages', 'dimensions', 'weight',
            'total_copies', 'shelf_location', 'description',
            'table_of_contents', 'keywords', 'cover_image',
            'pdf_file', 'preview_file', 'price', 'currency',
            'is_reference', 'is_digital'
        ]
    
    def create(self, validated_data):
        """Handle many-to-many relationships"""
        authors = validated_data.pop('authors', [])
        categories = validated_data.pop('categories', [])
        
        book = Book.objects.create(**validated_data)
        
        if authors:
            book.authors.set(authors)
        if categories:
            book.categories.set(categories)
        
        return book


# ==================== BOOK COPIES ====================
class BookCopySerializer(DynamicFieldsSerializer, TimestampMixin):
    """Serializer for BookCopy"""
    book_title = serializers.CharField(source='book.title', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    current_borrower = serializers.SerializerMethodField()
    
    class Meta:
        model = BookCopy
        fields = [
            'id', 'book', 'book_title', 'copy_number', 'barcode',
            'condition', 'notes', 'acquisition_date', 'acquisition_price',
            'supplier', 'is_available', 'current_borrower',
            'created_at', 'updated_at', 'is_active'
        ]
    
    def get_current_borrower(self, obj):
        """Get current borrower of this copy"""
        current_borrow = obj.borrow_records.filter(returned=False).first()
        if current_borrow:
            return {
                'id': current_borrow.borrower.id,
                'name': current_borrow.borrower.get_full_name(),
                'borrow_date': current_borrow.borrow_date
            }
        return None


# ==================== BORROWING SYSTEM ====================
class BorrowRecordSerializer(DynamicFieldsSerializer, TimestampMixin):
    """Serializer for BorrowRecord"""
    borrower_name = serializers.CharField(source='borrower.get_full_name', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    copy_barcode = serializers.CharField(source='copy.barcode', read_only=True, allow_null=True)
    is_overdue = serializers.BooleanField(read_only=True)
    overdue_days = serializers.IntegerField(read_only=True)
    calculated_fine = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = BorrowRecord
        fields = [
            'id', 'borrower', 'borrower_name', 'book', 'book_title',
            'copy', 'copy_barcode', 'borrow_date', 'due_date',
            'return_date', 'renewals', 'max_renewals', 'status',
            'returned', 'returned_condition', 'fine_amount', 'fine_paid',
            'damage_fee', 'approved_by', 'issued_by', 'received_by',
            'notes', 'is_overdue', 'overdue_days', 'calculated_fine',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = [
            'borrow_date', 'due_date', 'return_date', 'renewals',
            'status', 'is_overdue', 'overdue_days', 'calculated_fine'
        ]
    
    def validate(self, data):
        """Validate borrow record"""
        if data.get('returned') and not data.get('return_date'):
            data['return_date'] = timezone.now()
        
        return data


class BorrowRequestSerializer(serializers.Serializer):
    """Serializer for borrowing requests"""
    book_id = serializers.UUIDField()
    copy_id = serializers.UUIDField(required=False, allow_null=True)
    due_date = serializers.DateTimeField(required=False)
    
    def validate(self, data):
        """Validate borrow request"""
        try:
            book = Book.objects.get(id=data['book_id'], is_active=True)
        except Book.DoesNotExist:
            raise serializers.ValidationError({'book_id': 'Book not found.'})
        
        # Check if book is reference
        if book.is_reference:
            raise serializers.ValidationError({'book_id': 'Reference books cannot be borrowed.'})
        
        # Check availability
        if not book.is_available:
            raise serializers.ValidationError({'book_id': 'Book is not available for borrowing.'})
        
        # Check copy if specified
        if 'copy_id' in data and data['copy_id']:
            try:
                copy = BookCopy.objects.get(id=data['copy_id'], book=book)
                if not copy.is_available:
                    raise serializers.ValidationError({'copy_id': 'This copy is not available.'})
            except BookCopy.DoesNotExist:
                raise serializers.ValidationError({'copy_id': 'Copy not found for this book.'})
        
        return data


class ReturnBookSerializer(serializers.Serializer):
    """Serializer for returning books"""
    borrow_id = serializers.UUIDField()
    condition = serializers.CharField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_null=True)
    
    def validate(self, data):
        """Validate return request"""
        try:
            borrow = BorrowRecord.objects.get(id=data['borrow_id'])
        except BorrowRecord.DoesNotExist:
            raise serializers.ValidationError({'borrow_id': 'Borrow record not found.'})
        
        if borrow.returned:
            raise serializers.ValidationError({'borrow_id': 'Book already returned.'})
        
        return data


class RenewBookSerializer(serializers.Serializer):
    """Serializer for renewing books"""
    borrow_id = serializers.UUIDField()
    
    def validate(self, data):
        """Validate renewal request"""
        try:
            borrow = BorrowRecord.objects.get(id=data['borrow_id'])
        except BorrowRecord.DoesNotExist:
            raise serializers.ValidationError({'borrow_id': 'Borrow record not found.'})
        
        if borrow.returned:
            raise serializers.ValidationError({'borrow_id': 'Cannot renew returned book.'})
        
        if borrow.is_overdue:
            raise serializers.ValidationError({'borrow_id': 'Cannot renew overdue book.'})
        
        if borrow.renewals >= borrow.max_renewals:
            raise serializers.ValidationError({'borrow_id': 'Maximum renewals reached.'})
        
        return data


# ==================== BOOK REVIEWS ====================
class BookReviewSerializer(DynamicFieldsSerializer, TimestampMixin):
    """Serializer for BookReview"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    
    class Meta:
        model = BookReview
        fields = [
            'id', 'book', 'book_title', 'user', 'user_name',
            'rating', 'title', 'review', 'is_approved', 'helpful_votes',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['user', 'is_approved', 'helpful_votes']
    
    def validate_rating(self, value):
        """Validate rating value"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value
    
    def create(self, validated_data):
        """Set user from request"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        
        return super().create(validated_data)


# ==================== READING LISTS ====================
class ReadingListItemSerializer(DynamicFieldsSerializer, TimestampMixin):
    """Serializer for ReadingListItem"""
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_cover = serializers.ImageField(source='book.cover_image', read_only=True)
    
    class Meta:
        model = ReadingListItem
        fields = [
            'id', 'reading_list', 'book', 'book_title', 'book_cover',
            'added_date', 'priority', 'notes', 'completed', 'completed_date',
            'created_at', 'updated_at', 'is_active'
        ]


class ReadingListSerializer(DynamicFieldsSerializer, TimestampMixin):
    """Serializer for ReadingList"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    items = ReadingListItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = ReadingList
        fields = [
            'id', 'user', 'user_name', 'name', 'description',
            'books', 'is_public', 'item_count', 'items',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['user']
    
    def create(self, validated_data):
        """Set user from request"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        
        return super().create(validated_data)


# ==================== RESERVATIONS ====================
class BookReservationSerializer(DynamicFieldsSerializer, TimestampMixin):
    """Serializer for BookReservation"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_cover = serializers.ImageField(source='book.cover_image', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = BookReservation
        fields = [
            'id', 'user', 'user_name', 'book', 'book_title', 'book_cover',
            'requested_date', 'expiry_date', 'status', 'priority',
            'fulfilled_date', 'fulfilled_by', 'is_expired',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['user', 'requested_date', 'expiry_date', 'status']


class ReservationRequestSerializer(serializers.Serializer):
    """Serializer for reservation requests"""
    book_id = serializers.UUIDField()
    
    def validate(self, data):
        """Validate reservation request"""
        try:
            book = Book.objects.get(id=data['book_id'], is_active=True)
        except Book.DoesNotExist:
            raise serializers.ValidationError({'book_id': 'Book not found.'})
        
        # Check if book is available
        if book.is_available:
            raise serializers.ValidationError({'book_id': 'Book is available for immediate borrowing.'})
        
        # Check if user already has an active reservation for this book
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            existing_reservation = BookReservation.objects.filter(
                user=request.user,
                book=book,
                status__in=['pending', 'confirmed', 'ready']
            ).exists()
            
            if existing_reservation:
                raise serializers.ValidationError({'book_id': 'You already have an active reservation for this book.'})
        
        return data


# ==================== DIGITAL RESOURCES ====================
class DigitalResourceSerializer(DynamicFieldsSerializer, TimestampMixin):
    """Serializer for DigitalResource"""
    subject_name = serializers.CharField(source='subject.name', read_only=True, allow_null=True)
    file_size_mb = serializers.FloatField(read_only=True)
    duration_formatted = serializers.CharField(read_only=True)
    categories = BookCategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = DigitalResource
        fields = [
            'id', 'title', 'description', 'resource_type', 'file', 'url',
            'thumbnail', 'subject', 'subject_name', 'curriculum', 'grade_level',
            'author', 'publisher', 'publication_date', 'file_size', 'file_size_mb',
            'duration', 'duration_formatted', 'categories', 'is_public',
            'access_groups', 'download_count', 'view_count',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['download_count', 'view_count']


# ==================== STATISTICS ====================
class LibraryStatsSerializer(DynamicFieldsSerializer):
    """Serializer for LibraryStats"""
    class Meta:
        model = LibraryStats
        fields = [
            'id', 'date', 'total_books', 'total_copies', 'available_copies',
            'borrowed_copies', 'digital_resources', 'digital_downloads',
            'daily_borrows', 'daily_returns', 'daily_reservations',
            'active_borrowers', 'total_fines', 'fines_collected',
            'created_at', 'updated_at', 'is_active'
        ]


# ==================== SEARCH AND FILTER SERIALIZERS ====================
class BookSearchSerializer(serializers.Serializer):
    """Serializer for book search parameters"""
    query = serializers.CharField(required=False)
    category = serializers.UUIDField(required=False)
    subject = serializers.UUIDField(required=False)
    book_type = serializers.CharField(required=False)
    format = serializers.CharField(required=False)
    language = serializers.CharField(required=False)
    curriculum = serializers.CharField(required=False)
    grade_level = serializers.CharField(required=False)
    author = serializers.UUIDField(required=False)
    publisher = serializers.UUIDField(required=False)
    available_only = serializers.BooleanField(default=False)
    sort_by = serializers.CharField(default='title')
    sort_order = serializers.CharField(default='asc')


class DigitalResourceSearchSerializer(serializers.Serializer):
    """Serializer for digital resource search"""
    query = serializers.CharField(required=False)
    resource_type = serializers.CharField(required=False)
    subject = serializers.UUIDField(required=False)
    curriculum = serializers.CharField(required=False)
    grade_level = serializers.CharField(required=False)
    sort_by = serializers.CharField(default='-created_at')


# ==================== BULK OPERATIONS ====================
class BulkBookImportSerializer(serializers.Serializer):
    """Serializer for bulk book import"""
    books = BookCreateSerializer(many=True)


class BulkBookUpdateSerializer(serializers.Serializer):
    """Serializer for bulk book updates"""
    book_ids = serializers.ListField(child=serializers.UUIDField())
    data = serializers.DictField()


# ==================== EXPORT SERIALIZERS ====================
class BookExportSerializer(serializers.ModelSerializer):
    """Serializer for book exports"""
    authors = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='subject.name', allow_null=True)
    publisher_name = serializers.CharField(source='publisher.name', allow_null=True)
    
    class Meta:
        model = Book
        fields = [
            'title', 'subtitle', 'isbn', 'book_type', 'format', 'language',
            'subject_name', 'curriculum', 'grade_level', 'authors',
            'publisher_name', 'publication_year', 'edition', 'categories',
            'pages', 'total_copies', 'available_copies', 'shelf_location',
            'price', 'currency', 'is_reference', 'is_digital'
        ]
    
    def get_authors(self, obj):
        """Get comma-separated author names"""
        return ', '.join([author.full_name for author in obj.authors.all()])
    
    def get_categories(self, obj):
        """Get comma-separated category names"""
        return ', '.join([category.name for category in obj.categories.all()])



class TeacherResourceSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherResource
        fields = [
            'id', 'title', 'description', 'resource_type', 
            'file', 'thumbnail', 'subject', 'subject_name',
            'grade_level', 'curriculum', 'author', 'author_name',
            'created_by', 'created_by_name', 'download_count',
            'view_count', 'is_public', 'access_groups', 'is_active',
            'created_at', 'updated_at', 'file_size_mb', 'file_url',
            'thumbnail_url'
        ]
        read_only_fields = ['download_count', 'view_count', 'created_by']
    
    def get_file_size_mb(self, obj):
        if obj.file:
            try:
                return round(obj.file.size / (1024 * 1024), 2)
            except:
                return 0
        return 0
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TeacherResourceSummarySerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherResource
        fields = [
            'id', 'title', 'resource_type', 'subject', 'subject_name',
            'grade_level', 'download_count', 'view_count', 'is_active',
            'created_at', 'file_size_mb'
        ]
    
    def get_file_size_mb(self, obj):
        if obj.file:
            try:
                return round(obj.file.size / (1024 * 1024), 2)
            except:
                return 0
        return 0