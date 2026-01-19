// TeacherGrades.jsx - COMPLETE VERSION WITH PROPER API INTEGRATION
import React, { useState, useEffect, useMemo } from 'react';
import {
  Container, Row, Col, Card, Table, Button, Badge,
  Alert, Spinner, Form, InputGroup, Tabs, Tab,
  ProgressBar, Dropdown, Modal
} from 'react-bootstrap';
import {
  Calculator,
  Book,
  People,
  Search,
  Plus,
  Pencil,
  Save,
  Download,
  Upload,
  BarChart,
  FileText,
  Award,
  Person,
  CheckCircle,
  ExclamationTriangle,
  XCircle,
  Eye,
  Clock,
  Filter,
  ChevronDown,
  ArrowClockwise,
  FileEarmarkSpreadsheet,
  FileEarmarkPdf,
  FileEarmarkArrowDown
} from 'react-bootstrap-icons';
import { gradesAPI } from '../../services/gradesAPI';
import { academicsAPI } from '../../services/academicAPI';
import { useAuth } from '../../context/AuthContext';
import './TeacherGrades.css';

const TeacherGrades = () => {
  const { currentUser } = useAuth();
  
  // State management
  const [loading, setLoading] = useState(true);
  const [fetchingClasses, setFetchingClasses] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Data state
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState('');
  const [students, setStudents] = useState([]);
  const [assessments, setAssessments] = useState([]);
  const [grades, setGrades] = useState({});
  const [classDetail, setClassDetail] = useState(null);
  
  // UI state
  const [activeTab, setActiveTab] = useState('entry');
  const [searchQuery, setSearchQuery] = useState('');
  const [showImportModal, setShowImportModal] = useState(false);
  const [bulkEditMode, setBulkEditMode] = useState(false);
  const [bulkScore, setBulkScore] = useState('');
  const [showExportModal, setShowExportModal] = useState(false);

  // ==================== API FUNCTIONS ====================
  
  const fetchClasses = async () => {
    try {
      setFetchingClasses(true);
      setError('');
      
      console.log('🔄 Fetching teacher classes using academicAPI...');
      
      // Try different approaches to get classes
      let result;
      
      // First try: Get classes for current teacher
      if (currentUser?.id) {
        result = await academicAPI.getClasses({ teacher_id: currentUser.id });
      }
      
      // Second try: Get all classes if teacher-specific fails
      if (!result?.success || !result.data) {
        result = await academicAPI.getClasses();
      }
      
      if (result.success && result.data) {
        // Handle both paginated and non-paginated responses
        const classesData = result.data.results || result.data;
        
        if (Array.isArray(classesData) && classesData.length > 0) {
          console.log(`✅ Found ${classesData.length} classes`);
          setClasses(classesData);
          setSelectedClass(classesData[0].id);
          await fetchClassData(classesData[0].id);
        } else {
          setError('No classes found for this teacher');
        }
      } else {
        setError(result.message || 'Failed to fetch classes');
      }
    } catch (err) {
      console.error('Error fetching classes:', err);
      setError('Failed to load classes. Please check your connection.');
    } finally {
      setFetchingClasses(false);
      setLoading(false);
    }
  };

  const fetchClassData = async (classId) => {
    if (!classId) return;
    
    try {
      setLoading(true);
      setError('');
      setStudents([]);
      setAssessments([]);
      setGrades({});
      
      console.log(`🔄 Fetching data for class: ${classId}`);
      
      // 1. Fetch class details
      const classResult = await academicAPI.getClass(classId);
      if (classResult.success) {
        setClassDetail(classResult.data);
      }
      
      // 2. Fetch students in class
      const studentsResult = await academicAPI.getClassStudents(classId);
      if (studentsResult.success) {
        const studentsData = studentsResult.data.results || studentsResult.data || [];
        console.log(`✅ Found ${studentsData.length} students`);
        setStudents(studentsData);
      }
      
      // 3. Fetch assessments for this class
      // Note: You might need to implement this in academicAPI or use gradesAPI
      // For now, we'll fetch grades and extract assessments from them
      await fetchGradesForClass(classId);
      
    } catch (err) {
      console.error('Error fetching class data:', err);
      setError('Failed to load class data');
    } finally {
      setLoading(false);
    }
  };

  const fetchGradesForClass = async (classId) => {
    try {
      // Fetch grades using gradesAPI
      const gradesResult = await gradesAPI.getByClass(classId);
      
      if (gradesResult.success) {
        const gradesData = gradesResult.data?.results || gradesResult.data || [];
        console.log(`✅ Found ${gradesData.length} grade records`);
        
        // Extract unique assessments from grades
        const uniqueAssessments = {};
        const gradesMap = {};
        
        gradesData.forEach(grade => {
          // Extract assessment info
          if (grade.assessment) {
            const assessment = grade.assessment;
            const assessmentId = assessment.id || assessment;
            
            uniqueAssessments[assessmentId] = {
              id: assessmentId,
              name: assessment.name || assessment.title || `Assessment ${assessmentId}`,
              total_marks: assessment.total_marks || assessment.max_score || 100,
              type: assessment.type || 'assignment'
            };
          }
          
          // Organize grades by student and assessment
          if (grade.student && grade.assessment) {
            const studentId = typeof grade.student === 'object' ? grade.student.id : grade.student;
            const assessmentId = typeof grade.assessment === 'object' ? grade.assessment.id : grade.assessment;
            
            if (!gradesMap[studentId]) {
              gradesMap[studentId] = {};
            }
            
            gradesMap[studentId][assessmentId] = {
              id: grade.id,
              score: grade.marks_obtained || grade.score,
              percentage: grade.percentage,
              grade: grade.grade,
              comments: grade.comments || '',
              is_absent: grade.is_absent || false,
              is_exempted: grade.is_exempted || false,
              graded_at: grade.graded_at
            };
          }
        });
        
        setAssessments(Object.values(uniqueAssessments));
        setGrades(gradesMap);
        
        // If no assessments found, create default ones
        if (Object.keys(uniqueAssessments).length === 0 && students.length > 0) {
          createDefaultAssessments();
        }
      }
    } catch (err) {
      console.error('Error fetching grades:', err);
      createDefaultAssessments();
    }
  };

  const createDefaultAssessments = () => {
    const defaultAssessments = [
      { id: 1, name: 'Midterm Exam', total_marks: 100, type: 'exam' },
      { id: 2, name: 'Assignment 1', total_marks: 50, type: 'assignment' },
      { id: 3, name: 'Final Project', total_marks: 30, type: 'project' }
    ];
    setAssessments(defaultAssessments);
    
    // Initialize empty grades structure
    const initialGrades = {};
    students.forEach(student => {
      initialGrades[student.id] = {};
      defaultAssessments.forEach(assessment => {
        initialGrades[student.id][assessment.id] = {};
      });
    });
    setGrades(initialGrades);
  };

  // ==================== GRADE MANAGEMENT ====================
  
  const handleGradeChange = (studentId, assessmentId, field, value) => {
    setGrades(prev => ({
      ...prev,
      [studentId]: {
        ...prev[studentId],
        [assessmentId]: {
          ...prev[studentId]?.[assessmentId],
          [field]: field === 'score' ? (value === '' ? '' : parseFloat(value)) : value,
          modified: true
        }
      }
    }));
  };

  const saveGrade = async (studentId, assessmentId, gradeData) => {
    try {
      const existingGrade = grades[studentId]?.[assessmentId];
      
      const payload = {
        student: studentId,
        assessment: assessmentId,
        marks_obtained: parseFloat(gradeData.score) || 0,
        comments: gradeData.comments || '',
        is_absent: gradeData.is_absent || false,
        is_exempted: gradeData.is_exempted || false,
        graded_by: currentUser.id
      };
      
      let result;
      if (existingGrade?.id) {
        result = await gradesAPI.update(existingGrade.id, payload);
      } else {
        result = await gradesAPI.create(payload);
      }
      
      return result;
    } catch (err) {
      console.error('Error saving grade:', err);
      return { 
        success: false, 
        error: err.response?.data?.message || err.message 
      };
    }
  };

  const saveAllGrades = async () => {
    try {
      setSaving(true);
      setError('');
      
      const updates = [];
      Object.entries(grades).forEach(([studentId, studentGrades]) => {
        Object.entries(studentGrades).forEach(([assessmentId, gradeData]) => {
          if (gradeData.modified || (gradeData.score !== undefined && gradeData.score !== '')) {
            updates.push(saveGrade(studentId, assessmentId, gradeData));
          }
        });
      });
      
      if (updates.length === 0) {
        setError('No changes to save');
        return;
      }
      
      const results = await Promise.all(updates);
      const failed = results.filter(r => !r.success);
      
      if (failed.length > 0) {
        setError(`${failed.length} grades failed to save. Please try again.`);
      } else {
        setSuccess(`${updates.length} grades saved successfully!`);
        setTimeout(() => setSuccess(''), 3000);
        
        // Refresh data
        await fetchGradesForClass(selectedClass);
      }
    } catch (err) {
      setError('Failed to save grades: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const applyBulkScore = (score) => {
    if (!score || isNaN(score)) {
      setError('Please enter a valid score');
      return;
    }
    
    const numericScore = parseFloat(score);
    
    const updatedGrades = { ...grades };
    students.forEach(student => {
      assessments.forEach(assessment => {
        const maxScore = assessment.total_marks || 100;
        const finalScore = Math.min(numericScore, maxScore);
        
        if (!updatedGrades[student.id]) {
          updatedGrades[student.id] = {};
        }
        
        updatedGrades[student.id][assessment.id] = {
          ...updatedGrades[student.id][assessment.id],
          score: finalScore,
          modified: true
        };
      });
    });
    
    setGrades(updatedGrades);
    setBulkEditMode(false);
    setBulkScore('');
    setSuccess(`Applied score ${numericScore} to all students`);
    setTimeout(() => setSuccess(''), 3000);
  };

  // ==================== CALCULATIONS & HELPERS ====================
  
  const filteredStudents = useMemo(() => {
    if (!searchQuery) return students;
    
    const query = searchQuery.toLowerCase();
    return students.filter(student => {
      const fullName = student.full_name || 
                      `${student.first_name || ''} ${student.last_name || ''}`.trim();
      const admissionNumber = student.admission_number || student.student_id || '';
      
      return fullName.toLowerCase().includes(query) ||
             admissionNumber.toLowerCase().includes(query) ||
             student.email?.toLowerCase().includes(query);
    });
  }, [students, searchQuery]);
  
  const calculateStudentAverage = (studentId) => {
    const studentGrades = grades[studentId];
    if (!studentGrades) return null;
    
    const validGrades = Object.values(studentGrades)
      .filter(grade => 
        grade.score != null && 
        !isNaN(grade.score) && 
        !grade.is_absent && 
        !grade.is_exempted
      )
      .map(grade => parseFloat(grade.score));
    
    if (validGrades.length === 0) return null;
    
    const sum = validGrades.reduce((a, b) => a + b, 0);
    return (sum / validGrades.length).toFixed(1);
  };
  
  const calculateAssessmentAverage = (assessmentId) => {
    const validGrades = Object.values(grades)
      .map(studentGrades => studentGrades[assessmentId])
      .filter(grade => 
        grade?.score != null && 
        !isNaN(grade.score) && 
        !grade.is_absent && 
        !grade.is_exempted
      )
      .map(grade => parseFloat(grade.score));
    
    if (validGrades.length === 0) return null;
    
    const sum = validGrades.reduce((a, b) => a + b, 0);
    return (sum / validGrades.length).toFixed(1);
  };
  
  const getGradeColor = (score, maxScore = 100) => {
    if (score === null || score === undefined) return 'secondary';
    const percentage = (score / maxScore) * 100;
    
    if (percentage >= 90) return 'success';
    if (percentage >= 80) return 'primary';
    if (percentage >= 70) return 'info';
    if (percentage >= 60) return 'warning';
    return 'danger';
  };
  
  const getStatusBadge = (studentId) => {
    const avg = calculateStudentAverage(studentId);
    if (avg === null) {
      return { text: 'No Grades', variant: 'secondary', icon: <Clock size={12} /> };
    }
    
    const percentage = parseFloat(avg);
    if (percentage >= 70) {
      return { text: 'Passing', variant: 'success', icon: <CheckCircle size={12} /> };
    } else if (percentage >= 60) {
      return { text: 'Needs Help', variant: 'warning', icon: <ExclamationTriangle size={12} /> };
    } else {
      return { text: 'At Risk', variant: 'danger', icon: <XCircle size={12} /> };
    }
  };

  // ==================== EXPORT FUNCTION ====================
  
  const handleExport = (format = 'csv') => {
    try {
      // Create CSV data
      const headers = ['Student ID', 'Student Name', 'Admission Number', 'Email'];
      assessments.forEach(a => {
        headers.push(`${a.name} (Max: ${a.total_marks})`);
        headers.push('Comments');
      });
      headers.push('Average', 'Status');
      
      const rows = filteredStudents.map(student => {
        const avg = calculateStudentAverage(student.id);
        const status = getStatusBadge(student.id);
        const studentName = student.full_name || 
                          `${student.first_name || ''} ${student.last_name || ''}`.trim();
        
        const row = [
          student.id,
          studentName,
          student.admission_number || 'N/A',
          student.email || 'N/A'
        ];
        
        assessments.forEach(assessment => {
          const grade = grades[student.id]?.[assessment.id];
          row.push(grade?.score || '');
          row.push(grade?.comments || '');
        });
        
        row.push(avg || '');
        row.push(status.text);
        
        return row;
      });
      
      // Escape CSV values
      const escapeCSV = (str) => {
        if (str === null || str === undefined) return '';
        const string = String(str);
        if (string.includes(',') || string.includes('"') || string.includes('\n')) {
          return `"${string.replace(/"/g, '""')}"`;
        }
        return string;
      };
      
      const csvContent = [
        headers.map(escapeCSV).join(','),
        ...rows.map(row => row.map(escapeCSV).join(','))
      ].join('\n');
      
      // Create download link
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `grades_${classDetail?.name || selectedClass}_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      setSuccess('Grades exported successfully!');
      setTimeout(() => setSuccess(''), 3000);
      setShowExportModal(false);
      
    } catch (err) {
      setError('Export failed: ' + err.message);
    }
  };

  // ==================== INITIAL LOAD ====================
  
  useEffect(() => {
    if (currentUser) {
      fetchClasses();
    }
  }, [currentUser]);

  // ==================== RENDER FUNCTIONS ====================
  
  const renderGradeEntryTable = () => (
    <div className="table-responsive grade-entry-table">
      <Table striped bordered hover className="mb-0">
        <thead className="bg-light sticky-top">
          <tr>
            <th style={{ minWidth: '200px', position: 'sticky', left: 0, backgroundColor: '#f8f9fa' }}>
              <div className="d-flex align-items-center">
                <Person className="me-2" size={16} />
                Student
              </div>
            </th>
            {assessments.map(assessment => {
              const avg = calculateAssessmentAverage(assessment.id);
              return (
                <th key={assessment.id} style={{ minWidth: '180px' }}>
                  <div className="text-center">
                    <div className="fw-semibold small">{assessment.name}</div>
                    <Badge bg="secondary" className="small mt-1">
                      Max: {assessment.total_marks}
                    </Badge>
                    {avg && (
                      <div className="text-muted small mt-1">
                        Avg: {avg}
                      </div>
                    )}
                  </div>
                </th>
              );
            })}
            <th style={{ minWidth: '120px', position: 'sticky', right: 0, backgroundColor: '#f8f9fa' }}>
              <div className="text-center">
                <BarChart className="me-1" size={14} />
                Average
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          {filteredStudents.map(student => {
            const avg = calculateStudentAverage(student.id);
            const status = getStatusBadge(student.id);
            const studentName = student.full_name || 
                              `${student.first_name || ''} ${student.last_name || ''}`.trim();
            
            return (
              <tr key={student.id}>
                <td style={{ position: 'sticky', left: 0, backgroundColor: 'white' }}>
                  <div className="d-flex align-items-center">
                    <div className="me-2">
                      <Person className="text-muted" size={16} />
                    </div>
                    <div>
                      <div className="fw-semibold">{studentName}</div>
                      <small className="text-muted">{student.admission_number || 'No ID'}</small>
                      {student.email && (
                        <div className="small text-muted">{student.email}</div>
                      )}
                      <div className="mt-1">
                        <Badge bg={status.variant} className="d-inline-flex align-items-center">
                          {status.icon}
                          <span className="ms-1">{status.text}</span>
                        </Badge>
                      </div>
                    </div>
                  </div>
                </td>
                
                {assessments.map(assessment => {
                  const grade = grades[student.id]?.[assessment.id];
                  const maxScore = assessment.total_marks || 100;
                  
                  return (
                    <td key={assessment.id}>
                      <div className="grade-cell">
                        <div className="d-flex gap-1 mb-1">
                          <Form.Control
                            type="number"
                            size="sm"
                            placeholder="Score"
                            min="0"
                            max={maxScore}
                            step="0.1"
                            value={grade?.score || ''}
                            onChange={(e) => handleGradeChange(
                              student.id,
                              assessment.id,
                              'score',
                              e.target.value
                            )}
                            disabled={grade?.is_absent || grade?.is_exempted}
                            className={grade?.modified ? 'border-warning' : ''}
                          />
                        </div>
                        
                        <div className="d-flex gap-1 mb-1">
                          <Form.Control
                            as="textarea"
                            rows={1}
                            size="sm"
                            placeholder="Comments"
                            value={grade?.comments || ''}
                            onChange={(e) => handleGradeChange(
                              student.id,
                              assessment.id,
                              'comments',
                              e.target.value
                            )}
                            style={{ fontSize: '0.8rem' }}
                            className={grade?.modified ? 'border-warning' : ''}
                          />
                        </div>
                        
                        <div className="d-flex justify-content-between align-items-center">
                          <div className="d-flex gap-2">
                            <Form.Check
                              type="checkbox"
                              id={`absent-${student.id}-${assessment.id}`}
                              label="Absent"
                              checked={grade?.is_absent || false}
                              onChange={(e) => handleGradeChange(
                                student.id,
                                assessment.id,
                                'is_absent',
                                e.target.checked
                              )}
                              className="small"
                            />
                            <Form.Check
                              type="checkbox"
                              id={`exempt-${student.id}-${assessment.id}`}
                              label="Exempt"
                              checked={grade?.is_exempted || false}
                              onChange={(e) => handleGradeChange(
                                student.id,
                                assessment.id,
                                'is_exempted',
                                e.target.checked
                              )}
                              className="small"
                            />
                          </div>
                          
                          {grade?.score !== undefined && grade?.score !== '' && (
                            <Badge bg={getGradeColor(grade.score, maxScore)}>
                              {grade.score}/{maxScore}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </td>
                  );
                })}
                
                <td style={{ position: 'sticky', right: 0, backgroundColor: 'white' }}>
                  <div className="text-center">
                    {avg ? (
                      <Badge bg={getGradeColor(parseFloat(avg))} className="fs-6 px-3 py-2">
                        {avg}%
                      </Badge>
                    ) : (
                      <span className="text-muted">-</span>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </Table>
    </div>
  );

  const renderOverview = () => {
    const classStats = {
      totalStudents: students.length,
      gradedStudents: students.filter(s => {
        const gradesForStudent = grades[s.id];
        if (!gradesForStudent) return false;
        return Object.values(gradesForStudent).some(g => g.score !== undefined && g.score !== '');
      }).length,
      classAverage: () => {
        const averages = students.map(s => calculateStudentAverage(s.id)).filter(avg => avg !== null);
        if (averages.length === 0) return null;
        const sum = averages.reduce((a, b) => a + parseFloat(b), 0);
        return (sum / averages.length).toFixed(1);
      },
      passingRate: () => {
        const passing = students.filter(s => {
          const avg = calculateStudentAverage(s.id);
          return avg !== null && parseFloat(avg) >= 70;
        }).length;
        return students.length > 0 ? Math.round((passing / students.length) * 100) : 0;
      }
    };
    
    return (
      <div className="overview-content">
        {classDetail && (
          <Card className="border-0 shadow-sm mb-4">
            <Card.Body>
              <Row className="align-items-center">
                <Col md={8}>
                  <h4 className="mb-1">{classDetail.name}</h4>
                  <p className="text-muted mb-0">
                    Grade {classDetail.grade_level} • Section {classDetail.section} • 
                    {classDetail.stream ? ` ${classDetail.stream}` : ''}
                  </p>
                  {classDetail.description && (
                    <p className="mt-2 small">{classDetail.description}</p>
                  )}
                </Col>
                <Col md={4} className="text-end">
                  <Badge bg="info" className="fs-6">
                    {students.length} Students
                  </Badge>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        )}
        
        <Row className="mb-4">
          <Col md={3}>
            <Card className="border-0 shadow-sm h-100">
              <Card.Body className="text-center">
                <People size={32} className="text-primary mb-2" />
                <div className="h2 text-primary mb-1">{classStats.totalStudents}</div>
                <div className="text-muted">Total Students</div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="border-0 shadow-sm h-100">
              <Card.Body className="text-center">
                <CheckCircle size={32} className="text-success mb-2" />
                <div className="h2 text-success mb-1">{classStats.gradedStudents}</div>
                <div className="text-muted">Graded Students</div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="border-0 shadow-sm h-100">
              <Card.Body className="text-center">
                <BarChart size={32} className="text-info mb-2" />
                <div className="h2 text-info mb-1">{classStats.classAverage() || '0'}%</div>
                <div className="text-muted">Class Average</div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="border-0 shadow-sm h-100">
              <Card.Body className="text-center">
                <Award size={32} className="text-warning mb-2" />
                <div className="h2 text-warning mb-1">{classStats.passingRate()}%</div>
                <div className="text-muted">Passing Rate</div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
        
        <Card className="border-0 shadow-sm">
          <Card.Header className="bg-white">
            <h5 className="mb-0 d-flex align-items-center">
              <BarChart className="me-2" size={18} />
              Student Performance
            </h5>
          </Card.Header>
          <Card.Body>
            <Table striped hover>
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Completed</th>
                  <th>Average</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredStudents.map(student => {
                  const avg = calculateStudentAverage(student.id);
                  const completed = assessments.filter(a => {
                    const grade = grades[student.id]?.[a.id];
                    return grade?.score !== undefined && grade?.score !== '';
                  }).length;
                  const status = getStatusBadge(student.id);
                  const studentName = student.full_name || 
                                    `${student.first_name || ''} ${student.last_name || ''}`.trim();
                  
                  return (
                    <tr key={student.id}>
                      <td>
                        <div className="fw-semibold">{studentName}</div>
                        <small className="text-muted">{student.admission_number || 'No ID'}</small>
                      </td>
                      <td>
                        <div className="d-flex align-items-center">
                          <div className="progress flex-grow-1 me-2" style={{ height: '8px' }}>
                            <ProgressBar 
                              now={(completed / assessments.length) * 100} 
                              variant={completed === assessments.length ? 'success' : 'warning'}
                            />
                          </div>
                          <small>{completed}/{assessments.length}</small>
                        </div>
                      </td>
                      <td>
                        {avg ? (
                          <Badge bg={getGradeColor(parseFloat(avg))} className="fs-6">
                            {avg}%
                          </Badge>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                      <td>
                        <Badge bg={status.variant} className="d-flex align-items-center">
                          {status.icon}
                          <span className="ms-1">{status.text}</span>
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </Table>
          </Card.Body>
        </Card>
      </div>
    );
  };

  // ==================== RENDER ====================
  
  if (loading && !selectedClass) {
    return (
      <Container className="mt-4">
        <div className="text-center py-5">
          <Spinner animation="border" role="status" variant="primary" />
          <p className="mt-3 text-muted">Loading grade management...</p>
        </div>
      </Container>
    );
  }
  
  return (
    <Container fluid className="mt-3 teacher-grades-container">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h3 mb-1 d-flex align-items-center">
                <Award className="me-2" size={24} />
                Grade Management
              </h1>
              <p className="text-muted mb-0">
                Enter, manage, and analyze student grades
              </p>
            </div>
            
            <div className="d-flex gap-2">
              <Dropdown>
                <Dropdown.Toggle variant="outline-primary">
                  <Download className="me-2" size={16} />
                  Export
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item onClick={() => handleExport('csv')}>
                    <FileEarmarkSpreadsheet className="me-2" size={14} />
                    Export as CSV
                  </Dropdown.Item>
                  <Dropdown.Item onClick={() => setShowExportModal(true)}>
                    <FileEarmarkPdf className="me-2" size={14} />
                    Export as PDF
                  </Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
              
              <Button
                variant="primary"
                onClick={saveAllGrades}
                disabled={saving}
              >
                {saving ? (
                  <>
                    <Spinner animation="border" size="sm" className="me-2" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="me-2" size={16} />
                    Save All Grades
                  </>
                )}
              </Button>
            </div>
          </div>
        </Col>
      </Row>
      
      {/* Alerts */}
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')} className="mb-3">
          <ExclamationTriangle className="me-2" size={16} />
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess('')} className="mb-3">
          <CheckCircle className="me-2" size={16} />
          {success}
        </Alert>
      )}
      
      {/* Controls */}
      <Card className="border-0 shadow-sm mb-4">
        <Card.Body>
          <Row className="g-3">
            <Col md={4}>
              <Form.Group>
                <Form.Label className="d-flex align-items-center">
                  <Book className="me-2" size={16} />
                  Class
                </Form.Label>
                <Form.Select
                  value={selectedClass}
                  onChange={(e) => {
                    setSelectedClass(e.target.value);
                    fetchClassData(e.target.value);
                  }}
                  disabled={fetchingClasses || classes.length === 0}
                >
                  {fetchingClasses ? (
                    <option>Loading classes...</option>
                  ) : classes.length === 0 ? (
                    <option>No classes available</option>
                  ) : (
                    classes.map(classItem => (
                      <option key={classItem.id} value={classItem.id}>
                        {classItem.name} - Grade {classItem.grade_level}
                      </option>
                    ))
                  )}
                </Form.Select>
              </Form.Group>
            </Col>
            
            <Col md={5}>
              <Form.Group>
                <Form.Label className="d-flex align-items-center">
                  <Search className="me-2" size={16} />
                  Search Students
                </Form.Label>
                <InputGroup>
                  <Form.Control
                    placeholder="Search by name, ID, or email..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    disabled={students.length === 0}
                  />
                  <Button 
                    variant="outline-secondary" 
                    disabled={students.length === 0}
                  >
                    <Search size={16} />
                  </Button>
                </InputGroup>
              </Form.Group>
            </Col>
            
            <Col md={3}>
              <Form.Label>Quick Actions</Form.Label>
              <div className="d-flex gap-2">
                <Button
                  variant={bulkEditMode ? "primary" : "outline-secondary"}
                  size="sm"
                  onClick={() => setBulkEditMode(!bulkEditMode)}
                  disabled={students.length === 0 || assessments.length === 0}
                >
                  <Pencil size={14} />
                </Button>
                <Button
                  variant="outline-secondary"
                  size="sm"
                  onClick={() => fetchClassData(selectedClass)}
                >
                  <ArrowClockwise size={14} />
                </Button>
              </div>
            </Col>
          </Row>
          
          {bulkEditMode && (
            <div className="mt-3 p-3 bg-light rounded">
              <div className="d-flex align-items-center gap-3">
                <span className="fw-semibold">Bulk Edit:</span>
                <Form.Control
                  type="number"
                  placeholder="Enter score for all"
                  value={bulkScore}
                  onChange={(e) => setBulkScore(e.target.value)}
                  style={{ width: '150px' }}
                  size="sm"
                />
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => applyBulkScore(bulkScore)}
                >
                  Apply to All
                </Button>
                <Button
                  variant="outline-secondary"
                  size="sm"
                  onClick={() => {
                    setBulkEditMode(false);
                    setBulkScore('');
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </Card.Body>
      </Card>
      
      {/* Main Content Tabs */}
      <Tabs activeKey={activeTab} onSelect={setActiveTab} className="mb-3">
        <Tab
          eventKey="entry"
          title={
            <span className="d-flex align-items-center">
              <Calculator className="me-2" size={16} />
              Grade Entry
              {assessments.length > 0 && (
                <Badge bg="primary" className="ms-2">
                  {assessments.length}
                </Badge>
              )}
            </span>
          }
        >
          <Card className="border-0 shadow-sm">
            <Card.Body className="p-0">
              {students.length > 0 && assessments.length > 0 ? (
                renderGradeEntryTable()
              ) : (
                <div className="text-center py-5">
                  <Calculator size={48} className="text-muted mb-3" />
                  <h5 className="text-muted">No Data Available</h5>
                  <p className="text-muted">
                    {!selectedClass ? 'Select a class to begin' :
                     students.length === 0 ? 'No students found in this class' :
                     'No assessments found for this class'}
                  </p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Tab>
        
        <Tab
          eventKey="overview"
          title={
            <span className="d-flex align-items-center">
              <BarChart className="me-2" size={16} />
              Overview
            </span>
          }
        >
          {renderOverview()}
        </Tab>
      </Tabs>
      
      {/* Export Modal */}
      <Modal show={showExportModal} onHide={() => setShowExportModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>
            <FileEarmarkArrowDown className="me-2" size={18} />
            Export Grades
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Select export format:</p>
          <div className="d-grid gap-2">
            <Button variant="outline-primary" onClick={() => handleExport('csv')}>
              <FileEarmarkSpreadsheet className="me-2" size={16} />
              CSV Format (Excel compatible)
            </Button>
            <Button variant="outline-danger" disabled>
              <FileEarmarkPdf className="me-2" size={16} />
              PDF Format (Coming Soon)
            </Button>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowExportModal(false)}>
            Cancel
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default TeacherGrades;