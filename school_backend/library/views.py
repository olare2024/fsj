from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from django.utils import timezone
from datetime import timedelta, datetime
import json
import csv
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db import transaction

from library.models import (
    BookCategory, Author, Publisher, Book, BookCopy,
    BorrowRecord, BookReview, ReadingList, ReadingListItem,
    BookReservation, DigitalResource, LibraryStats, TeacherResource
)
from library.serializers import *
from accounts.models import User


# ==================== PERMISSION CLASSES ====================
class IsLibrarian(BasePermission):
    """Check if user is a librarian"""
    def has_permission(self, request, view):
        return request.user.role == 'librarian'


class IsStudentOrTeacher(BasePermission):
    """Check if user is student or teacher"""
    def has_permission(self, request, view):
        return request.user.role in ['student', 'teacher']


class CanBorrowBooks(BasePermission):
    """Check if user can borrow books"""
    def has_permission(self, request, view):
        if request.user.role in ['student', 'teacher', 'staff']:
            # Check if user has overdue books
            overdue_count = BorrowRecord.objects.filter(
                borrower=request.user,
                returned=False,
                due_date__lt=timezone.now()
            ).count()
            
            # Check if user has unpaid fines
            unpaid_fines = BorrowRecord.objects.filter(
                borrower=request.user,
                fine_paid=False,
                fine_amount__gt=0
            ).aggregate(total=Sum('fine_amount'))['total'] or 0
            
            return overdue_count == 0 and unpaid_fines == 0
        
        return False


# ==================== CATEGORY VIEWSETS ====================
class BookCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for BookCategory CRUD operations"""
    queryset = BookCategory.objects.all()
    serializer_class = BookCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['parent']
    search_fields = ['name', 'description']
    
    def get_serializer_class(self):
        if self.action == 'list' and self.request.query_params.get('tree'):
            return BookCategoryTreeSerializer
        return BookCategorySerializer
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree structure"""
        categories = BookCategory.objects.filter(parent__isnull=True)
        serializer = BookCategoryTreeSerializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        """Get books in this category"""
        category = self.get_object()
        books = Book.objects.filter(categories=category)
        
        page = self.paginate_queryset(books)
        if page is not None:
            serializer = BookSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BookSummarySerializer(books, many=True)
        return Response(serializer.data)


# ==================== AUTHOR VIEWSETS ====================
class AuthorViewSet(viewsets.ModelViewSet):
    """ViewSet for Author CRUD operations"""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'middle_name', 'nationality']
    
    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        """Get books by this author"""
        author = self.get_object()
        books = author.books.all()
        
        page = self.paginate_queryset(books)
        if page is not None:
            serializer = BookSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BookSummarySerializer(books, many=True)
        return Response(serializer.data)


# ==================== PUBLISHER VIEWSETS ====================
class PublisherViewSet(viewsets.ModelViewSet):
    """ViewSet for Publisher CRUD operations"""
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'city', 'country']


# ==================== BOOK VIEWSETS ====================
class BookViewSet(viewsets.ModelViewSet):
    """ViewSet for Book CRUD operations"""
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'book_type', 'format', 'language', 'subject', 'curriculum',
        'grade_level', 'publisher', 'is_reference', 'is_digital'
    ]
    search_fields = ['title', 'subtitle', 'isbn', 'description', 'keywords']
    ordering_fields = ['title', 'publication_year', 'total_copies', 'available_copies']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookCreateSerializer
        elif self.action == 'list':
            return BookSummarySerializer
        return BookDetailSerializer
    
    def get_queryset(self):
        """Filter books based on availability and other criteria"""
        queryset = super().get_queryset()
        
        # Filter by available only
        available_only = self.request.query_params.get('available_only')
        if available_only and available_only.lower() == 'true':
            queryset = queryset.filter(available_copies__gt=0)
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
        
        return queryset.distinct()
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get only available books"""
        books = self.get_queryset().filter(available_copies__gt=0)
        
        page = self.paginate_queryset(books)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular books (most borrowed)"""
        books = self.get_queryset().annotate(
            borrow_count=Count('borrow_records')
        ).order_by('-borrow_count')[:20]  # Top 20
        
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        """Get new arrivals (added in last 30 days)"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        books = self.get_queryset().filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:20]
        
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def copies(self, request, pk=None):
        """Get copies of this book"""
        book = self.get_object()
        copies = book.copies.all()
        
        serializer = BookCopySerializer(copies, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def borrow_history(self, request, pk=None):
        """Get borrow history for this book"""
        book = self.get_object()
        borrows = book.borrow_records.all().order_by('-borrow_date')
        
        page = self.paginate_queryset(borrows)
        if page is not None:
            serializer = BorrowRecordSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BorrowRecordSerializer(borrows, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get reviews for this book"""
        book = self.get_object()
        reviews = book.reviews.filter(is_approved=True)
        
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = BookReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BookReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_review(self, request, pk=None):
        """Add a review for this book"""
        book = self.get_object()
        
        # Check if user already reviewed this book
        existing_review = BookReview.objects.filter(
            book=book,
            user=request.user
        ).exists()
        
        if existing_review:
            return Response(
                {'error': 'You have already reviewed this book.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = BookReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(book=book)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        """Reserve this book"""
        book = self.get_object()
        
        # Check if book is available
        if book.is_available:
            return Response(
                {'error': 'Book is available for immediate borrowing.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already has an active reservation
        existing_reservation = BookReservation.objects.filter(
            user=request.user,
            book=book,
            status__in=['pending', 'confirmed', 'ready']
        ).exists()
        
        if existing_reservation:
            return Response(
                {'error': 'You already have an active reservation for this book.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create reservation
        reservation = BookReservation.objects.create(
            user=request.user,
            book=book,
            status='pending'
        )
        
        serializer = BookReservationSerializer(reservation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookCopyViewSet(viewsets.ModelViewSet):
    """ViewSet for BookCopy CRUD operations"""
    queryset = BookCopy.objects.all()
    serializer_class = BookCopySerializer
    permission_classes = [IsAuthenticated, IsLibrarian | IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['book', 'condition', 'is_active']
    
    @action(detail=True, methods=['post'])
    def update_condition(self, request, pk=None):
        """Update copy condition"""
        copy = self.get_object()
        condition = request.data.get('condition')
        
        if condition not in dict(BookCopy._meta.get_field('condition').choices):
            return Response(
                {'error': 'Invalid condition value.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        copy.condition = condition
        copy.save()
        
        serializer = self.get_serializer(copy)
        return Response(serializer.data)


# ==================== BORROWING VIEWSETS ====================
class BorrowRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for BorrowRecord CRUD operations"""
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = [
        'borrower', 'book', 'status', 'returned', 'is_active'
    ]
    ordering_fields = ['borrow_date', 'due_date', 'return_date']
    
    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user
        
        if user.role == 'librarian' or user.is_staff:
            return self.queryset
        else:
            # Users can only see their own borrow records
            return self.queryset.filter(borrower=user)
    
    @action(detail=False, methods=['post'])
    def borrow(self, request):
        """Borrow a book"""
        serializer = BorrowRequestSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        book = Book.objects.get(id=data['book_id'])
        
        # Check if user can borrow
        if not CanBorrowBooks().has_permission(request, self):
            return Response(
                {'error': 'Cannot borrow books. Check for overdue books or unpaid fines.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Find available copy
            if data.get('copy_id'):
                copy = BookCopy.objects.get(id=data['copy_id'])
            else:
                # Find first available copy
                copy = book.copies.filter(
                    borrow_records__returned=True
                ).first() or book.copies.filter(
                    borrow_records__isnull=True
                ).first()
                
                if not copy:
                    return Response(
                        {'error': 'No available copies found.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Create borrow record
            borrow_record = BorrowRecord.objects.create(
                borrower=request.user,
                book=book,
                copy=copy,
                borrow_date=timezone.now(),
                due_date=data.get('due_date') or (timezone.now() + timedelta(days=14)),
                status='approved'
            )
            
            # Update book availability
            book.update_availability()
        
        serializer = BorrowRecordSerializer(borrow_record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """Return a borrowed book"""
        borrow_record = self.get_object()
        
        if borrow_record.returned:
            return Response(
                {'error': 'Book already returned.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReturnBookSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        with transaction.atomic():
            # Update borrow record
            borrow_record.returned = True
            borrow_record.return_date = timezone.now()
            borrow_record.status = 'returned'
            
            if data.get('condition'):
                borrow_record.returned_condition = data['condition']
            
            if data.get('notes'):
                borrow_record.notes = data['notes']
            
            # Calculate fine if overdue
            if borrow_record.is_overdue:
                borrow_record.fine_amount = borrow_record.calculated_fine
            
            borrow_record.save()
            
            # Update book availability
            borrow_record.book.update_availability()
        
        serializer = BorrowRecordSerializer(borrow_record)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """Renew a borrowed book"""
        borrow_record = self.get_object()
        
        serializer = RenewBookSerializer(data={'borrow_id': str(borrow_record.id)})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            borrow_record.renew(request.user)
            serializer = BorrowRecordSerializer(borrow_record)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue borrow records"""
        overdue_records = self.get_queryset().filter(
            returned=False,
            due_date__lt=timezone.now()
        ).order_by('due_date')
        
        page = self.paginate_queryset(overdue_records)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(overdue_records, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current borrows (not returned)"""
        current_borrows = self.get_queryset().filter(returned=False)
        
        page = self.paginate_queryset(current_borrows)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(current_borrows, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def pay_fine(self, request, pk=None):
        """Pay fine for overdue book"""
        borrow_record = self.get_object()
        
        if borrow_record.fine_paid:
            return Response(
                {'error': 'Fine already paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if borrow_record.fine_amount <= 0:
            return Response(
                {'error': 'No fine to pay.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # In a real app, you would integrate with payment gateway
        # For now, just mark as paid
        borrow_record.fine_paid = True
        borrow_record.save()
        
        serializer = self.get_serializer(borrow_record)
        return Response(serializer.data)


# ==================== REVIEW VIEWSETS ====================
class BookReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for BookReview CRUD operations"""
    queryset = BookReview.objects.all()
    serializer_class = BookReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['book', 'user', 'is_approved']
    ordering_fields = ['-created_at', 'rating', 'helpful_votes']
    
    def get_queryset(self):
        """Filter reviews"""
        queryset = super().get_queryset()
        
        # Regular users only see approved reviews
        if not (self.request.user.role == 'librarian' or self.request.user.is_staff):
            queryset = queryset.filter(is_approved=True)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set user when creating review"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def vote_helpful(self, request, pk=None):
        """Vote a review as helpful"""
        review = self.get_object()
        review.vote_helpful()
        
        serializer = self.get_serializer(review)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a review (librarians only)"""
        if not (request.user.role == 'librarian' or request.user.is_staff):
            return Response(
                {'error': 'Only librarians can approve reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        review = self.get_object()
        review.is_approved = True
        review.save()
        
        serializer = self.get_serializer(review)
        return Response(serializer.data)


# ==================== READING LIST VIEWSETS ====================
class ReadingListViewSet(viewsets.ModelViewSet):
    """ViewSet for ReadingList CRUD operations"""
    queryset = ReadingList.objects.all()
    serializer_class = ReadingListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'is_public']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        """Users can only see their own lists and public lists"""
        user = self.request.user
        
        # Get user's lists and public lists
        return self.queryset.filter(
            Q(user=user) | Q(is_public=True)
        ).distinct()
    
    def perform_create(self, serializer):
        """Set user when creating reading list"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_book(self, request, pk=None):
        """Add a book to reading list"""
        reading_list = self.get_object()
        book_id = request.data.get('book_id')
        
        if not book_id:
            return Response(
                {'error': 'book_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response(
                {'error': 'Book not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if book already in list
        existing_item = ReadingListItem.objects.filter(
            reading_list=reading_list,
            book=book
        ).exists()
        
        if existing_item:
            return Response(
                {'error': 'Book already in reading list.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add to list
        item = ReadingListItem.objects.create(
            reading_list=reading_list,
            book=book
        )
        
        serializer = ReadingListItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def remove_book(self, request, pk=None):
        """Remove a book from reading list"""
        reading_list = self.get_object()
        book_id = request.data.get('book_id')
        
        if not book_id:
            return Response(
                {'error': 'book_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = ReadingListItem.objects.get(
                reading_list=reading_list,
                book_id=book_id
            )
            item.delete()
            return Response({'message': 'Book removed from reading list.'})
        except ReadingListItem.DoesNotExist:
            return Response(
                {'error': 'Book not found in reading list.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark a book as completed in reading list"""
        reading_list = self.get_object()
        book_id = request.data.get('book_id')
        
        if not book_id:
            return Response(
                {'error': 'book_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = ReadingListItem.objects.get(
                reading_list=reading_list,
                book_id=book_id
            )
            item.completed = True
            item.completed_date = timezone.now()
            item.save()
            
            serializer = ReadingListItemSerializer(item)
            return Response(serializer.data)
        except ReadingListItem.DoesNotExist:
            return Response(
                {'error': 'Book not found in reading list.'},
                status=status.HTTP_404_NOT_FOUND
            )


# ==================== RESERVATION VIEWSETS ====================
class BookReservationViewSet(viewsets.ModelViewSet):
    """ViewSet for BookReservation CRUD operations"""
    queryset = BookReservation.objects.all()
    serializer_class = BookReservationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'book', 'status']
    ordering_fields = ['requested_date', 'priority', 'expiry_date']
    
    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user
        
        if user.role == 'librarian' or user.is_staff:
            return self.queryset
        else:
            # Users can only see their own reservations
            return self.queryset.filter(user=user)
    
    @action(detail=False, methods=['post'])
    def reserve(self, request):
        """Create a new reservation"""
        serializer = ReservationRequestSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        book = Book.objects.get(id=data['book_id'])
        
        # Create reservation
        reservation = BookReservation.objects.create(
            user=request.user,
            book=book,
            status='pending'
        )
        
        serializer = BookReservationSerializer(reservation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a reservation"""
        reservation = self.get_object()
        
        if reservation.status in ['cancelled', 'expired', 'fulfilled']:
            return Response(
                {'error': 'Cannot cancel a reservation in this state.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'cancelled'
        reservation.save()
        
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def fulfill(self, request, pk=None):
        """Fulfill a reservation (librarians only)"""
        if not (request.user.role == 'librarian' or request.user.is_staff):
            return Response(
                {'error': 'Only librarians can fulfill reservations.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reservation = self.get_object()
        
        if reservation.is_expired:
            return Response(
                {'error': 'Reservation has expired.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if reservation.status != 'pending':
            return Response(
                {'error': 'Reservation is not in pending state.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if book is now available
        if not reservation.book.is_available:
            return Response(
                {'error': 'Book is not available yet.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'ready'
        reservation.fulfilled_date = timezone.now()
        reservation.fulfilled_by = request.user
        reservation.save()
        
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)


# ==================== DIGITAL RESOURCE VIEWSETS ====================
class DigitalResourceViewSet(viewsets.ModelViewSet):
    """ViewSet for DigitalResource CRUD operations"""
    queryset = DigitalResource.objects.all()
    serializer_class = DigitalResourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource_type', 'subject', 'curriculum', 'grade_level', 'is_public']
    search_fields = ['title', 'description', 'author', 'publisher']
    ordering_fields = ['-created_at', 'download_count', 'view_count']
    
    def get_queryset(self):
        """Filter resources based on access"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Filter by user groups if resource has access restrictions
        if not (user.role == 'librarian' or user.is_staff):
            queryset = queryset.filter(
                Q(is_public=True) | Q(access_groups__in=user.groups.all())
            ).distinct()
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Download a digital resource"""
        resource = self.get_object()
        
        # Check access
        if not resource.is_public and not (
            resource.access_groups.filter(id__in=request.user.groups.all()).exists() or
            request.user.role == 'librarian' or request.user.is_staff
        ):
            return Response(
                {'error': 'You do not have permission to download this resource.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Increment download count
        resource.increment_download()
        
        # In a real app, you would serve the file
        # For API response, return download info
        return Response({
            'message': 'Download started',
            'resource': resource.title,
            'file_url': resource.file.url if resource.file else None,
            'url': resource.url
        })
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Increment view count"""
        resource = self.get_object()
        resource.increment_view()
        
        serializer = self.get_serializer(resource)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular digital resources"""
        resources = self.get_queryset().order_by('-download_count')[:20]
        serializer = self.get_serializer(resources, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get resources grouped by type"""
        resources = self.get_queryset()
        grouped = {}
        
        for resource in resources:
            r_type = resource.get_resource_type_display()
            if r_type not in grouped:
                grouped[r_type] = []
            
            serializer = self.get_serializer(resource)
            grouped[r_type].append(serializer.data)
        
        return Response(grouped)


# ==================== STATISTICS VIEWS ====================
class LibraryStatsView(APIView):
    """View for library statistics"""
    permission_classes = [IsAuthenticated, IsLibrarian | IsAdminUser]
    
    def get(self, request):
        """Get library statistics"""
        # Overall statistics
        total_books = Book.objects.count()
        total_copies = Book.objects.aggregate(total=Sum('total_copies'))['total'] or 0
        available_copies = Book.objects.aggregate(total=Sum('available_copies'))['total'] or 0
        borrowed_copies = total_copies - available_copies
        
        total_digital = DigitalResource.objects.count()
        total_downloads = DigitalResource.objects.aggregate(total=Sum('download_count'))['total'] or 0
        
        # Borrow statistics
        active_borrows = BorrowRecord.objects.filter(returned=False).count()
        overdue_borrows = BorrowRecord.objects.filter(
            returned=False,
            due_date__lt=timezone.now()
        ).count()
        
        # Today's activity
        today = timezone.now().date()
        today_borrows = BorrowRecord.objects.filter(borrow_date__date=today).count()
        today_returns = BorrowRecord.objects.filter(return_date__date=today).count()
        
        # Fines
        total_fines = BorrowRecord.objects.filter(fine_paid=False).aggregate(
            total=Sum('fine_amount')
        )['total'] or 0
        
        # Top books
        top_books = Book.objects.annotate(
            borrow_count=Count('borrow_records')
        ).order_by('-borrow_count')[:10]
        
        top_books_data = BookSummarySerializer(top_books, many=True).data
        
        # Top digital resources
        top_resources = DigitalResource.objects.order_by('-download_count')[:10]
        top_resources_data = DigitalResourceSerializer(top_resources, many=True).data
        
        stats = {
            'overall': {
                'total_books': total_books,
                'total_copies': total_copies,
                'available_copies': available_copies,
                'borrowed_copies': borrowed_copies,
                'borrow_rate': (borrowed_copies / total_copies * 100) if total_copies > 0 else 0,
                'digital_resources': total_digital,
                'total_downloads': total_downloads,
            },
            'borrowing': {
                'active_borrows': active_borrows,
                'overdue_borrows': overdue_borrows,
                'overdue_rate': (overdue_borrows / active_borrows * 100) if active_borrows > 0 else 0,
                'today_borrows': today_borrows,
                'today_returns': today_returns,
                'total_fines': total_fines,
            },
            'top_books': top_books_data,
            'top_resources': top_resources_data,
        }
        
        return Response(stats)


class UserLibraryStatsView(APIView):
    """View for user library statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's library statistics"""
        user = request.user
        
        # Borrow statistics
        total_borrows = BorrowRecord.objects.filter(borrower=user).count()
        active_borrows = BorrowRecord.objects.filter(borrower=user, returned=False).count()
        overdue_borrows = BorrowRecord.objects.filter(
            borrower=user,
            returned=False,
            due_date__lt=timezone.now()
        ).count()
        
        # Reviews
        total_reviews = BookReview.objects.filter(user=user).count()
        approved_reviews = BookReview.objects.filter(user=user, is_approved=True).count()
        
        # Reading lists
        reading_lists = ReadingList.objects.filter(user=user).count()
        reading_list_items = ReadingListItem.objects.filter(reading_list__user=user).count()
        completed_items = ReadingListItem.objects.filter(
            reading_list__user=user,
            completed=True
        ).count()
        
        # Fines
        unpaid_fines = BorrowRecord.objects.filter(
            borrower=user,
            fine_paid=False,
            fine_amount__gt=0
        ).aggregate(total=Sum('fine_amount'))['total'] or 0
        
        # Recently borrowed
        recent_borrows = BorrowRecord.objects.filter(
            borrower=user
        ).order_by('-borrow_date')[:5]
        recent_borrows_data = BorrowRecordSerializer(recent_borrows, many=True).data
        
        stats = {
            'borrowing': {
                'total_borrows': total_borrows,
                'active_borrows': active_borrows,
                'overdue_borrows': overdue_borrows,
                'unpaid_fines': unpaid_fines,
            },
            'engagement': {
                'total_reviews': total_reviews,
                'approved_reviews': approved_reviews,
                'reading_lists': reading_lists,
                'reading_list_items': reading_list_items,
                'completed_items': completed_items,
                'completion_rate': (completed_items / reading_list_items * 100) if reading_list_items > 0 else 0,
            },
            'recent_borrows': recent_borrows_data,
        }
        
        return Response(stats)


class DailyStatsView(APIView):
    """View for daily statistics"""
    permission_classes = [IsAuthenticated, IsLibrarian | IsAdminUser]
    
    def get(self, request):
        """Get daily statistics for the last 30 days"""
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Generate dates
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Get or create stats for each date
        stats_data = []
        for date in dates:
            stats, created = LibraryStats.objects.get_or_create(date=date)
            if created:
                # Calculate stats for this date
                stats.total_books = Book.objects.filter(
                    created_at__date__lte=date
                ).count()
                
                stats.total_copies = Book.objects.filter(
                    created_at__date__lte=date
                ).aggregate(total=Sum('total_copies'))['total'] or 0
                
                stats.borrowed_copies = BorrowRecord.objects.filter(
                    borrow_date__date__lte=date,
                    returned=False
                ).count()
                
                stats.available_copies = stats.total_copies - stats.borrowed_copies
                
                stats.daily_borrows = BorrowRecord.objects.filter(
                    borrow_date__date=date
                ).count()
                
                stats.daily_returns = BorrowRecord.objects.filter(
                    return_date__date=date
                ).count()
                
                stats.save()
            
            serializer = LibraryStatsSerializer(stats)
            stats_data.append(serializer.data)
        
        return Response(stats_data)


# ==================== SEARCH VIEWS ====================
class BookSearchView(APIView):
    """Advanced book search"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Search books with advanced filters"""
        serializer = BookSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        queryset = Book.objects.all()
        
        # Apply filters
        if data.get('query'):
            queryset = queryset.filter(
                Q(title__icontains=data['query']) |
                Q(subtitle__icontains=data['query']) |
                Q(description__icontains=data['query']) |
                Q(keywords__icontains=data['query'])
            )
        
        if data.get('category'):
            queryset = queryset.filter(categories__id=data['category'])
        
        if data.get('subject'):
            queryset = queryset.filter(subject__id=data['subject'])
        
        if data.get('book_type'):
            queryset = queryset.filter(book_type=data['book_type'])
        
        if data.get('format'):
            queryset = queryset.filter(format=data['format'])
        
        if data.get('language'):
            queryset = queryset.filter(language=data['language'])
        
        if data.get('curriculum'):
            queryset = queryset.filter(curriculum=data['curriculum'])
        
        if data.get('grade_level'):
            queryset = queryset.filter(grade_level=data['grade_level'])
        
        if data.get('author'):
            queryset = queryset.filter(authors__id=data['author'])
        
        if data.get('publisher'):
            queryset = queryset.filter(publisher__id=data['publisher'])
        
        if data.get('available_only'):
            queryset = queryset.filter(available_copies__gt=0)
        
        # Apply sorting
        sort_by = data['sort_by']
        if data['sort_order'] == 'desc':
            sort_by = '-' + sort_by
        
        queryset = queryset.order_by(sort_by).distinct()
        
        # Paginate
        paginator = Paginator(queryset, 20)
        page_number = request.data.get('page', 1)
        page = paginator.get_page(page_number)
        
        serializer = BookSummarySerializer(page, many=True)
        return Response({
            'results': serializer.data,
            'total': paginator.count,
            'page': page_number,
            'pages': paginator.num_pages
        })


class DigitalResourceSearchView(APIView):
    """Advanced digital resource search"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Search digital resources"""
        serializer = DigitalResourceSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        queryset = DigitalResource.objects.all()
        
        # Apply filters
        if data.get('query'):
            queryset = queryset.filter(
                Q(title__icontains=data['query']) |
                Q(description__icontains=data['query']) |
                Q(author__icontains=data['query'])
            )
        
        if data.get('resource_type'):
            queryset = queryset.filter(resource_type=data['resource_type'])
        
        if data.get('subject'):
            queryset = queryset.filter(subject__id=data['subject'])
        
        if data.get('curriculum'):
            queryset = queryset.filter(curriculum=data['curriculum'])
        
        if data.get('grade_level'):
            queryset = queryset.filter(grade_level=data['grade_level'])
        
        # Apply sorting
        queryset = queryset.order_by(data['sort_by']).distinct()
        
        # Paginate
        paginator = Paginator(queryset, 20)
        page_number = request.data.get('page', 1)
        page = paginator.get_page(page_number)
        
        serializer = DigitalResourceSerializer(page, many=True)
        return Response({
            'results': serializer.data,
            'total': paginator.count,
            'page': page_number,
            'pages': paginator.num_pages
        })


# ==================== BULK OPERATIONS ====================
class BulkBookImportView(APIView):
    """Bulk import books"""
    permission_classes = [IsAuthenticated, IsLibrarian | IsAdminUser]
    
    def post(self, request):
        """Import multiple books at once"""
        serializer = BulkBookImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        books_data = serializer.validated_data['books']
        created_books = []
        errors = []
        
        for book_data in books_data:
            try:
                book_serializer = BookCreateSerializer(data=book_data)
                if book_serializer.is_valid():
                    book = book_serializer.save()
                    created_books.append(book)
                else:
                    errors.append({
                        'data': book_data,
                        'errors': book_serializer.errors
                    })
            except Exception as e:
                errors.append({
                    'data': book_data,
                    'error': str(e)
                })
        
        return Response({
            'created': len(created_books),
            'errors': errors,
            'books': BookSummarySerializer(created_books, many=True).data
        })


class BulkBookUpdateView(APIView):
    """Bulk update books"""
    permission_classes = [IsAuthenticated, IsLibrarian | IsAdminUser]
    
    def post(self, request):
        """Update multiple books at once"""
        serializer = BulkBookUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        book_ids = serializer.validated_data['book_ids']
        update_data = serializer.validated_data['data']
        
        updated_count = 0
        errors = []
        
        for book_id in book_ids:
            try:
                book = Book.objects.get(id=book_id)
                for key, value in update_data.items():
                    setattr(book, key, value)
                book.save()
                updated_count += 1
            except Book.DoesNotExist:
                errors.append(f'Book {book_id} not found')
            except Exception as e:
                errors.append(f'Error updating book {book_id}: {str(e)}')
        
        return Response({
            'updated': updated_count,
            'errors': errors
        })


# ==================== TEACHER RESOURCE VIEWSETS ====================
class TeacherResourceViewSet(viewsets.ModelViewSet):
    """ViewSet for TeacherResource CRUD operations"""
    queryset = TeacherResource.objects.all()
    serializer_class = TeacherResourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'resource_type', 'subject', 'curriculum', 
        'grade_level', 'is_public', 'author', 'created_by'
    ]
    search_fields = ['title', 'description']
    ordering_fields = ['-created_at', 'download_count', 'view_count', 'title']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TeacherResourceSummarySerializer
        return TeacherResourceSerializer
    
    def get_queryset(self):
        """Filter resources based on access"""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Filter by user groups if resource has access restrictions
        if not (user.role == 'librarian' or user.is_staff or user.role == 'teacher'):
            queryset = queryset.filter(
                Q(is_public=True) | Q(access_groups__in=user.groups.all())
            ).distinct()
        
        # Teachers can see their own resources and public ones
        if user.role == 'teacher':
            queryset = queryset.filter(
                Q(is_public=True) | 
                Q(access_groups__in=user.groups.all()) |
                Q(created_by=user)
            ).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by when creating resource"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Download a teacher resource"""
        resource = self.get_object()
        
        # Check access
        if not resource.is_public and not (
            resource.access_groups.filter(id__in=request.user.groups.all()).exists() or
            request.user.role in ['librarian', 'teacher', 'staff'] or
            resource.created_by == request.user
        ):
            return Response(
                {'error': 'You do not have permission to download this resource.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Increment download count
        resource.increment_download()
        
        # Return download info
        return Response({
            'message': 'Download started',
            'resource': resource.title,
            'file_url': resource.file.url if resource.file else None,
            'download_count': resource.download_count
        })
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Increment view count"""
        resource = self.get_object()
        resource.increment_view()
        
        serializer = self.get_serializer(resource)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_resources(self, request):
        """Get resources created by the current user"""
        resources = self.get_queryset().filter(created_by=request.user)
        
        page = self.paginate_queryset(resources)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(resources, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_subject(self, request):
        """Get resources grouped by subject"""
        resources = self.get_queryset()
        grouped = {}
        
        for resource in resources:
            if resource.subject:
                subject_name = resource.subject.name
                if subject_name not in grouped:
                    grouped[subject_name] = []
                
                serializer = TeacherResourceSummarySerializer(resource)
                grouped[subject_name].append(serializer.data)
        
        return Response(grouped)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular teacher resources"""
        resources = self.get_queryset().order_by('-download_count')[:20]
        serializer = self.get_serializer(resources, many=True)
        return Response(serializer.data)



# ==================== EXPORT VIEWS ====================
class BookExportView(APIView):
    """Export books to various formats"""
    permission_classes = [IsAuthenticated, IsLibrarian | IsAdminUser]
    
    def get(self, request):
        """Export books"""
        format_type = request.query_params.get('format', 'json')
        books = Book.objects.all()
        
        if format_type == 'json':
            serializer = BookExportSerializer(books, many=True)
            return Response(serializer.data)
        
        elif format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="books_export.csv"'
            
            writer = csv.writer(response)
            
            # Write headers
            writer.writerow([
                'Title', 'Subtitle', 'ISBN', 'Type', 'Format', 'Language',
                'Subject', 'Curriculum', 'Grade Level', 'Authors',
                'Publisher', 'Publication Year', 'Edition', 'Categories',
                'Pages', 'Total Copies', 'Available Copies', 'Shelf Location',
                'Price', 'Currency', 'Is Reference', 'Is Digital'
            ])
            
            # Write data
            for book in books:
                writer.writerow([
                    book.title,
                    book.subtitle or '',
                    book.isbn or '',
                    book.get_book_type_display(),
                    book.get_format_display(),
                    book.get_language_display(),
                    book.subject.name if book.subject else '',
                    book.curriculum or '',
                    book.grade_level or '',
                    ', '.join([author.full_name for author in book.authors.all()]),
                    book.publisher.name if book.publisher else '',
                    book.publication_year or '',
                    book.edition or '',
                    ', '.join([category.name for category in book.categories.all()]),
                    book.pages or '',
                    book.total_copies,
                    book.available_copies,
                    book.shelf_location or '',
                    book.price or '',
                    book.currency,
                    'Yes' if book.is_reference else 'No',
                    'Yes' if book.is_digital else 'No'
                ])
            
            return response
        
        else:
            return Response(
                {'error': 'Unsupported format. Use json or csv.'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ==================== NOTIFICATION VIEWS ====================
class LibraryNotificationView(APIView):
    """Library notifications"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get library notifications for user"""
        user = request.user
        notifications = []
        
        # Overdue books
        overdue_books = BorrowRecord.objects.filter(
            borrower=user,
            returned=False,
            due_date__lt=timezone.now()
        )
        
        for borrow in overdue_books:
            notifications.append({
                'type': 'overdue',
                'message': f'Book "{borrow.book.title}" is overdue',
                'date': borrow.due_date,
                'book_id': str(borrow.book.id),
                'borrow_id': str(borrow.id),
                'fine': borrow.calculated_fine
            })
        
        # Reservations ready
        ready_reservations = BookReservation.objects.filter(
            user=user,
            status='ready'
        )
        
        for reservation in ready_reservations:
            notifications.append({
                'type': 'reservation_ready',
                'message': f'Your reservation for "{reservation.book.title}" is ready for pickup',
                'date': reservation.fulfilled_date or reservation.updated_at,
                'book_id': str(reservation.book.id),
                'reservation_id': str(reservation.id)
            })
        
        # Books due soon (within 3 days)
        due_soon = BorrowRecord.objects.filter(
            borrower=user,
            returned=False,
            due_date__gte=timezone.now(),
            due_date__lte=timezone.now() + timedelta(days=3)
        )
        
        for borrow in due_soon:
            notifications.append({
                'type': 'due_soon',
                'message': f'Book "{borrow.book.title}" is due soon',
                'date': borrow.due_date,
                'book_id': str(borrow.book.id),
                'borrow_id': str(borrow.id),
                'days_left': (borrow.due_date.date() - timezone.now().date()).days
            })
        
        return Response(notifications)


# ==================== RECOMMENDATION VIEWS ====================
class BookRecommendationsView(APIView):
    """Book recommendations for users"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get book recommendations"""
        user = request.user
        
        recommendations = []
        
        # Based on borrowed books
        borrowed_books = Book.objects.filter(
            borrow_records__borrower=user
        ).distinct()
        
        if borrowed_books.exists():
            # Find books in same categories
            for book in borrowed_books[:3]:  # Limit to 3 borrowed books
                similar_books = Book.objects.filter(
                    categories__in=book.categories.all(),
                    is_active=True,
                    available_copies__gt=0
                ).exclude(
                    id__in=borrowed_books.values_list('id', flat=True)
                ).distinct()[:5]
                
                for similar in similar_books:
                    recommendations.append({
                        'book': BookSummarySerializer(similar).data,
                        'reason': f'Similar to "{book.title}"',
                        'confidence': 'high'
                    })
        
        # Based on user's Class/subject
        if user.role == 'student' and user.student_Class:
            # Get books for student's subjects
            subjects = user.student_Class.subjects.all()
            subject_books = Book.objects.filter(
                subject__in=subjects,
                is_active=True,
                available_copies__gt=0
            ).exclude(
                id__in=borrowed_books.values_list('id', flat=True)
            ).distinct()[:10]
            
            for book in subject_books:
                recommendations.append({
                    'book': BookSummarySerializer(book).data,
                    'reason': 'Recommended for your subjects',
                    'confidence': 'medium'
                })
        
        # Popular books
        popular_books = Book.objects.annotate(
            borrow_count=Count('borrow_records')
        ).filter(
            is_active=True,
            available_copies__gt=0
        ).exclude(
            id__in=borrowed_books.values_list('id', flat=True)
        ).order_by('-borrow_count')[:10]
        
        for book in popular_books:
            recommendations.append({
                'book': BookSummarySerializer(book).data,
                'reason': 'Popular among other users',
                'confidence': 'low'
            })
        
        # Remove duplicates
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            book_id = rec['book']['id']
            if book_id not in seen:
                seen.add(book_id)
                unique_recommendations.append(rec)
        
        return Response(unique_recommendations[:20])  # Limit to 20 recommendations



# ==================== ADDITIONAL VIEWS ====================
class UserCurrentBorrowsView(APIView):
    """Get current borrows for logged in user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's current borrows"""
        borrows = BorrowRecord.objects.filter(
            borrower=request.user,
            returned=False
        ).order_by('due_date')
        
        serializer = BorrowRecordSerializer(borrows, many=True)
        return Response(serializer.data)


class UserReadingProgressView(APIView):
    """Get user's reading progress"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get reading progress"""
        user = request.user
        
        # Reading lists
        reading_lists = ReadingList.objects.filter(user=user)
        total_items = ReadingListItem.objects.filter(reading_list__user=user).count()
        completed_items = ReadingListItem.objects.filter(
            reading_list__user=user,
            completed=True
        ).count()
        
        # Books borrowed this month
        this_month = timezone.now().month
        this_year = timezone.now().year
        
        monthly_borrows = BorrowRecord.objects.filter(
            borrower=user,
            borrow_date__month=this_month,
            borrow_date__year=this_year
        ).count()
        
        # Books read (completed in reading lists)
        completed_books = ReadingListItem.objects.filter(
            reading_list__user=user,
            completed=True
        ).values_list('book__title', flat=True)
        
        return Response({
            'reading_lists': reading_lists.count(),
            'total_items': total_items,
            'completed_items': completed_items,
            'completion_rate': (completed_items / total_items * 100) if total_items > 0 else 0,
            'monthly_borrows': monthly_borrows,
            'completed_books': list(completed_books),
            'current_borrows': BorrowRecord.objects.filter(
                borrower=user,
                returned=False
            ).count()
        })


class LibrarianOverdueListView(APIView):
    """Get overdue list for librarians"""
    permission_classes = [IsAuthenticated, IsLibrarian | IsAdminUser]
    
    def get(self, request):
        """Get all overdue books"""
        overdue = BorrowRecord.objects.filter(
            returned=False,
            due_date__lt=timezone.now()
        ).order_by('due_date')
        
        # Calculate totals
        total_fines = overdue.aggregate(total=Sum('calculated_fine'))['total'] or 0
        total_books = overdue.count()
        
        serializer = BorrowRecordSerializer(overdue, many=True)
        return Response({
            'overdue_books': serializer.data,
            'total_books': total_books,
            'total_fines': total_fines
        })


class LibrarianFineManagementView(APIView):
    """Manage fines for librarians"""
    permission_classes = [IsAuthenticated, IsLibrarian | IsAdminUser]
    
    def get(self, request):
        """Get all unpaid fines"""
        unpaid_fines = BorrowRecord.objects.filter(
            fine_paid=False,
            fine_amount__gt=0
        ).order_by('-due_date')
        
        total_unpaid = unpaid_fines.aggregate(total=Sum('fine_amount'))['total'] or 0
        
        serializer = BorrowRecordSerializer(unpaid_fines, many=True)
        return Response({
            'unpaid_fines': serializer.data,
            'total_unpaid': total_unpaid
        })
    
    def post(self, request):
        """Mark fines as paid"""
        borrow_id = request.data.get('borrow_id')
        
        try:
            borrow = BorrowRecord.objects.get(id=borrow_id)
            borrow.fine_paid = True
            borrow.save()
            
            serializer = BorrowRecordSerializer(borrow)
            return Response(serializer.data)
        except BorrowRecord.DoesNotExist:
            return Response(
                {'error': 'Borrow record not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class LibrarianInventoryCheckView(APIView):
    """Inventory check for librarians"""
    permission_classes = [IsAuthenticated, IsLibrarian | IsAdminUser]
    
    def get(self, request):
        """Get inventory status"""
        # Books with no available copies
        out_of_stock = Book.objects.filter(available_copies=0)
        
        # Reference books
        reference_books = Book.objects.filter(is_reference=True)
        
        # Damaged copies
        damaged_copies = BookCopy.objects.filter(condition='damaged')
        
        # Missing copies (should be available but borrowed)
        missing_copies = []
        for book in Book.objects.all():
            expected_available = book.total_copies - book.borrow_records.filter(
                returned=False
            ).count()
            
            if expected_available != book.available_copies:
                missing_copies.append({
                    'book': book.title,
                    'expected': expected_available,
                    'actual': book.available_copies,
                    'difference': book.available_copies - expected_available
                })
        
        return Response({
            'out_of_stock': BookSummarySerializer(out_of_stock, many=True).data,
            'reference_books_count': reference_books.count(),
            'damaged_copies': BookCopySerializer(damaged_copies, many=True).data,
            'missing_copies': missing_copies,
            'total_books': Book.objects.count(),
            'total_copies': Book.objects.aggregate(total=Sum('total_copies'))['total'] or 0,
            'total_available': Book.objects.aggregate(total=Sum('available_copies'))['total'] or 0
        })


class PublicCatalogView(APIView):
    """Public book catalog (no authentication required)"""
    permission_classes = []
    
    def get(self, request):
        """Get public book catalog"""
        books = Book.objects.filter(is_active=True).order_by('title')[:100]  # Limit to 100
        
        categories = BookCategory.objects.all()
        popular_books = Book.objects.annotate(
            borrow_count=Count('borrow_records')
        ).order_by('-borrow_count')[:10]
        
        new_arrivals = Book.objects.filter(
            is_active=True
        ).order_by('-created_at')[:10]
        
        return Response({
            'books': BookSummarySerializer(books, many=True).data,
            'categories': BookCategorySerializer(categories, many=True).data,
            'popular_books': BookSummarySerializer(popular_books, many=True).data,
            'new_arrivals': BookSummarySerializer(new_arrivals, many=True).data,
            'stats': {
                'total_books': Book.objects.count(),
                'available_books': Book.objects.filter(available_copies__gt=0).count(),
                'digital_resources': DigitalResource.objects.filter(is_public=True).count()
            }
        })


class PublicBookDetailView(APIView):
    """Public book details"""
    permission_classes = []
    
    def get(self, request, book_id):
        """Get book details"""
        try:
            book = Book.objects.get(id=book_id, is_active=True)
            reviews = book.reviews.filter(is_approved=True)[:10]  # Limit to 10 reviews
            
            return Response({
                'book': BookSummarySerializer(book).data,
                'reviews': BookReviewSerializer(reviews, many=True).data,
                'available': book.is_available,
                'average_rating': book.average_rating
            })
        except Book.DoesNotExist:
            return Response(
                {'error': 'Book not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class PublicDigitalResourcesView(APIView):
    """Public digital resources"""
    permission_classes = []
    
    def get(self, request):
        """Get public digital resources"""
        resources = DigitalResource.objects.filter(is_public=True).order_by('-created_at')[:50]
        
        # Group by type
        grouped = {}
        for resource in resources:
            r_type = resource.get_resource_type_display()
            if r_type not in grouped:
                grouped[r_type] = []
            
            serializer = DigitalResourceSerializer(resource)
            grouped[r_type].append(serializer.data)
        
        return Response({
            'resources': grouped,
            'total': resources.count()
        })