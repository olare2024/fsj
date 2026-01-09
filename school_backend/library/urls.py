from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

# Create a main router
router = DefaultRouter()

# Book categories
router.register(r'categories', views.BookCategoryViewSet, basename='category')

# Authors and publishers
router.register(r'authors', views.AuthorViewSet, basename='author')
router.register(r'publishers', views.PublisherViewSet, basename='publisher')

# Books
router.register(r'books', views.BookViewSet, basename='book')
router.register(r'book-copies', views.BookCopyViewSet, basename='bookcopy')

# Borrowing system
router.register(r'borrows', views.BorrowRecordViewSet, basename='borrow')

# Reviews
router.register(r'reviews', views.BookReviewViewSet, basename='review')

# Reading lists
router.register(r'reading-lists', views.ReadingListViewSet, basename='readinglist')

# Reservations
router.register(r'reservations', views.BookReservationViewSet, basename='reservation')

# Digital resources
router.register(r'digital-resources', views.DigitalResourceViewSet, basename='digitalresource')

# Teacher resources - ADD THIS LINE
router.register(r'teacher-resources', views.TeacherResourceViewSet, basename='teacherresource')

# API endpoints
urlpatterns = [
    # Main API routes
    path('', include(router.urls)),
    
    # Statistics and analytics
    path('stats/overall/', views.LibraryStatsView.as_view(), name='library-stats'),
    path('stats/user/', views.UserLibraryStatsView.as_view(), name='user-library-stats'),
    path('stats/daily/', views.DailyStatsView.as_view(), name='daily-library-stats'),
    
    # Search endpoints
    path('search/books/', views.BookSearchView.as_view(), name='book-search'),
    path('search/digital/', views.DigitalResourceSearchView.as_view(), name='digital-search'),
    
    # Bulk operations
    path('bulk/import/', views.BulkBookImportView.as_view(), name='bulk-book-import'),
    path('bulk/update/', views.BulkBookUpdateView.as_view(), name='bulk-book-update'),
    path('export/books/', views.BookExportView.as_view(), name='book-export'),
    
    # Notifications
    path('notifications/', views.LibraryNotificationView.as_view(), name='library-notifications'),
    
    # Recommendations
    path('recommendations/', views.BookRecommendationsView.as_view(), name='book-recommendations'),
    
    # User endpoints
    path('user/current-borrows/', views.UserCurrentBorrowsView.as_view(), name='user-current-borrows'),
    path('user/reading-progress/', views.UserReadingProgressView.as_view(), name='user-reading-progress'),
    
    # Librarian endpoints
    path('librarian/overdue-list/', views.LibrarianOverdueListView.as_view(), name='librarian-overdue-list'),
    path('librarian/fine-management/', views.LibrarianFineManagementView.as_view(), name='librarian-fine-management'),
    path('librarian/inventory-check/', views.LibrarianInventoryCheckView.as_view(), name='librarian-inventory-check'),
    
    # Public endpoints (for catalog)
    path('public/catalog/', views.PublicCatalogView.as_view(), name='public-catalog'),
    path('public/books/<uuid:book_id>/', views.PublicBookDetailView.as_view(), name='public-book-detail'),
    path('public/digital/', views.PublicDigitalResourcesView.as_view(), name='public-digital-resources'),
]