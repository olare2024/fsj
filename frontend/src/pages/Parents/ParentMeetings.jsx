import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

function ParentMeetings() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('schedule');
  const [children, setChildren] = useState([]);
  const [selectedChild, setSelectedChild] = useState('');
  const [selectedTeacher, setSelectedTeacher] = useState('');
  const [meetingDate, setMeetingDate] = useState('');
  const [meetingTime, setMeetingTime] = useState('');
  const [meetingPurpose, setMeetingPurpose] = useState('');
  const [upcomingMeetings, setUpcomingMeetings] = useState([]);
  const [pastMeetings, setPastMeetings] = useState([]);

  // Mock data - in real app, this would come from API
  useEffect(() => {
    // Mock children data
    const mockChildren = [
      {
        id: 'child1',
        name: 'Sarah Johnson',
        grade: 'Grade 7A',
        curriculum: 'CBC',
        teachers: [
          { id: 'teacher1', name: 'Mr. Robert Mutiso', subject: 'Mathematics' },
          { id: 'teacher2', name: 'Mrs. Grace Mwende', subject: 'English' },
          { id: 'teacher3', name: 'Dr. James Kariuki', subject: 'Science' }
        ]
      },
      {
        id: 'child2',
        name: 'David Johnson', 
        grade: 'Grade 9B',
        curriculum: 'IGCSE',
        teachers: [
          { id: 'teacher4', name: 'Dr. David Kimani', subject: 'Physics' },
          { id: 'teacher5', name: 'Prof. Sarah Mwangi', subject: 'Chemistry' },
          { id: 'teacher6', name: 'Mr. Robert Mutiso', subject: 'Mathematics' }
        ]
      }
    ];

    // Mock meetings data
    const mockUpcomingMeetings = [
      {
        id: 1,
        child: 'Sarah Johnson',
        teacher: 'Mr. Robert Mutiso',
        subject: 'Mathematics',
        date: '2024-01-25',
        time: '14:00',
        purpose: 'Mathematics performance review',
        status: 'Confirmed',
        type: 'Virtual'
      },
      {
        id: 2,
        child: 'David Johnson',
        teacher: 'Dr. David Kimani',
        subject: 'Physics',
        date: '2024-02-01',
        time: '15:30',
        purpose: 'IGCSE preparation discussion',
        status: 'Pending',
        type: 'In-person'
      }
    ];

    const mockPastMeetings = [
      {
        id: 3,
        child: 'Sarah Johnson',
        teacher: 'Mrs. Grace Mwende',
        subject: 'English',
        date: '2024-01-10',
        time: '10:00',
        purpose: 'Reading comprehension improvement',
        notes: 'Good progress noted. Recommended additional reading practice.',
        followUp: 'Schedule follow-up in 4 weeks'
      },
      {
        id: 4,
        child: 'David Johnson',
        teacher: 'Prof. Sarah Mwangi',
        subject: 'Chemistry',
        date: '2023-12-15',
        time: '11:30',
        purpose: 'Laboratory performance review',
        notes: 'Excellent practical skills. Focus on theoretical concepts needed.',
        followUp: 'Completed'
      }
    ];

    setChildren(mockChildren);
    setUpcomingMeetings(mockUpcomingMeetings);
    setPastMeetings(mockPastMeetings);
    
    // Set default selected child
    if (mockChildren.length > 0) {
      setSelectedChild(mockChildren[0].id);
    }
  }, []);

  const handleScheduleMeeting = (e) => {
    e.preventDefault();
    // In real app, this would make an API call
    const newMeeting = {
      id: upcomingMeetings.length + 1,
      child: children.find(c => c.id === selectedChild)?.name,
      teacher: children.find(c => c.id === selectedChild)?.teachers.find(t => t.id === selectedTeacher)?.name,
      subject: children.find(c => c.id === selectedChild)?.teachers.find(t => t.id === selectedTeacher)?.subject,
      date: meetingDate,
      time: meetingTime,
      purpose: meetingPurpose,
      status: 'Pending',
      type: 'Virtual'
    };

    setUpcomingMeetings(prev => [newMeeting, ...prev]);
    
    // Reset form
    setMeetingDate('');
    setMeetingTime('');
    setMeetingPurpose('');
    setSelectedTeacher('');
    
    alert('Meeting request submitted successfully!');
  };

  const cancelMeeting = (meetingId) => {
    if (window.confirm('Are you sure you want to cancel this meeting?')) {
      setUpcomingMeetings(prev => prev.filter(meeting => meeting.id !== meetingId));
      alert('Meeting cancelled successfully.');
    }
  };

  const rescheduleMeeting = (meetingId) => {
    const meeting = upcomingMeetings.find(m => m.id === meetingId);
    if (meeting) {
      setMeetingDate(meeting.date);
      setMeetingTime(meeting.time);
      setMeetingPurpose(meeting.purpose);
      setActiveTab('schedule');
      setUpcomingMeetings(prev => prev.filter(m => m.id !== meetingId));
    }
  };

  const availableTimeSlots = [
    '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
    '14:00', '14:30', '15:00', '15:30', '16:00', '16:30'
  ];

  return (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item"><Link to="/dashboard">Dashboard</Link></li>
              <li className="breadcrumb-item"><Link to="/parent-dashboard">Parent</Link></li>
              <li className="breadcrumb-item active">Parent-Teacher Meetings</li>
            </ol>
          </nav>
          
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h1 className="display-5 fw-bold text-primary">Parent-Teacher Meetings</h1>
              <p className="lead mb-0">Schedule and manage meetings with teachers</p>
            </div>
            <div className="text-end">
              <div className="badge bg-primary fs-6">
                {upcomingMeetings.length} Upcoming
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Tabs */}
      <div className="card">
        <div className="card-header">
          <ul className="nav nav-tabs card-header-tabs">
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'schedule' ? 'active' : ''}`}
                onClick={() => setActiveTab('schedule')}
              >
                <i className="bi bi-calendar-plus me-2"></i>
                Schedule Meeting
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'upcoming' ? 'active' : ''}`}
                onClick={() => setActiveTab('upcoming')}
              >
                <i className="bi bi-calendar-check me-2"></i>
                Upcoming Meetings
                <span className="badge bg-primary ms-2">{upcomingMeetings.length}</span>
              </button>
            </li>
            <li className="nav-item">
              <button
                className={`nav-link ${activeTab === 'history' ? 'active' : ''}`}
                onClick={() => setActiveTab('history')}
              >
                <i className="bi bi-clock-history me-2"></i>
                Meeting History
              </button>
            </li>
          </ul>
        </div>

        <div className="card-body">
          {/* Schedule Meeting Tab */}
          {activeTab === 'schedule' && (
            <div className="row">
              <div className="col-md-8">
                <h5>Schedule New Meeting</h5>
                <form onSubmit={handleScheduleMeeting}>
                  <div className="row mb-3">
                    <div className="col-md-6">
                      <label className="form-label">Select Child</label>
                      <select 
                        className="form-select"
                        value={selectedChild}
                        onChange={(e) => setSelectedChild(e.target.value)}
                        required
                      >
                        <option value="">Choose child...</option>
                        {children.map(child => (
                          <option key={child.id} value={child.id}>
                            {child.name} - {child.grade} ({child.curriculum})
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="col-md-6">
                      <label className="form-label">Select Teacher</label>
                      <select 
                        className="form-select"
                        value={selectedTeacher}
                        onChange={(e) => setSelectedTeacher(e.target.value)}
                        required
                        disabled={!selectedChild}
                      >
                        <option value="">Choose teacher...</option>
                        {selectedChild && children.find(c => c.id === selectedChild)?.teachers.map(teacher => (
                          <option key={teacher.id} value={teacher.id}>
                            {teacher.name} - {teacher.subject}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="row mb-3">
                    <div className="col-md-6">
                      <label className="form-label">Meeting Date</label>
                      <input
                        type="date"
                        className="form-control"
                        value={meetingDate}
                        onChange={(e) => setMeetingDate(e.target.value)}
                        min={new Date().toISOString().split('T')[0]}
                        required
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label">Meeting Time</label>
                      <select 
                        className="form-select"
                        value={meetingTime}
                        onChange={(e) => setMeetingTime(e.target.value)}
                        required
                      >
                        <option value="">Choose time...</option>
                        {availableTimeSlots.map(slot => (
                          <option key={slot} value={slot}>
                            {slot}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="mb-3">
                    <label className="form-label">Purpose of Meeting</label>
                    <textarea
                      className="form-control"
                      rows="4"
                      value={meetingPurpose}
                      onChange={(e) => setMeetingPurpose(e.target.value)}
                      placeholder="Please describe the purpose of this meeting and any specific topics you'd like to discuss..."
                      required
                    ></textarea>
                  </div>

                  <div className="mb-3">
                    <label className="form-label">Meeting Type</label>
                    <div>
                      <div className="form-check form-check-inline">
                        <input className="form-check-input" type="radio" name="meetingType" id="virtual" defaultChecked />
                        <label className="form-check-label" htmlFor="virtual">
                          Virtual Meeting
                        </label>
                      </div>
                      <div className="form-check form-check-inline">
                        <input className="form-check-input" type="radio" name="meetingType" id="inPerson" />
                        <label className="form-check-label" htmlFor="inPerson">
                          In-person Meeting
                        </label>
                      </div>
                    </div>
                  </div>

                  <button type="submit" className="btn btn-primary">
                    <i className="bi bi-send me-2"></i>
                    Schedule Meeting
                  </button>
                </form>
              </div>

              <div className="col-md-4">
                <h5>Meeting Guidelines</h5>
                <div className="card bg-light">
                  <div className="card-body">
                    <h6>Before the Meeting:</h6>
                    <ul className="small">
                      <li>Review your child's recent performance</li>
                      <li>Prepare specific questions or concerns</li>
                      <li>Check the meeting platform requirements</li>
                      <li>Test your audio/video equipment</li>
                    </ul>

                    <h6>During the Meeting:</h6>
                    <ul className="small">
                      <li>Be punctual and respectful of time</li>
                      <li>Discuss both strengths and areas for improvement</li>
                      <li>Ask for specific suggestions for support</li>
                      <li>Take notes for follow-up actions</li>
                    </ul>

                    <h6>Meeting Duration:</h6>
                    <p className="small mb-0">
                      Standard meetings are 30 minutes. For more complex issues, 
                      consider scheduling a follow-up meeting.
                    </p>
                  </div>
                </div>

                <div className="card mt-3">
                  <div className="card-header bg-primary text-white">
                    <h6 className="mb-0">Quick Contacts</h6>
                  </div>
                  <div className="card-body">
                    <div className="small">
                      <div className="mb-2">
                        <strong>School Office:</strong><br/>
                        +254 720 123 456
                      </div>
                      <div className="mb-2">
                        <strong>Email:</strong><br/>
                        meetings@delvok.ac.ke
                      </div>
                      <div>
                        <strong>Office Hours:</strong><br/>
                        Mon-Fri: 8:00 AM - 4:00 PM
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Upcoming Meetings Tab */}
          {activeTab === 'upcoming' && (
            <div>
              <h5>Upcoming Meetings</h5>
              {upcomingMeetings.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-calendar-x display-1 text-muted"></i>
                  <h4 className="mt-3">No Upcoming Meetings</h4>
                  <p className="text-muted">
                    You don't have any scheduled meetings. Schedule a meeting to get started.
                  </p>
                  <button 
                    className="btn btn-primary"
                    onClick={() => setActiveTab('schedule')}
                  >
                    Schedule a Meeting
                  </button>
                </div>
              ) : (
                <div className="row">
                  {upcomingMeetings.map(meeting => (
                    <div key={meeting.id} className="col-md-6 mb-3">
                      <div className="card">
                        <div className="card-body">
                          <div className="d-flex justify-content-between align-items-start mb-2">
                            <div>
                              <h6 className="mb-0">{meeting.teacher}</h6>
                              <small className="text-muted">{meeting.subject}</small>
                            </div>
                            <span className={`badge ${
                              meeting.status === 'Confirmed' ? 'bg-success' : 'bg-warning'
                            }`}>
                              {meeting.status}
                            </span>
                          </div>
                          
                          <p className="mb-2"><strong>Child:</strong> {meeting.child}</p>
                          <p className="mb-2"><strong>Purpose:</strong> {meeting.purpose}</p>
                          
                          <div className="row mb-3">
                            <div className="col-6">
                              <small><strong>Date:</strong><br/>{new Date(meeting.date).toLocaleDateString()}</small>
                            </div>
                            <div className="col-6">
                              <small><strong>Time:</strong><br/>{meeting.time}</small>
                            </div>
                          </div>

                          <div className="d-flex gap-2">
                            <button 
                              className="btn btn-outline-primary btn-sm"
                              onClick={() => rescheduleMeeting(meeting.id)}
                            >
                              Reschedule
                            </button>
                            <button 
                              className="btn btn-outline-danger btn-sm"
                              onClick={() => cancelMeeting(meeting.id)}
                            >
                              Cancel
                            </button>
                            <button className="btn btn-outline-info btn-sm">
                              Add to Calendar
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Meeting History Tab */}
          {activeTab === 'history' && (
            <div>
              <h5>Meeting History</h5>
              {pastMeetings.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-clock-history display-1 text-muted"></i>
                  <h4 className="mt-3">No Past Meetings</h4>
                  <p className="text-muted">
                    Your meeting history will appear here after completed meetings.
                  </p>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-bordered">
                    <thead className="table-light">
                      <tr>
                        <th>Date</th>
                        <th>Teacher</th>
                        <th>Subject</th>
                        <th>Child</th>
                        <th>Purpose</th>
                        <th>Notes</th>
                        <th>Follow-up</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pastMeetings.map(meeting => (
                        <tr key={meeting.id}>
                          <td>{new Date(meeting.date).toLocaleDateString()}</td>
                          <td>{meeting.teacher}</td>
                          <td>{meeting.subject}</td>
                          <td>{meeting.child}</td>
                          <td>{meeting.purpose}</td>
                          <td>
                            <button 
                              className="btn btn-outline-info btn-sm"
                              data-bs-toggle="tooltip" 
                              title={meeting.notes}
                            >
                              View Notes
                            </button>
                          </td>
                          <td>
                            <span className={`badge ${
                              meeting.followUp === 'Completed' ? 'bg-success' : 'bg-warning'
                            }`}>
                              {meeting.followUp}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Additional Resources */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card bg-light">
            <div className="card-body">
              <h6 className="mb-3">Meeting Resources</h6>
              <div className="row">
                <div className="col-md-3 mb-2">
                  <button className="btn btn-outline-primary btn-sm w-100">
                    <i className="bi bi-download me-2"></i>
                    Meeting Preparation Guide
                  </button>
                </div>
                <div className="col-md-3 mb-2">
                  <button className="btn btn-outline-success btn-sm w-100">
                    <i className="bi bi-question-circle me-2"></i>
                    FAQ for Parents
                  </button>
                </div>
                <div className="col-md-3 mb-2">
                  <button className="btn btn-outline-info btn-sm w-100">
                    <i className="bi bi-camera-video me-2"></i>
                    Virtual Meeting Guide
                  </button>
                </div>
                <div className="col-md-3 mb-2">
                  <button className="btn btn-outline-warning btn-sm w-100">
                    <i className="bi bi-telephone me-2"></i>
                    Contact Support
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ParentMeetings;