# blog/serializers.py
from rest_framework import serializers
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import (
    BlogCategory, BlogPost, DiscussionThread, DiscussionPost,
    BlogComment, PostLike, DiscussionVote, StudyGroup,
    StudyGroupMembership, Notification
)
from users.serializers import CustomUserSerializer, UserMinimalSerializer
from academic.serializers import SubjectSerializer, ClassSerializer, StudentSerializer, TeacherSerializer
from administration.serializers import AcademicYearSerializer


class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for blog categories"""
    post_count = serializers.IntegerField(read_only=True)
    discussion_count = serializers.IntegerField(read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = BlogCategory
        fields = [
            'id', 'name', 'slug', 'description', 'color', 'icon',
            'parent', 'parent_name', 'order', 'accessible_to_students',
            'accessible_to_teachers', 'accessible_to_parents',
            'post_count', 'discussion_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class BlogCategoryMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for blog categories (for dropdowns)"""
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug', 'color', 'icon']


class BlogPostListSerializer(serializers.ModelSerializer):
    """Serializer for blog post listings (optimized for performance)"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    # Engagement metrics
    comment_count = serializers.IntegerField(read_only=True)
    reading_time = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author_name', 'author_avatar',
            'category', 'category_name', 'category_color', 'content_type',
            'subject', 'subject_name', 'featured_image', 'status',
            'published_date', 'views_count', 'likes_count', 'comment_count',
            'reading_time', 'is_liked', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'views_count', 'likes_count'
        ]
    
    def get_author_avatar(self, obj):
        """Get author avatar URL"""
        if hasattr(obj.author, 'avatar') and obj.author.avatar:
            return obj.author.avatar.url
        return None
    
    def get_is_liked(self, obj):
        """Check if current user liked this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single blog post"""
    author_details = CustomUserSerializer(read_only=True, source='author')
    co_authors_details = UserMinimalSerializer(read_only=True, source='co_authors', many=True)
    category_details = BlogCategorySerializer(read_only=True, source='category')
    subject_details = SubjectSerializer(read_only=True, source='subject')
    classroom_details = ClassRoomSerializer(read_only=True, source='specific_class')
    
    # Engagement metrics
    comment_count = serializers.IntegerField(read_only=True)
    reading_time = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'author_details', 'co_authors_details',
            'category', 'category_details', 'content_type', 'tags', 'subject', 'subject_details',
            'audience', 'specific_class', 'classroom_details', 'featured_image', 'attachments',
            'status', 'published_date', 'scheduled_date', 'meta_title', 'meta_description',
            'keywords', 'views_count', 'likes_count', 'shares_count', 'requires_approval',
            'approved_by', 'approved_at', 'comment_count', 'reading_time', 'is_liked',
            'can_edit', 'can_delete', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'views_count', 'likes_count', 'shares_count',
            'approved_at'
        ]
    
    def get_is_liked(self, obj):
        """Check if current user liked this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_can_edit(self, obj):
        """Check if current user can edit this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return (obj.author == request.user or 
                    request.user.is_staff or 
                    request.user.is_superuser)
        return False
    
    def get_can_delete(self, obj):
        """Check if current user can delete this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return (obj.author == request.user or 
                    request.user.is_staff or 
                    request.user.is_superuser)
        return False


class BlogPostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating blog posts"""
    class Meta:
        model = BlogPost
        fields = [
            'title', 'content', 'excerpt', 'category', 'content_type', 'tags',
            'subject', 'audience', 'specific_class', 'featured_image', 'attachments',
            'status', 'scheduled_date', 'meta_title', 'meta_description', 'keywords',
            'requires_approval', 'co_authors'
        ]
    
    def validate(self, data):
        """Validate blog post data"""
        if data.get('status') == 'scheduled' and not data.get('scheduled_date'):
            raise serializers.ValidationError({
                'scheduled_date': 'Scheduled date is required for scheduled posts.'
            })
        
        if data.get('audience') == 'specific_class' and not data.get('specific_class'):
            raise serializers.ValidationError({
                'specific_class': 'Specific class is required when audience is set to specific class.'
            })
        
        return data
    
    def create(self, validated_data):
        """Set author to current user"""
        co_authors = validated_data.pop('co_authors', [])
        validated_data['author'] = self.context['request'].user
        post = super().create(validated_data)
        
        if co_authors:
            post.co_authors.set(co_authors)
        
        return post


class BlogPostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating blog posts"""
    class Meta:
        model = BlogPost
        fields = [
            'title', 'content', 'excerpt', 'category', 'content_type', 'tags',
            'subject', 'audience', 'specific_class', 'featured_image', 'attachments',
            'status', 'scheduled_date', 'meta_title', 'meta_description', 'keywords',
            'requires_approval', 'co_authors'
        ]
    
    def validate(self, data):
        """Validate update data"""
        instance = self.instance
        
        if data.get('status') == 'scheduled' and not data.get('scheduled_date'):
            if not instance.scheduled_date:
                raise serializers.ValidationError({
                    'scheduled_date': 'Scheduled date is required for scheduled posts.'
                })
        
        if data.get('audience') == 'specific_class' and not data.get('specific_class'):
            if not instance.specific_class:
                raise serializers.ValidationError({
                    'specific_class': 'Specific class is required when audience is set to specific class.'
                })
        
        return data


class DiscussionThreadListSerializer(serializers.ModelSerializer):
    """Serializer for discussion thread listings"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    created_by_avatar = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    
    # Activity metrics
    is_active = serializers.BooleanField(read_only=True)
    last_activity_relative = serializers.SerializerMethodField()
    participant_names = serializers.SerializerMethodField()
    
    class Meta:
        model = DiscussionThread
        fields = [
            'id', 'title', 'slug', 'description', 'created_by_name', 'created_by_avatar',
            'category', 'category_name', 'discussion_type', 'subject', 'subject_name',
            'classroom', 'classroom_name', 'privacy_level', 'views_count', 'reply_count',
            'participant_count', 'last_activity', 'is_pinned', 'is_locked', 'is_active',
            'last_activity_relative', 'participant_names', 'created_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'views_count', 'reply_count', 'participant_count'
        ]
    
    def get_created_by_avatar(self, obj):
        """Get creator avatar URL"""
        if hasattr(obj.created_by, 'avatar') and obj.created_by.avatar:
            return obj.created_by.avatar.url
        return None
    
    def get_last_activity_relative(self, obj):
        """Get relative time for last activity"""
        from django.utils.timesince import timesince
        return timesince(obj.last_activity) + ' ago'
    
    def get_participant_names(self, obj):
        """Get names of recent participants"""
        participants = obj.posts.values_list('author__first_name', 'author__last_name').distinct()[:3]
        return [f"{first} {last}" for first, last in participants]


class DiscussionThreadDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for discussion threads"""
    created_by_details = CustomUserSerializer(read_only=True, source='created_by')
    moderators_details = UserMinimalSerializer(read_only=True, source='moderators', many=True)
    category_details = BlogCategorySerializer(read_only=True, source='category')
    subject_details = SubjectSerializer(read_only=True, source='subject')
    classroom_details = ClassRoomSerializer(read_only=True, source='classroom')
    invited_users_details = UserMinimalSerializer(read_only=True, source='invited_users', many=True)
    
    # Permissions
    can_participate = serializers.SerializerMethodField()
    can_moderate = serializers.SerializerMethodField()
    is_creator = serializers.SerializerMethodField()
    
    class Meta:
        model = DiscussionThread
        fields = [
            'id', 'title', 'slug', 'description', 'created_by_details', 'moderators_details',
            'category', 'category_details', 'discussion_type', 'subject', 'subject_details',
            'classroom', 'classroom_details', 'privacy_level', 'invited_users_details',
            'views_count', 'reply_count', 'participant_count', 'last_activity',
            'is_pinned', 'is_locked', 'is_anonymous', 'can_participate', 'can_moderate',
            'is_creator', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'views_count', 'reply_count', 'participant_count'
        ]
    
    def get_can_participate(self, obj):
        """Check if current user can participate"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_participate(request.user)
        return False
    
    def get_can_moderate(self, obj):
        """Check if current user can moderate"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return (request.user in obj.moderators.all() or
                    request.user == obj.created_by or
                    request.user.is_staff or
                    request.user.is_superuser)
        return False
    
    def get_is_creator(self, obj):
        """Check if current user is the creator"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user == obj.created_by
        return False


class DiscussionThreadCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating discussion threads"""
    class Meta:
        model = DiscussionThread
        fields = [
            'title', 'description', 'category', 'discussion_type', 'subject',
            'classroom', 'privacy_level', 'invited_users', 'is_anonymous'
        ]
    
    def create(self, validated_data):
        """Set creator to current user"""
        invited_users = validated_data.pop('invited_users', [])
        validated_data['created_by'] = self.context['request'].user
        thread = super().create(validated_data)
        
        if invited_users:
            thread.invited_users.set(invited_users)
        
        return thread


class DiscussionPostSerializer(serializers.ModelSerializer):
    """Serializer for discussion posts"""
    author_details = UserMinimalSerializer(read_only=True, source='author')
    parent_details = serializers.SerializerMethodField()
    discussion_details = DiscussionThreadListSerializer(read_only=True, source='discussion')
    
    # Engagement
    net_votes = serializers.IntegerField(read_only=True)
    user_vote = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    reply_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = DiscussionPost
        fields = [
            'id', 'discussion', 'discussion_details', 'parent', 'parent_details',
            'author_details', 'content', 'content_html', 'attachments', 'code_snippet',
            'is_approved', 'approved_by', 'approved_at', 'upvotes', 'downvotes',
            'net_votes', 'is_answer', 'user_vote', 'can_edit', 'can_delete',
            'reply_count', 'created_at', 'updated_at', 'edited_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'edited_at', 'upvotes', 'downvotes'
        ]
    
    def get_parent_details(self, obj):
        """Get minimal parent post details"""
        if obj.parent:
            return {
                'id': obj.parent.id,
                'author_name': obj.parent.author.get_full_name(),
                'content_preview': obj.parent.content[:100] + '...' if len(obj.parent.content) > 100 else obj.parent.content
            }
        return None
    
    def get_user_vote(self, obj):
        """Get current user's vote on this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(user=request.user).first()
            if vote:
                return vote.vote_type
        return None
    
    def get_can_edit(self, obj):
        """Check if current user can edit this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return (obj.author == request.user or
                    request.user in obj.discussion.moderators.all() or
                    request.user.is_staff or
                    request.user.is_superuser)
        return False
    
    def get_can_delete(self, obj):
        """Check if current user can delete this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return (obj.author == request.user or
                    request.user in obj.discussion.moderators.all() or
                    request.user.is_staff or
                    request.user.is_superuser)
        return False


class DiscussionPostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating discussion posts"""
    class Meta:
        model = DiscussionPost
        fields = ['discussion', 'parent', 'content', 'code_snippet', 'attachments']
    
    def validate(self, data):
        """Validate discussion post data"""
        discussion = data.get('discussion')
        parent = data.get('parent')
        
        if discussion and discussion.is_locked:
            raise serializers.ValidationError({
                'discussion': 'This discussion is locked and cannot accept new posts.'
            })
        
        if parent and parent.discussion != discussion:
            raise serializers.ValidationError({
                'parent': 'Parent post must belong to the same discussion.'
            })
        
        return data
    
    def create(self, validated_data):
        """Set author to current user"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class BlogCommentSerializer(serializers.ModelSerializer):
    """Serializer for blog comments"""
    author_details = UserMinimalSerializer(read_only=True, source='author')
    post_details = BlogPostListSerializer(read_only=True, source='post')
    parent_details = serializers.SerializerMethodField()
    
    # Engagement
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    reply_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = BlogComment
        fields = [
            'id', 'post', 'post_details', 'parent', 'parent_details',
            'author_details', 'content', 'is_approved', 'approved_by',
            'approved_at', 'likes_count', 'can_edit', 'can_delete',
            'reply_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'likes_count'
        ]
    
    def get_parent_details(self, obj):
        """Get minimal parent comment details"""
        if obj.parent:
            return {
                'id': obj.parent.id,
                'author_name': obj.parent.author.get_full_name(),
                'content_preview': obj.parent.content[:50] + '...' if len(obj.parent.content) > 50 else obj.parent.content
            }
        return None
    
    def get_can_edit(self, obj):
        """Check if current user can edit this comment"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return (obj.author == request.user or
                    request.user.is_staff or
                    request.user.is_superuser)
        return False
    
    def get_can_delete(self, obj):
        """Check if current user can delete this comment"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return (obj.author == request.user or
                    request.user.is_staff or
                    request.user.is_superuser)
        return False


class BlogCommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating blog comments"""
    class Meta:
        model = BlogComment
        fields = ['post', 'parent', 'content']
    
    def create(self, validated_data):
        """Set author to current user"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class PostLikeSerializer(serializers.ModelSerializer):
    """Serializer for post likes"""
    user_details = UserMinimalSerializer(read_only=True, source='user')
    post_details = BlogPostListSerializer(read_only=True, source='post')
    
    class Meta:
        model = PostLike
        fields = ['id', 'user', 'user_details', 'post', 'post_details', 'created_at']
        read_only_fields = ['created_at']


class DiscussionVoteSerializer(serializers.ModelSerializer):
    """Serializer for discussion votes"""
    user_details = UserMinimalSerializer(read_only=True, source='user')
    post_details = DiscussionPostSerializer(read_only=True, source='post')
    
    class Meta:
        model = DiscussionVote
        fields = ['id', 'user', 'user_details', 'post', 'post_details', 'vote_type', 'created_at']
        read_only_fields = ['created_at']


class StudyGroupSerializer(serializers.ModelSerializer):
    """Serializer for study groups"""
    creator_details = CustomUserSerializer(read_only=True, source='creator')
    subject_details = SubjectSerializer(read_only=True, source='subject')
    classroom_details = ClassRoomSerializer(read_only=True, source='classroom')
    academic_year_details = AcademicYearSerializer(read_only=True, source='academic_year')
    moderators_details = UserMinimalSerializer(read_only=True, source='moderators', many=True)
    
    # Membership info
    member_count = serializers.IntegerField(read_only=True)
    is_member = serializers.SerializerMethodField()
    is_moderator = serializers.SerializerMethodField()
    is_creator = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()
    
    class Meta:
        model = StudyGroup
        fields = [
            'id', 'name', 'slug', 'description', 'creator_details', 'subject_details',
            'classroom_details', 'academic_year_details', 'moderators_details',
            'max_members', 'is_public', 'join_code', 'last_activity', 'meeting_schedule',
            'member_count', 'is_member', 'is_moderator', 'is_creator', 'can_join',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_activity']
    
    def get_is_member(self, obj):
        """Check if current user is a member"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists()
        return False
    
    def get_is_moderator(self, obj):
        """Check if current user is a moderator"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.moderators.filter(id=request.user.id).exists()
        return False
    
    def get_is_creator(self, obj):
        """Check if current user is the creator"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user == obj.creator
        return False
    
    def get_can_join(self, obj):
        """Check if current user can join this group"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if obj.is_full:
                return False
            if not obj.is_public and not self.get_is_member(obj):
                return False
            return True
        return False


class StudyGroupCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating study groups"""
    class Meta:
        model = StudyGroup
        fields = [
            'name', 'description', 'subject', 'classroom', 'academic_year',
            'max_members', 'is_public', 'meeting_schedule'
        ]
    
    def create(self, validated_data):
        """Set creator to current user and generate join code"""
        validated_data['creator'] = self.context['request'].user
        group = super().create(validated_data)
        group.generate_join_code()
        return group


class StudyGroupMembershipSerializer(serializers.ModelSerializer):
    """Serializer for study group memberships"""
    user_details = CustomUserSerializer(read_only=True, source='user')
    group_details = StudyGroupSerializer(read_only=True, source='group')
    
    class Meta:
        model = StudyGroupMembership
        fields = [
            'id', 'group', 'group_details', 'user', 'user_details', 'role',
            'joined_at', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['joined_at', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    user_details = UserMinimalSerializer(read_only=True, source='user')
    content_object = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user_details', 'notification_type', 'title', 'message',
            'content_type', 'object_id', 'content_object', 'is_read',
            'read_at', 'time_ago', 'created_at'
        ]
        read_only_fields = ['created_at', 'read_at']
    
    def get_content_object(self, obj):
        """Get the related object for this notification"""
        if obj.content_type and obj.object_id:
            try:
                model_class = obj.content_type.model_class()
                instance = model_class.objects.get(pk=obj.object_id)
                
                # Return appropriate serializer based on content type
                if hasattr(instance, 'get_absolute_url'):
                    return {
                        'id': instance.id,
                        'title': getattr(instance, 'title', str(instance)),
                        'url': instance.get_absolute_url()
                    }
            except:
                pass
        return None
    
    def get_time_ago(self, obj):
        """Get relative time for notification"""
        from django.utils.timesince import timesince
        return timesince(obj.created_at) + ' ago'


# Dashboard and Analytics Serializers
class BlogDashboardSerializer(serializers.Serializer):
    """Serializer for blog dashboard data"""
    total_posts = serializers.IntegerField()
    total_discussions = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    recent_posts = BlogPostListSerializer(many=True)
    active_discussions = DiscussionThreadListSerializer(many=True)
    popular_categories = BlogCategorySerializer(many=True)


class UserBlogActivitySerializer(serializers.Serializer):
    """Serializer for user blog activity"""
    posts_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()
    discussions_created = serializers.IntegerField()
    discussion_posts_count = serializers.IntegerField()
    likes_given = serializers.IntegerField()
    recent_activity = serializers.JSONField()


class BlogAnalyticsSerializer(serializers.Serializer):
    """Serializer for blog analytics"""
    posts_published = serializers.IntegerField()
    posts_by_type = serializers.JSONField()
    engagement_metrics = serializers.JSONField()
    top_posts = BlogPostListSerializer(many=True)
    active_users = serializers.JSONField()


# Utility Serializers
class ContentSearchSerializer(serializers.Serializer):
    """Serializer for search results"""
    id = serializers.UUIDField()
    title = serializers.CharField()
    content = serializers.CharField()
    content_type = serializers.CharField()
    model_name = serializers.CharField()
    created_at = serializers.DateTimeField()
    author_name = serializers.CharField()
    url = serializers.CharField()


class MentionUserSerializer(serializers.Serializer):
    """Serializer for user mentions"""
    id = serializers.UUIDField()
    name = serializers.CharField()
    username = serializers.CharField()
    avatar = serializers.CharField(allow_null=True)
    type = serializers.CharField()  # student, teacher, etc.