# teachers/resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from .models import TeacherDocument, TeacherProfile, Department
from accounts.models import User


class TeacherProfileResource(resources.ModelResource):
    """Django-import-export resource for TeacherProfile"""
    
    # Define foreign key fields with string references
    teacher = fields.Field(
        column_name='teacher',
        attribute='teacher',
        widget=ForeignKeyWidget('accounts.User', 'email')  # String reference
    )
    
    department = fields.Field(
        column_name='department',
        attribute='department',
        widget=ForeignKeyWidget('teachers.Department', 'name')  # String reference
    )
    
    # Define many-to-many fields with string references
    subjects = fields.Field(
        column_name='subjects',
        attribute='subjects',
        widget=ManyToManyWidget('academics.Subject', field='name', separator=',')  # String reference
    )
    
    classes = fields.Field(
        column_name='classes',
        attribute='classes',
        widget=ManyToManyWidget('academics.Class', field='name', separator=',')  # String reference
    )
    
    # Virtual fields for calculated values
    tsc_compliant = fields.Field(
        column_name='tsc_compliant',
        attribute='tsc_compliant',
        readonly=True
    )
    
    workload_percentage = fields.Field(
        column_name='workload_percentage',
        attribute='workload_percentage',
        readonly=True
    )
    
    class Meta:
        model = TeacherProfile
        import_id_fields = ['tsc_number']
        exclude = ('id', 'created_at', 'updated_at', 'is_active', 'achievements')
        export_order = (
            'tsc_number', 'teacher', 'teacher__id_number', 'teacher__email', 
            'teacher__phone_number', 'employment_type', 'employment_status', 
            'teaching_level', 'tsc_status', 'highest_qualification', 'department',
            'subjects', 'classes', 'tsc_compliant', 'cbc_trained', 'workload_percentage'
        )
        skip_unchanged = True
        report_skipped = True
        use_bulk = True
    
    def dehydrate_teacher(self, teacher_profile):
        """Custom export for teacher field"""
        return teacher_profile.full_name
    
    def dehydrate_department(self, teacher_profile):
        """Custom export for department"""
        return str(teacher_profile.department) if teacher_profile.department else ''
    
    def dehydrate_tsc_compliant(self, teacher_profile):
        """Export TSC compliance status"""
        return 'Yes' if teacher_profile.tsc_compliant else 'No'
    
    def dehydrate_cbc_trained(self, teacher_profile):
        """Export CBC training status"""
        return 'Yes' if teacher_profile.cbc_trained else 'No'
    
    def dehydrate_workload_percentage(self, teacher_profile):
        """Export workload percentage"""
        if teacher_profile.weekly_periods:
            utilization = (teacher_profile.weekly_periods / 45 * 100) if teacher_profile.weekly_periods else 0
            return f"{utilization:.1f}%"
        return "0%"
    
    def before_import_row(self, row, **kwargs):
        """Pre-process import row"""
        # Ensure TSC number format
        tsc_number = row.get('tsc_number', '')
        if tsc_number and not tsc_number.startswith('TSC/'):
            row['tsc_number'] = f"TSC/{tsc_number}"
        
        # Convert employment type
        emp_type = row.get('employment_type', '').lower()
        if 'permanent' in emp_type and 'tsc' in emp_type:
            row['employment_type'] = 'permanent_tsc'
        elif 'contract' in emp_type and 'tsc' in emp_type:
            row['employment_type'] = 'contract_tsc'
        elif 'intern' in emp_type:
            row['employment_type'] = 'intern'
        elif 'bom' in emp_type:
            row['employment_type'] = 'bom'
        elif 'pta' in emp_type:
            row['employment_type'] = 'pta'
        elif 'volunteer' in emp_type:
            row['employment_type'] = 'volunteer'
        elif 'part-time' in emp_type or 'part_time' in emp_type:
            row['employment_type'] = 'part_time'
        elif 'substitute' in emp_type:
            row['employment_type'] = 'substitute'
        
        # Convert employment status
        emp_status = row.get('employment_status', '').lower()
        if 'active' in emp_status:
            row['employment_status'] = 'active'
        elif 'leave' in emp_status:
            if 'study' in emp_status:
                row['employment_status'] = 'study_leave'
            elif 'maternity' in emp_status:
                row['employment_status'] = 'maternity_leave'
            elif 'paternity' in emp_status:
                row['employment_status'] = 'paternity_leave'
            elif 'sick' in emp_status:
                row['employment_status'] = 'sick_leave'
            else:
                row['employment_status'] = 'on_leave'
        elif 'suspended' in emp_status:
            row['employment_status'] = 'suspended'
        elif 'terminated' in emp_status:
            row['employment_status'] = 'terminated'
        elif 'retired' in emp_status:
            row['employment_status'] = 'retired'
        elif 'resigned' in emp_status:
            row['employment_status'] = 'resigned'
        elif 'transferred' in emp_status:
            row['employment_status'] = 'transferred'
        elif 'deceased' in emp_status:
            row['employment_status'] = 'deceased'
        
        # Convert teaching level
        teaching_level = row.get('teaching_level', '').lower()
        if 'junior' in teaching_level and 'secondary' in teaching_level:
            row['teaching_level'] = 'junior_secondary'
        elif 'senior' in teaching_level and 'secondary' in teaching_level:
            row['teaching_level'] = 'senior_secondary'
        elif 'primary' in teaching_level:
            row['teaching_level'] = 'primary'
        elif 'ecde' in teaching_level or 'early' in teaching_level:
            row['teaching_level'] = 'ecde'
        elif 'special' in teaching_level:
            row['teaching_level'] = 'special_needs'
        elif 'technical' in teaching_level or 'tvet' in teaching_level:
            row['teaching_level'] = 'technical'
    
    def after_import_row(self, row, row_result, **kwargs):
        """Post-process import row"""
        if row_result.import_type == resources.RowResult.IMPORT_TYPE_NEW:
            # Send welcome email for new teachers
            # You can implement this later
            pass
        elif row_result.import_type == resources.RowResult.IMPORT_TYPE_UPDATE:
            # Log update activity
            # You can implement this later
            pass
    
    def before_save_instance(self, instance, using_transactions, dry_run):
        """Custom logic before saving instance"""
        if not dry_run:
            # Ensure teacher's user account is properly linked
            if instance.teacher and not instance.teacher.staff_id:
                instance.teacher.staff_id = instance.tsc_number
                instance.teacher.save()


class DepartmentResource(resources.ModelResource):
    """Django-import-export resource for Department"""
    
    hod = fields.Field(
        column_name='hod',
        attribute='hod',
        widget=ForeignKeyWidget('teachers.TeacherProfile', 'tsc_number')  # String reference
    )
    
    academic_year = fields.Field(
        column_name='academic_year',
        attribute='academic_year',
        widget=ForeignKeyWidget('academics.AcademicYear', 'name')  # String reference
    )
    
    # Virtual fields
    teacher_count = fields.Field(
        column_name='teacher_count',
        attribute='teacher_count',
        readonly=True
    )
    
    student_count = fields.Field(
        column_name='student_count',
        attribute='student_count',
        readonly=True
    )
    
    class Meta:
        model = Department
        import_id_fields = ['code']
        exclude = ('id', 'created_at', 'updated_at', 'is_active')
        export_order = (
            'code', 'name', 'tsc_category', 'cbc_pathway', 'hod',
            'teacher_count', 'student_count', 'description'
        )
    
    def dehydrate_hod(self, department):
        """Custom export for HOD field"""
        if department.hod:
            return department.hod.full_name
        return ''
    
    def dehydrate_teacher_count(self, department):
        """Export teacher count"""
        return department.teacher_count
    
    def dehydrate_student_count(self, department):
        """Export student count"""
        return department.student_count
    
    def before_import_row(self, row, **kwargs):
        """Pre-process import row"""
        # Ensure department code is uppercase
        code = row.get('code', '')
        if code:
            row['code'] = code.upper()
        
        # Set default TSC category if not provided
        if not row.get('tsc_category'):
            row['tsc_category'] = 'junior_secondary'
    
    def after_import_instance(self, instance, new, **kwargs):
        """Post-process after instance is created"""
        # You can add additional logic here if needed
        pass


class TeacherDocumentResource(resources.ModelResource):
    """Django-import-export resource for TeacherDocument"""
    
    teacher = fields.Field(
        column_name='teacher',
        attribute='teacher',
        widget=ForeignKeyWidget('teachers.TeacherProfile', 'tsc_number')  # String reference
    )
    
    verified_by = fields.Field(
        column_name='verified_by',
        attribute='verified_by',
        widget=ForeignKeyWidget('accounts.User', 'email')  # String reference
    )
    
    # Virtual fields
    file_url = fields.Field(
        column_name='file_url',
        attribute='file_url',
        readonly=True
    )
    
    days_to_expiry = fields.Field(
        column_name='days_to_expiry',
        attribute='days_to_expiry',
        readonly=True
    )
    
    class Meta:
        model = TeacherDocument
        import_id_fields = ['id']
        exclude = ('id', 'created_at', 'updated_at', 'is_active')
        export_order = (
            'teacher', 'document_type', 'title', 'status', 'expiry_date',
            'days_to_expiry', 'file_url', 'verified_by', 'verification_date'
        )
    
    def dehydrate_teacher(self, document):
        """Custom export for teacher field"""
        return document.teacher.full_name
    
    def dehydrate_document_file(self, document):
        """Export document file path"""
        if document.document_file:
            return document.document_file.url
        return ''
    
    def dehydrate_file_url(self, document):
        """Export document file URL"""
        return document.file_url or ''
    
    def dehydrate_days_to_expiry(self, document):
        """Export days until expiry"""
        return document.days_to_expiry if document.days_to_expiry else ''
    
    def before_import_row(self, row, **kwargs):
        """Pre-process import row"""
        # Ensure document type is valid
        doc_type = row.get('document_type', '').lower()
        
        # Map common document type names to model choices
        type_mapping = {
            'tsc': 'tsc_certificate',
            'good conduct': 'good_conduct',
            'certificate of good conduct': 'good_conduct',
            'academic': 'academic_certificate',
            'transcript': 'transcript',
            'cbc': 'cbc_certificate',
            'tpd': 'tpd_certificate',
            'id': 'id_copy',
            'national id': 'id_copy',
            'passport': 'id_copy',
            'kra': 'kra_pin',
            'nssf': 'nssf_card',
            'nhif': 'nhif_card',
            'appointment': 'appointment_letter',
            'confirmation': 'confirmation_letter',
            'promotion': 'promotion_letter',
            'transfer': 'transfer_letter',
            'medical': 'medical_report',
            'birth': 'birth_certificate',
            'marriage': 'marriage_certificate',
            'police': 'police_clearance',
            'cv': 'cv_resume',
            'resume': 'cv_resume',
            'reference': 'reference_letter',
            'appraisal': 'performance_appraisal',
            'performance': 'performance_appraisal',
            'leave': 'leave_document',
            'disciplinary': 'disciplinary',
        }
        
        for key, value in type_mapping.items():
            if key in doc_type:
                row['document_type'] = value
                break
    
    def after_import_instance(self, instance, new, **kwargs):
        """Post-process after instance is created"""
        # Auto-verify documents if they are from a trusted source
        # This is just an example - customize based on your needs
        trusted_doc_types = ['tsc_certificate', 'good_conduct', 'id_copy']
        if new and instance.document_type in trusted_doc_types:
            instance.status = 'verified'
            # You would typically set verified_by to the importing user
            # instance.verified_by = kwargs.get('user')


# Additional resources for other models if needed
class TeacherQualificationResource(resources.ModelResource):
    """Resource for TeacherQualification model"""
    
    teacher = fields.Field(
        column_name='teacher',
        attribute='teacher',
        widget=ForeignKeyWidget('teachers.TeacherProfile', 'tsc_number')
    )
    
    class Meta:
        model = 'teachers.TeacherQualification'  # String reference
        fields = ('teacher', 'qualification_type', 'title', 'institution', 
                  'field_of_study', 'start_date', 'end_date', 'is_completed')
    
    def dehydrate_teacher(self, qualification):
        """Custom export for teacher field"""
        return qualification.teacher.full_name


class TeacherTrainingResource(resources.ModelResource):
    """Resource for TeacherTraining model"""
    
    teacher = fields.Field(
        column_name='teacher',
        attribute='teacher',
        widget=ForeignKeyWidget('teachers.TeacherProfile', 'tsc_number')
    )
    
    class Meta:
        model = 'teachers.TeacherTraining'  # String reference
        fields = ('teacher', 'training_type', 'title', 'organizer', 
                  'start_date', 'end_date', 'status', 'is_certified')
    
    def dehydrate_teacher(self, training):
        """Custom export for teacher field"""
        return training.teacher.full_name


class TeacherLeaveResource(resources.ModelResource):
    """Resource for TeacherLeave model"""
    
    teacher = fields.Field(
        column_name='teacher',
        attribute='teacher',
        widget=ForeignKeyWidget('teachers.TeacherProfile', 'tsc_number')
    )
    
    cover_teacher = fields.Field(
        column_name='cover_teacher',
        attribute='cover_teacher',
        widget=ForeignKeyWidget('teachers.TeacherProfile', 'tsc_number')
    )
    
    class Meta:
        model = 'teachers.TeacherLeave'  # String reference
        fields = ('teacher', 'leave_type', 'start_date', 'end_date', 
                  'days_requested', 'status', 'cover_teacher')
    
    def dehydrate_teacher(self, leave):
        """Custom export for teacher field"""
        return leave.teacher.full_name
    
    def dehydrate_cover_teacher(self, leave):
        """Custom export for cover teacher field"""
        return leave.cover_teacher.full_name if leave.cover_teacher else ''