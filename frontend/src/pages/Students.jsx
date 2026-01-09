import React, { useState, useEffect } from 'react';
import {studentsAPI} from '../services/studentAPI.js';

function Students() {
  const [students, setStudents] = useState([]);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [selectedGrade, setSelectedGrade] = useState('all');
  const [showForm, setShowForm] = useState(false);
  const [statistics, setStatistics] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    admissionNumber: '',
    firstName: '',
    lastName: '',
    grade: '',
    stream: '',
    dateOfBirth: '',
    gender: '',
    parentName: '',
    parentPhone: '',
    parentEmail: '',
    address: ''
  });

  const gradeLevels = {
    'Lower Primary (1-3)': ['1', '2', '3'],
    'Upper Primary (4-6)': ['4', '5', '6'],
    'Junior Secondary (7-9)': ['7', '8', '9'],
    'Senior Secondary (10-12)': ['10', '11', '12']
  };

  useEffect(() => {
    fetchStudents();
    fetchStatistics();
  }, []);

  useEffect(() => {
    if (selectedGrade === 'all') {
      setFilteredStudents(students);
    } else {
      setFilteredStudents(students.filter(student => student.grade === selectedGrade));
    }
  }, [selectedGrade, students]);

  const fetchStudents = async () => {
    setLoading(true);
    try {
      const response = await studentsAPI.getAll();
      setStudents(response.data);
    } catch (error) {
      console.error('Error fetching students:', error);
      alert('Error loading students data');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await studentsAPI.getStatistics();
      setStatistics(response.data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await studentsAPI.create(formData);
      fetchStudents();
      fetchStatistics();
      setShowForm(false);
      setFormData({
        admissionNumber: '',
        firstName: '',
        lastName: '',
        grade: '',
        stream: '',
        dateOfBirth: '',
        gender: '',
        parentName: '',
        parentPhone: '',
        parentEmail: '',
        address: ''
      });
      alert('Student added successfully!');
    } catch (error) {
      console.error('Error adding student:', error);
      alert(error.response?.data?.error || 'Error adding student');
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const getTotalStudents = () => {
    return statistics.reduce((total, stat) => total + parseInt(stat.total), 0);
  };

  if (loading) {
    return (
      <div className="container mt-4">
        <div className="loading-spinner">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Student Management</h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : 'Add New Student'}
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="row mb-4">
        <div className="col-md-3 mb-3">
          <div className="card text-white bg-primary stat-card">
            <div className="card-body">
              <h5 className="card-title">Total Students</h5>
              <h2 className="card-text">{getTotalStudents()}</h2>
            </div>
          </div>
        </div>
        {statistics.slice(0, 3).map(stat => (
          <div key={stat.grade} className="col-md-3 mb-3">
            <div className="card text-white bg-success stat-card">
              <div className="card-body">
                <h5 className="card-title">Grade {stat.grade}</h5>
                <h2 className="card-text">{stat.total}</h2>
                <small>👦 {stat.males} 👧 {stat.females}</small>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Add Student Form */}
      {showForm && (
        <div className="card mb-4">
          <div className="card-header bg-primary text-white">
            <h5 className="card-title mb-0">Add New Student</h5>
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="row">
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Admission Number *</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      name="admissionNumber" 
                      value={formData.admissionNumber} 
                      onChange={handleChange} 
                      required 
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">First Name *</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      name="firstName" 
                      value={formData.firstName} 
                      onChange={handleChange} 
                      required 
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Last Name *</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      name="lastName" 
                      value={formData.lastName} 
                      onChange={handleChange} 
                      required 
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Grade *</label>
                    <select 
                      className="form-select" 
                      name="grade" 
                      value={formData.grade} 
                      onChange={handleChange} 
                      required
                    >
                      <option value="">Select Grade</option>
                      {Object.entries(gradeLevels).map(([level, grades]) => (
                        <optgroup key={level} label={level}>
                          {grades.map(grade => (
                            <option key={grade} value={grade}>Grade {grade}</option>
                          ))}
                        </optgroup>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Parent Name *</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      name="parentName" 
                      value={formData.parentName} 
                      onChange={handleChange} 
                      required 
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Parent Phone *</label>
                    <input 
                      type="tel" 
                      className="form-control" 
                      name="parentPhone" 
                      value={formData.parentPhone} 
                      onChange={handleChange} 
                      required 
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Gender *</label>
                    <select 
                      className="form-select" 
                      name="gender" 
                      value={formData.gender} 
                      onChange={handleChange} 
                      required
                    >
                      <option value="">Select Gender</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Date of Birth *</label>
                    <input 
                      type="date" 
                      className="form-control" 
                      name="dateOfBirth" 
                      value={formData.dateOfBirth} 
                      onChange={handleChange} 
                      required 
                    />
                  </div>
                </div>
              </div>
              <div className="mb-3">
                <label className="form-label">Address</label>
                <textarea 
                  className="form-control" 
                  name="address" 
                  value={formData.address} 
                  onChange={handleChange} 
                  rows="3"
                />
              </div>
              <button type="submit" className="btn btn-success">Add Student</button>
            </form>
          </div>
        </div>
      )}

      {/* Filter and Students Table */}
      <div className="card">
        <div className="card-header d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Students List</h5>
          <select 
            className="form-select w-auto" 
            value={selectedGrade} 
            onChange={(e) => setSelectedGrade(e.target.value)}
          >
            <option value="all">All Grades</option>
            {Object.entries(gradeLevels).map(([level, grades]) => (
              <optgroup key={level} label={level}>
                {grades.map(grade => (
                  <option key={grade} value={grade}>Grade {grade}</option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-striped table-hover">
              <thead className="table-dark">
                <tr>
                  <th>Admission No.</th>
                  <th>Name</th>
                  <th>Grade</th>
                  <th>Gender</th>
                  <th>Parent Phone</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredStudents.map(student => (
                  <tr key={student.id}>
                    <td>{student.admission_number}</td>
                    <td>{student.first_name} {student.last_name}</td>
                    <td>Grade {student.grade}</td>
                    <td>{student.gender}</td>
                    <td>{student.parent_phone}</td>
                    <td>
                      <span className={`badge ${student.status === 'Active' ? 'bg-success' : 'bg-warning'}`}>
                        {student.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredStudents.length === 0 && (
              <div className="text-center py-4">
                <p className="text-muted">No students found</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Students;