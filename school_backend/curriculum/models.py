#curriculum/models.py

from django.db import models
from django.conf import settings
import uuid

class Curriculum(models.Model):
    CURRICULUM_TYPES = (
        ('cbc', 'CBC - Competency Based Curriculum'),
        ('icse', 'ICSE - Indian Certificate of Secondary Education'),
        ('american', 'American Curriculum'),
        ('igcse', 'IGCSE - International General Certificate'),
        ('combined', 'Combined Curriculum'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, choices=CURRICULUM_TYPES, unique=True)
    full_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # Curriculum details
    country_origin = models.CharField(max_length=100, default='Kenya')
    implementing_body = models.CharField(max_length=200, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Academic structure
    grade_levels = models.JSONField(default=list, help_text="Supported grade levels")
    assessment_methods = models.JSONField(default=list, help_text="Primary assessment methods")
    key_features = models.JSONField(default=list, help_text="Key features of this curriculum")
    
    # Status
    is_active = models.BooleanField(default=True)
    implementation_date = models.DateField(null=True, blank=True)
    
    # Coordinator
    coordinator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, blank=True, limit_choices_to={'role': 'curriculum_coordinator'})
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Curriculum"
        verbose_name_plural = "Curricula"
        ordering = ['name']

    def __str__(self):
        return self.get_name_display()

class CBCStrand(models.Model):
    """CBC Competency Areas"""
    LEARNING_AREAS = (
        ('mathematical', 'Mathematical'),
        ('language', 'Language'),
        ('environmental', 'Environmental'),
        ('creative', 'Creative'),
        ('psychomotor', 'Psychomotor'),
        ('religious', 'Religious Education'),
        ('pastoral', 'Pastoral Instruction'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, limit_choices_to={'name': 'cbc'})
    learning_area = models.CharField(max_length=20, choices=LEARNING_AREAS)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Grade levels
    grade_levels = models.JSONField(default=list, help_text="Grade levels this strand applies to")
    
    # Core competencies
    core_competencies = models.JSONField(default=list, help_text="Core competencies covered")
    learning_outcomes = models.JSONField(default=list, help_text="Overall learning outcomes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CBC Strand"
        verbose_name_plural = "CBC Strands"
        unique_together = ['learning_area', 'name']
        ordering = ['learning_area', 'code']

    def __str__(self):
        return f"{self.code} - {self.name}"

class CBCSubStrand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    strand = models.ForeignKey(CBCStrand, on_delete=models.CASCADE, related_name='sub_strands')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    
    # Specific details
    specific_learning_outcomes = models.JSONField(default=list)
    key_inquiry_questions = models.JSONField(default=list)
    learning_resources = models.JSONField(default=list)
    suggested_activities = models.JSONField(default=list)
    
    # Assessment
    assessment_methods = models.JSONField(default=list)
    assessment_rubrics = models.JSONField(default=list, help_text="Assessment criteria and rubrics")
    
    # Timeline
    suggested_weeks = models.IntegerField(default=2, help_text="Suggested weeks to cover this sub-strand")
    priority_level = models.CharField(max_length=20, choices=(
        ('core', 'Core'),
        ('supplementary', 'Supplementary'),
        ('enrichment', 'Enrichment'),
    ), default='core')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CBC Sub-Strand"
        verbose_name_plural = "CBC Sub-Strands"
        unique_together = ['strand', 'code']
        ordering = ['strand', 'code']

    def __str__(self):
        return f"{self.code} - {self.name}"

class ICSESubject(models.Model):
    """ICSE Subject Specifications"""
    SUBJECT_GROUPS = (
        ('group1', 'Group I - Compulsory'),
        ('group2', 'Group II - Any Two'),
        ('group3', 'Group III - Any One'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, limit_choices_to={'name': 'icse'})
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    subject_group = models.CharField(max_length=10, choices=SUBJECT_GROUPS)
    description = models.TextField(blank=True, null=True)
    
    # Subject details
    is_compulsory = models.BooleanField(default=False)
    has_practical = models.BooleanField(default=False)
    theory_marks = models.IntegerField(default=80)
    practical_marks = models.IntegerField(default=20)
    total_marks = models.IntegerField(default=100)
    
    # Syllabus information
    syllabus_content = models.JSONField(default=list, help_text="Detailed syllabus content")
    prescribed_books = models.JSONField(default=list, help_text="Recommended textbooks")
    reference_books = models.JSONField(default=list, help_text="Reference materials")
    
    # Grade levels
    available_grades = models.JSONField(default=list, help_text="Grades where this subject is offered")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ICSE Subject"
        verbose_name_plural = "ICSE Subjects"
        ordering = ['subject_group', 'name']

    def __str__(self):
        return f"{self.code} - {self.name}"

class AmericanStandard(models.Model):
    """Common Core State Standards and other American standards"""
    DOMAIN_CHOICES = (
        ('ela', 'English Language Arts'),
        ('math', 'Mathematics'),
        ('science', 'Science'),
        ('social_studies', 'Social Studies'),
        ('arts', 'Arts'),
        ('physical_education', 'Physical Education'),
        ('world_languages', 'World Languages'),
    )

    GRADE_LEVEL_CHOICES = (
        ('k', 'Kindergarten'),
        ('1', 'Grade 1'),
        ('2', 'Grade 2'),
        ('3', 'Grade 3'),
        ('4', 'Grade 4'),
        ('5', 'Grade 5'),
        ('6', 'Grade 6'),
        ('7', 'Grade 7'),
        ('8', 'Grade 8'),
        ('9-10', 'Grades 9-10'),
        ('11-12', 'Grades 11-12'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, limit_choices_to={'name': 'american'})
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    grade_level = models.CharField(max_length=10, choices=GRADE_LEVEL_CHOICES)
    standard_code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    
    # Standard details
    cluster = models.CharField(max_length=100, blank=True, null=True, help_text="Standard cluster/group")
    category = models.CharField(max_length=100, blank=True, null=True)
    complexity_level = models.CharField(max_length=20, choices=(
        ('basic', 'Basic'),
        ('proficient', 'Proficient'),
        ('advanced', 'Advanced'),
    ), default='proficient')
    
    # Learning objectives
    learning_objectives = models.JSONField(default=list)
    essential_questions = models.JSONField(default=list)
    vocabulary = models.JSONField(default=list, help_text="Key vocabulary terms")
    
    # Assessment
    performance_indicators = models.JSONField(default=list)
    assessment_ideas = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "American Standard"
        verbose_name_plural = "American Standards"
        ordering = ['domain', 'grade_level', 'standard_code']

    def __str__(self):
        return f"{self.standard_code} - {self.description[:50]}..."

class AmericanCourse(models.Model):
    """American Curriculum Course Offerings"""
    COURSE_TYPES = (
        ('core', 'Core Course'),
        ('elective', 'Elective Course'),
        ('honors', 'Honors Course'),
        ('ap', 'Advanced Placement'),
        ('dual_enrollment', 'Dual Enrollment'),
    )

    CREDIT_TYPES = (
        ('english', 'English'),
        ('math', 'Mathematics'),
        ('science', 'Science'),
        ('social_studies', 'Social Studies'),
        ('foreign_language', 'Foreign Language'),
        ('arts', 'Arts'),
        ('physical_education', 'Physical Education'),
        ('elective', 'Elective'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, limit_choices_to={'name': 'american'})
    name = models.CharField(max_length=100)
    course_code = models.CharField(max_length=20, unique=True)
    course_type = models.CharField(max_length=20, choices=COURSE_TYPES)
    credit_type = models.CharField(max_length=20, choices=CREDIT_TYPES)
    
    # Course details
    description = models.TextField(blank=True, null=True)
    credits = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    grade_levels = models.JSONField(default=list, help_text="Grade levels this course is offered")
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True)
    
    # Syllabus
    course_objectives = models.JSONField(default=list)
    units_of_study = models.JSONField(default=list, help_text="Course units and topics")
    learning_outcomes = models.JSONField(default=list)
    assessment_methods = models.JSONField(default=list)
    
    # Resources
    required_materials = models.JSONField(default=list)
    recommended_texts = models.JSONField(default=list)
    online_resources = models.JSONField(default=list)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "American Course"
        verbose_name_plural = "American Courses"
        ordering = ['credit_type', 'course_type', 'name']

    def __str__(self):
        return f"{self.course_code} - {self.name}"

class CurriculumMapping(models.Model):
    """Mapping between different curricula for integrated teaching"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, related_name='source_mappings')
    target_curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, related_name='target_mappings')
    
    # Mapping details
    source_component = models.CharField(max_length=100, help_text="Component from source curriculum")
    source_identifier = models.CharField(max_length=100, help_text="Identifier in source curriculum")
    target_component = models.CharField(max_length=100, help_text="Corresponding component in target curriculum")
    target_identifier = models.CharField(max_length=100, help_text="Identifier in target curriculum")
    
    # Relationship
    mapping_strength = models.CharField(max_length=20, choices=(
        ('exact', 'Exact Match'),
        ('close', 'Close Match'),
        ('partial', 'Partial Match'),
        ('supplementary', 'Supplementary'),
    ), default='close')
    
    # Additional information
    notes = models.TextField(blank=True, null=True)
    confidence_level = models.IntegerField(default=80, help_text="Confidence in mapping (0-100)")
    
    # Status
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Curriculum Mapping"
        verbose_name_plural = "Curriculum Mappings"
        unique_together = ['source_curriculum', 'target_curriculum', 'source_identifier', 'target_identifier']
        ordering = ['source_curriculum', 'target_curriculum']

    def __str__(self):
        return f"{self.source_curriculum} → {self.target_curriculum}: {self.source_identifier}"

class CurriculumImplementation(models.Model):
    """Track curriculum implementation across classes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    class_enrolled = models.ForeignKey('academics.Class', on_delete=models.CASCADE)
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.CASCADE)
    
    # Implementation details
    implementation_date = models.DateField()
    is_primary = models.BooleanField(default=True, help_text="Whether this is the primary curriculum for the class")
    implementation_status = models.CharField(max_length=20, choices=(
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('suspended', 'Suspended'),
    ), default='planned')
    
    # Resources
    textbooks_used = models.JSONField(default=list)
    digital_resources = models.JSONField(default=list)
    teaching_aids = models.JSONField(default=list)
    
    # Assessment approach
    assessment_strategy = models.JSONField(default=list)
    grading_system_used = models.ForeignKey('grading.GradingScale', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Teacher information
    lead_teacher = models.ForeignKey('teachers.TeacherProfile', on_delete=models.SET_NULL, null=True, blank=True)
    supporting_teachers = models.ManyToManyField('teachers.TeacherProfile', related_name='supporting_curricula', blank=True)
    
    # Progress tracking
    progress_notes = models.TextField(blank=True, null=True)
    challenges_faced = models.JSONField(default=list)
    success_stories = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Curriculum Implementation"
        verbose_name_plural = "Curriculum Implementations"
        unique_together = ['curriculum', 'class_enrolled', 'academic_year']
        ordering = ['academic_year', 'class_enrolled']

    def __str__(self):
        return f"{self.curriculum} - {self.class_enrolled} - {self.academic_year}"

class LearningObjective(models.Model):
    """Cross-curricular learning objectives"""
    BLOOM_LEVELS = (
        ('remember', 'Remember'),
        ('understand', 'Understand'),
        ('apply', 'Apply'),
        ('analyze', 'Analyze'),
        ('evaluate', 'Evaluate'),
        ('create', 'Create'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, null=True, blank=True)
    
    # Objective details
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    bloom_level = models.CharField(max_length=20, choices=BLOOM_LEVELS)
    grade_levels = models.JSONField(default=list, help_text="Grade levels this objective applies to")
    
    # Assessment criteria
    success_criteria = models.JSONField(default=list)
    assessment_methods = models.JSONField(default=list)
    differentiation_strategies = models.JSONField(default=list, help_text="Strategies for different learners")
    
    # Cross-curricular links
    cross_curricular_links = models.JSONField(default=list)
    real_world_connections = models.JSONField(default=list)
    
    # Resources
    teaching_resources = models.JSONField(default=list)
    learning_activities = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Learning Objective"
        verbose_name_plural = "Learning Objectives"
        ordering = ['curriculum', 'code']

    def __str__(self):
        return f"{self.code} - {self.description[:50]}..."

class ResourceLibrary(models.Model):
    """Central repository for curriculum resources"""
    RESOURCE_TYPES = (
        ('textbook', 'Textbook'),
        ('workbook', 'Workbook'),
        ('digital', 'Digital Resource'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('worksheet', 'Worksheet'),
        ('lesson_plan', 'Lesson Plan'),
        ('assessment', 'Assessment Tool'),
        ('other', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Resource details
    author = models.CharField(max_length=200, blank=True, null=True)
    publisher = models.CharField(max_length=200, blank=True, null=True)
    publication_year = models.IntegerField(null=True, blank=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    
    # Access information
    resource_file = models.FileField(upload_to='curriculum/resources/', blank=True, null=True)
    resource_url = models.URLField(blank=True, null=True)
    access_notes = models.TextField(blank=True, null=True)
    
    # Curriculum alignment
    grade_levels = models.JSONField(default=list)
    subjects = models.JSONField(default=list)
    topics = models.JSONField(default=list)
    learning_objectives = models.ManyToManyField(LearningObjective, blank=True)
    
    # Usage tracking
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Resource Library"
        verbose_name_plural = "Resource Library"
        ordering = ['curriculum', 'resource_type', 'title']

    def __str__(self):
        return f"{self.title} - {self.get_resource_type_display()}"

class ProfessionalDevelopment(models.Model):
    """Curriculum-related professional development"""
    DEVELOPMENT_TYPES = (
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('conference', 'Conference'),
        ('training', 'Training Session'),
        ('online_course', 'Online Course'),
        ('peer_learning', 'Peer Learning'),
        ('other', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    development_type = models.CharField(max_length=20, choices=DEVELOPMENT_TYPES)
    
    # Event details
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=200, blank=True, null=True)
    facilitator = models.CharField(max_length=200, blank=True, null=True)
    
    # Target audience
    target_teachers = models.ManyToManyField('teachers.TeacherProfile', blank=True)
    target_grades = models.JSONField(default=list)
    target_subjects = models.JSONField(default=list)
    
    # Resources
    materials = models.JSONField(default=list)
    resource_files = models.FileField(upload_to='curriculum/pd_resources/', blank=True, null=True)
    
    # Outcomes
    learning_objectives = models.JSONField(default=list)
    expected_outcomes = models.JSONField(default=list)
    
    # Status
    is_completed = models.BooleanField(default=False)
    attendance_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Professional Development"
        verbose_name_plural = "Professional Development"
        ordering = ['-start_date', 'title']

    def __str__(self):
        return f"{self.title} - {self.curriculum}"