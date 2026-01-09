import api from './api.js';

// ==================== NEWS CONSTANTS ====================

export const NEWS_CONSTANTS = {
  STATUS: {
    DRAFT: 'draft',
    PUBLISHED: 'published',
    ARCHIVED: 'archived',
    SCHEDULED: 'scheduled',
    HIDDEN: 'hidden'
  },
  
  CATEGORY: {
    GENERAL: 'general',
    ACADEMICS: 'academics',
    EVENTS: 'events',
    ACHIEVEMENTS: 'achievements',
    SPORTS: 'sports',
    ARTS: 'arts',
    COMMUNITY: 'community',
    TECHNOLOGY: 'technology',
    ANNOUNCEMENTS: 'announcements',
    URGENT: 'urgent'
  },
  
  TYPE: {
    ARTICLE: 'article',
    NOTICE: 'notice',
    ANNOUNCEMENT: 'announcement',
    EVENT: 'event',
    UPDATE: 'update',
    BLOG: 'blog'
  },
  
  PRIORITY: {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
    URGENT: 'urgent'
  },
  
  AUDIENCE: {
    ALL: 'all',
    STUDENTS: 'students',
    PARENTS: 'parents',
    TEACHERS: 'teachers',
    STAFF: 'staff',
    PUBLIC: 'public'
  },
  
  VISIBILITY: {
    PUBLIC: 'public',
    PRIVATE: 'private',
    RESTRICTED: 'restricted'
  },
  
  MAX_TITLE_LENGTH: 200,
  MAX_EXCERPT_LENGTH: 300,
  ITEMS_PER_PAGE: 10,
  CACHE_TTL: 5 * 60 * 1000, // 5 minutes
  MAX_FILE_SIZE: 10 * 1024 * 1024 // 10MB
};

// ==================== CACHE MANAGEMENT ====================

const newsCache = new Map();

const getCacheKey = (endpoint, params = {}) => {
  const paramString = JSON.stringify(params);
  return `${endpoint}_${paramString}`;
};

const setCache = (key, data) => {
  newsCache.set(key, {
    data,
    timestamp: Date.now(),
    ttl: NEWS_CONSTANTS.CACHE_TTL
  });
};

const getCache = (key) => {
  const cached = newsCache.get(key);
  if (!cached) return null;
  
  const isExpired = Date.now() - cached.timestamp > cached.ttl;
  if (isExpired) {
    newsCache.delete(key);
    return null;
  }
  
  return cached.data;
};

const clearCache = (pattern = null) => {
  if (!pattern) {
    newsCache.clear();
  } else {
    for (const [key] of newsCache) {
      if (key.includes(pattern)) {
        newsCache.delete(key);
      }
    }
  }
};

// ==================== ERROR HANDLER ====================

const handleNewsError = (error, defaultMessage = 'An error occurred') => {
  console.error('🔴 News API Error:', error);
  
  if (error.response) {
    const serverError = error.response.data;
    const status = error.response.status;
    
    // Handle specific status codes
    switch (status) {
      case 400:
        return {
          success: false,
          message: serverError.detail || serverError.message || 'Invalid request',
          errors: serverError.errors || serverError.details,
          status: 400,
          data: serverError
        };
      
      case 401:
        return {
          success: false,
          message: 'Authentication required to access news',
          status: 401,
          requiresAuth: true
        };
      
      case 403:
        return {
          success: false,
          message: 'You do not have permission to access this news',
          status: 403,
          forbidden: true
        };
      
      case 404:
        return {
          success: false,
          message: 'News article not found',
          status: 404,
          notFound: true
        };
      
      case 429:
        return {
          success: false,
          message: 'Too many requests. Please try again later.',
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
      message: 'Unable to connect to server. Please check your internet connection.',
      status: 0,
      networkError: true
    };
  } else {
    return {
      success: false,
      message: error.message || defaultMessage,
      status: -1
    };
  }
};

// ==================== NEWS API ====================

export const newsAPI = {
  // ==================== CACHE MANAGEMENT ====================
  
  clearCache,
  
  getCacheStats: () => {
    return {
      size: newsCache.size,
      keys: Array.from(newsCache.keys()),
      entries: Array.from(newsCache.entries()).map(([key, value]) => ({
        key,
        timestamp: new Date(value.timestamp).toISOString(),
        age: Date.now() - value.timestamp,
        ttl: value.ttl
      }))
    };
  },
  
  // ==================== NEWS LISTING & SEARCH ====================
  
  /**
   * Get all news articles with pagination and filtering
   */
  getAllNews: async (params = {}) => {
    const cacheKey = getCacheKey('all_news', params);
    const cached = getCache(cacheKey);
    
    if (cached && !params.refresh) {
      console.log('📦 Serving news from cache:', cacheKey);
      return cached;
    }
    
    try {
      console.log('🔄 Fetching news with params:', params);
      
      const response = await api.get('/news/', { params });
      console.log('✅ News fetched successfully:', response.data.count);
      
      const result = {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count,
        next: response.data.next,
        previous: response.data.previous,
        page: params.page || 1,
        pageSize: params.page_size || NEWS_CONSTANTS.ITEMS_PER_PAGE,
        filters: params,
        timestamp: Date.now()
      };
      
      // Cache the result
      setCache(cacheKey, result);
      
      return result;
    } catch (error) {
      console.error('❌ Error fetching news:', error);
      return handleNewsError(error, 'Failed to fetch news articles');
    }
  },
  
  /**
   * Get latest news (for homepage)
   */
  getLatestNews: async (params = {}) => {
    const defaultParams = {
      ordering: '-published_date',
      status: NEWS_CONSTANTS.STATUS.PUBLISHED,
      page_size: params.limit || 6,
      ...params
    };
    
    return newsAPI.getAllNews(defaultParams);
  },
  
  /**
   * Get featured news articles
   */
  getFeaturedNews: async (limit = 3) => {
    try {
      const response = await api.get('/news/featured/', {
        params: { limit }
      });
      
      return {
        success: true,
        data: response.data,
        count: response.data.length,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error fetching featured news:', error);
      return handleNewsError(error, 'Failed to fetch featured news');
    }
  },
  
  /**
   * Get news by category
   */
  getNewsByCategory: async (category, params = {}) => {
    const categoryParams = {
      category,
      status: NEWS_CONSTANTS.STATUS.PUBLISHED,
      ordering: '-published_date',
      ...params
    };
    
    return newsAPI.getAllNews(categoryParams);
  },
  
  /**
   * Search news articles
   */
  searchNews: async (query, params = {}) => {
    try {
      const searchParams = {
        search: query,
        ordering: '-published_date',
        ...params
      };
      
      const response = await api.get('/news/search/', { params: searchParams });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count,
        query,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error searching news:', error);
      return handleNewsError(error, 'Failed to search news');
    }
  },
  
  /**
   * Get trending news (based on views or likes)
   */
  getTrendingNews: async (period = 'week', limit = 5) => {
    try {
      const response = await api.get('/news/trending/', {
        params: { period, limit }
      });
      
      return {
        success: true,
        data: response.data,
        period,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error fetching trending news:', error);
      return handleNewsError(error, 'Failed to fetch trending news');
    }
  },
  
  // ==================== SINGLE NEWS OPERATIONS ====================
  
  /**
   * Get single news article by ID
   */
  getNewsById: async (newsId, params = {}) => {
    const cacheKey = getCacheKey(`news_${newsId}`, params);
    const cached = getCache(cacheKey);
    
    if (cached && !params.refresh) {
      console.log('📦 Serving single news from cache:', cacheKey);
      return cached;
    }
    
    try {
      console.log('🔄 Fetching news article:', newsId);
      
      const response = await api.get(`/news/${newsId}/`, { params });
      
      const result = {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
      
      // Cache the result
      setCache(cacheKey, result);
      
      // Track view (non-blocking)
      setTimeout(() => {
        newsAPI.trackNewsView(newsId).catch(console.error);
      }, 1000);
      
      return result;
    } catch (error) {
      console.error('❌ Error fetching news article:', error);
      return handleNewsError(error, 'Failed to fetch news article');
    }
  },
  
  /**
   * Get news by slug (SEO friendly)
   */
  getNewsBySlug: async (slug) => {
    try {
      const response = await api.get(`/news/slug/${slug}/`);
      
      return {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error fetching news by slug:', error);
      return handleNewsError(error, 'Failed to fetch news article');
    }
  },
  
  // ==================== NEWS CRUD OPERATIONS ====================
  
  /**
   * Create new news article
   */
  createNews: async (newsData) => {
    try {
      console.log('🔄 Creating news article:', newsData.title);
      
      // Validate required fields
      const requiredFields = ['title', 'content', 'category', 'author'];
      const missingFields = requiredFields.filter(field => !newsData[field]);
      
      if (missingFields.length > 0) {
        return {
          success: false,
          message: `Missing required fields: ${missingFields.join(', ')}`,
          missingFields
        };
      }
      
      // Handle file upload if present
      let formData = null;
      if (newsData.featured_image && newsData.featured_image instanceof File) {
        if (newsData.featured_image.size > NEWS_CONSTANTS.MAX_FILE_SIZE) {
          return {
            success: false,
            message: `File size exceeds ${NEWS_CONSTANTS.MAX_FILE_SIZE / 1024 / 1024}MB limit`,
            maxSize: NEWS_CONSTANTS.MAX_FILE_SIZE
          };
        }
        
        formData = new FormData();
        Object.keys(newsData).forEach(key => {
          if (key === 'featured_image') {
            formData.append(key, newsData[key]);
          } else {
            formData.append(key, newsData[key]);
          }
        });
      }
      
      const response = formData 
        ? await api.post('/news/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
        : await api.post('/news/', newsData);
      
      console.log('✅ News created successfully:', response.data.id);
      
      // Clear relevant cache
      clearCache('all_news');
      
      return {
        success: true,
        message: 'News article created successfully',
        data: response.data,
        id: response.data.id
      };
    } catch (error) {
      console.error('❌ Error creating news:', error);
      return handleNewsError(error, 'Failed to create news article');
    }
  },
  
  /**
   * Update news article
   */
  updateNews: async (newsId, newsData) => {
    try {
      console.log('🔄 Updating news article:', newsId);
      
      // Handle file upload if present
      let formData = null;
      if (newsData.featured_image && newsData.featured_image instanceof File) {
        if (newsData.featured_image.size > NEWS_CONSTANTS.MAX_FILE_SIZE) {
          return {
            success: false,
            message: `File size exceeds ${NEWS_CONSTANTS.MAX_FILE_SIZE / 1024 / 1024}MB limit`,
            maxSize: NEWS_CONSTANTS.MAX_FILE_SIZE
          };
        }
        
        formData = new FormData();
        Object.keys(newsData).forEach(key => {
          if (key === 'featured_image') {
            formData.append(key, newsData[key]);
          } else {
            formData.append(key, newsData[key]);
          }
        });
      }
      
      const response = formData 
        ? await api.patch(`/news/${newsId}/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
        : await api.patch(`/news/${newsId}/`, newsData);
      
      console.log('✅ News updated successfully:', newsId);
      
      // Clear cache for this news and listings
      clearCache(`news_${newsId}`);
      clearCache('all_news');
      
      return {
        success: true,
        message: 'News article updated successfully',
        data: response.data
      };
    } catch (error) {
      console.error('❌ Error updating news:', error);
      return handleNewsError(error, 'Failed to update news article');
    }
  },
  
  /**
   * Delete news article
   */
  deleteNews: async (newsId) => {
    try {
      console.log('🔄 Deleting news article:', newsId);
      
      const response = await api.delete(`/news/${newsId}/`);
      
      console.log('✅ News deleted successfully:', newsId);
      
      // Clear cache
      clearCache(`news_${newsId}`);
      clearCache('all_news');
      
      return {
        success: true,
        message: 'News article deleted successfully',
        data: response.data
      };
    } catch (error) {
      console.error('❌ Error deleting news:', error);
      return handleNewsError(error, 'Failed to delete news article');
    }
  },
  
  /**
   * Publish news article
   */
  publishNews: async (newsId) => {
    try {
      const response = await api.post(`/news/${newsId}/publish/`);
      
      // Clear cache
      clearCache(`news_${newsId}`);
      clearCache('all_news');
      
      return {
        success: true,
        message: 'News article published successfully',
        data: response.data
      };
    } catch (error) {
      console.error('❌ Error publishing news:', error);
      return handleNewsError(error, 'Failed to publish news article');
    }
  },
  
  /**
   * Archive news article
   */
  archiveNews: async (newsId) => {
    try {
      const response = await api.post(`/news/${newsId}/archive/`);
      
      // Clear cache
      clearCache(`news_${newsId}`);
      clearCache('all_news');
      
      return {
        success: true,
        message: 'News article archived successfully',
        data: response.data
      };
    } catch (error) {
      console.error('❌ Error archiving news:', error);
      return handleNewsError(error, 'Failed to archive news article');
    }
  },
  
  // ==================== NEWS ANALYTICS ====================
  
  /**
   * Track news view (increment view count)
   */
  trackNewsView: async (newsId) => {
    try {
      // Use beacon API for better performance if available
      if (navigator.sendBeacon) {
        const data = new FormData();
        data.append('news_id', newsId);
        navigator.sendBeacon(`/api/v1/news/${newsId}/track-view/`, data);
        return { success: true, method: 'beacon' };
      }
      
      // Fallback to regular API call
      await api.post(`/news/${newsId}/track-view/`);
      return { success: true, method: 'api' };
    } catch (error) {
      console.error('❌ Error tracking news view:', error);
      return { success: false, error: error.message };
    }
  },
  
  /**
   * Like news article
   */
  likeNews: async (newsId) => {
    try {
      const response = await api.post(`/news/${newsId}/like/`);
      
      return {
        success: true,
        message: 'News article liked',
        data: response.data
      };
    } catch (error) {
      console.error('❌ Error liking news:', error);
      return handleNewsError(error, 'Failed to like news article');
    }
  },
  
  /**
   * Unlike news article
   */
  unlikeNews: async (newsId) => {
    try {
      const response = await api.post(`/news/${newsId}/unlike/`);
      
      return {
        success: true,
        message: 'News article unliked',
        data: response.data
      };
    } catch (error) {
      console.error('❌ Error unliking news:', error);
      return handleNewsError(error, 'Failed to unlike news article');
    }
  },
  
  /**
   * Get news statistics
   */
  getNewsStats: async (period = 'month') => {
    try {
      const response = await api.get('/news/statistics/', {
        params: { period }
      });
      
      return {
        success: true,
        data: response.data,
        period,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error fetching news statistics:', error);
      return handleNewsError(error, 'Failed to fetch news statistics');
    }
  },
  
  // ==================== COMMENTS & INTERACTIONS ====================
  
  /**
   * Get comments for news article
   */
  getNewsComments: async (newsId, params = {}) => {
    try {
      const response = await api.get(`/news/${newsId}/comments/`, { params });
      
      return {
        success: true,
        data: response.data.results || response.data,
        count: response.data.count,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error fetching comments:', error);
      return handleNewsError(error, 'Failed to fetch comments');
    }
  },
  
  /**
   * Add comment to news article
   */
  addComment: async (newsId, commentData) => {
    try {
      const response = await api.post(`/news/${newsId}/comments/`, commentData);
      
      return {
        success: true,
        message: 'Comment added successfully',
        data: response.data
      };
    } catch (error) {
      console.error('❌ Error adding comment:', error);
      return handleNewsError(error, 'Failed to add comment');
    }
  },
  
  /**
   * Delete comment
   */
  deleteComment: async (newsId, commentId) => {
    try {
      await api.delete(`/news/${newsId}/comments/${commentId}/`);
      
      return {
        success: true,
        message: 'Comment deleted successfully'
      };
    } catch (error) {
      console.error('❌ Error deleting comment:', error);
      return handleNewsError(error, 'Failed to delete comment');
    }
  },
  
  // ==================== CATEGORIES & TAGS ====================
  
  /**
   * Get all news categories
   */
  getCategories: async () => {
    const cacheKey = 'news_categories';
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/news/categories/');
      
      const result = {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      console.error('❌ Error fetching categories:', error);
      return handleNewsError(error, 'Failed to fetch categories');
    }
  },
  
  /**
   * Get all news tags
   */
  getTags: async () => {
    const cacheKey = 'news_tags';
    const cached = getCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const response = await api.get('/news/tags/');
      
      const result = {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
      
      setCache(cacheKey, result);
      return result;
    } catch (error) {
      console.error('❌ Error fetching tags:', error);
      return handleNewsError(error, 'Failed to fetch tags');
    }
  },
  
  // ==================== UTILITY FUNCTIONS ====================
  
  /**
   * Validate news data
   */
  validateNewsData: (newsData) => {
    const errors = [];
    const warnings = [];
    
    // Required fields
    if (!newsData.title?.trim()) {
      errors.push('Title is required');
    } else if (newsData.title.length > NEWS_CONSTANTS.MAX_TITLE_LENGTH) {
      errors.push(`Title must be less than ${NEWS_CONSTANTS.MAX_TITLE_LENGTH} characters`);
    }
    
    if (!newsData.content?.trim()) {
      errors.push('Content is required');
    }
    
    if (!newsData.category) {
      errors.push('Category is required');
    }
    
    // Optional field warnings
    if (newsData.excerpt && newsData.excerpt.length > NEWS_CONSTANTS.MAX_EXCERPT_LENGTH) {
      warnings.push(`Excerpt is long (${newsData.excerpt.length} characters). Consider shortening it.`);
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      hasWarnings: warnings.length > 0
    };
  },
  
  /**
   * Format news data for display
   */
  formatNewsForDisplay: (news) => {
    if (!news) return null;
    
    return {
      id: news.id,
      title: news.title,
      excerpt: news.excerpt || news.content?.substring(0, 150) + '...',
      content: news.content,
      featured_image: news.featured_image,
      category: news.category,
      author: news.author,
      published_date: news.published_date ? new Date(news.published_date) : null,
      read_time: news.read_time || Math.ceil((news.content?.length || 0) / 200) + ' min read',
      views: news.views || 0,
      likes: news.likes || 0,
      comments_count: news.comments_count || 0,
      tags: news.tags || [],
      status: news.status,
      is_featured: news.is_featured || false,
      priority: news.priority || NEWS_CONSTANTS.PRIORITY.MEDIUM,
      audience: news.audience || NEWS_CONSTANTS.AUDIENCE.ALL,
      visibility: news.visibility || NEWS_CONSTANTS.VISIBILITY.PUBLIC
    };
  },
  
  /**
   * Generate SEO-friendly slug
   */
  generateSlug: (title) => {
    return title
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/--+/g, '-')
      .trim();
  },
  
  /**
   * Calculate read time
   */
  calculateReadTime: (content) => {
    const wordsPerMinute = 200;
    const wordCount = content.split(/\s+/).length;
    const readTime = Math.ceil(wordCount / wordsPerMinute);
    return `${readTime} min read`;
  },
  
  /**
   * Get related news articles
   */
  getRelatedNews: async (newsId, limit = 3) => {
    try {
      const response = await api.get(`/news/${newsId}/related/`, {
        params: { limit }
      });
      
      return {
        success: true,
        data: response.data,
        count: response.data.length,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error fetching related news:', error);
      return handleNewsError(error, 'Failed to fetch related news');
    }
  },
  
  /**
   * Upload news image
   */
  uploadNewsImage: async (file) => {
    try {
      if (!file || !(file instanceof File)) {
        return {
          success: false,
          message: 'Invalid file provided'
        };
      }
      
      if (file.size > NEWS_CONSTANTS.MAX_FILE_SIZE) {
        return {
          success: false,
          message: `File size exceeds ${NEWS_CONSTANTS.MAX_FILE_SIZE / 1024 / 1024}MB limit`
        };
      }
      
      const formData = new FormData();
      formData.append('image', file);
      
      const response = await api.post('/news/upload-image/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      return {
        success: true,
        message: 'Image uploaded successfully',
        data: response.data,
        url: response.data.url
      };
    } catch (error) {
      console.error('❌ Error uploading image:', error);
      return handleNewsError(error, 'Failed to upload image');
    }
  },
  
  /**
   * Get news archive (grouped by month/year)
   */
  getNewsArchive: async () => {
    try {
      const response = await api.get('/news/archive/');
      
      return {
        success: true,
        data: response.data,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ Error fetching news archive:', error);
      return handleNewsError(error, 'Failed to fetch news archive');
    }
  },
  
  /**
   * Get news by author
   */
  getNewsByAuthor: async (authorId, params = {}) => {
    try {
      const authorParams = {
        author: authorId,
        ...params
      };
      
      return newsAPI.getAllNews(authorParams);
    } catch (error) {
      console.error('❌ Error fetching news by author:', error);
      return handleNewsError(error, 'Failed to fetch author news');
    }
  },
  
  // ==================== HEALTH CHECK ====================
  
  /**
   * Check news API health
   */
  healthCheck: async () => {
    try {
      const startTime = Date.now();
      const response = await api.get('/news/health/', {
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
   * Test API connectivity
   */
  testConnectivity: async () => {
    const endpoints = [
      { method: 'GET', path: '/news/' },
      { method: 'GET', path: '/news/categories/' },
      { method: 'OPTIONS', path: '/news/' }
    ];
    
    const results = [];
    
    for (const endpoint of endpoints) {
      try {
        const response = await api({
          method: endpoint.method,
          url: endpoint.path,
          timeout: 3000
        });
        
        results.push({
          endpoint: endpoint.path,
          method: endpoint.method,
          status: response.status,
          success: true,
          responseTime: response.config.metadata?.responseTime || 'N/A'
        });
      } catch (error) {
        results.push({
          endpoint: endpoint.path,
          method: endpoint.method,
          status: error.response?.status || 0,
          success: false,
          error: error.message
        });
      }
    }
    
    return {
      success: results.every(r => r.success),
      results,
      timestamp: Date.now()
    };
  }
};

export default newsAPI;