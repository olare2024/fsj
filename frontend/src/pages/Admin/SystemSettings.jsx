import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function SystemSettings() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({});
  const [isSaving, setIsSaving] = useState(false);

  // Mock settings data - in real app, this would come from API
  useEffect(() => {
    const mockSettings = {
      general: {
        schoolName: 'Delvok Academy',
        schoolCode: 'DEL001',
        academicYear: '2024',
        timezone: 'Africa/Nairobi',
        language: 'en',
        dateFormat: 'DD/MM/YYYY',
        currency: 'KES'
      },
      academic: {
        currentTerm: 'Term 1',
        termStart: '2024-01-08',
        termEnd: '2024-04-05',
        gradingSystem: 'percentage',
        passingGrade: 50,
        maxAbsenceDays: 10,
        autoPromotion: true
      },
      cbc: {
        competencyThreshold: 70,
        assessmentTypes: ['Written', 'Practical', 'Oral', 'Project'],
        reportingFrequency: 'weekly',
        parentAccess: true,
        competencyTracking: true
      },
      cambridge: {
        examRegistrationDeadline: '2024-08-31',
        predictedGrades: true,
        universityPathways: true,
        internationalBenchmarking: true,
        examFees: 15000
      },
      notifications: {
        emailNotifications: true,
        smsNotifications: true,
        parentAlerts: true,
        teacherAlerts: true,
        adminAlerts: true,
        lowGradeThreshold: 60,
        absenceAlertThreshold: 3
      },
      security: {
        passwordExpiry: 90,
        sessionTimeout: 60,
        twoFactorAuth: false,
        loginAttempts: 5,
        ipWhitelist: [],
        auditLogging: true
      }
    };

    setSettings(mockSettings);
  }, []);

  const handleSettingChange = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  const handleSaveSettings = async (category) => {
    setIsSaving(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsSaving(false);
    alert(`${category.charAt(0).toUpperCase() + category.slice(1)} settings saved successfully!`);
  };

  const handleSaveAll = async () => {
    setIsSaving(true);
    // Simulate API call for all settings
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsSaving(false);
    alert('All settings saved successfully!');
  };

  const handleResetSettings = (category) => {
    if (window.confirm(`Are you sure you want to reset ${category} settings to default?`)) {
      // In real app, this would reset to default values
      alert(`${category} settings reset to default.`);
    }
  };

  const renderGeneralSettings = () => (
    <div className="row">
      <div className="col-md-6">
        <div className="mb-3">
          <label className="form-label">School Name</label>
          <input
            type="text"
            className="form-control"
            value={settings.general?.schoolName || ''}
            onChange={(e) => handleSettingChange('general', 'schoolName', e.target.value)}
          />
        </div>
        <div className="mb-3">
          <label className="form-label">School Code</label>
          <input
            type="text"
            className="form-control"
            value={settings.general?.schoolCode || ''}
            onChange={(e) => handleSettingChange('general', 'schoolCode', e.target.value)}
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Academic Year</label>
          <input
            type="text"
            className="form-control"
            value={settings.general?.academicYear || ''}
            onChange={(e) => handleSettingChange('general', 'academicYear', e.target.value)}
          />
        </div>
      </div>
      <div className="col-md-6">
        <div className="mb-3">
          <label className="form-label">Timezone</label>
          <select
            className="form-select"
            value={settings.general?.timezone || ''}
            onChange={(e) => handleSettingChange('general', 'timezone', e.target.value)}
          >
            <option value="Africa/Nairobi">East Africa Time (EAT)</option>
            <option value="UTC">UTC</option>
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">Language</label>
          <select
            className="form-select"
            value={settings.general?.language || ''}
            onChange={(e) => handleSettingChange('general', 'language', e.target.value)}
          >
            <option value="en">English</option>
            <option value="sw">Kiswahili</option>
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">Currency</label>
          <select
            className="form-select"
            value={settings.general?.currency || ''}
            onChange={(e) => handleSettingChange('general', 'currency', e.target.value)}
          >
            <option value="KES">Kenyan Shilling (KES)</option>
            <option value="USD">US Dollar (USD)</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderAcademicSettings = () => (
    <div className="row">
      <div className="col-md-6">
        <div className="mb-3">
          <label className="form-label">Current Term</label>
          <select
            className="form-select"
            value={settings.academic?.currentTerm || ''}
            onChange={(e) => handleSettingChange('academic', 'currentTerm', e.target.value)}
          >
            <option value="Term 1">Term 1</option>
            <option value="Term 2">Term 2</option>
            <option value="Term 3">Term 3</option>
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">Term Start Date</label>
          <input
            type="date"
            className="form-control"
            value={settings.academic?.termStart || ''}
            onChange={(e) => handleSettingChange('academic', 'termStart', e.target.value)}
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Term End Date</label>
          <input
            type="date"
            className="form-control"
            value={settings.academic?.termEnd || ''}
            onChange={(e) => handleSettingChange('academic', 'termEnd', e.target.value)}
          />
        </div>
      </div>
      <div className="col-md-6">
        <div className="mb-3">
          <label className="form-label">Grading System</label>
          <select
            className="form-select"
            value={settings.academic?.gradingSystem || ''}
            onChange={(e) => handleSettingChange('academic', 'gradingSystem', e.target.value)}
          >
            <option value="percentage">Percentage</option>
            <option value="letter">Letter Grade</option>
            <option value="points">Points</option>
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">Passing Grade (%)</label>
          <input
            type="number"
            className="form-control"
            min="0"
            max="100"
            value={settings.academic?.passingGrade || 50}
            onChange={(e) => handleSettingChange('academic', 'passingGrade', parseInt(e.target.value))}
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Maximum Absence Days</label>
          <input
            type="number"
            className="form-control"
            min="0"
            value={settings.academic?.maxAbsenceDays || 10}
            onChange={(e) => handleSettingChange('academic', 'maxAbsenceDays', parseInt(e.target.value))}
          />
        </div>
        <div className="form-check form-switch mb-3">
          <input
            className="form-check-input"
            type="checkbox"
            checked={settings.academic?.autoPromotion || false}
            onChange={(e) => handleSettingChange('academic', 'autoPromotion', e.target.checked)}
          />
          <label className="form-check-label">Automatic Promotion</label>
        </div>
      </div>
    </div>
  );

  const renderCBCSettings = () => (
    <div className="row">
      <div className="col-md-6">
        <div className="mb-3">
          <label className="form-label">Competency Threshold (%)</label>
          <input
            type="number"
            className="form-control"
            min="0"
            max="100"
            value={settings.cbc?.competencyThreshold || 70}
            onChange={(e) => handleSettingChange('cbc', 'competencyThreshold', parseInt(e.target.value))}
          />
          <div className="form-text">
            Minimum percentage required for competency mastery
          </div>
        </div>
        <div className="mb-3">
          <label className="form-label">Assessment Types</label>
          <div>
            {settings.cbc?.assessmentTypes?.map((type, index) => (
              <div key={index} className="form-check">
                <input
                  className="form-check-input"
                  type="checkbox"
                  checked={true}
                  readOnly
                />
                <label className="form-check-label">{type}</label>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="col-md-6">
        <div className="mb-3">
          <label className="form-label">Reporting Frequency</label>
          <select
            className="form-select"
            value={settings.cbc?.reportingFrequency || 'weekly'}
            onChange={(e) => handleSettingChange('cbc', 'reportingFrequency', e.target.value)}
          >
            <option value="weekly">Weekly</option>
            <option value="biweekly">Bi-weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>
        <div className="form-check form-switch mb-3">
          <input
            className="form-check-input"
            type="checkbox"
            checked={settings.cbc?.parentAccess || false}
            onChange={(e) => handleSettingChange('cbc', 'parentAccess', e.target.checked)}
          />
          <label className="form-check-label">Parent Access to Competency Reports</label>
        </div>
        <div className="form-check form-switch mb-3">
          <input
            className="form-check-input"
            type="checkbox"
            checked={settings.cbc?.competencyTracking || false}
            onChange={(e) => handleSettingChange('cbc', 'competencyTracking', e.target.checked)}
          />
          <label className="form-check-label">Enable Competency Tracking</label>
        </div>
      </div>
    </div>
  );

  const renderCambridgeSettings = () => (
    <div className="row">
      <div className="col-md-6">
        <div className="mb-3">
          <label className="form-label">Exam Registration Deadline</label>
          <input
            type="date"
            className="form-control"
            value={settings.cambridge?.examRegistrationDeadline || ''}
            onChange={(e) => handleSettingChange('cambridge', 'examRegistrationDeadline', e.target.value)}
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Exam Fees (KES)</label>
          <input
            type="number"
            className="form-control"
            value={settings.cambridge?.examFees || 0}
            onChange={(e) => handleSettingChange('cambridge', 'examFees', parseInt(e.target.value))}
          />
        </div>
      </div>
      <div className="col-md-6">
        <div className="form-check form-switch mb-3">
          <input
            className="form-check-input"
            type="checkbox"
            checked={settings.cambridge?.predictedGrades || false}
            onChange={(e) => handleSettingChange('cambridge', 'predictedGrades', e.target.checked)}
          />
          <label className="form-check-label">Enable Predicted Grades</label>
        </div>
        <div className="form-check form-switch mb-3">
          <input
            className="form-check-input"
            type="checkbox"
            checked={settings.cambridge?.universityPathways || false}
            onChange={(e) => handleSettingChange('cambridge', 'universityPathways', e.target.checked)}
          />
          <label className="form-check-label">University Pathways Tracking</label>
        </div>
        <div className="form-check form-switch mb-3">
          <input
            className="form-check-input"
            type="checkbox"
            checked={settings.cambridge?.internationalBenchmarking || false}
            onChange={(e) => handleSettingChange('cambridge', 'internationalBenchmarking', e.target.checked)}
          />
          <label className="form-check-label">International Benchmarking</label>
        </div>
      </div>
    </div>
  );

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/dashboard">Dashboard</Link></li>
              <li className="breadcrumb-item"><Link to="/admin">Admin</Link></li>
              <li className="breadcrumb-item active">System Settings</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-primary">System Settings</h1>
              <p className="lead mb-0">Configure and manage system-wide settings</p>
            </div>
            <div className="text-end">
              <button 
                className="btn btn-primary"
                onClick={handleSaveAll}
                disabled={isSaving}
              >
                {isSaving ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2"></span>
                    Saving...
                  </>
                ) : (
                  <>
                    <i className="bi bi-save me-2"></i>
                    Save All Changes
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs">
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'general' ? 'active' : ''}`}
                onClick={() => setActiveTab('general')}
              >
                <i className="bi bi-gear me-2"></i>
                General
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'academic' ? 'active' : ''}`}
                onClick={() => setActiveTab('academic')}
              >
                <i className="bi bi-journal-bookmark me-2"></i>
                Academic
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'cbc' ? 'active' : ''}`}
                onClick={() => setActiveTab('cbc')}
              >
                <i className="bi bi-flag me-2"></i>
                CBC Settings
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'cambridge' ? 'active' : ''}`}
                onClick={() => setActiveTab('cambridge')}
              >
                <i className="bi bi-globe me-2"></i>
                Cambridge Settings
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'notifications' ? 'active' : ''}`}
                onClick={() => setActiveTab('notifications')}
              >
                <i className="bi bi-bell me-2"></i>
                Notifications
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'security' ? 'active' : ''}`}
                onClick={() => setActiveTab('security')}
              >
                <i className="bi bi-shield-check me-2"></i>
                Security
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* General Settings */}
          {activeTab === 'general' && renderGeneralSettings()}

          {/* Academic Settings */}
          {activeTab === 'academic' && renderAcademicSettings()}

          {/* CBC Settings */}
          {activeTab === 'cbc' && renderCBCSettings()}

          {/* Cambridge Settings */}
          {activeTab === 'cambridge' && renderCambridgeSettings()}

          {/* Notifications Settings */}
          {activeTab === 'notifications' && (
            <div className="row">
              <div className="col-md-6">
                <div className="form-check form-switch mb-3">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.notifications?.emailNotifications || false}
                    onChange={(e) => handleSettingChange('notifications', 'emailNotifications', e.target.checked)}
                  />
                  <label className="form-check-label">Email Notifications</label>
                </div>
                <div className="form-check form-switch mb-3">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.notifications?.smsNotifications || false}
                    onChange={(e) => handleSettingChange('notifications', 'smsNotifications', e.target.checked)}
                  />
                  <label className="form-check-label">SMS Notifications</label>
                </div>
                <div className="form-check form-switch mb-3">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.notifications?.parentAlerts || false}
                    onChange={(e) => handleSettingChange('notifications', 'parentAlerts', e.target.checked)}
                  />
                  <label className="form-check-label">Parent Alerts</label>
                </div>
              </div>
              <div className="col-md-6">
                <div className="mb-3">
                  <label className="form-label">Low Grade Alert Threshold (%)</label>
                  <input
                    type="number"
                    className="form-control"
                    min="0"
                    max="100"
                    value={settings.notifications?.lowGradeThreshold || 60}
                    onChange={(e) => handleSettingChange('notifications', 'lowGradeThreshold', parseInt(e.target.value))}
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Absence Alert Threshold (Days)</label>
                  <input
                    type="number"
                    className="form-control"
                    min="0"
                    value={settings.notifications?.absenceAlertThreshold || 3}
                    onChange={(e) => handleSettingChange('notifications', 'absenceAlertThreshold', parseInt(e.target.value))}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Security Settings */}
          {activeTab === 'security' && (
            <div className="row">
              <div className="col-md-6">
                <div className="mb-3">
                  <label className="form-label">Password Expiry (Days)</label>
                  <input
                    type="number"
                    className="form-control"
                    min="0"
                    value={settings.security?.passwordExpiry || 90}
                    onChange={(e) => handleSettingChange('security', 'passwordExpiry', parseInt(e.target.value))}
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Session Timeout (Minutes)</label>
                  <input
                    type="number"
                    className="form-control"
                    min="1"
                    value={settings.security?.sessionTimeout || 60}
                    onChange={(e) => handleSettingChange('security', 'sessionTimeout', parseInt(e.target.value))}
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Max Login Attempts</label>
                  <input
                    type="number"
                    className="form-control"
                    min="1"
                    max="10"
                    value={settings.security?.loginAttempts || 5}
                    onChange={(e) => handleSettingChange('security', 'loginAttempts', parseInt(e.target.value))}
                  />
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-check form-switch mb-3">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.security?.twoFactorAuth || false}
                    onChange={(e) => handleSettingChange('security', 'twoFactorAuth', e.target.checked)}
                  />
                  <label className="form-check-label">Two-Factor Authentication</label>
                </div>
                <div className="form-check form-switch mb-3">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.security?.auditLogging || false}
                    onChange={(e) => handleSettingChange('security', 'auditLogging', e.target.checked)}
                  />
                  <label className="form-check-label">Audit Logging</label>
                </div>
                <div className="mb-3">
                  <label className="form-label">IP Whitelist</label>
                  <textarea
                    className="form-control"
                    rows="3"
                    placeholder="Enter IP addresses (one per line)"
                    value={settings.security?.ipWhitelist?.join('\n') || ''}
                    onChange={(e) => handleSettingChange('security', 'ipWhitelist', e.target.value.split('\n'))}
                  ></textarea>
                  <div className="form-text">
                    Leave empty to allow access from any IP address
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="row mt-4">
            <div className="col-12">
              <div className="d-flex justify-content-between">
                <button 
                  className="btn btn-outline-secondary"
                  onClick={() => handleResetSettings(activeTab)}
                >
                  <i className="bi bi-arrow-clockwise me-2"></i>
                  Reset to Default
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={() => handleSaveSettings(activeTab)}
                  disabled={isSaving}
                >
                  {isSaving ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      Saving...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-save me-2"></i>
                      Save {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Settings
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header bg-light">
              <h6 className="mb-0">System Information</h6>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-3">
                  <strong>System Version:</strong> 2.1.0
                </div>
                <div className="col-md-3">
                  <strong>Last Backup:</strong> 2024-01-15 02:00
                </div>
                <div className="col-md-3">
                  <strong>Database Size:</strong> 245 MB
                </div>
                <div className="col-md-3">
                  <strong>Active Users:</strong> 1,247
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SystemSettings;