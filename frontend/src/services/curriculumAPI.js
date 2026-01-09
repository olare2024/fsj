// src/services/curriculumAPI.js
import api from './api';

const curriculumAPI = {
  // ====================
  // CURRICULUM OVERVIEW
  // ====================
  getCurriculumOverview: async () => {
    try {
      const response = await api.get('/curriculum/overview');
      return response.data;
    } catch (error) {
      console.error('Error fetching curriculum overview:', error);
      throw error;
    }
  },

  getDashboardStats: async () => {
    try {
      const response = await api.get('/curriculum/dashboard-stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching curriculum dashboard stats:', error);
      throw error;
    }
  },

  // ====================
  // SUBJECT MANAGEMENT
  // ====================
  getAllSubjects: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/subjects', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching subjects:', error);
      throw error;
    }
  },

  getSubjectDetails: async (subjectId) => {
    try {
      const response = await api.get(`/curriculum/subjects/${subjectId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching subject details:', error);
      throw error;
    }
  },

  createSubject: async (subjectData) => {
    try {
      const response = await api.post('/curriculum/subjects', subjectData);
      return response.data;
    } catch (error) {
      console.error('Error creating subject:', error);
      throw error;
    }
  },

  updateSubject: async (subjectId, updates) => {
    try {
      const response = await api.put(`/curriculum/subjects/${subjectId}`, updates);
      return response.data;
    } catch (error) {
      console.error('Error updating subject:', error);
      throw error;
    }
  },

  updateSubjectStatus: async (subjectId, status) => {
    try {
      const response = await api.put(`/curriculum/subjects/${subjectId}/status`, { status });
      return response.data;
    } catch (error) {
      console.error('Error updating subject status:', error);
      throw error;
    }
  },

  deleteSubject: async (subjectId) => {
    try {
      const response = await api.delete(`/curriculum/subjects/${subjectId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting subject:', error);
      throw error;
    }
  },

  // ====================
  // SUBJECT UNITS/TOPICS
  // ====================
  getSubjectUnits: async (subjectId, params = {}) => {
    try {
      const response = await api.get(`/curriculum/subjects/${subjectId}/units`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching subject units:', error);
      throw error;
    }
  },

  createSubjectUnit: async (subjectId, unitData) => {
    try {
      const response = await api.post(`/curriculum/subjects/${subjectId}/units`, unitData);
      return response.data;
    } catch (error) {
      console.error('Error creating subject unit:', error);
      throw error;
    }
  },

  updateSubjectUnit: async (unitId, updates) => {
    try {
      const response = await api.put(`/curriculum/units/${unitId}`, updates);
      return response.data;
    } catch (error) {
      console.error('Error updating subject unit:', error);
      throw error;
    }
  },

  reorderUnits: async (subjectId, unitOrder) => {
    try {
      const response = await api.put(`/curriculum/subjects/${subjectId}/reorder-units`, { unit_order: unitOrder });
      return response.data;
    } catch (error) {
      console.error('Error reordering units:', error);
      throw error;
    }
  },

  // ====================
  // LESSON PLANS
  // ====================
  getAllLessonPlans: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/lesson-plans', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching lesson plans:', error);
      throw error;
    }
  },

  getLessonPlanDetails: async (lessonId) => {
    try {
      const response = await api.get(`/curriculum/lesson-plans/${lessonId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching lesson plan details:', error);
      throw error;
    }
  },

  createLessonPlan: async (lessonData) => {
    try {
      const response = await api.post('/curriculum/lesson-plans', lessonData);
      return response.data;
    } catch (error) {
      console.error('Error creating lesson plan:', error);
      throw error;
    }
  },

  updateLessonPlan: async (lessonId, updates) => {
    try {
      const response = await api.put(`/curriculum/lesson-plans/${lessonId}`, updates);
      return response.data;
    } catch (error) {
      console.error('Error updating lesson plan:', error);
      throw error;
    }
  },

  duplicateLessonPlan: async (lessonId, newData = {}) => {
    try {
      const response = await api.post(`/curriculum/lesson-plans/${lessonId}/duplicate`, newData);
      return response.data;
    } catch (error) {
      console.error('Error duplicating lesson plan:', error);
      throw error;
    }
  },

  publishLessonPlan: async (lessonId) => {
    try {
      const response = await api.put(`/curriculum/lesson-plans/${lessonId}/publish`);
      return response.data;
    } catch (error) {
      console.error('Error publishing lesson plan:', error);
      throw error;
    }
  },

  archiveLessonPlan: async (lessonId) => {
    try {
      const response = await api.put(`/curriculum/lesson-plans/${lessonId}/archive`);
      return response.data;
    } catch (error) {
      console.error('Error archiving lesson plan:', error);
      throw error;
    }
  },

  getLessonTemplates: async () => {
    try {
      const response = await api.get('/curriculum/lesson-templates');
      return response.data;
    } catch (error) {
      console.error('Error fetching lesson templates:', error);
      throw error;
    }
  },

  // ====================
  // TEACHING RESOURCES
  // ====================
  getAllResources: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/resources', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching teaching resources:', error);
      throw error;
    }
  },

  getResourceDetails: async (resourceId) => {
    try {
      const response = await api.get(`/curriculum/resources/${resourceId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching resource details:', error);
      throw error;
    }
  },

  addTeachingResource: async (resourceData) => {
    try {
      const response = await api.post('/curriculum/resources', resourceData);
      return response.data;
    } catch (error) {
      console.error('Error adding teaching resource:', error);
      throw error;
    }
  },

  updateResource: async (resourceId, updates) => {
    try {
      const response = await api.put(`/curriculum/resources/${resourceId}`, updates);
      return response.data;
    } catch (error) {
      console.error('Error updating resource:', error);
      throw error;
    }
  },

  deleteResource: async (resourceId) => {
    try {
      const response = await api.delete(`/curriculum/resources/${resourceId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting resource:', error);
      throw error;
    }
  },

  shareResource: async (resourceId, shareData) => {
    try {
      const response = await api.post(`/curriculum/resources/${resourceId}/share`, shareData);
      return response.data;
    } catch (error) {
      console.error('Error sharing resource:', error);
      throw error;
    }
  },

  downloadResource: async (resourceId) => {
    try {
      const response = await api.get(`/curriculum/resources/${resourceId}/download`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error downloading resource:', error);
      throw error;
    }
  },

  previewResource: async (resourceId) => {
    try {
      const response = await api.get(`/curriculum/resources/${resourceId}/preview`);
      return response.data;
    } catch (error) {
      console.error('Error previewing resource:', error);
      throw error;
    }
  },

  // ====================
  // RESOURCE LIBRARY
  // ====================
  getResourceLibrary: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/resource-library', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching resource library:', error);
      throw error;
    }
  },

  getResourceCategories: async () => {
    try {
      const response = await api.get('/curriculum/resource-categories');
      return response.data;
    } catch (error) {
      console.error('Error fetching resource categories:', error);
      throw error;
    }
  },

  addResourceToLibrary: async (resourceData) => {
    try {
      const response = await api.post('/curriculum/resource-library', resourceData);
      return response.data;
    } catch (error) {
      console.error('Error adding resource to library:', error);
      throw error;
    }
  },

  rateResource: async (resourceId, rating, review = '') => {
    try {
      const response = await api.post(`/curriculum/resources/${resourceId}/rate`, {
        rating,
        review
      });
      return response.data;
    } catch (error) {
      console.error('Error rating resource:', error);
      throw error;
    }
  },

  // ====================
  // ASSESSMENT TOOLS
  // ====================
  getAllAssessments: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/assessments', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching assessments:', error);
      throw error;
    }
  },

  getAssessmentDetails: async (assessmentId) => {
    try {
      const response = await api.get(`/curriculum/assessments/${assessmentId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching assessment details:', error);
      throw error;
    }
  },

  createAssessmentTool: async (assessmentData) => {
    try {
      const response = await api.post('/curriculum/assessments', assessmentData);
      return response.data;
    } catch (error) {
      console.error('Error creating assessment tool:', error);
      throw error;
    }
  },

  updateAssessment: async (assessmentId, updates) => {
    try {
      const response = await api.put(`/curriculum/assessments/${assessmentId}`, updates);
      return response.data;
    } catch (error) {
      console.error('Error updating assessment:', error);
      throw error;
    }
  },

  deleteAssessment: async (assessmentId) => {
    try {
      const response = await api.delete(`/curriculum/assessments/${assessmentId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting assessment:', error);
      throw error;
    }
  },

  publishAssessment: async (assessmentId) => {
    try {
      const response = await api.put(`/curriculum/assessments/${assessmentId}/publish`);
      return response.data;
    } catch (error) {
      console.error('Error publishing assessment:', error);
      throw error;
    }
  },

  cloneAssessment: async (assessmentId) => {
    try {
      const response = await api.post(`/curriculum/assessments/${assessmentId}/clone`);
      return response.data;
    } catch (error) {
      console.error('Error cloning assessment:', error);
      throw error;
    }
  },

  // ====================
  // ASSESSMENT QUESTIONS
  // ====================
  getAssessmentQuestions: async (assessmentId) => {
    try {
      const response = await api.get(`/curriculum/assessments/${assessmentId}/questions`);
      return response.data;
    } catch (error) {
      console.error('Error fetching assessment questions:', error);
      throw error;
    }
  },

  addQuestionToAssessment: async (assessmentId, questionData) => {
    try {
      const response = await api.post(`/curriculum/assessments/${assessmentId}/questions`, questionData);
      return response.data;
    } catch (error) {
      console.error('Error adding question to assessment:', error);
      throw error;
    }
  },

  updateQuestion: async (questionId, updates) => {
    try {
      const response = await api.put(`/curriculum/questions/${questionId}`, updates);
      return response.data;
    } catch (error) {
      console.error('Error updating question:', error);
      throw error;
    }
  },

  deleteQuestion: async (questionId) => {
    try {
      const response = await api.delete(`/curriculum/questions/${questionId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting question:', error);
      throw error;
    }
  },

  reorderQuestions: async (assessmentId, questionOrder) => {
    try {
      const response = await api.put(`/curriculum/assessments/${assessmentId}/reorder-questions`, {
        question_order: questionOrder
      });
      return response.data;
    } catch (error) {
      console.error('Error reordering questions:', error);
      throw error;
    }
  },

  // ====================
  // CURRICULUM STANDARDS
  // ====================
  getCurriculumStandards: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/standards', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching curriculum standards:', error);
      throw error;
    }
  },

  getStandardDetails: async (standardId) => {
    try {
      const response = await api.get(`/curriculum/standards/${standardId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching standard details:', error);
      throw error;
    }
  },

  createStandard: async (standardData) => {
    try {
      const response = await api.post('/curriculum/standards', standardData);
      return response.data;
    } catch (error) {
      console.error('Error creating curriculum standard:', error);
      throw error;
    }
  },

  updateStandard: async (standardId, updates) => {
    try {
      const response = await api.put(`/curriculum/standards/${standardId}`, updates);
      return response.data;
    } catch (error) {
      console.error('Error updating standard:', error);
      throw error;
    }
  },

  mapStandardToSubject: async (standardId, subjectId) => {
    try {
      const response = await api.post(`/curriculum/standards/${standardId}/map-subject`, {
        subject_id: subjectId
      });
      return response.data;
    } catch (error) {
      console.error('Error mapping standard to subject:', error);
      throw error;
    }
  },

  // ====================
  // SUBJECT PLANS/SCHEMES OF WORK
  // ====================
  getSubjectPlans: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/subject-plans', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching subject plans:', error);
      throw error;
    }
  },

  getSubjectPlanDetails: async (planId) => {
    try {
      const response = await api.get(`/curriculum/subject-plans/${planId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching subject plan details:', error);
      throw error;
    }
  },

  createSubjectPlan: async (planData) => {
    try {
      const response = await api.post('/curriculum/subject-plans', planData);
      return response.data;
    } catch (error) {
      console.error('Error creating subject plan:', error);
      throw error;
    }
  },

  updateSubjectPlan: async (planId, updates) => {
    try {
      const response = await api.put(`/curriculum/subject-plans/${planId}`, updates);
      return response.data;
    } catch (error) {
      console.error('Error updating subject plan:', error);
      throw error;
    }
  },

  generateSchemeOfWork: async (subjectId, term) => {
    try {
      const response = await api.post('/curriculum/generate-scheme', {
        subject_id: subjectId,
        term
      });
      return response.data;
    } catch (error) {
      console.error('Error generating scheme of work:', error);
      throw error;
    }
  },

  // ====================
  // TEACHER ASSIGNMENTS
  // ====================
  getTeacherAssignments: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/teacher-assignments', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching teacher assignments:', error);
      throw error;
    }
  },

  assignSubjectToTeacher: async (subjectId, teacherId, data = {}) => {
    try {
      const response = await api.post('/curriculum/assign-subject', {
        subject_id: subjectId,
        teacher_id: teacherId,
        ...data
      });
      return response.data;
    } catch (error) {
      console.error('Error assigning subject to teacher:', error);
      throw error;
    }
  },

  updateTeacherAssignment: async (assignmentId, updates) => {
    try {
      const response = await api.put(`/curriculum/teacher-assignments/${assignmentId}`, updates);
      return response.data;
    } catch (error) {
      console.error('Error updating teacher assignment:', error);
      throw error;
    }
  },

  getTeacherWorkload: async (teacherId) => {
    try {
      const response = await api.get(`/curriculum/teachers/${teacherId}/workload`);
      return response.data;
    } catch (error) {
      console.error('Error fetching teacher workload:', error);
      throw error;
    }
  },

  // ====================
  // REVIEW & APPROVAL
  // ====================
  getPendingReviews: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/pending-reviews', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching pending reviews:', error);
      throw error;
    }
  },

  processReview: async (reviewId, reviewData) => {
    try {
      const response = await api.post(`/curriculum/reviews/${reviewId}/process`, reviewData);
      return response.data;
    } catch (error) {
      console.error('Error processing review:', error);
      throw error;
    }
  },

  submitForReview: async (itemType, itemId, reviewers = []) => {
    try {
      const response = await api.post('/curriculum/submit-review', {
        item_type: itemType,
        item_id: itemId,
        reviewers
      });
      return response.data;
    } catch (error) {
      console.error('Error submitting for review:', error);
      throw error;
    }
  },

  getReviewHistory: async (itemType, itemId) => {
    try {
      const response = await api.get('/curriculum/review-history', {
        params: { item_type: itemType, item_id: itemId }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching review history:', error);
      throw error;
    }
  },

  // ====================
  // PERFORMANCE ANALYTICS
  // ====================
  getPerformanceData: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/performance-data', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching performance data:', error);
      throw error;
    }
  },

  getCurriculumAnalytics: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/analytics', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching curriculum analytics:', error);
      throw error;
    }
  },

  getUsageStatistics: async (resourceId = null) => {
    try {
      const response = await api.get('/curriculum/usage-statistics', {
        params: { resource_id: resourceId }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching usage statistics:', error);
      throw error;
    }
  },

  getTeacherPerformance: async (teacherId = null) => {
    try {
      const response = await api.get('/curriculum/teacher-performance', {
        params: { teacher_id: teacherId }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching teacher performance:', error);
      throw error;
    }
  },

  // ====================
  // RECENT UPDATES & ACTIVITY
  // ====================
  getRecentUpdates: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/recent-updates', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching recent updates:', error);
      throw error;
    }
  },

  getActivityFeed: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/activity-feed', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching activity feed:', error);
      throw error;
    }
  },

  // ====================
  // IMPORT/EXPORT
  // ====================
  importCurriculumData: async (importData) => {
    try {
      const response = await api.post('/curriculum/import', importData);
      return response.data;
    } catch (error) {
      console.error('Error importing curriculum data:', error);
      throw error;
    }
  },

  exportCurriculumData: async (exportParams) => {
    try {
      const response = await api.post('/curriculum/export', exportParams, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting curriculum data:', error);
      throw error;
    }
  },

  downloadTemplate: async (templateType) => {
    try {
      const response = await api.get(`/curriculum/templates/${templateType}`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error downloading template:', error);
      throw error;
    }
  },

  // ====================
  // COLLABORATION
  // ====================
  getCollaborators: async (itemType, itemId) => {
    try {
      const response = await api.get('/curriculum/collaborators', {
        params: { item_type: itemType, item_id: itemId }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching collaborators:', error);
      throw error;
    }
  },

  addCollaborator: async (itemType, itemId, collaboratorId, permissions = ['view']) => {
    try {
      const response = await api.post('/curriculum/collaborators', {
        item_type: itemType,
        item_id: itemId,
        collaborator_id: collaboratorId,
        permissions
      });
      return response.data;
    } catch (error) {
      console.error('Error adding collaborator:', error);
      throw error;
    }
  },

  removeCollaborator: async (collaborationId) => {
    try {
      const response = await api.delete(`/curriculum/collaborators/${collaborationId}`);
      return response.data;
    } catch (error) {
      console.error('Error removing collaborator:', error);
      throw error;
    }
  },

  updateCollaboratorPermissions: async (collaborationId, permissions) => {
    try {
      const response = await api.put(`/curriculum/collaborators/${collaborationId}`, { permissions });
      return response.data;
    } catch (error) {
      console.error('Error updating collaborator permissions:', error);
      throw error;
    }
  },

  // ====================
  // VERSION CONTROL
  // ====================
  getVersionHistory: async (itemType, itemId) => {
    try {
      const response = await api.get('/curriculum/version-history', {
        params: { item_type: itemType, item_id: itemId }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching version history:', error);
      throw error;
    }
  },

  restoreVersion: async (versionId) => {
    try {
      const response = await api.post(`/curriculum/versions/${versionId}/restore`);
      return response.data;
    } catch (error) {
      console.error('Error restoring version:', error);
      throw error;
    }
  },

  compareVersions: async (versionId1, versionId2) => {
    try {
      const response = await api.get('/curriculum/compare-versions', {
        params: { version_id_1: versionId1, version_id_2: versionId2 }
      });
      return response.data;
    } catch (error) {
      console.error('Error comparing versions:', error);
      throw error;
    }
  },

  // ====================
  // CURRICULUM MAPPING
  // ====================
  getCurriculumMap: async (academicYear, term) => {
    try {
      const response = await api.get('/curriculum/map', {
        params: { academic_year: academicYear, term }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching curriculum map:', error);
      throw error;
    }
  },

  mapResourceToLesson: async (resourceId, lessonId) => {
    try {
      const response = await api.post('/curriculum/map-resource', {
        resource_id: resourceId,
        lesson_id: lessonId
      });
      return response.data;
    } catch (error) {
      console.error('Error mapping resource to lesson:', error);
      throw error;
    }
  },

  mapAssessmentToStandard: async (assessmentId, standardId) => {
    try {
      const response = await api.post('/curriculum/map-assessment', {
        assessment_id: assessmentId,
        standard_id: standardId
      });
      return response.data;
    } catch (error) {
      console.error('Error mapping assessment to standard:', error);
      throw error;
    }
  },

  // ====================
  // TIMELINE & SCHEDULING
  // ====================
  getCurriculumTimeline: async (subjectId, term) => {
    try {
      const response = await api.get('/curriculum/timeline', {
        params: { subject_id: subjectId, term }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching curriculum timeline:', error);
      throw error;
    }
  },

  getAcademicCalendar: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/academic-calendar', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching academic calendar:', error);
      throw error;
    }
  },

  scheduleCurriculumItem: async (itemType, itemId, scheduleData) => {
    try {
      const response = await api.post('/curriculum/schedule', {
        item_type: itemType,
        item_id: itemId,
        ...scheduleData
      });
      return response.data;
    } catch (error) {
      console.error('Error scheduling curriculum item:', error);
      throw error;
    }
  },

  // ====================
  // TAGS & CATEGORIES
  // ====================
  getAllTags: async () => {
    try {
      const response = await api.get('/curriculum/tags');
      return response.data;
    } catch (error) {
      console.error('Error fetching tags:', error);
      throw error;
    }
  },

  createTag: async (tagData) => {
    try {
      const response = await api.post('/curriculum/tags', tagData);
      return response.data;
    } catch (error) {
      console.error('Error creating tag:', error);
      throw error;
    }
  },

  assignTags: async (itemType, itemId, tags) => {
    try {
      const response = await api.post('/curriculum/assign-tags', {
        item_type: itemType,
        item_id: itemId,
        tags
      });
      return response.data;
    } catch (error) {
      console.error('Error assigning tags:', error);
      throw error;
    }
  },

  // ====================
  // SEARCH
  // ====================
  searchCurriculum: async (query, filters = {}) => {
    try {
      const response = await api.get('/curriculum/search', {
        params: { q: query, ...filters }
      });
      return response.data;
    } catch (error) {
      console.error('Error searching curriculum:', error);
      throw error;
    }
  },

  advancedSearch: async (searchParams) => {
    try {
      const response = await api.post('/curriculum/advanced-search', searchParams);
      return response.data;
    } catch (error) {
      console.error('Error performing advanced search:', error);
      throw error;
    }
  },

  // ====================
  // REPORTS
  // ====================
  generateCurriculumReport: async (reportType, params = {}) => {
    try {
      const response = await api.post('/curriculum/reports', {
        report_type: reportType,
        ...params
      });
      return response.data;
    } catch (error) {
      console.error('Error generating curriculum report:', error);
      throw error;
    }
  },

  getCurriculumSummary: async (academicYear, term) => {
    try {
      const response = await api.get('/curriculum/summary', {
        params: { academic_year: academicYear, term }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching curriculum summary:', error);
      throw error;
    }
  },

  getGapAnalysis: async (subjectId = null) => {
    try {
      const response = await api.get('/curriculum/gap-analysis', {
        params: { subject_id: subjectId }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching gap analysis:', error);
      throw error;
    }
  },

  // ====================
  // SETTINGS & PREFERENCES
  // ====================
  getCurriculumSettings: async () => {
    try {
      const response = await api.get('/curriculum/settings');
      return response.data;
    } catch (error) {
      console.error('Error fetching curriculum settings:', error);
      throw error;
    }
  },

  updateCurriculumSettings: async (settings) => {
    try {
      const response = await api.put('/curriculum/settings', settings);
      return response.data;
    } catch (error) {
      console.error('Error updating curriculum settings:', error);
      throw error;
    }
  },

  getUserPreferences: async () => {
    try {
      const response = await api.get('/curriculum/user-preferences');
      return response.data;
    } catch (error) {
      console.error('Error fetching user preferences:', error);
      throw error;
    }
  },

  updateUserPreferences: async (preferences) => {
    try {
      const response = await api.put('/curriculum/user-preferences', preferences);
      return response.data;
    } catch (error) {
      console.error('Error updating user preferences:', error);
      throw error;
    }
  },

  // ====================
  // NOTIFICATIONS
  // ====================
  getCurriculumNotifications: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/notifications', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching curriculum notifications:', error);
      throw error;
    }
  },

  markNotificationAsRead: async (notificationId) => {
    try {
      const response = await api.put(`/curriculum/notifications/${notificationId}/read`);
      return response.data;
    } catch (error) {
      console.error('Error marking notification as read:', error);
      throw error;
    }
  },

  clearAllNotifications: async () => {
    try {
      const response = await api.delete('/curriculum/notifications');
      return response.data;
    } catch (error) {
      console.error('Error clearing notifications:', error);
      throw error;
    }
  },

  // ====================
  // BACKUP & RESTORE
  // ====================
  backupCurriculumData: async () => {
    try {
      const response = await api.post('/curriculum/backup');
      return response.data;
    } catch (error) {
      console.error('Error backing up curriculum data:', error);
      throw error;
    }
  },

  restoreCurriculumData: async (backupId) => {
    try {
      const response = await api.post(`/curriculum/restore/${backupId}`);
      return response.data;
    } catch (error) {
      console.error('Error restoring curriculum data:', error);
      throw error;
    }
  },

  getBackupHistory: async () => {
    try {
      const response = await api.get('/curriculum/backup-history');
      return response.data;
    } catch (error) {
      console.error('Error fetching backup history:', error);
      throw error;
    }
  },

  // ====================
  // HELPER FUNCTIONS
  // ====================
  validateSubjectData: (data) => {
    const errors = [];
    
    if (!data.name) errors.push('Subject name is required');
    if (!data.code) errors.push('Subject code is required');
    if (!data.type) errors.push('Subject type is required');
    
    return {
      isValid: errors.length === 0,
      errors
    };
  },

  validateLessonPlanData: (data) => {
    const errors = [];
    
    if (!data.title) errors.push('Lesson title is required');
    if (!data.subject_id) errors.push('Subject is required');
    if (!data.class) errors.push('Class is required');
    if (!data.term) errors.push('Term is required');
    if (!data.week) errors.push('Week is required');
    if (!data.objectives || data.objectives.length === 0) errors.push('At least one learning objective is required');
    
    return {
      isValid: errors.length === 0,
      errors
    };
  },

  formatLessonPlanForAPI: (lessonData) => {
    return {
      title: lessonData.title,
      subject_id: lessonData.subjectId,
      class: lessonData.class,
      term: lessonData.term,
      week: lessonData.week,
      duration: lessonData.duration || 40,
      objectives: Array.isArray(lessonData.objectives) ? lessonData.objectives : [lessonData.objectives],
      materials: Array.isArray(lessonData.materials) ? lessonData.materials : [lessonData.materials],
      activities: Array.isArray(lessonData.activities) ? lessonData.activities : [lessonData.activities],
      assessment: lessonData.assessment || '',
      notes: lessonData.notes || '',
      attachments: lessonData.attachments || []
    };
  },

  formatAssessmentForAPI: (assessmentData) => {
    return {
      title: assessmentData.title,
      subject_id: assessmentData.subjectId,
      class: assessmentData.class,
      type: assessmentData.type,
      max_score: assessmentData.maxScore || 100,
      duration: assessmentData.duration || 60,
      questions: assessmentData.questions || [],
      rubric: assessmentData.rubric || '',
      due_date: assessmentData.dueDate,
      instructions: assessmentData.instructions || ''
    };
  },

  // ====================
  // BULK OPERATIONS
  // ====================
  bulkCreateLessons: async (lessonsData) => {
    try {
      const response = await api.post('/curriculum/lessons/bulk-create', lessonsData);
      return response.data;
    } catch (error) {
      console.error('Error bulk creating lessons:', error);
      throw error;
    }
  },

  bulkUpdateResources: async (resourceIds, updates) => {
    try {
      const response = await api.put('/curriculum/resources/bulk-update', {
        resource_ids: resourceIds,
        updates
      });
      return response.data;
    } catch (error) {
      console.error('Error bulk updating resources:', error);
      throw error;
    }
  },

  bulkDeleteItems: async (itemType, itemIds) => {
    try {
      const response = await api.delete('/curriculum/bulk-delete', {
        data: { item_type: itemType, item_ids: itemIds }
      });
      return response.data;
    } catch (error) {
      console.error('Error bulk deleting items:', error);
      throw error;
    }
  },

  // ====================
  // SYSTEM HEALTH
  // ====================
  getSystemHealth: async () => {
    try {
      const response = await api.get('/curriculum/system-health');
      return response.data;
    } catch (error) {
      console.error('Error fetching system health:', error);
      throw error;
    }
  },

  clearCache: async () => {
    try {
      const response = await api.post('/curriculum/clear-cache');
      return response.data;
    } catch (error) {
      console.error('Error clearing cache:', error);
      throw error;
    }
  },

  // ====================
  // AUDIT LOGS
  // ====================
  getAuditLogs: async (params = {}) => {
    try {
      const response = await api.get('/curriculum/audit-logs', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching audit logs:', error);
      throw error;
    }
  }
};

export default curriculumAPI;