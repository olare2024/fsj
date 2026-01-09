// ==================== UTILITY FUNCTIONS ====================

export const apiUtils = {
  isTokenExpiring: () => {
    const token = localStorage.getItem('access_token');
    if (!token) return true;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expiresIn = payload.exp * 1000 - Date.now();
      return expiresIn < 5 * 60 * 1000; // 5 minutes
    } catch {
      return true;
    }
  },

  clearAuth: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  isAuthenticated: () => {
    const token = localStorage.getItem('access_token');
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  },

  getUserRole: () => {
    const user = apiUtils.getCurrentUser();
    return user?.role || null;
  },

  hasRole: (role) => {
    const userRole = apiUtils.getUserRole();
    return userRole === role;
  },

  requiresPasswordChange: () => {
    const user = apiUtils.getCurrentUser();
    return user?.requires_password_change || false;
  },

  getDashboardUrl: () => {
    const user = apiUtils.getCurrentUser();
    if (!user) return '/login';
    
    if (user.requires_password_change) {
      return '/change-password';
    }
    
    const role = user.role;
    const dashboardMap = {
      'student': '/student/dashboard',
      'teacher': '/teacher/dashboard',
      'parent': '/parent/dashboard',
      'admin': '/admin/dashboard',
      'staff': '/staff/dashboard',
      'accountant': '/finance/dashboard'
    };
    
    return dashboardMap[role] || '/dashboard';
  },

  initializeAuth: async (authAPI) => {
    const token = localStorage.getItem('access_token');
    if (!token) return null;

    try {
      await authAPI.verifyToken(token);
      
      const userResponse = await authAPI.getCurrentUser();
      if (userResponse.success) {
        localStorage.setItem('user', JSON.stringify(userResponse.data));
        return userResponse.data;
      }
    } catch (error) {
      apiUtils.clearAuth();
    }
    
    return null;
  }
};

export default apiUtils;