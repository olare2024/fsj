import api from './api.js';

// ==================== SEARCH CONSTANTS ====================

export const SEARCH_CONSTANTS = {
  // Searchable entity types
  ENTITY_TYPES: {
    STUDENT: 'student',
    TEACHER: 'teacher',
    PARENT: 'parent',
    STAFF: 'staff',
    COURSE: 'course',
    CLASS: 'class',
    SUBJECT: 'subject',
    ASSIGNMENT: 'assignment',
    EVENT: 'event',
    NEWS: 'news',
    DOCUMENT: 'document',
    RESOURCE: 'resource',
    USER: 'user',
    GRADE: 'grade',
    PAYMENT: 'payment',
    ANNOUNCEMENT: 'announcement',
    LIBRARY_BOOK: 'library_book',
    FACILITY: 'facility',
    TRANSPORT: 'transport'
  },
  
  // Search scopes
  SCOPE: {
    GLOBAL: 'global',
    ACADEMIC: 'academic',
    ADMINISTRATIVE: 'administrative',
    FINANCIAL: 'financial',
    LIBRARY: 'library',
    EVENTS: 'events',
    RESOURCES: 'resources'
  },
  
  // Search operators
  OPERATOR: {
    CONTAINS: 'contains',
    EQUALS: 'equals',
    STARTS_WITH: 'starts_with',
    ENDS_WITH: 'ends_with',
    GREATER_THAN: 'greater_than',
    LESS_THAN: 'less_than',
    BETWEEN: 'between',
    IN: 'in'
  },
  
  // Sort options
  SORT: {
    RELEVANCE: 'relevance',
    DATE_ASC: 'date_asc',
    DATE_DESC: 'date_desc',
    NAME_ASC: 'name_asc',
    NAME_DESC: 'name_desc',
    SCORE_ASC: 'score_asc',
    SCORE_DESC: 'score_desc'
  },
  
  // Filter operators
  FILTER_TYPE: {
    TEXT: 'text',
    NUMBER: 'number',
    DATE: 'date',
    BOOLEAN: 'boolean',
    SELECT: 'select',
    MULTI_SELECT: 'multi_select',
    RANGE: 'range'
  },
  
  // Default limits
  DEFAULT_LIMIT: 20,
  MAX_LIMIT: 100,
  SUGGESTION_LIMIT: 10,
  
  // Cache settings
  CACHE_TTL: {
    SUGGESTIONS: 1 * 60 * 1000, // 1 minute
    RESULTS: 5 * 60 * 1000, // 5 minutes
    FILTERS: 30 * 60 * 1000 // 30 minutes
  }
};

// ==================== CACHE MANAGEMENT ====================

const searchCache = new Map();
const cacheTimeouts = new Map();

const getCacheKey = (endpoint, params = {}) => {
  const paramString = JSON.stringify(params);
  return `${endpoint}_${paramString}`;
};

const setCache = (key, data, ttl = SEARCH_CONSTANTS.CACHE_TTL.RESULTS) => {
  searchCache.set(key, {
    data,
    timestamp: Date.now(),
    ttl
  });
  
  // Clear existing timeout if any
  if (cacheTimeouts.has(key)) {
    clearTimeout(cacheTimeouts.get(key));
  }
  
  // Set new timeout for auto-cleanup
  const timeout = setTimeout(() => {
    searchCache.delete(key);
    cacheTimeouts.delete(key);
  }, ttl);
  
  cacheTimeouts.set(key, timeout);
};

const getCache = (key) => {
  const cached = searchCache.get(key);
  if (!cached) return null;
  
  const isExpired = Date.now() - cached.timestamp > cached.ttl;
  if (isExpired) {
    searchCache.delete(key);
    if (cacheTimeouts.has(key)) {
      clearTimeout(cacheTimeouts.get(key));
      cacheTimeouts.delete(key);
    }
    return null;
  }
  
  return cached.data;
};

const clearCache = (pattern = null) => {
  if (!pattern) {
    searchCache.clear();
    cacheTimeouts.forEach(timeout => clearTimeout(timeout));
    cacheTimeouts.clear();
  } else {
    for (const [key] of searchCache) {
      if (key.includes(pattern)) {
        searchCache.delete(key);
        if (cacheTimeouts.has(key)) {
          clearTimeout(cacheTimeouts.get(key));
          cacheTimeouts.delete(key);
        }
      }
    }
  }
};

// ==================== ERROR HANDLER ====================

const handleSearchError = (error, defaultMessage = 'Search error occurred') => {
  console.error('🔍 Search API Error:', error);
  
  if (error.response) {
    const serverError = error.response.data;
    const status = error.response.status;
    
    // Handle specific status codes
    switch (status) {
      case 400:
        return {
          success: false,
          message: serverError.detail || serverError.message || 'Invalid search parameters',
          errors: serverError.errors || serverError.details,
          status: 400,
          data: serverError
        };
      
      case 401:
        return {
          success: false,
          message: 'Authentication required for search',
          status: 401,
          requiresAuth: true
        };
      
      case 403:
        return {
          success: false,
          message: 'You do not have permission to search this content',
          status: 403,
          forbidden: true
        };
      
      case 404:
        return {
          success: false,
          message: 'Search endpoint not found',
          status: 404,
          notFound: true
        };
      
      case 429:
        return {
          success: false,
          message: 'Too many search requests. Please try again later.',
          status: 429,
          rateLimited: true
        };
      
      default:
        return {
          success: false,
          message: serverError.detail || serverError.message || defaultMessage,
          status: status,
          data: serverError
        };
    }
  } else if (error.request) {
    return {
      success: false,
      message: 'Unable to connect to search service. Please check your internet connection.',
      status: 0,
      networkError: true
    };
  } else if (error.code === 'ECONNABORTED') {
    return {
      success: false,
      message: 'Search request timed out. Please try again.',
      status: -1,
      timeout: true
    };
  } else {
    return {
      success: false,
      message: error.message || defaultMessage,
      status: -1
    };
  }
};

// ==================== SEARCH API ====================

export const searchAPI = {
  // ==================== CACHE MANAGEMENT ====================
  
  clearCache,
  
  getCacheStats: () => {
    return {
      size: searchCache.size,
      timeouts: cacheTimeouts.size,
      keys: Array.from(searchCache.keys()),
      entries: Array.from(searchCache.entries()).map(([key, value]) => ({
        key,
        timestamp: new Date(value.timestamp).toISOString(),
        age: Date.now() - value.timestamp,
        ttl: value.ttl,
        expiresIn: value.ttl - (Date.now() - value.timestamp)
      }))
    };
  },
  
  // ==================== UNIVERSAL SEARCH ====================
  
  /**
   * Universal search across all entities
   */
  search: async (query, params = {}) => {
    const cacheKey = getCacheKey('search', { query, ...params });
    const cached = getCache(cacheKey);
    
    if (cached && !params.refresh) {
      console.log('📦 Serving search from cache:', query);
      return cached;
    }
    
    try {
      console.log('🔍 Searching for:', query);
      
      const response = await api.post('/search/', {
        query: query.trim(),
        ...params
      });
      
      console.log('✅ Search results:', response.data.total || 0, 'items found');
      
      const result = {
        success: true,
        data: response.data.results || response.data,
        total: response.data.total || response.data.count || 0,
        query: query.trim(),
        scope: params.scope || SEARCH_CONSTANTS.SCOPE.GLOBAL,
        filters: params.filters || {},
        pagination: {
          page: response.data.page || 1,
          pages: response.data.pages || 1,
          page_size: response.data.page_size || SEARCH_CONSTANTS.DEFAULT_LIMIT,
          has_next: response.data.has_next || false,
          has_previous: response.data.has_previous || false,
          next: response.data.next,
          previous: response.data.previous
        },
        facets: response.data.facets || {},
        suggestions: response.data.suggestions || [],
        timestamp: Date.now(),
        responseTime: response.config.metadata?.responseTime || null
      };
      
      setCache(cacheKey, result);
      
      // Track search analytics
      searchAPI.trackSearchAnalytics(query, result.total, params.scope).catch(console.error);
      
      return result;
    } catch (error) {
      console.error('❌ Search error:', error);
      return handleSearchError(error, 'Search failed');
    }
  },
  
  /**
   * Quick search for suggestions (autocomplete)
   */
  quickSearch: async (query, params = {}) => {
    const cacheKey = getCacheKey('quick_search', { query, ...params });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/search/quick/', {
        params: {
          q: query.trim(),
          limit: SEARCH_CONSTANTS.SUGGESTION_LIMIT,
          ...params
        }
      });
      
      const result = {
        success: true,
        data: response.data.suggestions || response.data,
        query: query.trim(),
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, SEARCH_CONSTANTS.CACHE_TTL.SUGGESTIONS);
      return result;
    } catch (error) {
      console.error('❌ Quick search error:', error);
      return handleSearchError(error, 'Quick search failed');
    }
  },
  
  /**
   * Advanced search with complex queries
   */
  advancedSearch: async (searchCriteria, params = {}) => {
    try {
      console.log('🔍 Advanced search with criteria:', searchCriteria);
      
      const response = await api.post('/search/advanced/', {
        criteria: searchCriteria,
        ...params
      });
      
      const result = {
        success: true,
        data: response.data.results || response.data,
        total: response.data.total || response.data.count || 0,
        criteria: searchCriteria,
        timestamp: Date.now(),
        responseTime: response.config.metadata?.responseTime || null
      };
      
      return result;
    } catch (error) {
      console.error('❌ Advanced search error:', error);
      return handleSearchError(error, 'Advanced search failed');
    }
  },
  
  // ==================== ENTITY-SPECIFIC SEARCH ====================
  
  /**
   * Search students
   */
  searchStudents: async (query, params = {}) => {
    const entityParams = {
      entity_type: SEARCH_CONSTANTS.ENTITY_TYPES.STUDENT,
      ...params
    };
    
    return searchAPI.search(query, entityParams);
  },
  
  /**
   * Search teachers
   */
  searchTeachers: async (query, params = {}) => {
    const entityParams = {
      entity_type: SEARCH_CONSTANTS.ENTITY_TYPES.TEACHER,
      ...params
    };
    
    return searchAPI.search(query, entityParams);
  },
  
  /**
   * Search parents
   */
  searchParents: async (query, params = {}) => {
    const entityParams = {
      entity_type: SEARCH_CONSTANTS.ENTITY_TYPES.PARENT,
      ...params
    };
    
    return searchAPI.search(query, entityParams);
  },
  
  /**
   * Search courses
   */
  searchCourses: async (query, params = {}) => {
    const entityParams = {
      entity_type: SEARCH_CONSTANTS.ENTITY_TYPES.COURSE,
      ...params
    };
    
    return searchAPI.search(query, entityParams);
  },
  
  /**
   * Search classes
   */
  searchClasses: async (query, params = {}) => {
    const entityParams = {
      entity_type: SEARCH_CONSTANTS.ENTITY_TYPES.CLASS,
      ...params
    };
    
    return searchAPI.search(query, entityParams);
  },
  
  /**
   * Search events
   */
  searchEvents: async (query, params = {}) => {
    const entityParams = {
      entity_type: SEARCH_CONSTANTS.ENTITY_TYPES.EVENT,
      ...params
    };
    
    return searchAPI.search(query, entityParams);
  },
  
  /**
   * Search assignments
   */
  searchAssignments: async (query, params = {}) => {
    const entityParams = {
      entity_type: SEARCH_CONSTANTS.ENTITY_TYPES.ASSIGNMENT,
      ...params
    };
    
    return searchAPI.search(query, entityParams);
  },
  
  /**
   * Search documents
   */
  searchDocuments: async (query, params = {}) => {
    const entityParams = {
      entity_type: SEARCH_CONSTANTS.ENTITY_TYPES.DOCUMENT,
      ...params
    };
    
    return searchAPI.search(query, entityParams);
  },
  
  // ==================== SCOPED SEARCH ====================
  
  /**
   * Search within academic scope
   */
  searchAcademic: async (query, params = {}) => {
    const scopeParams = {
      scope: SEARCH_CONSTANTS.SCOPE.ACADEMIC,
      ...params
    };
    
    return searchAPI.search(query, scopeParams);
  },
  
  /**
   * Search within financial scope
   */
  searchFinancial: async (query, params = {}) => {
    const scopeParams = {
      scope: SEARCH_CONSTANTS.SCOPE.FINANCIAL,
      ...params
    };
    
    return searchAPI.search(query, scopeParams);
  },
  
  /**
   * Search within library scope
   */
  searchLibrary: async (query, params = {}) => {
    const scopeParams = {
      scope: SEARCH_CONSTANTS.SCOPE.LIBRARY,
      ...params
    };
    
    return searchAPI.search(query, scopeParams);
  },
  
  // ==================== FILTERS & FACETS ====================
  
  /**
   * Get available search filters for a scope
   */
  getFilters: async (scope = SEARCH_CONSTANTS.SCOPE.GLOBAL) => {
    const cacheKey = getCacheKey('filters', { scope });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/search/filters/', {
        params: { scope }
      });
      
      const result = {
        success: true,
        data: response.data,
        scope,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, SEARCH_CONSTANTS.CACHE_TTL.FILTERS);
      return result;
    } catch (error) {
      console.error('❌ Error getting filters:', error);
      return handleSearchError(error, 'Failed to get search filters');
    }
  },
  
  /**
   * Get search facets for a query
   */
  getFacets: async (query, params = {}) => {
    try {
      const response = await api.get('/search/facets/', {
        params: { q: query, ...params }
      });
      
      return {
        success: true,
        data: response.data,
        query,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error getting facets:', error);
      return handleSearchError(error, 'Failed to get search facets');
    }
  },
  
  // ==================== SUGGESTIONS & AUTOCOMPLETE ====================
  
  /**
   * Get search suggestions
   */
  getSuggestions: async (query, limit = SEARCH_CONSTANTS.SUGGESTION_LIMIT) => {
    const cacheKey = getCacheKey('suggestions', { query, limit });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/search/suggestions/', {
        params: { q: query, limit }
      });
      
      const result = {
        success: true,
        data: response.data.suggestions || response.data,
        query,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, SEARCH_CONSTANTS.CACHE_TTL.SUGGESTIONS);
      return result;
    } catch (error) {
      console.error('❌ Error getting suggestions:', error);
      return handleSearchError(error, 'Failed to get search suggestions');
    }
  },
  
  /**
   * Get popular searches
   */
  getPopularSearches: async (limit = 10, period = 'week') => {
    const cacheKey = getCacheKey('popular_searches', { limit, period });
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/search/popular/', {
        params: { limit, period }
      });
      
      const result = {
        success: true,
        data: response.data,
        period,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result, SEARCH_CONSTANTS.CACHE_TTL.FILTERS);
      return result;
    } catch (error) {
      console.error('❌ Error getting popular searches:', error);
      return handleSearchError(error, 'Failed to get popular searches');
    }
  },
  
  /**
   * Get search history for current user
   */
  getSearchHistory: async (limit = 20) => {
    try {
      const response = await api.get('/search/history/', {
        params: { limit }
      });
      
      return {
        success: true,
        data: response.data.history || response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error getting search history:', error);
      return handleSearchError(error, 'Failed to get search history');
    }
  },
  
  /**
   * Clear search history
   */
  clearSearchHistory: async () => {
    try {
      const response = await api.delete('/search/history/');
      
      return {
        success: true,
        message: response.data.message || 'Search history cleared',
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error clearing search history:', error);
      return handleSearchError(error, 'Failed to clear search history');
    }
  },
  
  // ==================== SEARCH ANALYTICS ====================
  
  /**
   * Track search analytics
   */
  trackSearchAnalytics: async (query, resultsCount, scope = null) => {
    try {
      // Use beacon API for better performance if available
      if (navigator.sendBeacon) {
        const data = new FormData();
        data.append('query', query);
        data.append('results_count', resultsCount);
        data.append('scope', scope || SEARCH_CONSTANTS.SCOPE.GLOBAL);
        data.append('timestamp', Date.now());
        data.append('user_agent', navigator.userAgent);
        
        navigator.sendBeacon('/api/v1/search/analytics/track/', data);
        return { success: true, method: 'beacon' };
      }
      
      // Fallback to regular API call
      await api.post('/search/analytics/track/', {
        query,
        results_count: resultsCount,
        scope: scope || SEARCH_CONSTANTS.SCOPE.GLOBAL,
        timestamp: Date.now(),
        user_agent: navigator.userAgent
      });
      
      return { success: true, method: 'api' };
    } catch (error) {
      console.error('❌ Error tracking search analytics:', error);
      return { success: false, error: error.message };
    }
  },
  
  /**
   * Get search analytics
   */
  getSearchAnalytics: async (period = 'week') => {
    try {
      const response = await api.get('/search/analytics/', {
        params: { period }
      });
      
      return {
        success: true,
        data: response.data,
        period,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error getting search analytics:', error);
      return handleSearchError(error, 'Failed to get search analytics');
    }
  },
  
  // ==================== SEARCH INDEX MANAGEMENT ====================
  
  /**
   * Reindex search data
   */
  reindex: async (entityType = null) => {
    try {
      const response = await api.post('/search/reindex/', {
        entity_type: entityType
      });
      
      return {
        success: true,
        message: response.data.message || 'Reindexing started',
        job_id: response.data.job_id,
        entity_type: entityType,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error reindexing:', error);
      return handleSearchError(error, 'Failed to reindex search data');
    }
  },
  
  /**
   * Get index status
   */
  getIndexStatus: async () => {
    try {
      const response = await api.get('/search/index-status/');
      
      return {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error getting index status:', error);
      return handleSearchError(error, 'Failed to get index status');
    }
  },
  
  // ==================== UTILITY FUNCTIONS ====================
  
  /**
   * Build search query string
   */
  buildQueryString: (params) => {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        if (Array.isArray(value)) {
          value.forEach(v => searchParams.append(key, v));
        } else if (typeof value === 'object') {
          searchParams.append(key, JSON.stringify(value));
        } else {
          searchParams.append(key, value);
        }
      }
    });
    
    return searchParams.toString();
  },
  
  /**
   * Parse search query parameters
   */
  parseQueryParams: (queryString) => {
    const params = new URLSearchParams(queryString);
    const result = {};
    
    for (const [key, value] of params) {
      try {
        // Try to parse as JSON (for arrays/objects)
        result[key] = JSON.parse(value);
      } catch {
        // Keep as string if not valid JSON
        result[key] = value;
      }
    }
    
    return result;
  },
  
  /**
   * Format search result for display
   */
  formatSearchResult: (result) => {
    if (!result) return null;
    
    const entityType = result.entity_type || result.type;
    const entityId = result.id || result._id;
    
    const formatted = {
      id: entityId,
      type: entityType,
      title: result.title || result.name || result.full_name || result.email || 'Untitled',
      description: result.description || result.excerpt || result.summary || result.details || '',
      path: result.path || result.url || result.link || `/${entityType}s/${entityId}`,
      relevance: result.relevance || result.score || 0,
      metadata: result.metadata || {},
      entity_data: result.entity_data || result.data || result,
      created_at: result.created_at || result.created,
      updated_at: result.updated_at || result.updated
    };
    
    // Add type-specific formatting
    switch (entityType) {
      case SEARCH_CONSTANTS.ENTITY_TYPES.STUDENT:
        formatted.icon = 'person';
        formatted.badge = 'Student';
        formatted.description = `Grade: ${result.grade_level || result.class || 'N/A'} | ID: ${result.student_id || entityId}`;
        break;
        
      case SEARCH_CONSTANTS.ENTITY_TYPES.TEACHER:
        formatted.icon = 'person-badge';
        formatted.badge = 'Teacher';
        formatted.description = `Department: ${result.department || 'N/A'} | Subjects: ${result.subjects?.join(', ') || 'N/A'}`;
        break;
        
      case SEARCH_CONSTANTS.ENTITY_TYPES.COURSE:
        formatted.icon = 'journal';
        formatted.badge = 'Course';
        formatted.description = `Code: ${result.code || 'N/A'} | Credits: ${result.credits || 0}`;
        break;
        
      case SEARCH_CONSTANTS.ENTITY_TYPES.EVENT:
        formatted.icon = 'calendar-event';
        formatted.badge = 'Event';
        formatted.description = `Date: ${result.date ? new Date(result.date).toLocaleDateString() : 'N/A'} | Location: ${result.location || 'N/A'}`;
        break;
        
      case SEARCH_CONSTANTS.ENTITY_TYPES.ASSIGNMENT:
        formatted.icon = 'journal-text';
        formatted.badge = 'Assignment';
        formatted.description = `Due: ${result.due_date ? new Date(result.due_date).toLocaleDateString() : 'N/A'} | Status: ${result.status || 'N/A'}`;
        break;
        
      default:
        formatted.icon = 'file-text';
        formatted.badge = entityType?.replace('_', ' ') || 'Item';
    }
    
    return formatted;
  },
  
  /**
   * Get icon for entity type
   */
  getEntityIcon: (entityType) => {
    const iconMap = {
      [SEARCH_CONSTANTS.ENTITY_TYPES.STUDENT]: 'bi-person',
      [SEARCH_CONSTANTS.ENTITY_TYPES.TEACHER]: 'bi-person-badge',
      [SEARCH_CONSTANTS.ENTITY_TYPES.PARENT]: 'bi-people',
      [SEARCH_CONSTANTS.ENTITY_TYPES.STAFF]: 'bi-person-badge',
      [SEARCH_CONSTANTS.ENTITY_TYPES.COURSE]: 'bi-journal',
      [SEARCH_CONSTANTS.ENTITY_TYPES.CLASS]: 'bi-mortarboard',
      [SEARCH_CONSTANTS.ENTITY_TYPES.SUBJECT]: 'bi-book',
      [SEARCH_CONSTANTS.ENTITY_TYPES.ASSIGNMENT]: 'bi-journal-text',
      [SEARCH_CONSTANTS.ENTITY_TYPES.EVENT]: 'bi-calendar-event',
      [SEARCH_CONSTANTS.ENTITY_TYPES.NEWS]: 'bi-newspaper',
      [SEARCH_CONSTANTS.ENTITY_TYPES.DOCUMENT]: 'bi-file-text',
      [SEARCH_CONSTANTS.ENTITY_TYPES.RESOURCE]: 'bi-folder',
      [SEARCH_CONSTANTS.ENTITY_TYPES.USER]: 'bi-person-circle',
      [SEARCH_CONSTANTS.ENTITY_TYPES.GRADE]: 'bi-journal-check',
      [SEARCH_CONSTANTS.ENTITY_TYPES.PAYMENT]: 'bi-cash',
      [SEARCH_CONSTANTS.ENTITY_TYPES.ANNOUNCEMENT]: 'bi-megaphone',
      [SEARCH_CONSTANTS.ENTITY_TYPES.LIBRARY_BOOK]: 'bi-book',
      [SEARCH_CONSTANTS.ENTITY_TYPES.FACILITY]: 'bi-building',
      [SEARCH_CONSTANTS.ENTITY_TYPES.TRANSPORT]: 'bi-bus-front'
    };
    
    return iconMap[entityType] || 'bi-file-text';
  },
  
  /**
   * Get color for entity type
   */
  getEntityColor: (entityType) => {
    const colorMap = {
      [SEARCH_CONSTANTS.ENTITY_TYPES.STUDENT]: 'primary',
      [SEARCH_CONSTANTS.ENTITY_TYPES.TEACHER]: 'warning',
      [SEARCH_CONSTANTS.ENTITY_TYPES.PARENT]: 'info',
      [SEARCH_CONSTANTS.ENTITY_TYPES.STAFF]: 'secondary',
      [SEARCH_CONSTANTS.ENTITY_TYPES.COURSE]: 'success',
      [SEARCH_CONSTANTS.ENTITY_TYPES.CLASS]: 'primary',
      [SEARCH_CONSTANTS.ENTITY_TYPES.SUBJECT]: 'info',
      [SEARCH_CONSTANTS.ENTITY_TYPES.ASSIGNMENT]: 'danger',
      [SEARCH_CONSTANTS.ENTITY_TYPES.EVENT]: 'warning',
      [SEARCH_CONSTANTS.ENTITY_TYPES.NEWS]: 'success',
      [SEARCH_CONSTANTS.ENTITY_TYPES.DOCUMENT]: 'secondary',
      [SEARCH_CONSTANTS.ENTITY_TYPES.RESOURCE]: 'info',
      [SEARCH_CONSTANTS.ENTITY_TYPES.USER]: 'primary',
      [SEARCH_CONSTANTS.ENTITY_TYPES.GRADE]: 'success',
      [SEARCH_CONSTANTS.ENTITY_TYPES.PAYMENT]: 'success',
      [SEARCH_CONSTANTS.ENTITY_TYPES.ANNOUNCEMENT]: 'warning',
      [SEARCH_CONSTANTS.ENTITY_TYPES.LIBRARY_BOOK]: 'info',
      [SEARCH_CONSTANTS.ENTITY_TYPES.FACILITY]: 'secondary',
      [SEARCH_CONSTANTS.ENTITY_TYPES.TRANSPORT]: 'primary'
    };
    
    return colorMap[entityType] || 'secondary';
  },
  
  /**
   * Calculate relevance score (for local filtering)
   */
  calculateRelevance: (item, query) => {
    if (!query.trim()) return 0;
    
    const queryWords = query.toLowerCase().split(/\s+/);
    let score = 0;
    
    // Check title
    if (item.title) {
      const title = item.title.toLowerCase();
      queryWords.forEach(word => {
        if (title.includes(word)) score += 10;
        if (title.startsWith(word)) score += 5;
      });
    }
    
    // Check description
    if (item.description) {
      const description = item.description.toLowerCase();
      queryWords.forEach(word => {
        if (description.includes(word)) score += 5;
      });
    }
    
    // Check tags
    if (item.tags && Array.isArray(item.tags)) {
      const tags = item.tags.map(t => t.toLowerCase());
      queryWords.forEach(word => {
        if (tags.includes(word)) score += 3;
      });
    }
    
    // Exact match bonus
    if (item.title && item.title.toLowerCase() === query.toLowerCase()) {
      score += 20;
    }
    
    return score;
  },
  
  // ==================== LOCAL SEARCH FUNCTIONS ====================
  
  /**
   * Perform local search (client-side filtering)
   */
  localSearch: async (data, query, options = {}) => {
    try {
      const startTime = Date.now();
      const { 
        limit = SEARCH_CONSTANTS.DEFAULT_LIMIT, 
        offset = 0,
        sortBy = SEARCH_CONSTANTS.SORT.RELEVANCE,
        fields = ['title', 'description', 'tags']
      } = options;
      
      if (!query.trim()) {
        return {
          success: true,
          data: [],
          total: 0,
          query,
          timestamp: Date.now(),
          responseTime: 0
        };
      }
      
      // Calculate relevance for each item
      const itemsWithRelevance = data.map(item => ({
        ...item,
        relevance: searchAPI.calculateRelevance(item, query)
      }));
      
      // Filter items with relevance > 0
      const filteredItems = itemsWithRelevance.filter(item => item.relevance > 0);
      
      // Sort items
      let sortedItems = [...filteredItems];
      
      switch (sortBy) {
        case SEARCH_CONSTANTS.SORT.RELEVANCE:
          sortedItems.sort((a, b) => b.relevance - a.relevance);
          break;
        case SEARCH_CONSTANTS.SORT.DATE_DESC:
          sortedItems.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
          break;
        case SEARCH_CONSTANTS.SORT.NAME_ASC:
          sortedItems.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
          break;
      }
      
      // Apply pagination
      const paginatedItems = sortedItems.slice(offset, offset + limit);
      
      const endTime = Date.now();
      
      return {
        success: true,
        data: paginatedItems,
        total: filteredItems.length,
        query,
        pagination: {
          page: Math.floor(offset / limit) + 1,
          pages: Math.ceil(filteredItems.length / limit),
          page_size: limit,
          has_next: offset + limit < filteredItems.length,
          has_previous: offset > 0
        },
        timestamp: Date.now(),
        responseTime: endTime - startTime
      };
    } catch (error) {
      console.error('❌ Local search error:', error);
      return {
        success: false,
        message: 'Local search failed',
        error: error.message
      };
    }
  },
  
  // ==================== HEALTH & MONITORING ====================
  
  /**
   * Check search service health
   */
  healthCheck: async () => {
    try {
      const startTime = Date.now();
      const response = await api.get('/search/health/', {
        timeout: 5000
      });
      const endTime = Date.now();
      
      return {
        success: true,
        status: 'healthy',
        responseTime: endTime - startTime,
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        success: false,
        status: 'unhealthy',
        message: error.message,
        timestamp: Date.now()
      };
    }
  },
  
  /**
   * Get search service status
   */
  getServiceStatus: async () => {
    try {
      const response = await api.get('/search/status/');
      
      return {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        success: false,
        status: 'offline',
        message: error.message,
        timestamp: Date.now()
      };
    }
  },
  
  /**
   * Test search functionality
   */
  testSearch: async (testQuery = 'test') => {
    const tests = [
      { name: 'Quick Search', func: () => searchAPI.quickSearch(testQuery) },
      { name: 'Universal Search', func: () => searchAPI.search(testQuery, { limit: 5 }) },
      { name: 'Suggestions', func: () => searchAPI.getSuggestions(testQuery) },
      { name: 'Filters', func: () => searchAPI.getFilters() }
    ];
    
    const results = [];
    
    for (const test of tests) {
      try {
        const startTime = Date.now();
        const result = await test.func();
        const endTime = Date.now();
        
        results.push({
          test: test.name,
          success: result.success || false,
          responseTime: endTime - startTime,
          data: result.data ? `${Array.isArray(result.data) ? result.data.length : 1} items` : 'No data',
          error: result.success ? null : result.message
        });
      } catch (error) {
        results.push({
          test: test.name,
          success: false,
          responseTime: null,
          data: null,
          error: error.message
        });
      }
    }
    
    return {
      success: results.every(r => r.success),
      tests: results,
      timestamp: Date.now()
    };
  }
};

export default searchAPI;