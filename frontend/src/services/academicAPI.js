// services/academicAPI.js - IMPROVED VERSION
import api, { apiUtils } from './api';

/**
 * Academics-related constants for consistent usage across the application
 */
export const ACADEMIC_CONSTANTS = {
  // Setup validation constants
  SETUP_STATUS: {
    COMPLETE: 'complete',
    INCOMPLETE: 'incomplete',
    ERROR: 'error'
  },
  
  // Setup item priorities (order of creation matters)
  SETUP_PRIORITY: {
    ACADEMIC_YEARS: 1,
    ACADEMIC_TERMS: 2,
    GRADE_LEVELS: 3,
    SUBJECT_CATEGORIES: 4,
    SUBJECTS: 5,
    CLASSES: 6,
    STREAMS: 7
  },
  
  ATTENDANCE_STATUS: {
    PRESENT: 'present',
    ABSENT: 'absent',
    LATE: 'late',
    EXCUSED: 'excused'
  },
  GRADE_CHOICES: {
    'A': 12,
    'A-': 11,
    'B+': 10,
    'B': 9,
    'B-': 8,
    'C+': 7,
    'C': 6,
    'C-': 5,
    'D+': 4,
    'D': 3,
    'D-': 2,
    'E': 1
  }
};

/**
 * Setup validation rules
 */
export const SETUP_VALIDATION_RULES = {
  MIN_ACADEMIC_YEARS: 1,
  MIN_TERMS_PER_YEAR: 1,
  MIN_SUBJECTS: 5,
  MIN_CLASSES: 1,
  MIN_GRADE_LEVELS: 1
};

/**
 * Simple in-memory cache for academic data
 */
export const academicCache = {
  data: new Map(),
  
  set(key, value, ttl = 60000) { // Default 1 minute TTL
    this.data.set(key, {
      value,
      timestamp: Date.now(),
      ttl
    });
  },
  
  get(key) {
    const item = this.data.get(key);
    if (!item) return null;
    
    if (Date.now() - item.timestamp > item.ttl) {
      this.data.delete(key);
      return null;
    }
    
    return item.value;
  },
  
  delete(key) {
    this.data.delete(key);
  },
  
  clear() {
    this.data.clear();
  }
};

/**
 * Standardized error handler for all API calls
 */
export const handleAPIError = (error) => {
  // Special handling for 500 errors related to missing setup
  if (error.response?.status === 500) {
    const errorPath = error.config?.url || '';
    
    // Check for academic setup errors
    if (errorPath.includes('academics')) {
      return {
        success: false,
        error: {
          message: 'Academic setup incomplete or server error',
          details: 'Check if academic models exist and database is properly configured',
          status: 500,
          code: 'ACADEMIC_SETUP_ERROR',
          path: errorPath,
          solution: 'Run database migrations and ensure academic data is configured'
        },
        requiresSetup: true
      };
    }
  }
  
  // Handle 404 for missing endpoints
  if (error.response?.status === 404) {
    return {
      success: false,
      error: {
        message: 'API endpoint not found',
        details: 'The requested endpoint does not exist',
        status: 404,
        code: 'ENDPOINT_NOT_FOUND',
        path: error.config?.url
      }
    };
  }
  
  return {
    success: false,
    error: {
      message: apiUtils.getErrorMessage(error),
      details: error.response?.data,
      status: error.response?.status,
      code: error.code,
      path: error.config?.url
    }
  };
};

/**
 * Check if API error is due to incomplete setup
 * @param {Object} apiResponse - API response object
 * @returns {boolean}
 */
export const isSetupError = (apiResponse) => {
  return apiResponse?.error?.code === 'SETUP_INCOMPLETE' || 
         apiResponse?.requiresSetup === true ||
         apiResponse?.error?.code === 'SETUP_REQUIRED' ||
         apiResponse?.error?.code === 'ACADEMIC_SETUP_ERROR';
};

/**
 * Get setup completion checklist
 */
export const getSetupChecklist = (setupStatus) => {
  if (!setupStatus?.data?.items) return [];
  
  return setupStatus.data.items.map(item => ({
    name: item.name,
    completed: item.is_configured,
    count: item.count,
    minRequired: item.min_required || 1,
    endpoint: item.endpoint,
    priority: ACADEMIC_CONSTANTS.SETUP_PRIORITY[item.model_name?.toUpperCase()] || 99
  })).sort((a, b) => a.priority - b.priority);
};

/**
 * Calculate next setup action
 */
export const getNextSetupAction = (setupStatus) => {
  const checklist = getSetupChecklist(setupStatus);
  const incompleteItem = checklist.find(item => !item.completed);
  
  if (!incompleteItem) {
    return {
      action: 'none',
      message: 'Setup complete',
      priority: 0
    };
  }
  
  const actionMap = {
    'Academic Years': { 
      action: 'create_academic_year', 
      endpoint: '/academics/academic-years/',
      instruction: 'Create at least one academic year'
    },
    'Academic Terms': { 
      action: 'create_academic_term', 
      endpoint: '/academics/academic-terms/',
      instruction: 'Create terms for the current academic year'
    },
    'Subjects': { 
      action: 'create_subject', 
      endpoint: '/academics/subjects/',
      instruction: 'Create subjects for your school'
    },
    'Classrooms': { 
      action: 'create_classroom', 
      endpoint: '/academics/classrooms/',
      instruction: 'Create classroom groups'
    },
    'Grade Levels': { 
      action: 'create_grade_level', 
      endpoint: '/academics/grade-levels/',
      instruction: 'Define grade levels'
    }
  };
  
  return {
    action: actionMap[incompleteItem.name]?.action || 'configure',
    item: incompleteItem.name,
    priority: incompleteItem.priority,
    endpoint: incompleteItem.endpoint,
    instruction: actionMap[incompleteItem.name]?.instruction || `Configure ${incompleteItem.name}`,
    message: `Next: ${incompleteItem.name} (${incompleteItem.count}/${incompleteItem.minRequired})`
  };
};

/**
 * Setup progress tracker component
 */
export const getSetupProgressData = (setupProgress) => {
  const milestones = [
    { threshold: 0, label: 'Not started', color: 'red', canAccess: 'Nothing' },
    { threshold: 20, label: 'Basic setup', color: 'orange', canAccess: 'Student data' },
    { threshold: 40, label: 'Partial setup', color: 'yellow', canAccess: 'Attendance' },
    { threshold: 60, label: 'Mostly complete', color: 'light-green', canAccess: 'Grades' },
    { threshold: 80, label: 'Almost complete', color: 'green', canAccess: 'Assignments' },
    { threshold: 100, label: 'Complete', color: 'dark-green', canAccess: 'Everything' }
  ];
  
  const currentMilestone = [...milestones]
    .reverse()
    .find(m => setupProgress >= m.threshold) || milestones[0];
  
  const nextMilestone = milestones.find(m => m.threshold > setupProgress);
  
  return {
    percentage: setupProgress,
    milestone: currentMilestone.label,
    color: currentMilestone.color,
    canAccess: currentMilestone.canAccess,
    nextMilestone: nextMilestone ? {
      threshold: nextMilestone.threshold,
      label: nextMilestone.label,
      needed: nextMilestone.threshold - setupProgress
    } : null,
    isComplete: setupProgress >= 100
  };
};

/**
 * Validate if setup meets minimum requirements
 */
export const validateSetupRequirements = (setupData) => {
  const issues = [];
  
  if (!setupData.academicYears || setupData.academicYears.length < SETUP_VALIDATION_RULES.MIN_ACADEMIC_YEARS) {
    issues.push({
      code: 'INSUFFICIENT_ACADEMIC_YEARS',
      message: `Need at least ${SETUP_VALIDATION_RULES.MIN_ACADEMIC_YEARS} academic year`,
      required: SETUP_VALIDATION_RULES.MIN_ACADEMIC_YEARS,
      actual: setupData.academicYears?.length || 0
    });
  }
  
  if (!setupData.subjects || setupData.subjects.length < SETUP_VALIDATION_RULES.MIN_SUBJECTS) {
    issues.push({
      code: 'INSUFFICIENT_SUBJECTS',
      message: `Need at least ${SETUP_VALIDATION_RULES.MIN_SUBJECTS} subjects`,
      required: SETUP_VALIDATION_RULES.MIN_SUBJECTS,
      actual: setupData.subjects?.length || 0
    });
  }
  
  if (!setupData.classes || setupData.classes.length < SETUP_VALIDATION_RULES.MIN_CLASSES) {
    issues.push({
      code: 'INSUFFICIENT_CLASSES',
      message: `Need at least ${SETUP_VALIDATION_RULES.MIN_CLASSES} classroom`,
      required: SETUP_VALIDATION_RULES.MIN_CLASSES,
      actual: setupData.classes?.length || 0
    });
  }
  
  return {
    isValid: issues.length === 0,
    issues,
    passed: SETUP_VALIDATION_RULES.MIN_SUBJECTS - (setupData.subjects?.length || 0)
  };
};

/**
 * Performance monitoring utility
 */
export const performanceMonitor = {
  timers: new Map(),
  
  start(timerName) {
    this.timers.set(timerName, {
      startTime: performance.now(),
      endTime: null,
      duration: null
    });
  },
  
  end(timerName) {
    const timer = this.timers.get(timerName);
    if (timer) {
      timer.endTime = performance.now();
      timer.duration = timer.endTime - timer.startTime;
      return timer.duration;
    }
    return null;
  },
  
  getDuration(timerName) {
    const timer = this.timers.get(timerName);
    return timer?.duration || null;
  },
  
  logSlowResponse(timerName, threshold = 1000) {
    const duration = this.getDuration(timerName);
    if (duration && duration > threshold) {
      console.warn(`⏱️ Slow response detected for ${timerName}: ${duration.toFixed(0)}ms`);
    }
  },
  
  clear() {
    this.timers.clear();
  }
};

/**
 * Main academics API object with all methods - FIXED VERSION
 */
export const academicsAPI = {
  // ==================== PERFORMANCE MONITORING ====================
  
  enablePerformanceLogging: true,
  
  logPerformance(endpoint, duration, dataSize = null) {
    if (this.enablePerformanceLogging && duration > 100) {
      console.log(`📊 API Performance: ${endpoint} - ${duration.toFixed(0)}ms${dataSize ? `, ${dataSize} items` : ''}`);
    }
  },
  
  // ==================== OPTIMIZED SETUP ENDPOINTS ====================

  /**
   * Quick setup check - FIXED VERSION with fallback
   */
  quickSetupCheck: async () => {
    const timerName = 'quickSetupCheck';
    performanceMonitor.start(timerName);
    const cacheKey = 'quickSetupCheck';
    
    // Check cache first
    const cached = academicCache.get(cacheKey);
    if (cached) {
      performanceMonitor.end(timerName);
      return {
        ...cached,
        fromCache: true,
        responseTimeMs: 0
      };
    }
    
    try {
      const response = await api.get('/academics/setup/quick-check/');
      const duration = performanceMonitor.end(timerName);
      this.logPerformance('setup/quick-check', duration);
      
      const result = {
        success: true,
        data: response.data,
        status: response.status,
        requiresSetup: !response.data.is_setup_complete,
        missingItems: response.data.missing_items || [],
        fromCache: response.data.from_cache || false,
        responseTimeMs: response.data.response_time_ms || duration,
        timestamp: response.data.timestamp
      };
      
      // Cache successful result
      academicCache.set(cacheKey, result, 30000); // 30 seconds
      
      return result;
    } catch (error) {
      performanceMonitor.end(timerName);
      
      // If the endpoint doesn't exist, provide a fallback
      if (error.response?.status === 404) {
        console.warn('setup/quick-check endpoint not found, using fallback check');
        return this.fallbackQuickSetupCheck();
      }
      
      return handleAPIError(error);
    }
  },

  /**
   * Fallback setup check when main endpoint fails
   */
  fallbackQuickSetupCheck: async () => {
    try {
      // Try to get essential data instead
      const essentialData = await api.get('/academics/essential-data/');
      
      const hasMinimumData = essentialData.data.has_minimum_data || false;
      const checks = {
        academic_years: essentialData.data.data?.academic_years?.length > 0,
        academic_terms: essentialData.data.data?.current_terms?.length > 0,
        grade_levels: essentialData.data.data?.grade_levels?.length > 0,
        subjects: essentialData.data.data?.subjects?.length > 0,
        classrooms: essentialData.data.data?.classrooms?.length > 0,
        has_current_year: essentialData.data.has_current_year || false,
        has_current_term: essentialData.data.data?.current_terms?.some(term => term.is_current) || false
      };
      
      const essentialChecks = [
        checks.academic_years,
        checks.academic_terms,
        checks.grade_levels,
        checks.subjects,
        checks.classrooms
      ];
      
      const isSetupComplete = essentialChecks.every(Boolean);
      
      const missingItems = [];
      const itemNames = {
        academic_years: 'Academic Years',
        academic_terms: 'Academic Terms',
        grade_levels: 'Grade Levels',
        subjects: 'Subjects',
        classrooms: 'Classrooms',
      };
      
      for (const [key, displayName] of Object.entries(itemNames)) {
        if (!checks[key]) {
          missingItems.push({
            name: displayName,
            key: key,
            endpoint: `/api/v1/academics/${key.replace('_', '-')}/`,
            priority: 1
          });
        }
      }
      
      return {
        success: true,
        data: {
          is_setup_complete: isSetupComplete,
          checks,
          missing_items: missingItems,
          missing_count: missingItems.length,
          timestamp: new Date().toISOString(),
          from_cache: false
        },
        requiresSetup: !isSetupComplete,
        missingItems,
        fromCache: false,
        responseTimeMs: 0
      };
    } catch (fallbackError) {
      // If even fallback fails, return basic error
      return {
        success: false,
        error: {
          message: 'Failed to check academic setup',
          details: 'All setup check endpoints are unavailable',
          code: 'SETUP_CHECK_FAILED'
        },
        requiresSetup: true
      };
    }
  },

  /**
   * Get essential setup data
   */
  getEssentialData: async () => {
    const timerName = 'getEssentialData';
    performanceMonitor.start(timerName);
    const cacheKey = 'getEssentialData';
    
    const cached = academicCache.get(cacheKey);
    if (cached) {
      performanceMonitor.end(timerName);
      return {
        ...cached,
        fromCache: true,
        responseTimeMs: 0
      };
    }
    
    try {
      const response = await api.get('/academics/essential-data/');
      const duration = performanceMonitor.end(timerName);
      
      const data = response.data.data || {};
      const dataSize = Object.keys(data).reduce((acc, key) => acc + (data[key]?.length || 0), 0);
      
      this.logPerformance('setup/essential-data', duration, dataSize);
      
      const result = {
        success: true,
        data: response.data,
        status: response.status,
        hasMinimumData: response.data.has_minimum_data || false,
        hasCurrentYear: response.data.has_current_year || false,
        fromCache: response.data.from_cache || false,
        responseTimeMs: response.data.response_time_ms || duration,
        timestamp: response.data.timestamp,
        counts: response.data.counts || {}
      };
      
      // Cache for 2 minutes
      academicCache.set(cacheKey, result, 120000);
      
      return result;
    } catch (error) {
      performanceMonitor.end(timerName);
      
      // Fallback to individual endpoints if essential-data fails
      if (error.response?.status === 404) {
        console.warn('essential-data endpoint not found, falling back to individual calls');
        return this.getEssentialDataFallback();
      }
      
      return handleAPIError(error);
    }
  },

  /**
   * Fallback for essential data
   */
  getEssentialDataFallback: async () => {
    try {
      // Call individual endpoints
      const [yearsResponse, gradeLevelsResponse, subjectsResponse] = await Promise.all([
        api.get('/academics/academic-years/?is_active=true&page_size=10'),
        api.get('/academics/grade-levels/?is_active=true&page_size=12'),
        api.get('/academics/subjects/?is_active=true&page_size=50')
      ]);
      
      const data = {
        academic_years: yearsResponse.data.results || [],
        grade_levels: gradeLevelsResponse.data.results || [],
        subjects: subjectsResponse.data.results || [],
        current_year: null,
        current_terms: [],
        classrooms: []
      };
      
      // Find current year
      const currentYear = data.academic_years.find(year => year.is_current);
      if (currentYear) {
        data.current_year = currentYear;
        
        // Get terms for current year
        const termsResponse = await api.get(`/academics/academic-terms/?academic_year=${currentYear.id}&is_active=true`);
        data.current_terms = termsResponse.data.results || [];
      }
      
      const hasMinimumData = data.subjects.length > 0 && data.grade_levels.length > 0;
      const hasCurrentYear = currentYear !== undefined;
      
      return {
        success: true,
        data: {
          data,
          has_minimum_data: hasMinimumData,
          has_current_year: hasCurrentYear,
          counts: {
            academic_years: data.academic_years.length,
            grade_levels: data.grade_levels.length,
            subjects: data.subjects.length,
            current_terms: data.current_terms.length,
            classrooms: data.classrooms.length
          },
          timestamp: new Date().toISOString(),
          from_cache: false
        },
        hasMinimumData,
        hasCurrentYear,
        fromCache: false,
        responseTimeMs: 0
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Get lightweight classrooms - FIXED URL
   */
  getLightweightClassrooms: async () => {
    const timerName = 'getLightweightClassrooms';
    performanceMonitor.start(timerName);
    const cacheKey = 'lightweightClassrooms';
    
    const cached = academicCache.get(cacheKey);
    if (cached) {
      performanceMonitor.end(timerName);
      return {
        ...cached,
        fromCache: true,
        responseTimeMs: 0
      };
    }
    
    try {
      // FIXED: Correct endpoint URL
      const response = await api.get('/academics/lightweight/classrooms/');
      const duration = performanceMonitor.end(timerName);
      
      this.logPerformance('lightweight/classrooms', duration, response.data.count);
      
      const result = {
        success: true,
        data: response.data,
        status: response.status,
        count: response.data.count || 0,
        responseTimeMs: response.data.response_time_ms || duration
      };
      
      academicCache.set(cacheKey, result, 60000); // 1 minute
      
      return result;
    } catch (error) {
      performanceMonitor.end(timerName);
      
      // Fallback to regular classrooms endpoint
      if (error.response?.status === 404) {
        console.warn('lightweight/classrooms endpoint not found, using regular classrooms');
        return this.getClassrooms({ page_size: 50 });
      }
      
      return handleAPIError(error);
    }
  },

  /**
   * Get essential subjects - FIXED URL
   */
  getEssentialSubjects: async () => {
    const timerName = 'getEssentialSubjects';
    performanceMonitor.start(timerName);
    const cacheKey = 'essentialSubjects';
    
    const cached = academicCache.get(cacheKey);
    if (cached) {
      performanceMonitor.end(timerName);
      return {
        ...cached,
        fromCache: true,
        responseTimeMs: 0
      };
    }
    
    try {
      // FIXED: Correct endpoint URL
      const response = await api.get('/academics/lightweight/subjects/');
      const duration = performanceMonitor.end(timerName);
      
      const data = response.data;
      const totalSubjects = data.total_subjects || data.subjects?.length || 0;
      
      this.logPerformance('lightweight/subjects', duration, totalSubjects);
      
      const result = {
        success: true,
        data: response.data,
        status: response.status,
        totalSubjects,
        totalCategories: data.total_categories || data.categories?.length || 0,
        fromCache: data.from_cache || false
      };
      
      academicCache.set(cacheKey, result, 60000); // 1 minute
      
      return result;
    } catch (error) {
      performanceMonitor.end(timerName);
      
      // Fallback to regular subjects endpoint
      if (error.response?.status === 404) {
        console.warn('lightweight/subjects endpoint not found, using regular subjects');
        return this.getSubjects({ page_size: 50 });
      }
      
      return handleAPIError(error);
    }
  },

  /**
   * Get classrooms summary - FIXED URL
   */
  getClassroomsSummary: async () => {
    const timerName = 'getClassroomsSummary';
    performanceMonitor.start(timerName);
    const cacheKey = 'classroomsSummary';
    
    const cached = academicCache.get(cacheKey);
    if (cached) {
      performanceMonitor.end(timerName);
      return {
        ...cached,
        fromCache: true,
        responseTimeMs: 0
      };
    }
    
    try {
      // FIXED: Correct endpoint URL
      const response = await api.get('/academics/summaries/classrooms/');
      const duration = performanceMonitor.end(timerName);
      
      this.logPerformance('summaries/classrooms', duration);
      
      const result = {
        success: true,
        data: response.data,
        status: response.status,
        total: response.data.total || 0,
        hasCurrentYear: response.data.has_current_year || false
      };
      
      academicCache.set(cacheKey, result, 120000); // 2 minutes
      
      return result;
    } catch (error) {
      performanceMonitor.end(timerName);
      
      // Fallback
      if (error.response?.status === 404) {
        return {
          success: true,
          data: {
            total: 0,
            has_current_year: false,
            by_grade_level: []
          },
          total: 0,
          hasCurrentYear: false
        };
      }
      
      return handleAPIError(error);
    }
  },

  /**
   * Optimized academic system initialization - IMPROVED
   */
  initializeAcademicSystem: async () => {
    const timerName = 'initializeAcademicSystem';
    performanceMonitor.start(timerName);
    const cacheKey = 'academicSystemInitialized';
    
    const cached = academicCache.get(cacheKey);
    if (cached) {
      performanceMonitor.end(timerName);
      return {
        ...cached,
        fromCache: true
      };
    }
    
    try {
      console.time('AcademicSystemLoad');
      
      // 1. Quick setup check with retry
      let setupCheck;
      try {
        setupCheck = await this.quickSetupCheck();
      } catch (error) {
        // If quick check fails, try fallback
        setupCheck = await this.fallbackQuickSetupCheck();
      }
      
      if (!setupCheck.success) {
        console.timeEnd('AcademicSystemLoad');
        return setupCheck;
      }
      
      const requiresSetup = setupCheck.requiresSetup || !setupCheck.data?.is_setup_complete;
      
      // If setup is incomplete, get essential data for setup guidance
      if (requiresSetup) {
        const essentialData = await this.getEssentialData();
        
        if (!essentialData.success) {
          console.timeEnd('AcademicSystemLoad');
          return essentialData;
        }
        
        const duration = performanceMonitor.end(timerName);
        console.timeEnd('AcademicSystemLoad');
        
        const result = {
          success: true,
          status: 'setup_required',
          data: essentialData.data.data || essentialData.data,
          missingItems: setupCheck.missingItems || setupCheck.data?.missing_items || [],
          performance: {
            totalTime: duration
          },
          requiresSetup: true
        };
        
        academicCache.set(cacheKey, result, 30000); // Cache for 30 seconds
        return result;
      }
      
      // Setup is complete, load lightweight data in parallel
      const [classrooms, subjects, summary] = await Promise.allSettled([
        this.getLightweightClassrooms(),
        this.getEssentialSubjects(),
        this.getClassroomsSummary()
      ]);
      
      const duration = performanceMonitor.end(timerName);
      console.timeEnd('AcademicSystemLoad');
      
      const result = {
        success: true,
        status: 'ready',
        data: {
          classrooms: classrooms.value?.data?.results || classrooms.value?.data?.data?.results || [],
          subjects: subjects.value?.data?.subjects || subjects.value?.data?.results || [],
          categories: subjects.value?.data?.categories || [],
          counts: {
            classrooms: classrooms.value?.data?.count || 0,
            subjects: subjects.value?.totalSubjects || 0,
            summary: summary.value?.data?.total || 0
          }
        },
        performance: {
          totalTime: duration,
          fromCache: setupCheck.fromCache || false
        }
      };
      
      academicCache.set(cacheKey, result, 60000); // Cache for 1 minute
      return result;
      
    } catch (error) {
      performanceMonitor.end(timerName);
      console.timeEnd('AcademicSystemLoad');
      return handleAPIError(error);
    }
  },

  // ==================== ORIGINAL SETUP ENDPOINTS ====================

  checkSetupStatus: async () => {
    const timerName = 'checkSetupStatus';
    performanceMonitor.start(timerName);
    
    try {
      const response = await api.get('/academics/setup/check/');
      const duration = performanceMonitor.end(timerName);
      
      this.logPerformance('setup/check', duration);
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        requiresSetup: !response.data.setup_complete,
        missingItems: response.data.missing_items || []
      };
    } catch (error) {
      performanceMonitor.end(timerName);
      return handleAPIError(error);
    }
  },

  getRequiredSetupItems: async () => {
    try {
      const response = await api.get('/academics/setup/required-items/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  getSetupStatus: async () => {
    try {
      const response = await api.get('/academics/setup/status/');
      return {
        success: true,
        data: response.data,
        status: response.status,
        isSetupComplete: response.data.overall_status === 'complete',
        setupProgress: response.data.setup_progress || 0,
        canCreateAssignments: response.data.can_create_assignments || false,
        canAccessGrades: response.data.can_access_grades || false,
        canAccessTimetable: response.data.can_access_timetable || false
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  validateAcademicSetup: async () => {
    try {
      const response = await api.post('/academics/setup/validate/');
      return {
        success: true,
        data: response.data,
        status: response.status,
        isValid: response.data.is_valid,
        hasErrors: response.data.has_errors,
        hasWarnings: response.data.has_warnings
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  canCreateAssignments: async () => {
    try {
      const response = await api.get('/academics/setup/status/');
      return {
        success: true,
        canCreate: response.data.can_create_assignments || false,
        setupProgress: response.data.setup_progress || 0,
        message: response.data.can_create_assignments 
          ? 'Setup complete. You can create assignments.' 
          : `Setup ${response.data.setup_progress}% complete. Configure more items to create assignments.`
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  // ==================== EXISTING ENDPOINTS WITH FIXED URLS ====================

  getSubjects: async (params = {}) => {
    const timerName = `getSubjects_${JSON.stringify(params)}`;
    performanceMonitor.start(timerName);
    
    try {
      const response = await api.get('/academics/subjects/', { params });
      const duration = performanceMonitor.end(timerName);
      
      this.logPerformance('subjects', duration, response.data.count);
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        count: response.data.count,
        responseTime: duration
      };
    } catch (error) {
      performanceMonitor.end(timerName);
      return handleAPIError(error);
    }
  },

  getClassrooms: async (params = {}) => {
    const timerName = `getClassrooms_${JSON.stringify(params)}`;
    performanceMonitor.start(timerName);
    
    try {
      const response = await api.get('/academics/classrooms/', { params });
      const duration = performanceMonitor.end(timerName);
      
      this.logPerformance('classrooms', duration, response.data.count);
      
      return {
        success: true,
        data: response.data,
        status: response.status,
        count: response.data.count,
        responseTime: duration
      };
    } catch (error) {
      performanceMonitor.end(timerName);
      return handleAPIError(error);
    }
  },

  getAcademicYears: async (params = {}) => {
    try {
      const response = await api.get('/academics/academic-years/', { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  getAcademicTerms: async (params = {}) => {
    try {
      const response = await api.get('/academics/academic-terms/', { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  getGradeLevels: async (params = {}) => {
    try {
      const response = await api.get('/academics/grade-levels/', { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  // ==================== MISSING ENDPOINTS - USE EXISTING ALTERNATIVES ====================

  /**
   * Get upcoming exams - Use exams endpoint with filter
   */
  getUpcomingExams: async (params = {}) => {
    try {
      // Use existing exams endpoint with upcoming filter
      const response = await api.get('/academics/exams/', { 
        params: { ...params, upcoming: true } 
      });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Get today's attendance summary - Use daily summary endpoint
   */
  getTodayAttendance: async () => {
    try {
      const response = await api.get('/academics/reports/daily/attendance-summary/');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  /**
   * Get student grade report - Use existing endpoint
   */
  getStudentGradeReport: async (params = {}) => {
    try {
      const response = await api.get('/academics/reports/student/grades/', { params });
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return handleAPIError(error);
    }
  },

  // ==================== CACHE MANAGEMENT ====================

  clearCache: () => {
    academicCache.clear();
  },

  getCacheStats: () => {
    return {
      size: academicCache.data.size,
      keys: Array.from(academicCache.data.keys())
    };
  }
};

export default academicsAPI;