import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Badge, Button, Form, InputGroup, Spinner } from 'react-bootstrap';
import { useAuth } from '../../context/AuthContext';

const Documents = () => {
  const { currentUser, isAuthenticated, loading: authLoading } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);

  const categories = ['all', 'academic', 'administrative', 'policy', 'curriculum', 'cbc', 'cambridge'];

  useEffect(() => {
    // Only fetch documents if user is authenticated
    if (isAuthenticated && currentUser) {
      const fetchDocuments = async () => {
        setLoading(true);
        
        const mockDocuments = [
          {
            id: 1,
            name: 'School Academic Calendar 2024',
            category: 'academic',
            type: 'pdf',
            size: '2.4 MB',
            uploaded: '2024-01-15',
            uploadedBy: 'Admin Office',
            downloads: 145,
            access: 'public'
          },
          // ... rest of your mock data
        ];

        setTimeout(() => {
          setDocuments(mockDocuments);
          setLoading(false);
        }, 1000);
      };

      fetchDocuments();
    }
  }, [isAuthenticated, currentUser]);

  // Safe access to user role
  const userRole = currentUser?.role || 'guest';

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || doc.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getFileIcon = (type) => {
    const icons = {
      'pdf': 'bi-file-earmark-pdf text-danger',
      'docx': 'bi-file-earmark-word text-primary',
      'xlsx': 'bi-file-earmark-excel text-success',
      'pptx': 'bi-file-earmark-ppt text-warning',
      'zip': 'bi-file-earmark-zip text-secondary'
    };
    return <i className={`bi ${icons[type] || 'bi-file-earmark'} me-2`}></i>;
  };

  const getCategoryBadge = (category) => {
    const variants = {
      'academic': 'primary',
      'administrative': 'info',
      'policy': 'warning',
      'curriculum': 'success',
      'cbc': 'danger',
      'cambridge': 'dark'
    };
    return <Badge bg={variants[category] || 'secondary'}>{category}</Badge>;
  };

  const getAccessBadge = (access) => {
    const variants = {
      'public': 'success',
      'teachers': 'info',
      'students': 'primary',
      'parents': 'warning',
      'admin': 'danger'
    };
    return <Badge bg={variants[access] || 'secondary'}>{access}</Badge>;
  };

  const canDownload = (document) => {
    if (document.access === 'public') return true;
    if (document.access === 'teachers' && userRole === 'teacher') return true;
    if (document.access === 'students' && userRole === 'student') return true;
    if (document.access === 'parents' && userRole === 'parent') return true;
    if (document.access === 'admin' && userRole === 'admin') return true;
    return false;
  };

  const canUpload = () => {
    return ['admin', 'teacher', 'staff'].includes(userRole);
  };

  // Show loading while auth is being checked
  if (authLoading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </div>
      </Container>
    );
  }

  // Show message if not authenticated
  if (!isAuthenticated) {
    return (
      <Container className="mt-4">
        <Card>
          <Card.Body className="text-center">
            <h4>Access Denied</h4>
            <p>Please log in to access documents.</p>
            <Button variant="primary" href="/login">
              Login
            </Button>
          </Card.Body>
        </Card>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading documents...</span>
          </Spinner>
        </div>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2>School Documents</h2>
            {canUpload() && (
              <Button variant="primary">
                <i className="bi bi-upload"></i> Upload Document
              </Button>
            )}
          </div>

          {/* Search and Filter */}
          <Card className="mb-4">
            <Card.Body>
              <Row>
                <Col md={8}>
                  <InputGroup>
                    <Form.Control
                      type="text"
                      placeholder="Search documents..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    <Button variant="outline-secondary">
                      <i className="bi bi-search"></i>
                    </Button>
                  </InputGroup>
                </Col>
                <Col md={4}>
                  <Form.Select 
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                  >
                    <option value="all">All Categories</option>
                    <option value="academic">Academic</option>
                    <option value="administrative">Administrative</option>
                    <option value="policy">Policies</option>
                    <option value="curriculum">Curriculum</option>
                    <option value="cbc">CBC Materials</option>
                    <option value="cambridge">Cambridge</option>
                  </Form.Select>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Documents Table */}
          <Card>
            <Card.Header>
              <h5 className="mb-0">Available Documents</h5>
            </Card.Header>
            <Card.Body>
              {filteredDocuments.length === 0 ? (
                <div className="text-center py-4">
                  <i className="bi bi-folder-x display-4 text-muted"></i>
                  <p className="mt-3">No documents found matching your criteria.</p>
                </div>
              ) : (
                <Table responsive striped hover>
                  <thead>
                    <tr>
                      <th>Document Name</th>
                      <th>Category</th>
                      <th>Type</th>
                      <th>Size</th>
                      <th>Uploaded</th>
                      <th>Access</th>
                      <th>Downloads</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredDocuments.map(doc => (
                      <tr key={doc.id}>
                        <td>
                          <div className="d-flex align-items-center">
                            {getFileIcon(doc.type)}
                            <div>
                              <strong>{doc.name}</strong>
                              <br />
                              <small className="text-muted">By {doc.uploadedBy}</small>
                            </div>
                          </div>
                        </td>
                        <td>{getCategoryBadge(doc.category)}</td>
                        <td>
                          <Badge bg="secondary" text="uppercase">
                            {doc.type}
                          </Badge>
                        </td>
                        <td>{doc.size}</td>
                        <td>{doc.uploaded}</td>
                        <td>{getAccessBadge(doc.access)}</td>
                        <td>
                          <Badge bg="light" text="dark">
                            {doc.downloads}
                          </Badge>
                        </td>
                        <td>
                          {canDownload(doc) ? (
                            <Button variant="outline-primary" size="sm">
                              <i className="bi bi-download"></i> Download
                            </Button>
                          ) : (
                            <Badge bg="secondary">No Access</Badge>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>

          {/* Quick Stats */}
          <Row className="mt-4">
            <Col md={2}>
              <Card className="text-center">
                <Card.Body>
                  <h4>{documents.length}</h4>
                  <small className="text-muted">Total Documents</small>
                </Card.Body>
              </Card>
            </Col>
            <Col md={2}>
              <Card className="text-center">
                <Card.Body>
                  <h4 className="text-primary">
                    {documents.filter(d => d.category === 'academic').length}
                  </h4>
                  <small className="text-muted">Academic</small>
                </Card.Body>
              </Card>
            </Col>
            <Col md={2}>
              <Card className="text-center">
                <Card.Body>
                  <h4 className="text-success">
                    {documents.filter(d => d.category === 'cbc').length}
                  </h4>
                  <small className="text-muted">CBC</small>
                </Card.Body>
              </Card>
            </Col>
            <Col md={2}>
              <Card className="text-center">
                <Card.Body>
                  <h4 className="text-info">
                    {documents.filter(d => d.category === 'cambridge').length}
                  </h4>
                  <small className="text-muted">Cambridge</small>
                </Card.Body>
              </Card>
            </Col>
            <Col md={2}>
              <Card className="text-center">
                <Card.Body>
                  <h4 className="text-warning">
                    {documents.filter(d => d.type === 'pdf').length}
                  </h4>
                  <small className="text-muted">PDF Files</small>
                </Card.Body>
              </Card>
            </Col>
            <Col md={2}>
              <Card className="text-center">
                <Card.Body>
                  <h4 className="text-danger">
                    {documents.reduce((total, doc) => total + doc.downloads, 0)}
                  </h4>
                  <small className="text-muted">Total Downloads</small>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>
    </Container>
  );
};

export default Documents;