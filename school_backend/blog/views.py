# blog/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType

from users import serializers

from .models import (
    BlogCategory, BlogPost, DiscussionThread, DiscussionPost,
    BlogComment, PostLike, DiscussionVote, StudyGroup,
    StudyGroupMembership, Notification
)
from .serializers import (
    BlogCategorySerializer, BlogCategoryMinimalSerializer,
    BlogPostListSerializer, BlogPostDetailSerializer, BlogPostCreateSerializer, BlogPostUpdateSerializer,
    DiscussionThreadListSerializer, DiscussionThreadDetailSerializer, DiscussionThreadCreateSerializer,
    DiscussionPostSerializer, DiscussionPostCreateSerializer,
    BlogCommentSerializer, BlogCommentCreateSerializer,
    PostLikeSerializer, DiscussionVoteSerializer,
    StudyGroupSerializer, StudyGroupCreateSerializer, StudyGroupMembershipSerializer,
    NotificationSerializer,
    BlogDashboardSerializer, UserBlogActivitySerializer, BlogAnalyticsSerializer,
    ContentSearchSerializer, MentionUserSerializer
)
from users.models import User
from academic.models import Student, Teacher, ClassRoom


class BlogCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog categories
    """
    permission_classes = [IsAuthenticated]
    queryset = BlogCategory.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['accessible_to_students', 'accessible_to_teachers', 'accessible_to_parents']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BlogCategoryMinimalSerializer
        return BlogCategorySerializer
    
    def get_queryset(self):
        """Filter categories based on user role"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_student:
            queryset = queryset.filter(accessible_to_students=True)
        elif user.is_teacher:
            queryset = queryset.filter(accessible_to_teachers=True)
        elif user.is_parent:
            queryset = queryset.filter(accessible_to_parents=True)
        
        return queryset.annotate(
            post_count=Count('posts', filter=Q(posts__status='published')),
            discussion_count=Count('discussions', filter=Q(discussions__is_active=True))
        )
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class BlogPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog posts
    """
    permission_classes = [IsAuthenticated]
    queryset = BlogPost.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'excerpt', 'tags']
    filterset_fields = ['category', 'content_type', 'subject', 'status', 'author', 'audience']
    ordering_fields = ['published_date', 'created_at', 'views_count', 'likes_count']
    ordering = ['-published_date', '-created_at']
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BlogPostListSerializer
        elif self.action == 'retrieve':
            return BlogPostDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            if self.action == 'create':
                return BlogPostCreateSerializer
            return BlogPostUpdateSerializer
        return BlogPostDetailSerializer
    
    def get_queryset(self):
        """Filter posts based on user role and permissions"""
        user = self.request.user
        queryset = super().get_queryset().select_related(
            'author', 'category', 'subject', 'specific_class'
        ).prefetch_related('co_authors', 'likes', 'comments')
        
        # Base queryset for different user types
        if user.is_student:
            student_profile = getattr(user, 'student_profile', None)
            if student_profile and student_profile.classroom:
                queryset = queryset.filter(
                    Q(status='published') &
                    (
                        Q(audience='all') |
                        Q(audience='students') |
                        Q(audience='specific_class', specific_class=student_profile.classroom)
                    )
                )
            else:
                queryset = queryset.filter(
                    Q(status='published') &
                    (Q(audience='all') | Q(audience='students'))
                )
                
        elif user.is_teacher:
            queryset = queryset.filter(
                Q(status='published') |
                Q(author=user) |
                Q(co_authors=user)
            ).distinct()
            
        elif user.is_parent:
            queryset = queryset.filter(
                Q(status='published') &
                (Q(audience='all') | Q(audience='parents'))
            )
            
        else:  # Staff and superusers
            queryset = queryset.all()
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def retrieve(self, request, *args, **kwargs):
        """Increment views count when post is viewed"""
        instance = self.get_object()
        
        # Check if user can view this post
        if not instance.can_view(request.user):
            return Response(
                {'error': 'You do not have permission to view this post.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Increment views count
        instance.increment_views()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like or unlike a blog post"""
        post = self.get_object()
        user = request.user
        
        like, created = PostLike.objects.get_or_create(user=user, post=post)
        
        if not created:
            # Unlike if already liked
            like.delete()
            post.likes_count = F('likes_count') - 1
            liked = False
        else:
            post.likes_count = F('likes_count') + 1
            liked = True
        
        post.save(update_fields=['likes_count'])
        post.refresh_from_db()
        
        return Response({
            'liked': liked,
            'likes_count': post.likes_count
        })
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a draft post"""
        post = self.get_object()
        
        if post.author != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only publish your own posts.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if post.status != 'draft':
            return Response(
                {'error': 'Only draft posts can be published.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        post.status = 'published'
        post.published_date = timezone.now()
        post.save()
        
        serializer = self.get_serializer(post)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        """Get current user's posts"""
        user = request.user
        posts = self.get_queryset().filter(
            Q(author=user) | Q(co_authors=user)
        ).distinct()
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured posts (most viewed or liked)"""
        featured_posts = self.get_queryset().filter(
            status='published'
        ).order_by('-views_count', '-likes_count')[:10]
        
        serializer = self.get_serializer(featured_posts, many=True)
        return Response(serializer.data)


class DiscussionThreadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing discussion threads
    """
    permission_classes = [IsAuthenticated]
    queryset = DiscussionThread.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    filterset_fields = ['category', 'discussion_type', 'subject', 'classroom', 'privacy_level']
    ordering_fields = ['last_activity', 'created_at', 'reply_count']
    ordering = ['-is_pinned', '-last_activity']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DiscussionThreadListSerializer
        elif self.action == 'retrieve':
            return DiscussionThreadDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            if self.action == 'create':
                return DiscussionThreadCreateSerializer
            return DiscussionThreadListSerializer
        return DiscussionThreadDetailSerializer
    
    def get_queryset(self):
        """Filter discussions based on user permissions"""
        user = self.request.user
        queryset = super().get_queryset().select_related(
            'created_by', 'category', 'subject', 'classroom'
        ).prefetch_related('moderators', 'invited_users', 'posts')
        
        # Filter based on privacy level and user role
        if user.is_student:
            student_profile = getattr(user, 'student_profile', None)
            if student_profile and student_profile.classroom:
                queryset = queryset.filter(
                    Q(privacy_level='public') |
                    Q(privacy_level='class_only', classroom=student_profile.classroom) |
                    Q(invited_users=user) |
                    Q(created_by=user)
                ).distinct()
            else:
                queryset = queryset.filter(
                    Q(privacy_level='public') |
                    Q(invited_users=user) |
                    Q(created_by=user)
                ).distinct()
                
        elif user.is_teacher:
            queryset = queryset.filter(
                Q(privacy_level='public') |
                Q(privacy_level='class_only') |
                Q(invited_users=user) |
                Q(created_by=user) |
                Q(moderators=user)
            ).distinct()
            
        else:  # Staff, parents, etc.
            queryset = queryset.filter(privacy_level='public')
        
        return queryset.annotate(
            participant_count=Count('posts__author', distinct=True)
        )
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def retrieve(self, request, *args, **kwargs):
        """Increment views count when discussion is viewed"""
        instance = self.get_object()
        
        # Check if user can view this discussion
        if not instance.can_participate(request.user):
            return Response(
                {'error': 'You do not have permission to view this discussion.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Increment views count
        instance.views_count = F('views_count') + 1
        instance.save(update_fields=['views_count'])
        instance.refresh_from_db()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        """Lock or unlock a discussion"""
        thread = self.get_object()
        
        if not (request.user in thread.moderators.all() or 
                request.user == thread.created_by or
                request.user.is_staff):
            return Response(
                {'error': 'You do not have permission to moderate this discussion.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        thread.is_locked = not thread.is_locked
        thread.save()
        
        return Response({
            'locked': thread.is_locked,
            'message': f'Discussion {"locked" if thread.is_locked else "unlocked"} successfully.'
        })
    
    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """Pin or unpin a discussion"""
        thread = self.get_object()
        
        if not (request.user in thread.moderators.all() or 
                request.user == thread.created_by or
                request.user.is_staff):
            return Response(
                {'error': 'You do not have permission to moderate this discussion.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        thread.is_pinned = not thread.is_pinned
        thread.save()
        
        return Response({
            'pinned': thread.is_pinned,
            'message': f'Discussion {"pinned" if thread.is_pinned else "unpinned"} successfully.'
        })
    
    @action(detail=False, methods=['get'])
    def my_discussions(self, request):
        """Get discussions created by current user"""
        user = request.user
        discussions = self.get_queryset().filter(created_by=user)
        
        page = self.paginate_queryset(discussions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(discussions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def participating(self, request):
        """Get discussions where user has participated"""
        user = request.user
        discussion_ids = DiscussionPost.objects.filter(
            author=user
        ).values_list('discussion_id', flat=True).distinct()
        
        discussions = self.get_queryset().filter(id__in=discussion_ids)
        
        page = self.paginate_queryset(discussions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(discussions, many=True)
        return Response(serializer.data)


class DiscussionPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing discussion posts
    """
    permission_classes = [IsAuthenticated]
    queryset = DiscussionPost.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['discussion', 'parent', 'author', 'is_approved']
    ordering_fields = ['created_at', 'upvotes']
    ordering = ['created_at']
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DiscussionPostCreateSerializer
        return DiscussionPostSerializer
    
    def get_queryset(self):
        """Filter posts based on discussion permissions"""
        user = self.request.user
        queryset = super().get_queryset().select_related(
            'discussion', 'author', 'parent', 'approved_by'
        ).prefetch_related('votes')
        
        # Only show posts from discussions the user can access
        accessible_discussions = DiscussionThread.objects.filter(
            Q(privacy_level='public') |
            Q(privacy_level='class_only') |
            Q(invited_users=user) |
            Q(created_by=user) |
            Q(moderators=user)
        ).distinct()
        
        return queryset.filter(discussion__in=accessible_discussions)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        """Check permissions before creating post"""
        discussion = serializer.validated_data['discussion']
        
        if not discussion.can_participate(self.request.user):
            raise serializers.ValidationError(
                'You do not have permission to post in this discussion.'
            )
        
        if discussion.is_locked:
            raise serializers.ValidationError(
                'This discussion is locked and cannot accept new posts.'
            )
        
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """Vote on a discussion post"""
        post = self.get_object()
        user = request.user
        vote_type = request.data.get('vote_type')
        
        if vote_type not in ['up', 'down']:
            return Response(
                {'error': 'Vote type must be "up" or "down".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already voted
        existing_vote = DiscussionVote.objects.filter(user=user, post=post).first()
        
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Remove vote if same type
                existing_vote.delete()
                if vote_type == 'up':
                    post.upvotes = F('upvotes') - 1
                else:
                    post.downvotes = F('downvotes') - 1
            else:
                # Change vote type
                if existing_vote.vote_type == 'up':
                    post.upvotes = F('upvotes') - 1
                    post.downvotes = F('downvotes') + 1
                else:
                    post.downvotes = F('downvotes') - 1
                    post.upvotes = F('upvotes') + 1
                existing_vote.vote_type = vote_type
                existing_vote.save()
        else:
            # New vote
            DiscussionVote.objects.create(user=user, post=post, vote_type=vote_type)
            if vote_type == 'up':
                post.upvotes = F('upvotes') + 1
            else:
                post.downvotes = F('downvotes') + 1
        
        post.save(update_fields=['upvotes', 'downvotes'])
        post.refresh_from_db()
        
        return Response({
            'net_votes': post.net_votes,
            'user_vote': vote_type if not existing_vote or existing_vote.vote_type != vote_type else None
        })
    
    @action(detail=True, methods=['post'])
    def mark_answer(self, request, pk=None):
        """Mark a post as the answer (for Q&A discussions)"""
        post = self.get_object()
        
        if post.discussion.discussion_type != 'qna':
            return Response(
                {'error': 'This discussion is not a Q&A discussion.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not (request.user == post.discussion.created_by or 
                request.user in post.discussion.moderators.all() or
                request.user.is_staff):
            return Response(
                {'error': 'Only discussion creators and moderators can mark answers.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        post.mark_as_answer()
        
        return Response({
            'is_answer': post.is_answer,
            'message': 'Post marked as answer successfully.'
        })


class BlogCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog comments
    """
    permission_classes = [IsAuthenticated]
    queryset = BlogComment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'parent', 'author', 'is_approved']
    ordering_fields = ['created_at', 'likes_count']
    ordering = ['created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BlogCommentCreateSerializer
        return BlogCommentSerializer
    
    def get_queryset(self):
        """Filter comments based on post permissions"""
        user = self.request.user
        queryset = super().get_queryset().select_related(
            'post', 'author', 'parent', 'approved_by'
        )
        
        # Only show comments for posts the user can view
        accessible_posts = BlogPost.objects.filter(
            Q(status='published') &
            (
                Q(audience='all') |
                Q(audience='students', author__is_student=True) |
                Q(audience='teachers', author__is_teacher=True) |
                Q(audience='parents', author__is_parent=True) |
                Q(audience='specific_class', specific_class__students=user.student_profile) |
                Q(author=user) |
                Q(co_authors=user)
            )
        ).distinct()
        
        return queryset.filter(post__in=accessible_posts, is_approved=True)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like a comment"""
        comment = self.get_object()
        comment.likes_count = F('likes_count') + 1
        comment.save(update_fields=['likes_count'])
        comment.refresh_from_db()
        
        return Response({
            'likes_count': comment.likes_count,
            'message': 'Comment liked successfully.'
        })


class StudyGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing study groups
    """
    permission_classes = [IsAuthenticated]
    queryset = StudyGroup.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['subject', 'classroom', 'academic_year', 'is_public']
    ordering_fields = ['last_activity', 'created_at']
    ordering = ['-last_activity']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StudyGroupCreateSerializer
        return StudyGroupSerializer
    
    def get_queryset(self):
        """Filter study groups based on user permissions"""
        user = self.request.user
        queryset = super().get_queryset().select_related(
            'creator', 'subject', 'classroom', 'academic_year'
        ).prefetch_related('moderators', 'members')
        
        if user.is_student:
            queryset = queryset.filter(
                Q(is_public=True) |
                Q(members=user) |
                Q(creator=user)
            ).distinct()
        elif user.is_teacher:
            # Teachers can see all groups
            pass
        
        return queryset.annotate(member_count=Count('members'))
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a study group"""
        group = self.get_object()
        user = request.user
        
        if not group.is_public and user not in group.invited_users.all():
            return Response(
                {'error': 'This is a private group and you are not invited.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if group.is_full:
            return Response(
                {'error': 'This study group is full.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership, created = StudyGroupMembership.objects.get_or_create(
            group=group, user=user
        )
        
        if not created and not membership.is_active:
            membership.is_active = True
            membership.save()
        
        return Response({
            'joined': True,
            'message': 'Successfully joined the study group.'
        })
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a study group"""
        group = self.get_object()
        user = request.user
        
        if user == group.creator:
            return Response(
                {'error': 'Group creator cannot leave the group. Transfer ownership first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            membership = StudyGroupMembership.objects.get(group=group, user=user)
            membership.is_active = False
            membership.save()
            
            return Response({
                'left': True,
                'message': 'Successfully left the study group.'
            })
        except StudyGroupMembership.DoesNotExist:
            return Response(
                {'error': 'You are not a member of this group.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def generate_join_code(self, request, pk=None):
        """Generate a new join code for the study group"""
        group = self.get_object()
        
        if request.user != group.creator and not request.user.is_staff:
            return Response(
                {'error': 'Only group creator can generate join codes.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        group.generate_join_code()
        
        return Response({
            'join_code': group.join_code,
            'message': 'New join code generated successfully.'
        })


class StudyGroupMembershipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing study group memberships
    """
    permission_classes = [IsAuthenticated]
    queryset = StudyGroupMembership.objects.all()
    serializer_class = StudyGroupMembershipSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group', 'user', 'role', 'is_active']
    
    def get_queryset(self):
        """Filter memberships based on user permissions"""
        user = self.request.user
        queryset = super().get_queryset().select_related('group', 'user')
        
        # Users can only see memberships for groups they belong to
        user_groups = StudyGroup.objects.filter(
            Q(members=user) | Q(creator=user) | Q(moderators=user)
        )
        
        return queryset.filter(group__in=user_groups)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications
    """
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'is_read']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Users can only see their own notifications"""
        return super().get_queryset().filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        
        if notification.user != request.user:
            return Response(
                {'error': 'You can only mark your own notifications as read.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return Response({
            'read': True,
            'message': 'Notification marked as read.'
        })
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        notifications = self.get_queryset().filter(is_read=False)
        updated_count = notifications.update(
            is_read=True, read_at=timezone.now()
        )
        
        return Response({
            'updated_count': updated_count,
            'message': f'Marked {updated_count} notifications as read.'
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        unread_count = self.get_queryset().filter(is_read=False).count()
        
        return Response({'unread_count': unread_count})


# Dashboard and Analytics Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def blog_dashboard(request):
    """
    Get blog dashboard data for current user
    """
    user = request.user
    
    # Total counts
    total_posts = BlogPost.objects.filter(status='published').count()
    total_discussions = DiscussionThread.objects.count()
    total_comments = BlogComment.objects.filter(is_approved=True).count()
    
    # Recent activity
    recent_posts = BlogPost.objects.filter(status='published').order_by('-published_date')[:5]
    active_discussions = DiscussionThread.objects.annotate(
        recent_activity_count=Count('posts', filter=Q(posts__created_at__gte=timezone.now()-timedelta(days=7)))
    ).order_by('-recent_activity_count')[:5]
    
    # Popular categories
    popular_categories = BlogCategory.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).order_by('-post_count')[:5]
    
    data = {
        'total_posts': total_posts,
        'total_discussions': total_discussions,
        'total_comments': total_comments,
        'recent_posts': BlogPostListSerializer(recent_posts, many=True, context={'request': request}).data,
        'active_discussions': DiscussionThreadListSerializer(active_discussions, many=True, context={'request': request}).data,
        'popular_categories': BlogCategorySerializer(popular_categories, many=True).data,
    }
    
    serializer = BlogDashboardSerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_blog_activity(request, user_id=None):
    """
    Get blog activity for a specific user
    """
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        user = request.user
    
    # User activity counts
    posts_count = BlogPost.objects.filter(author=user, status='published').count()
    comments_count = BlogComment.objects.filter(author=user, is_approved=True).count()
    discussions_created = DiscussionThread.objects.filter(created_by=user).count()
    discussion_posts_count = DiscussionPost.objects.filter(author=user).count()
    likes_given = PostLike.objects.filter(user=user).count()
    
    # Recent activity
    recent_activity = []
    
    # Add recent posts
    recent_posts = BlogPost.objects.filter(author=user, status='published').order_by('-published_date')[:5]
    for post in recent_posts:
        recent_activity.append({
            'type': 'post',
            'title': post.title,
            'date': post.published_date,
            'url': f"/blog/posts/{post.slug}"
        })
    
    # Add recent discussion posts
    recent_discussion_posts = DiscussionPost.objects.filter(author=user).order_by('-created_at')[:5]
    for post in recent_discussion_posts:
        recent_activity.append({
            'type': 'discussion_post',
            'title': f"Reply in {post.discussion.title}",
            'date': post.created_at,
            'url': f"/discussions/{post.discussion.slug}"
        })
    
    data = {
        'posts_count': posts_count,
        'comments_count': comments_count,
        'discussions_created': discussions_created,
        'discussion_posts_count': discussion_posts_count,
        'likes_given': likes_given,
        'recent_activity': sorted(recent_activity, key=lambda x: x['date'], reverse=True)[:10]
    }
    
    serializer = UserBlogActivitySerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def blog_analytics(request):
    """
    Get blog analytics (admin only)
    """
    # Posts statistics
    posts_published = BlogPost.objects.filter(status='published').count()
    posts_by_type = BlogPost.objects.filter(status='published').values(
        'content_type'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Engagement metrics
    total_views = BlogPost.objects.aggregate(total_views=sum('views_count'))['total_views'] or 0
    total_likes = BlogPost.objects.aggregate(total_likes=sum('likes_count'))['total_likes'] or 0
    total_comments = BlogComment.objects.filter(is_approved=True).count()
    
    # Top posts
    top_posts = BlogPost.objects.filter(status='published').order_by('-views_count')[:10]
    
    # Active users (users with recent activity)
    active_users = User.objects.filter(
        Q(blog_posts__published_date__gte=timezone.now()-timedelta(days=30)) |
        Q(discussion_posts__created_at__gte=timezone.now()-timedelta(days=30)) |
        Q(blog_comments__created_at__gte=timezone.now()-timedelta(days=30))
    ).distinct().count()
    
    data = {
        'posts_published': posts_published,
        'posts_by_type': list(posts_by_type),
        'engagement_metrics': {
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_views_per_post': total_views / posts_published if posts_published > 0 else 0
        },
        'top_posts': BlogPostListSerializer(top_posts, many=True, context={'request': request}).data,
        'active_users': active_users
    }
    
    serializer = BlogAnalyticsSerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_content(request):
    """
    Search across blog posts, discussions, and comments
    """
    query = request.GET.get('q', '')
    content_type = request.GET.get('type', 'all')
    
    if not query:
        return Response({'error': 'Search query is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    results = []
    
    # Search blog posts
    if content_type in ['all', 'posts']:
        posts = BlogPost.objects.filter(
            Q(status='published') &
            (Q(title__icontains=query) | Q(content__icontains=query) | Q(excerpt__icontains=query))
        )[:10]
        
        for post in posts:
            if post.can_view(request.user):
                results.append({
                    'id': post.id,
                    'title': post.title,
                    'content': post.excerpt or post.content[:200] + '...' if len(post.content) > 200 else post.content,
                    'content_type': 'post',
                    'model_name': 'BlogPost',
                    'created_at': post.published_date,
                    'author_name': post.author.get_full_name(),
                    'url': f"/blog/posts/{post.slug}"
                })
    
    # Search discussions
    if content_type in ['all', 'discussions']:
        discussions = DiscussionThread.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:10]
        
        for discussion in discussions:
            if discussion.can_participate(request.user):
                results.append({
                    'id': discussion.id,
                    'title': discussion.title,
                    'content': discussion.description[:200] + '...' if discussion.description and len(discussion.description) > 200 else discussion.description,
                    'content_type': 'discussion',
                    'model_name': 'DiscussionThread',
                    'created_at': discussion.created_at,
                    'author_name': discussion.created_by.get_full_name(),
                    'url': f"/discussions/{discussion.slug}"
                })
    
    # Search discussion posts
    if content_type in ['all', 'discussion_posts']:
        discussion_posts = DiscussionPost.objects.filter(
            Q(content__icontains=query)
        ).select_related('discussion')[:10]
        
        for post in discussion_posts:
            if post.discussion.can_participate(request.user):
                results.append({
                    'id': post.id,
                    'title': f"Post in {post.discussion.title}",
                    'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
                    'content_type': 'discussion_post',
                    'model_name': 'DiscussionPost',
                    'created_at': post.created_at,
                    'author_name': post.author.get_full_name(),
                    'url': f"/discussions/{post.discussion.slug}#post-{post.id}"
                })
    
    # Sort by creation date
    results.sort(key=lambda x: x['created_at'], reverse=True)
    
    serializer = ContentSearchSerializer(results, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mention_suggestions(request):
    """
    Get user suggestions for mentions
    """
    query = request.GET.get('q', '')
    
    if not query:
        return Response([])
    
    # Search users by name or username
    users = User.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(username__icontains=query)
    )[:10]
    
    suggestions = []
    for user in users:
        user_type = 'teacher' if user.is_teacher else 'student' if user.is_student else 'staff'
        
        suggestions.append({
            'id': user.id,
            'name': user.get_full_name(),
            'username': user.username,
            'avatar': user.avatar.url if hasattr(user, 'avatar') and user.avatar else None,
            'type': user_type
        })
    
    serializer = MentionUserSerializer(suggestions, many=True)
    return Response(serializer.data)