// src/services/counselingAPI.js
import api from './api';

const counselingAPI = {
  // ====================
  // COUNSELING OVERVIEW
  // ====================
  getCounselingOverview: async () => {
    try {
      const response = await api.get('/counseling/overview');
      return response.data;
    } catch (error) {
      console.error('Error fetching counseling overview:', error);
      throw error;
    }
  },

  getDashboardStats: async () => {
    try {
      const response = await api.get('/counseling/dashboard-stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  },

  // ====================
  // STUDENT COUNSELING
  // ====================
  getAllStudents: async (params = {}) => {
    try {
      const response = await api.get('/counseling/students', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching students:', error);
      throw error;
    }
  },

  getStudentDetails: async (studentId) => {
    try {
      const response = await api.get(`/counseling/students/${studentId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching student details:', error);
      throw error;
    }
  },

  getStudentCounselingHistory: async (studentId, params = {}) => {
    try {
      const response = await api.get(`/counseling/students/${studentId}/sessions`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching student counseling history:', error);
      throw error;
    }
  },

  getStudentRiskAssessment: async (studentId) => {
    try {
      const response = await api.get(`/counseling/students/${studentId}/risk-assessment`);
      return response.data;
    } catch (error) {
      console.error('Error fetching student risk assessment:', error);
      throw error;
    }
  },

  updateStudentCounselingStatus: async (studentId, data) => {
    try {
      const response = await api.put(`/counseling/students/${studentId}/status`, data);
      return response.data;
    } catch (error) {
      console.error('Error updating student counseling status:', error);
      throw error;
    }
  },

  // ====================
  // COUNSELING SESSIONS
  // ====================
  getAllSessions: async (params = {}) => {
    try {
      const response = await api.get('/counseling/sessions', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching counseling sessions:', error);
      throw error;
    }
  },

  getSessionDetails: async (sessionId) => {
    try {
      const response = await api.get(`/counseling/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching session details:', error);
      throw error;
    }
  },

  createSession: async (data) => {
    try {
      const response = await api.post('/counseling/sessions', data);
      return response.data;
    } catch (error) {
      console.error('Error creating counseling session:', error);
      throw error;
    }
  },

  updateSession: async (sessionId, data) => {
    try {
      const response = await api.put(`/counseling/sessions/${sessionId}`, data);
      return response.data;
    } catch (error) {
      console.error('Error updating counseling session:', error);
      throw error;
    }
  },

  cancelSession: async (sessionId, reason) => {
    try {
      const response = await api.put(`/counseling/sessions/${sessionId}/cancel`, { reason });
      return response.data;
    } catch (error) {
      console.error('Error canceling counseling session:', error);
      throw error;
    }
  },

  rescheduleSession: async (sessionId, newDate, newTime) => {
    try {
      const response = await api.put(`/counseling/sessions/${sessionId}/reschedule`, {
        new_date: newDate,
        new_time: newTime
      });
      return response.data;
    } catch (error) {
      console.error('Error rescheduling counseling session:', error);
      throw error;
    }
  },

  addSessionNotes: async (sessionId, notes) => {
    try {
      const response = await api.post(`/counseling/sessions/${sessionId}/notes`, { notes });
      return response.data;
    } catch (error) {
      console.error('Error adding session notes:', error);
      throw error;
    }
  },

  addSessionFollowUp: async (sessionId, followUpData) => {
    try {
      const response = await api.post(`/counseling/sessions/${sessionId}/follow-ups`, followUpData);
      return response.data;
    } catch (error) {
      console.error('Error adding session follow-up:', error);
      throw error;
    }
  },

  // ====================
  // REFERRALS
  // ====================
  getAllReferrals: async (params = {}) => {
    try {
      const response = await api.get('/counseling/referrals', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching referrals:', error);
      throw error;
    }
  },

  createReferral: async (data) => {
    try {
      const response = await api.post('/counseling/referrals', data);
      return response.data;
    } catch (error) {
      console.error('Error creating referral:', error);
      throw error;
    }
  },

  updateReferralStatus: async (referralId, status, notes = '') => {
    try {
      const response = await api.put(`/counseling/referrals/${referralId}/status`, {
        status,
        notes
      });
      return response.data;
    } catch (error) {
      console.error('Error updating referral status:', error);
      throw error;
    }
  },

  escalateReferral: async (referralId, escalationReason) => {
    try {
      const response = await api.post(`/counseling/referrals/${referralId}/escalate`, {
        escalation_reason: escalationReason
      });
      return response.data;
    } catch (error) {
      console.error('Error escalating referral:', error);
      throw error;
    }
  },

  // ====================
  // ASSESSMENTS & SURVEYS
  // ====================
  getAvailableAssessments: async () => {
    try {
      const response = await api.get('/counseling/assessments');
      return response.data;
    } catch (error) {
      console.error('Error fetching available assessments:', error);
      throw error;
    }
  },

  getStudentAssessments: async (studentId) => {
    try {
      const response = await api.get(`/counseling/students/${studentId}/assessments`);
      return response.data;
    } catch (error) {
      console.error('Error fetching student assessments:', error);
      throw error;
    }
  },

  administerAssessment: async (studentId, assessmentId, data) => {
    try {
      const response = await api.post(`/counseling/students/${studentId}/assessments/${assessmentId}`, data);
      return response.data;
    } catch (error) {
      console.error('Error administering assessment:', error);
      throw error;
    }
  },

  getAssessmentResults: async (assessmentRecordId) => {
    try {
      const response = await api.get(`/counseling/assessments/results/${assessmentRecordId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching assessment results:', error);
      throw error;
    }
  },

  createWellnessSurvey: async (surveyData) => {
    try {
      const response = await api.post('/counseling/wellness-surveys', surveyData);
      return response.data;
    } catch (error) {
      console.error('Error creating wellness survey:', error);
      throw error;
    }
  },

  getSurveyResponses: async (surveyId) => {
    try {
      const response = await api.get(`/counseling/wellness-surveys/${surveyId}/responses`);
      return response.data;
    } catch (error) {
      console.error('Error fetching survey responses:', error);
      throw error;
    }
  },

  // ====================
  // INTERVENTION PROGRAMS
  // ====================
  getAllInterventions: async (params = {}) => {
    try {
      const response = await api.get('/counseling/interventions', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching interventions:', error);
      throw error;
    }
  },

  getInterventionDetails: async (interventionId) => {
    try {
      const response = await api.get(`/counseling/interventions/${interventionId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching intervention details:', error);
      throw error;
    }
  },

  createIntervention: async (data) => {
    try {
      const response = await api.post('/counseling/interventions', data);
      return response.data;
    } catch (error) {
      console.error('Error creating intervention:', error);
      throw error;
    }
  },

  updateIntervention: async (interventionId, data) => {
    try {
      const response = await api.put(`/counseling/interventions/${interventionId}`, data);
      return response.data;
    } catch (error) {
      console.error('Error updating intervention:', error);
      throw error;
    }
  },

  enrollStudentInIntervention: async (interventionId, studentId) => {
    try {
      const response = await api.post(`/counseling/interventions/${interventionId}/enroll`, {
        student_id: studentId
      });
      return response.data;
    } catch (error) {
      console.error('Error enrolling student in intervention:', error);
      throw error;
    }
  },

  trackInterventionProgress: async (interventionId, studentId, progressData) => {
    try {
      const response = await api.post(`/counseling/interventions/${interventionId}/progress`, {
        student_id: studentId,
        ...progressData
      });
      return response.data;
    } catch (error) {
      console.error('Error tracking intervention progress:', error);
      throw error;
    }
  },

  // ====================
  // CRISIS MANAGEMENT
  // ====================
  getCrisisAlerts: async (params = {}) => {
    try {
      const response = await api.get('/counseling/crisis-alerts', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching crisis alerts:', error);
      throw error;
    }
  },

  createCrisisAlert: async (data) => {
    try {
      const response = await api.post('/counseling/crisis-alerts', data);
      return response.data;
    } catch (error) {
      console.error('Error creating crisis alert:', error);
      throw error;
    }
  },

  updateCrisisAlertStatus: async (alertId, status, notes = '') => {
    try {
      const response = await api.put(`/counseling/crisis-alerts/${alertId}/status`, {
        status,
        notes
      });
      return response.data;
    } catch (error) {
      console.error('Error updating crisis alert status:', error);
      throw error;
    }
  },

  getEmergencyContacts: async () => {
    try {
      const response = await api.get('/counseling/emergency-contacts');
      return response.data;
    } catch (error) {
      console.error('Error fetching emergency contacts:', error);
      throw error;
    }
  },

  addEmergencyContact: async (contactData) => {
    try {
      const response = await api.post('/counseling/emergency-contacts', contactData);
      return response.data;
    } catch (error) {
      console.error('Error adding emergency contact:', error);
      throw error;
    }
  },

  // ====================
  // PARENT/GUARDIAN ENGAGEMENT
  // ====================
  getParentContacts: async (studentId) => {
    try {
      const response = await api.get(`/counseling/students/${studentId}/parents`);
      return response.data;
    } catch (error) {
      console.error('Error fetching parent contacts:', error);
      throw error;
    }
  },

  scheduleParentMeeting: async (data) => {
    try {
      const response = await api.post('/counseling/parent-meetings', data);
      return response.data;
    } catch (error) {
      console.error('Error scheduling parent meeting:', error);
      throw error;
    }
  },

  logParentContact: async (studentId, contactData) => {
    try {
      const response = await api.post(`/counseling/students/${studentId}/parent-contacts`, contactData);
      return response.data;
    } catch (error) {
      console.error('Error logging parent contact:', error);
      throw error;
    }
  },

  sendParentUpdate: async (studentId, message) => {
    try {
      const response = await api.post(`/counseling/students/${studentId}/parent-updates`, {
        message
      });
      return response.data;
    } catch (error) {
      console.error('Error sending parent update:', error);
      throw error;
    }
  },

  // ====================
  // SUPPORT GROUPS
  // ====================
  getAllSupportGroups: async (params = {}) => {
    try {
      const response = await api.get('/counseling/support-groups', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching support groups:', error);
      throw error;
    }
  },

  createSupportGroup: async (data) => {
    try {
      const response = await api.post('/counseling/support-groups', data);
      return response.data;
    } catch (error) {
      console.error('Error creating support group:', error);
      throw error;
    }
  },

  addStudentToSupportGroup: async (groupId, studentId) => {
    try {
      const response = await api.post(`/counseling/support-groups/${groupId}/members`, {
        student_id: studentId
      });
      return response.data;
    } catch (error) {
      console.error('Error adding student to support group:', error);
      throw error;
    }
  },

  recordGroupSession: async (groupId, sessionData) => {
    try {
      const response = await api.post(`/counseling/support-groups/${groupId}/sessions`, sessionData);
      return response.data;
    } catch (error) {
      console.error('Error recording group session:', error);
      throw error;
    }
  },

  // ====================
  // RESOURCES & TRAINING
  // ====================
  getCounselingResources: async (category = '') => {
    try {
      const response = await api.get('/counseling/resources', {
        params: { category }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching counseling resources:', error);
      throw error;
    }
  },

  addCounselingResource: async (resourceData) => {
    try {
      const response = await api.post('/counseling/resources', resourceData);
      return response.data;
    } catch (error) {
      console.error('Error adding counseling resource:', error);
      throw error;
    }
  },

  getProfessionalDevelopment: async () => {
    try {
      const response = await api.get('/counseling/professional-development');
      return response.data;
    } catch (error) {
      console.error('Error fetching professional development:', error);
      throw error;
    }
  },

  enrollInTraining: async (trainingId) => {
    try {
      const response = await api.post(`/counseling/training/${trainingId}/enroll`);
      return response.data;
    } catch (error) {
      console.error('Error enrolling in training:', error);
      throw error;
    }
  },

  // ====================
  // REPORTING & ANALYTICS
  // ====================
  getCounselingAnalytics: async (params = {}) => {
    try {
      const response = await api.get('/counseling/analytics', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching counseling analytics:', error);
      throw error;
    }
  },

  generateCounselingReport: async (reportType, params = {}) => {
    try {
      const response = await api.post('/counseling/reports', {
        report_type: reportType,
        ...params
      });
      return response.data;
    } catch (error) {
      console.error('Error generating counseling report:', error);
      throw error;
    }
  },

  getMonthlySummary: async (month, year) => {
    try {
      const response = await api.get('/counseling/monthly-summary', {
        params: { month, year }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching monthly summary:', error);
      throw error;
    }
  },

  getTrendAnalysis: async (period = '6months') => {
    try {
      const response = await api.get('/counseling/trend-analysis', {
        params: { period }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching trend analysis:', error);
      throw error;
    }
  },

  // ====================
  // APPOINTMENT MANAGEMENT
  // ====================
  getCounselorSchedule: async (counselorId = null) => {
    try {
      const response = await api.get('/counseling/schedule', {
        params: { counselor_id: counselorId }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching counselor schedule:', error);
      throw error;
    }
  },

  getAvailableSlots: async (date, duration = 60) => {
    try {
      const response = await api.get('/counseling/available-slots', {
        params: { date, duration }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching available slots:', error);
      throw error;
    }
  },

  bookAppointment: async (appointmentData) => {
    try {
      const response = await api.post('/counseling/appointments', appointmentData);
      return response.data;
    } catch (error) {
      console.error('Error booking appointment:', error);
      throw error;
    }
  },

  updateAppointment: async (appointmentId, updates) => {
    try {
      const response = await api.put(`/counseling/appointments/${appointmentId}`, updates);
      return response.data;
    } catch (error) {
      console.error('Error updating appointment:', error);
      throw error;
    }
  },

  // ====================
  // DOCUMENTATION & NOTES
  // ====================
  getStudentCaseNotes: async (studentId) => {
    try {
      const response = await api.get(`/counseling/students/${studentId}/case-notes`);
      return response.data;
    } catch (error) {
      console.error('Error fetching student case notes:', error);
      throw error;
    }
  },

  addCaseNote: async (studentId, noteData) => {
    try {
      const response = await api.post(`/counseling/students/${studentId}/case-notes`, noteData);
      return response.data;
    } catch (error) {
      console.error('Error adding case note:', error);
      throw error;
    }
  },

  updateCaseNote: async (noteId, updates) => {
    try {
      const response = await api.put(`/counseling/case-notes/${noteId}`, updates);
      return response.data;
    } catch (error) {
      console.error('Error updating case note:', error);
      throw error;
    }
  },

  getTreatmentPlans: async (studentId) => {
    try {
      const response = await api.get(`/counseling/students/${studentId}/treatment-plans`);
      return response.data;
    } catch (error) {
      console.error('Error fetching treatment plans:', error);
      throw error;
    }
  },

  createTreatmentPlan: async (studentId, planData) => {
    try {
      const response = await api.post(`/counseling/students/${studentId}/treatment-plans`, planData);
      return response.data;
    } catch (error) {
      console.error('Error creating treatment plan:', error);
      throw error;
    }
  },

  // ====================
  // SETTINGS & PREFERENCES
  // ====================
  getCounselorProfile: async (counselorId = null) => {
    try {
      const response = await api.get('/counseling/counselor-profile', {
        params: { counselor_id: counselorId }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching counselor profile:', error);
      throw error;
    }
  },

  updateCounselorProfile: async (profileData) => {
    try {
      const response = await api.put('/counseling/counselor-profile', profileData);
      return response.data;
    } catch (error) {
      console.error('Error updating counselor profile:', error);
      throw error;
    }
  },

  getNotificationSettings: async () => {
    try {
      const response = await api.get('/counseling/notification-settings');
      return response.data;
    } catch (error) {
      console.error('Error fetching notification settings:', error);
      throw error;
    }
  },

  updateNotificationSettings: async (settings) => {
    try {
      const response = await api.put('/counseling/notification-settings', settings);
      return response.data;
    } catch (error) {
      console.error('Error updating notification settings:', error);
      throw error;
    }
  },

  // ====================
  // INTEGRATION & EXPORTS
  // ====================
  syncWithStudentRecords: async (studentIds = []) => {
    try {
      const response = await api.post('/counseling/sync-students', { student_ids: studentIds });
      return response.data;
    } catch (error) {
      console.error('Error syncing with student records:', error);
      throw error;
    }
  },

  exportCounselingData: async (exportType, params = {}) => {
    try {
      const response = await api.post('/counseling/export', {
        export_type: exportType,
        ...params
      }, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting counseling data:', error);
      throw error;
    }
  },

  backupCounselingRecords: async () => {
    try {
      const response = await api.post('/counseling/backup');
      return response.data;
    } catch (error) {
      console.error('Error backing up counseling records:', error);
      throw error;
    }
  },

  // ====================
  // SYSTEM & ADMIN
  // ====================
  getSystemHealth: async () => {
    try {
      const response = await api.get('/counseling/system-health');
      return response.data;
    } catch (error) {
      console.error('Error fetching system health:', error);
      throw error;
    }
  },

  getAuditLogs: async (params = {}) => {
    try {
      const response = await api.get('/counseling/audit-logs', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching audit logs:', error);
      throw error;
    }
  },

  clearCache: async () => {
    try {
      const response = await api.post('/counseling/clear-cache');
      return response.data;
    } catch (error) {
      console.error('Error clearing cache:', error);
      throw error;
    }
  },

  // ====================
  // QUICK ACTIONS
  // ====================
  sendReminder: async (sessionId, reminderType = 'email') => {
    try {
      const response = await api.post(`/counseling/sessions/${sessionId}/reminders`, {
        reminder_type: reminderType
      });
      return response.data;
    } catch (error) {
      console.error('Error sending reminder:', error);
      throw error;
    }
  },

  markAsUrgent: async (recordId, recordType, reason) => {
    try {
      const response = await api.post('/counseling/mark-urgent', {
        record_id: recordId,
        record_type: recordType,
        reason
      });
      return response.data;
    } catch (error) {
      console.error('Error marking as urgent:', error);
      throw error;
    }
  },

  createQuickNote: async (studentId, note) => {
    try {
      const response = await api.post(`/counseling/students/${studentId}/quick-notes`, {
        note
      });
      return response.data;
    } catch (error) {
      console.error('Error creating quick note:', error);
      throw error;
    }
  },

  // ====================
  // BULK OPERATIONS
  // ====================
  bulkUpdateSessions: async (sessionIds, updates) => {
    try {
      const response = await api.put('/counseling/sessions/bulk-update', {
        session_ids: sessionIds,
        updates
      });
      return response.data;
    } catch (error) {
      console.error('Error bulk updating sessions:', error);
      throw error;
    }
  },

  bulkCreateReferrals: async (referralsData) => {
    try {
      const response = await api.post('/counseling/referrals/bulk-create', referralsData);
      return response.data;
    } catch (error) {
      console.error('Error bulk creating referrals:', error);
      throw error;
    }
  },

  exportStudentReports: async (studentIds, reportType) => {
    try {
      const response = await api.post('/counseling/export-student-reports', {
        student_ids: studentIds,
        report_type: reportType
      }, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting student reports:', error);
      throw error;
    }
  },

  // ====================
  // REAL-TIME UPDATES
  // ====================
  subscribeToUpdates: async (subscriptionData) => {
    try {
      const response = await api.post('/counseling/subscribe', subscriptionData);
      return response.data;
    } catch (error) {
      console.error('Error subscribing to updates:', error);
      throw error;
    }
  },

  getRecentUpdates: async (since) => {
    try {
      const response = await api.get('/counseling/recent-updates', {
        params: { since }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching recent updates:', error);
      throw error;
    }
  },

  // ====================
  // HELPER FUNCTIONS
  // ====================
  validateSessionData: (data) => {
    const errors = [];
    
    if (!data.student_id) errors.push('Student ID is required');
    if (!data.scheduled_date) errors.push('Scheduled date is required');
    if (!data.scheduled_time) errors.push('Scheduled time is required');
    if (!data.session_type) errors.push('Session type is required');
    if (!data.counselor_id) errors.push('Counselor ID is required');
    
    return {
      isValid: errors.length === 0,
      errors
    };
  },

  formatSessionForAPI: (sessionData) => {
    return {
      student_id: sessionData.studentId,
      counselor_id: sessionData.counselorId,
      scheduled_date: sessionData.date,
      scheduled_time: sessionData.time,
      session_type: sessionData.type,
      duration: sessionData.duration || 60,
      location: sessionData.location || 'Counseling Office',
      reason: sessionData.reason || '',
      notes: sessionData.notes || '',
      priority: sessionData.priority || 'normal'
    };
  },

  formatReferralForAPI: (referralData) => {
    return {
      student_id: referralData.studentId,
      referred_by: referralData.referredBy,
      referral_reason: referralData.reason,
      urgency_level: referralData.urgency || 'medium',
      supporting_evidence: referralData.evidence || '',
      requested_actions: referralData.actions || [],
      notes: referralData.notes || ''
    };
  }
};

export default counselingAPI;