// src/pages/Auth/CompleteProfile.jsx - UPDATED WITH PROFILE COMPLETION TRACKING
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import authAPI from '../../services/authAPI';
import api from '../../services/api';
import '../../assets/css/CompleteProfile.css';

function CompleteProfile() {
  const { 
    currentUser, 
    updateUser, 
    isAuthenticated, 
    getDashboardUrl,
    markProfileCompleted,
    hasCompletedProfile,
    updateProfile
  } = useAuth();
  
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [studentSearch, setStudentSearch] = useState('');
  const [foundStudents, setFoundStudents] = useState([]);
  const [selectedStudents, setSelectedStudents] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  
  // Get user data and role
  const user = currentUser?.user || currentUser;
  const currentRole = user?.role || '';
  const userName = user?.first_name || user?.email || 'User';
  
  // Define role-specific form configurations based on Django model requirements
  const ROLE_CONFIGS = {
    student: {
      title: 'Student Profile Completion',
      description: 'Please complete your student profile to access the student portal',
      requiredFields: ['first_name', 'last_name', 'phone_number', 'date_of_birth', 'grade_level', 'current_class'],
      sections: [
        {
          title: 'Personal Information',
          fields: [
            { name: 'first_name', label: 'First Name', type: 'text', required: true },
            { name: 'last_name', label: 'Last Name', type: 'text', required: true },
            { name: 'middle_name', label: 'Middle Name', type: 'text', required: false },
            { name: 'date_of_birth', label: 'Date of Birth', type: 'date', required: true },
            { name: 'gender', label: 'Gender', type: 'select', options: [
              { value: '', label: 'Select Gender' },
              { value: 'male', label: 'Male' },
              { value: 'female', label: 'Female' },
              { value: 'other', label: 'Other' },
              { value: 'prefer_not_to_say', label: 'Prefer not to say' }
            ], required: false },
            { name: 'phone_number', label: 'Phone Number', type: 'tel', required: true, 
              placeholder: '+2547XXXXXXXX' },
            { name: 'alternative_phone', label: 'Alternative Phone', type: 'tel', required: false },
            { name: 'address', label: 'Address', type: 'textarea', required: false },
            { name: 'city', label: 'City', type: 'text', required: false },
            { name: 'country', label: 'Country', type: 'text', defaultValue: 'Kenya', required: false },
            { name: 'nationality', label: 'Nationality', type: 'text', defaultValue: 'Kenyan', required: false },
            { name: 'id_number', label: 'National ID/Passport', type: 'text', required: false },
          ]
        },
        {
          title: 'Academic Information',
          fields: [
            { name: 'admission_number', label: 'Admission Number', type: 'text', required: true, readOnly: true },
            { name: 'grade_level', label: 'Grade Level', type: 'text', required: true, 
              placeholder: 'e.g., Grade 10, Form 3' },
            { name: 'current_class', label: 'Current Class', type: 'text', required: true,
              placeholder: 'e.g., 10A, Form 3 East' },
            { name: 'academic_year', label: 'Academic Year', type: 'text', required: false,
              placeholder: 'YYYY-YYYY (e.g., 2024-2025)' },
            { name: 'primary_curriculum', label: 'Curriculum', type: 'select', options: [
              { value: '', label: 'Select Curriculum' },
              { value: 'cbc', label: 'CBC - Competency Based Curriculum' },
              { value: 'icse', label: 'ICSE - Indian Certificate of Secondary Education' },
              { value: 'american', label: 'American Curriculum' },
              { value: 'british', label: 'British Curriculum' },
              { value: 'montessori', label: 'Montessori' },
              { value: 'combined', label: 'Combined Curriculum' },
              { value: 'igcse', label: 'IGCSE' },
              { value: 'ib', label: 'International Baccalaureate' }
            ], required: false },
            { name: 'house', label: 'House', type: 'select', options: [
              { value: '', label: 'Select House' },
              { value: 'unity', label: 'Unity House' },
              { value: 'courage', label: 'Courage House' },
              { value: 'wisdom', label: 'Wisdom House' },
              { value: 'success', label: 'Success House' },
              { value: 'excellence', label: 'Excellence House' },
              { value: 'integrity', label: 'Integrity House' },
              { value: 'bravery', label: 'Bravery House' },
              { value: 'honor', label: 'Honor House' }
            ], required: false },
          ]
        },
        {
          title: 'Parent/Guardian Information',
          fields: [
            { name: 'parent_name', label: 'Parent/Guardian Name', type: 'text', required: false },
            { name: 'parent_email', label: 'Parent/Guardian Email', type: 'email', required: false },
            { name: 'parent_phone', label: 'Parent/Guardian Phone', type: 'tel', required: false },
            { name: 'parent_occupation', label: 'Parent Occupation', type: 'text', required: false },
          ]
        },
        {
          title: 'Emergency Contact',
          fields: [
            { name: 'emergency_contact_name', label: 'Emergency Contact Name', type: 'text', required: false },
            { name: 'emergency_contact_phone', label: 'Emergency Contact Phone', type: 'tel', required: false },
            { name: 'emergency_contact_relationship', label: 'Relationship', type: 'text', required: false },
            { name: 'emergency_contact_address', label: 'Emergency Contact Address', type: 'textarea', required: false },
          ]
        },
        {
          title: 'Medical Information',
          fields: [
            { name: 'blood_group', label: 'Blood Group', type: 'select', options: [
              { value: '', label: 'Select Blood Group' },
              { value: 'a_positive', label: 'A+' },
              { value: 'a_negative', label: 'A-' },
              { value: 'b_positive', label: 'B+' },
              { value: 'b_negative', label: 'B-' },
              { value: 'ab_positive', label: 'AB+' },
              { value: 'ab_negative', label: 'AB-' },
              { value: 'o_positive', label: 'O+' },
              { value: 'o_negative', label: 'O-' }
            ], required: false },
            { name: 'allergies', label: 'Allergies', type: 'textarea', required: false },
            { name: 'chronic_conditions', label: 'Chronic Conditions', type: 'textarea', required: false },
            { name: 'current_medications', label: 'Current Medications', type: 'textarea', required: false },
            { name: 'doctor_name', label: 'Doctor Name', type: 'text', required: false },
            { name: 'doctor_phone', label: 'Doctor Phone', type: 'tel', required: false },
            { name: 'medical_info', label: 'Medical Information', type: 'textarea', required: false },
          ]
        },
        {
          title: 'Additional Information',
          fields: [
            { name: 'previous_school', label: 'Previous School', type: 'text', required: false },
            { name: 'boarding_status', label: 'Boarding Status', type: 'select', options: [
              { value: 'day', label: 'Day Scholar' },
              { value: 'boarding', label: 'Boarding Student' },
              { value: 'flexible', label: 'Flexible Boarding' }
            ], required: false, defaultValue: 'day' },
          ]
        }
      ]
    },
    
    teacher: {
      title: 'Teacher Profile Completion',
      description: 'Please complete your teacher profile to access the teacher portal',
      requiredFields: ['first_name', 'last_name', 'phone_number', 'department', 'designation'],
      sections: [
        {
          title: 'Personal Information',
          fields: [
            { name: 'first_name', label: 'First Name', type: 'text', required: true },
            { name: 'last_name', label: 'Last Name', type: 'text', required: true },
            { name: 'middle_name', label: 'Middle Name', type: 'text', required: false },
            { name: 'date_of_birth', label: 'Date of Birth', type: 'date', required: false },
            { name: 'gender', label: 'Gender', type: 'select', options: [
              { value: '', label: 'Select Gender' },
              { value: 'male', label: 'Male' },
              { value: 'female', label: 'Female' },
              { value: 'other', label: 'Other' },
              { value: 'prefer_not_to_say', label: 'Prefer not to say' }
            ], required: false },
            { name: 'phone_number', label: 'Phone Number', type: 'tel', required: true },
            { name: 'alternative_phone', label: 'Alternative Phone', type: 'tel', required: false },
            { name: 'address', label: 'Address', type: 'textarea', required: false },
            { name: 'city', label: 'City', type: 'text', required: false },
            { name: 'country', label: 'Country', type: 'text', defaultValue: 'Kenya', required: false },
            { name: 'nationality', label: 'Nationality', type: 'text', defaultValue: 'Kenyan', required: false },
            { name: 'id_number', label: 'National ID/Passport', type: 'text', required: false },
          ]
        },
        {
          title: 'Professional Information',
          fields: [
            { name: 'staff_id', label: 'Staff ID', type: 'text', required: true, readOnly: true },
            { name: 'department', label: 'Department', type: 'text', required: true },
            { name: 'designation', label: 'Designation', type: 'text', required: true },
            { name: 'qualification', label: 'Qualifications', type: 'textarea', required: false },
            { name: 'specialization', label: 'Specialization', type: 'textarea', required: false },
            { name: 'years_of_experience', label: 'Years of Experience', type: 'number', required: false },
            { name: 'employment_date', label: 'Employment Date', type: 'date', required: false },
          ]
        },
        {
          title: 'Emergency Contact',
          fields: [
            { name: 'emergency_contact_name', label: 'Emergency Contact Name', type: 'text', required: false },
            { name: 'emergency_contact_phone', label: 'Emergency Contact Phone', type: 'tel', required: false },
            { name: 'emergency_contact_relationship', label: 'Relationship', type: 'text', required: false },
            { name: 'emergency_contact_address', label: 'Emergency Contact Address', type: 'textarea', required: false },
          ]
        },
        {
          title: 'Medical Information',
          fields: [
            { name: 'blood_group', label: 'Blood Group', type: 'select', options: [
              { value: '', label: 'Select Blood Group' },
              { value: 'a_positive', label: 'A+' },
              { value: 'a_negative', label: 'A-' },
              { value: 'b_positive', label: 'B+' },
              { value: 'b_negative', label: 'B-' },
              { value: 'ab_positive', label: 'AB+' },
              { value: 'ab_negative', label: 'AB-' },
              { value: 'o_positive', label: 'O+' },
              { value: 'o_negative', label: 'O-' }
            ], required: false },
            { name: 'medical_info', label: 'Medical Information', type: 'textarea', required: false },
          ]
        }
      ]
    },
    
    parent: {
      title: 'Parent Profile Completion',
      description: 'Please complete your parent profile and link to your child(ren)',
      requiredFields: ['first_name', 'last_name', 'phone_number', 'address'],
      sections: [
        {
          title: 'Personal Information',
          fields: [
            { name: 'first_name', label: 'First Name', type: 'text', required: true },
            { name: 'last_name', label: 'Last Name', type: 'text', required: true },
            { name: 'middle_name', label: 'Middle Name', type: 'text', required: false },
            { name: 'phone_number', label: 'Phone Number', type: 'tel', required: true },
            { name: 'address', label: 'Address', type: 'textarea', required: true },
            { name: 'city', label: 'City', type: 'text', required: false },
            { name: 'country', label: 'Country', type: 'text', defaultValue: 'Kenya', required: false },
            { name: 'parent_occupation', label: 'Occupation', type: 'text', required: false },
          ]
        },
        {
          title: 'Parent Information',
          fields: [
            { name: 'parent_name', label: 'Your Name (as Parent)', type: 'text', required: false },
            { name: 'parent_phone', label: 'Parent Phone', type: 'tel', required: false },
            { name: 'parent_email', label: 'Parent Email', type: 'email', required: false },
            { name: 'relationship', label: 'Relationship to Student(s)', type: 'select', options: [
              { value: '', label: 'Select Relationship' },
              { value: 'mother', label: 'Mother' },
              { value: 'father', label: 'Father' },
              { value: 'guardian', label: 'Guardian' },
              { value: 'grandparent', label: 'Grandparent' },
              { value: 'other', label: 'Other' }
            ], required: false },
          ]
        },
        {
          title: 'Emergency Contact',
          fields: [
            { name: 'emergency_contact_name', label: 'Emergency Contact Name', type: 'text', required: false },
            { name: 'emergency_contact_phone', label: 'Emergency Contact Phone', type: 'tel', required: false },
            { name: 'emergency_contact_relationship', label: 'Relationship', type: 'text', required: false },
            { name: 'emergency_contact_address', label: 'Emergency Contact Address', type: 'textarea', required: false },
          ]
        }
      ]
    },
    
    admin: {
      title: 'Administrator Profile Completion',
      description: 'Please complete your administrator profile',
      requiredFields: ['first_name', 'last_name', 'phone_number', 'address', 'department'],
      sections: [
        {
          title: 'Personal Information',
          fields: [
            { name: 'first_name', label: 'First Name', type: 'text', required: true },
            { name: 'last_name', label: 'Last Name', type: 'text', required: true },
            { name: 'middle_name', label: 'Middle Name', type: 'text', required: false },
            { name: 'phone_number', label: 'Phone Number', type: 'tel', required: true },
            { name: 'address', label: 'Address', type: 'textarea', required: true },
            { name: 'city', label: 'City', type: 'text', required: false },
            { name: 'country', label: 'Country', type: 'text', defaultValue: 'Kenya', required: false },
          ]
        },
        {
          title: 'Professional Information',
          fields: [
            { name: 'staff_id', label: 'Staff ID', type: 'text', required: true, readOnly: true },
            { name: 'department', label: 'Department', type: 'text', required: true },
            { name: 'designation', label: 'Designation', type: 'text', required: false },
            { name: 'qualification', label: 'Qualifications', type: 'textarea', required: false },
            { name: 'years_of_experience', label: 'Years of Experience', type: 'number', required: false },
          ]
        },
        {
          title: 'Emergency Contact',
          fields: [
            { name: 'emergency_contact_name', label: 'Emergency Contact Name', type: 'text', required: false },
            { name: 'emergency_contact_phone', label: 'Emergency Contact Phone', type: 'tel', required: false },
            { name: 'emergency_contact_relationship', label: 'Relationship', type: 'text', required: false },
          ]
        }
      ]
    },

    accountant: {
      title: 'Accountant Profile Completion',
      description: 'Please complete your accountant profile to access the finance portal',
      requiredFields: ['first_name', 'last_name', 'phone_number', 'address', 'department'],
      sections: [
        {
          title: 'Personal Information',
          fields: [
            { name: 'first_name', label: 'First Name', type: 'text', required: true },
            { name: 'last_name', label: 'Last Name', type: 'text', required: true },
            { name: 'middle_name', label: 'Middle Name', type: 'text', required: false },
            { name: 'phone_number', label: 'Phone Number', type: 'tel', required: true },
            { name: 'address', label: 'Address', type: 'textarea', required: true },
            { name: 'city', label: 'City', type: 'text', required: false },
            { name: 'country', label: 'Country', type: 'text', defaultValue: 'Kenya', required: false },
          ]
        },
        {
          title: 'Professional Information',
          fields: [
            { name: 'staff_id', label: 'Staff ID', type: 'text', required: true, readOnly: true },
            { name: 'department', label: 'Department', type: 'text', required: true },
            { name: 'designation', label: 'Designation', type: 'text', required: false },
            { name: 'qualification', label: 'Qualifications', type: 'textarea', required: false },
            { name: 'years_of_experience', label: 'Years of Experience', type: 'number', required: false },
          ]
        },
        {
          title: 'Emergency Contact',
          fields: [
            { name: 'emergency_contact_name', label: 'Emergency Contact Name', type: 'text', required: false },
            { name: 'emergency_contact_phone', label: 'Emergency Contact Phone', type: 'tel', required: false },
          ]
        }
      ]
    },

    librarian: {
      title: 'Librarian Profile Completion',
      description: 'Please complete your librarian profile to access the library portal',
      requiredFields: ['first_name', 'last_name', 'phone_number', 'address', 'department'],
      sections: [
        {
          title: 'Personal Information',
          fields: [
            { name: 'first_name', label: 'First Name', type: 'text', required: true },
            { name: 'last_name', label: 'Last Name', type: 'text', required: true },
            { name: 'middle_name', label: 'Middle Name', type: 'text', required: false },
            { name: 'phone_number', label: 'Phone Number', type: 'tel', required: true },
            { name: 'address', label: 'Address', type: 'textarea', required: true },
            { name: 'city', label: 'City', type: 'text', required: false },
          ]
        },
        {
          title: 'Professional Information',
          fields: [
            { name: 'staff_id', label: 'Staff ID', type: 'text', required: true, readOnly: true },
            { name: 'department', label: 'Department', type: 'text', required: true },
            { name: 'designation', label: 'Designation', type: 'text', required: false },
          ]
        }
      ]
    },

    it_support: {
      title: 'IT Support Profile Completion',
      description: 'Please complete your IT support profile',
      requiredFields: ['first_name', 'last_name', 'phone_number', 'address', 'department'],
      sections: [
        {
          title: 'Personal Information',
          fields: [
            { name: 'first_name', label: 'First Name', type: 'text', required: true },
            { name: 'last_name', label: 'Last Name', type: 'text', required: true },
            { name: 'phone_number', label: 'Phone Number', type: 'tel', required: true },
            { name: 'address', label: 'Address', type: 'textarea', required: true },
          ]
        },
        {
          title: 'Professional Information',
          fields: [
            { name: 'staff_id', label: 'Staff ID', type: 'text', required: true, readOnly: true },
            { name: 'department', label: 'Department', type: 'text', required: true },
            { name: 'designation', label: 'Designation', type: 'text', required: false },
          ]
        }
      ]
    },

    counselor: {
      title: 'School Counselor Profile Completion',
      description: 'Please complete your counselor profile',
      requiredFields: ['first_name', 'last_name', 'phone_number', 'address', 'department'],
      sections: [
        {
          title: 'Personal Information',
          fields: [
            { name: 'first_name', label: 'First Name', type: 'text', required: true },
            { name: 'last_name', label: 'Last Name', type: 'text', required: true },
            { name: 'phone_number', label: 'Phone Number', type: 'tel', required: true },
            { name: 'address', label: 'Address', type: 'textarea', required: true },
          ]
        },
        {
          title: 'Professional Information',
          fields: [
            { name: 'staff_id', label: 'Staff ID', type: 'text', required: true, readOnly: true },
            { name: 'department', label: 'Department', type: 'text', required: true },
            { name: 'designation', label: 'Designation', type: 'text', required: false },
            { name: 'qualification', label: 'Qualifications', type: 'textarea', required: false },
          ]
        }
      ]
    },

    office_staff: {
      title: 'Office Staff Profile Completion',
      description: 'Please complete your office staff profile',
      requiredFields: ['first_name', 'last_name', 'phone_number', 'address', 'department'],
      sections: [
        {
          title: 'Personal Information',
          fields: [
            { name: 'first_name', label: 'First Name', type: 'text', required: true },
            { name: 'last_name', label: 'Last Name', type: 'text', required: true },
            { name: 'phone_number', label: 'Phone Number', type: 'tel', required: true },
            { name: 'address', label: 'Address', type: 'textarea', required: true },
          ]
        },
        {
          title: 'Professional Information',
          fields: [
            { name: 'staff_id', label: 'Staff ID', type: 'text', required: true, readOnly: true },
            { name: 'department', label: 'Department', type: 'text', required: true },
            { name: 'designation', label: 'Designation', type: 'text', required: false },
          ]
        }
      ]
    },
    
    default: {
      title: 'Profile Completion',
      description: 'Please complete your profile',
      requiredFields: ['first_name', 'last_name', 'phone_number', 'address'],
      sections: [
        {
          title: 'Personal Information',
          fields: [
            { name: 'first_name', label: 'First Name', type: 'text', required: true },
            { name: 'last_name', label: 'Last Name', type: 'text', required: true },
            { name: 'phone_number', label: 'Phone Number', type: 'tel', required: true },
            { name: 'address', label: 'Address', type: 'textarea', required: true },
          ]
        }
      ]
    }
  };

  // Get current role config
  const roleConfig = ROLE_CONFIGS[currentRole] || ROLE_CONFIGS.default;
  
  // Initialize form data
  const [formData, setFormData] = useState(() => {
    const data = {};
    roleConfig.sections.forEach(section => {
      section.fields.forEach(field => {
        // Get value from current user or use default
        const userValue = user?.[field.name];
        // For dates, format properly
        if (field.type === 'date' && userValue) {
          data[field.name] = new Date(userValue).toISOString().split('T')[0];
        } else {
          data[field.name] = userValue || field.defaultValue || 
            (field.type === 'checkbox' ? false : '');
        }
      });
    });
    return data;
  });

  const [formErrors, setFormErrors] = useState({});

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // Check if user already has completed profile (prevent re-entering)
  useEffect(() => {
    const checkIfProfileAlreadyCompleted = async () => {
      if (user && hasCompletedProfile()) {
        console.log('✅ Profile already completed, redirecting to dashboard');
        const dashboardUrl = getDashboardUrl();
        navigate(dashboardUrl, { replace: true });
      }
    };
    
    checkIfProfileAlreadyCompleted();
  }, [user, hasCompletedProfile, getDashboardUrl, navigate]);

  // Auto-generate identifiers based on Django model logic
  useEffect(() => {
    if (currentRole && !loading) {
      const newData = { ...formData };
      let updated = false;

      // Generate admission number for students (simplified version of Django logic)
      if (currentRole === 'student' && !newData.admission_number) {
        const year = new Date().getFullYear();
        const randomNum = Math.floor(1000 + Math.random() * 9000);
        newData.admission_number = `DEL-STU-${year}-${randomNum.toString().padStart(4, '0')}`;
        updated = true;
      }

      // Generate staff ID for staff roles (simplified version of Django logic)
      const staffRoles = [
        'teacher', 'admin', 'accountant', 'librarian', 
        'it_support', 'counselor', 'office_staff',
        'head_teacher', 'curriculum_coordinator'
      ];
      
      if (staffRoles.includes(currentRole) && !newData.staff_id) {
        const year = new Date().getFullYear();
        const rolePrefix = {
          teacher: 'TCH',
          admin: 'ADM',
          accountant: 'ACC',
          librarian: 'LIB',
          it_support: 'IT',
          counselor: 'COU',
          office_staff: 'OFF',
          head_teacher: 'HT',
          curriculum_coordinator: 'CC'
        }[currentRole] || 'EMP';
        
        const randomNum = Math.floor(1000 + Math.random() * 9000);
        newData.staff_id = `DEL-${rolePrefix}-${year}-${randomNum.toString().padStart(4, '0')}`;
        updated = true;
      }

      if (updated) {
        setFormData(newData);
      }
    }
  }, [currentRole, formData, loading]);

  // Search for students by ID or name
  const searchStudents = async () => {
    if (!studentSearch.trim()) {
      setError('Please enter a student ID, admission number, or name');
      return;
    }

    setSearching(true);
    setError('');
    setFoundStudents([]);

    try {
      const response = await api.get(`/students/search/?q=${encodeURIComponent(studentSearch)}`);
      
      if (response.data.success && response.data.students) {
        setFoundStudents(response.data.students);
        if (response.data.students.length === 0) {
          setError('No students found with that search term');
        }
      } else {
        setError(response.data.message || 'Search failed. Please try again.');
      }
    } catch (error) {
      console.error('Search error:', error);
      
      // Fallback mock data for development
      if (process.env.NODE_ENV === 'development') {
        const mockStudents = [
          {
            id: 1,
            admission_number: 'DEL-STU-2024-0001',
            full_name: 'John Doe',
            grade_level: 'Grade 10',
            current_class: '10A',
            date_of_birth: '2008-05-15'
          },
          {
            id: 2,
            admission_number: 'DEL-STU-2024-0002',
            full_name: 'Jane Smith',
            grade_level: 'Grade 9',
            current_class: '9B',
            date_of_birth: '2009-08-22'
          }
        ].filter(s => 
          s.admission_number.toLowerCase().includes(studentSearch.toLowerCase()) ||
          s.full_name.toLowerCase().includes(studentSearch.toLowerCase())
        );
        
        setFoundStudents(mockStudents);
        if (mockStudents.length === 0) {
          setError('No students found with that search term');
        }
      } else {
        setError('Unable to search for students. Please try again later.');
      }
    } finally {
      setSearching(false);
    }
  };

  // Add student to selected list
  const addStudent = (student) => {
    if (!selectedStudents.some(s => s.id === student.id)) {
      setSelectedStudents(prev => [...prev, student]);
      setStudentSearch('');
      setFoundStudents([]);
    }
  };

  // Remove student from selected list
  const removeStudent = (studentId) => {
    setSelectedStudents(prev => prev.filter(s => s.id !== studentId));
  };

  // Validation function
  const validateForm = () => {
    const errors = {};
    
    // Check required fields
    roleConfig.requiredFields.forEach(fieldName => {
      const value = formData[fieldName];
      if (!value || (typeof value === 'string' && !value.trim())) {
        const fieldLabel = roleConfig.sections
          .flatMap(s => s.fields)
          .find(f => f.name === fieldName)?.label || fieldName;
        errors[fieldName] = `${fieldLabel} is required`;
      }
    });

    // Additional validation for parent role: must have at least one child linked
    if (currentRole === 'parent' && selectedStudents.length === 0) {
      errors['children'] = 'You must link at least one student to your account';
    }

    // Phone validation (Kenyan format)
    const phoneRegex = /^(\+254|0)[1-9]\d{8}$/;
    const validatePhone = (fieldName, value) => {
      if (value && !phoneRegex.test(value)) {
        errors[fieldName] = 'Please enter a valid Kenyan phone number (e.g., +254712345678 or 0712345678)';
      }
    };

    if (formData.phone_number) validatePhone('phone_number', formData.phone_number);
    if (formData.alternative_phone) validatePhone('alternative_phone', formData.alternative_phone);
    if (formData.parent_phone) validatePhone('parent_phone', formData.parent_phone);
    if (formData.emergency_contact_phone) validatePhone('emergency_contact_phone', formData.emergency_contact_phone);

    // Email validation
    if (formData.parent_email && !/\S+@\S+\.\S+/.test(formData.parent_email)) {
      errors.parent_email = 'Please enter a valid email address';
    }

    // Date validation for date_of_birth
    if (formData.date_of_birth) {
      const birthDate = new Date(formData.date_of_birth);
      const today = new Date();
      
      if (currentRole === 'student') {
        const minDate = new Date();
        minDate.setFullYear(today.getFullYear() - 25);
        const maxDate = new Date();
        maxDate.setFullYear(today.getFullYear() - 3);
        
        if (birthDate > maxDate) {
          errors.date_of_birth = 'Student must be at least 3 years old';
        }
        if (birthDate < minDate) {
          errors.date_of_birth = 'Student age seems unrealistic';
        }
      }
      
      if (['teacher', 'admin', 'staff'].includes(currentRole)) {
        const minDate = new Date();
        minDate.setFullYear(today.getFullYear() - 65);
        const maxDate = new Date();
        maxDate.setFullYear(today.getFullYear() - 21);
        
        if (birthDate > maxDate) {
          errors.date_of_birth = 'Must be at least 21 years old';
        }
        if (birthDate < minDate) {
          errors.date_of_birth = 'Please enter a valid date of birth';
        }
      }
    }

    // Validate academic year format
    if (formData.academic_year && !/^\d{4}-\d{4}$/.test(formData.academic_year)) {
      errors.academic_year = 'Academic year must be in format YYYY-YYYY';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    if (!validateForm()) {
      setError('Please fix the errors in the form before submitting.');
      return;
    }

    setSubmitting(true);
    setLoading(true);
    
    try {
      console.log('📤 Submitting profile data:', formData);

      // Clean the data
      const cleanedData = {};
      Object.keys(formData).forEach(key => {
        const value = formData[key];
        if (value !== null && value !== undefined && value !== '') {
          // Convert empty strings for required fields to null for Django
          cleanedData[key] = typeof value === 'string' ? value.trim() : value;
        }
      });

      // Add child relationships for parents
      if (currentRole === 'parent' && selectedStudents.length > 0) {
        cleanedData.linked_students = selectedStudents.map(s => s.id);
      }

      console.log('🧹 Cleaned data:', cleanedData);

      // Step 1: Update profile data
      const updateResponse = await updateProfile(cleanedData);
      
      console.log('📥 Profile Update Response:', updateResponse);

      if (updateResponse.success) {
        console.log('✅ Profile updated successfully');
        
        // Step 2: Mark profile as completed in backend
        const markCompleteResponse = await markProfileCompleted();
        
        if (markCompleteResponse.success) {
          console.log('✅ Profile marked as completed in backend');
          
          // Step 3: Update user in context to reflect profile_completed flag
          await updateUser();
          
          // Show success message
          setSuccess('Profile completed successfully! You will be redirected to your dashboard.');
          
          // Get redirect path
          const dashboardUrl = getDashboardUrl();
          console.log('🔄 Redirecting to:', dashboardUrl);
          
          // Redirect after 2 seconds
          setTimeout(() => {
            navigate(dashboardUrl, { 
              replace: true,
              state: {
                message: 'Welcome! Your profile has been completed successfully.',
                type: 'success'
              }
            });
          }, 2000);
        } else {
          // Mark as completed failed
          setError(markCompleteResponse.message || 'Failed to mark profile as completed. Please try again.');
          console.error('❌ Failed to mark profile as completed:', markCompleteResponse);
        }
      } else {
        // Handle API error response
        const errorMessage = updateResponse.message || 
                            updateResponse.error?.message || 
                            'Failed to update profile. Please check your data and try again.';
        setError(errorMessage);
        console.error('❌ Profile update failed:', updateResponse);
      }
    } catch (error) {
      console.error('💥 Profile update error:', error);
      const errorMsg = error.message || 'Network error occurred. Please check your connection and try again.';
      setError(errorMsg);
    } finally {
      setLoading(false);
      setSubmitting(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Clear field-specific error when user starts typing
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const formatDateForInput = (dateString) => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return dateString;
      return date.toISOString().split('T')[0];
    } catch (error) {
      console.warn('Date formatting error:', error);
      return dateString;
    }
  };

  const renderField = (field) => {
    const { name, label, type, required, options, readOnly, placeholder } = field;
    const value = formData[name];
    const error = formErrors[name];
    
    const commonProps = {
      name,
      id: name,
      value: value || '',
      onChange: handleChange,
      disabled: loading || readOnly || submitting,
      className: `form-control ${error ? 'is-invalid' : ''}`,
      required,
      placeholder
    };

    switch(type) {
      case 'select':
        return (
          <select {...commonProps}>
            {options?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );
      
      case 'textarea':
        return <textarea {...commonProps} rows="3" />;
      
      case 'checkbox':
        return (
          <div className="form-check">
            <input
              type="checkbox"
              {...commonProps}
              checked={value || false}
              className="form-check-input"
              id={name}
            />
            <label className="form-check-label" htmlFor={name}>
              {label}
            </label>
          </div>
        );
      
      case 'number':
        return <input type="number" {...commonProps} />;
      
      default:
        return <input type={type} {...commonProps} />;
    }
  };

  // Add backend user roles that were missing
  const backendUserRoles = [
    'head_teacher',
    'curriculum_coordinator'
  ];

  if (!currentRole) {
    return (
      <div className="container text-center py-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="mt-3">Loading user information...</p>
      </div>
    );
  }

  // Check if user has backend role but not in frontend config
  if (backendUserRoles.includes(currentRole) && !ROLE_CONFIGS[currentRole]) {
    // Use admin config for backend users
    const effectiveRoleConfig = ROLE_CONFIGS.admin;
    
    return (
      <div className="container-fluid py-4">
        <div className="row justify-content-center">
          <div className="col-12">
            <div className="card shadow-sm border-0">
              <div className="card-header bg-primary text-white text-center py-4">
                <h3 className="mb-0">Staff Profile Completion</h3>
                <p className="mb-0 mt-2">Hello {userName}! Please complete your profile to access the staff portal</p>
                <small className="opacity-75 d-block mt-1">
                  Role: {currentRole.replace('_', ' ').toUpperCase()} (Staff)
                </small>
              </div>
              
              <div className="card-body p-4">
                <div className="alert alert-info">
                  <i className="bi bi-info-circle me-2"></i>
                  <strong>Note:</strong> Please contact the administrator to configure your specific profile requirements.
                </div>
                
                <div className="text-center py-5">
                  <p>Your profile setup is being configured. Please contact the system administrator.</p>
                  <button 
                    className="btn btn-primary"
                    onClick={() => navigate('/dashboard')}
                  >
                    Go to Dashboard
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid py-4">
      <div className="row justify-content-center">
        <div className="col-12">
          <div className="card shadow-sm border-0">
            <div className="card-header bg-primary text-white text-center py-4">
              <h3 className="mb-0">{roleConfig.title}</h3>
              <p className="mb-0 mt-2">Hello {userName}! {roleConfig.description}</p>
              <small className="opacity-75 d-block mt-1">Role: {currentRole.replace('_', ' ').toUpperCase()}</small>
              
              {/* Profile Completion Progress */}
              <div className="mt-3">
                <div className="d-flex justify-content-between align-items-center mb-1">
                  <small>Profile Completion</small>
                  <small>{roleConfig.requiredFields.length} required fields</small>
                </div>
                <div className="progress" style={{ height: '8px' }}>
                  <div 
                    className="progress-bar bg-success" 
                    style={{ 
                      width: `${Object.keys(formData).filter(key => formData[key]).length / roleConfig.requiredFields.length * 100}%` 
                    }}
                  ></div>
                </div>
              </div>
            </div>
            
            <div className="card-body p-4">
              {success && (
                <div className="alert alert-success alert-dismissible fade show" role="alert">
                  <i className="bi bi-check-circle me-2"></i>
                  <strong>Success!</strong> {success}
                </div>
              )}

              {error && (
                <div className="alert alert-danger alert-dismissible fade show" role="alert">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  <strong>Error:</strong> {error}
                </div>
              )}

              <form onSubmit={handleSubmit} noValidate>
                {/* Student Search Section for Parents */}
                {currentRole === 'parent' && (
                  <div className="mb-5">
                    <h5 className="text-primary border-bottom pb-2 mb-4">
                      <i className="bi bi-person-plus me-2"></i>
                      Link Your Child(ren)
                    </h5>
                    
                    <div className="card border-primary mb-4">
                      <div className="card-header bg-primary bg-opacity-10">
                        <h6 className="mb-0">
                          <i className="bi bi-search me-2"></i>
                          Search for Students
                        </h6>
                        <small className="text-muted">Search by admission number, student ID, or name</small>
                      </div>
                      <div className="card-body">
                        <div className="row g-3">
                          <div className="col-md-8">
                            <div className="input-group">
                              <span className="input-group-text">
                                <i className="bi bi-person-badge"></i>
                              </span>
                              <input
                                type="text"
                                className="form-control"
                                placeholder="Enter admission number (e.g., DEL-STU-2024-0001) or student name"
                                value={studentSearch}
                                onChange={(e) => setStudentSearch(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), searchStudents())}
                                disabled={searching || submitting}
                              />
                              <button
                                type="button"
                                className="btn btn-primary"
                                onClick={searchStudents}
                                disabled={searching || !studentSearch.trim() || submitting}
                              >
                                {searching ? (
                                  <>
                                    <span className="spinner-border spinner-border-sm me-2"></span>
                                    Searching...
                                  </>
                                ) : (
                                  <>
                                    <i className="bi bi-search me-2"></i>
                                    Search
                                  </>
                                )}
                              </button>
                            </div>
                            <small className="text-muted mt-2 d-block">
                              Enter your child's admission number or name to link them to your account.
                            </small>
                          </div>
                        </div>

                        {/* Search Results */}
                        {foundStudents.length > 0 && (
                          <div className="mt-4">
                            <h6>Search Results:</h6>
                            <div className="list-group">
                              {foundStudents.map(student => (
                                <div key={student.id} className="list-group-item">
                                  <div className="d-flex justify-content-between align-items-center">
                                    <div>
                                      <h6 className="mb-1">{student.full_name}</h6>
                                      <small className="text-muted">
                                        Admission: {student.admission_number} | 
                                        Grade: {student.grade_level} | 
                                        Class: {student.current_class}
                                      </small>
                                    </div>
                                    <button
                                      type="button"
                                      className="btn btn-sm btn-outline-primary"
                                      onClick={() => addStudent(student)}
                                      disabled={selectedStudents.some(s => s.id === student.id) || submitting}
                                    >
                                      {selectedStudents.some(s => s.id === student.id) ? (
                                        <i className="bi bi-check-circle me-1"></i>
                                      ) : (
                                        <i className="bi bi-plus-circle me-1"></i>
                                      )}
                                      {selectedStudents.some(s => s.id === student.id) ? 'Added' : 'Add'}
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Selected Students */}
                        <div className="mt-4">
                          <h6>Linked Students ({selectedStudents.length})</h6>
                          {selectedStudents.length === 0 ? (
                            <div className="alert alert-warning">
                              <i className="bi bi-exclamation-triangle me-2"></i>
                              No students linked yet. You must link at least one student to proceed.
                            </div>
                          ) : (
                            <div className="list-group">
                              {selectedStudents.map(student => (
                                <div key={student.id} className="list-group-item">
                                  <div className="d-flex justify-content-between align-items-center">
                                    <div>
                                      <h6 className="mb-1">{student.full_name}</h6>
                                      <small className="text-muted">
                                        Admission: {student.admission_number} | 
                                        Grade: {student.grade_level} | 
                                        Class: {student.current_class}
                                      </small>
                                    </div>
                                    <button
                                      type="button"
                                      className="btn btn-sm btn-outline-danger"
                                      onClick={() => removeStudent(student.id)}
                                      disabled={submitting}
                                    >
                                      <i className="bi bi-x-circle"></i>
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                          {formErrors.children && (
                            <div className="text-danger mt-2">
                              <i className="bi bi-exclamation-circle me-1"></i>
                              {formErrors.children}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Regular Form Sections */}
                {roleConfig.sections.map((section, sectionIndex) => (
                  <div key={sectionIndex} className="mb-5">
                    <h5 className="text-primary border-bottom pb-2 mb-4">
                      <i className="bi bi-person-badge me-2"></i>
                      {section.title}
                    </h5>
                    
                    <div className="row">
                      {section.fields.map((field, fieldIndex) => (
                        <div 
                          key={fieldIndex} 
                          className={`col-md-${field.type === 'textarea' ? '12' : '6'} mb-3`}
                        >
                          {field.type !== 'checkbox' && (
                            <label className="form-label fw-semibold" htmlFor={field.name}>
                              {field.label} {field.required && <span className="text-danger">*</span>}
                            </label>
                          )}
                          
                          {renderField(field)}
                          
                          {field.readOnly && field.value && (
                            <div className="form-text">
                              <i className="bi bi-info-circle me-1"></i>
                              Auto-generated field
                            </div>
                          )}
                          
                          {formErrors[field.name] && (
                            <div className="invalid-feedback d-block">
                              <i className="bi bi-exclamation-circle me-1"></i>
                              {formErrors[field.name]}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}

                <div className="d-grid gap-2 mt-4">
                  <button 
                    type="submit" 
                    className="btn btn-primary btn-lg"
                    disabled={loading || submitting}
                  >
                    {submitting ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        Completing Profile...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check-circle me-2"></i>
                        Complete Profile & Continue
                      </>
                    )}
                  </button>
                  
                  <button 
                    type="button" 
                    className="btn btn-outline-secondary"
                    onClick={() => navigate('/dashboard')}
                    disabled={submitting}
                  >
                    <i className="bi bi-arrow-right me-2"></i>
                    Skip for Now
                  </button>
                </div>

                <div className="text-center mt-3">
                  <small className="text-muted">
                    <i className="bi bi-info-circle me-1"></i>
                    Fields marked with * are required. Your profile must be complete to access all features.
                  </small>
                  <br />
                  <small className="text-muted">
                    <i className="bi bi-shield-check me-1"></i>
                    Your profile completion will be saved permanently. You won't be asked to complete it again.
                  </small>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CompleteProfile;