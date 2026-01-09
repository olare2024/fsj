import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { downloadsAPI } from '../../services/downloadsAPI';

import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Form,
  Modal,
  Table,
  Badge,
  ProgressBar,
  Alert,
  Spinner,
  InputGroup,
  Dropdown,
  Tooltip,
  OverlayTrigger
} from 'react-bootstrap';
import {
  Search,
  Download,
  Clock,
  CloudUpload,
  Star,
  StarFill,
  StarHalf,
  FileEarmark,
  FileEarmarkPdf,
  FileEarmarkWord,
  FileEarmarkExcel,
  FileEarmarkPpt,
  FileEarmarkMusic,
  FileEarmarkZip,
  Trophy,
  Trash,
  CheckCircle,
  InfoCircle,
  FolderX,
  TrophyFill,
  ClockHistory,
  Filter,
  SortAlphaDown,
  SortNumericDown,
  Calendar,
  GraphUp,
  FileEarmarkArrowDown,
  FilePlus,
  XCircle,
  ChevronRight
} from 'react-bootstrap-icons';

const Downloads = () => {
  const { currentUser } = useAuth();
  const [downloads, setDownloads] = useState([]);
  const [popularDownloads, setPopularDownloads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('popular');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showDownloadModal, setShowDownloadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [downloadHistory, setDownloadHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [categories, setCategories] = useState([]);
  const [downloadStats, setDownloadStats] = useState(null);
  const [userRatings, setUserRatings] = useState([]);
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [fileToRate, setFileToRate] = useState(null);
  const [ratingValue, setRatingValue] = useState(5);
  const [uploading, setUploading] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [newFile, setNewFile] = useState({
    name: '',
    description: '',
    category: '',
    file: null,
    required_role: 'all'
  });

  const ROLE_CHOICES = [
    { value: 'all', label: 'All Users' },
    { value: 'student', label: 'Students Only' },
    { value: 'teacher', label: 'Teachers Only' },
    { value: 'parent', label: 'Parents Only' },
    { value: 'admin', label: 'Administrators Only' },
    { value: 'staff', label: 'Staff Only' }
  ];

  const FILE_TYPES = [
    { value: 'pdf', label: 'PDF Document', icon: FileEarmarkPdf, color: 'danger' },
    { value: 'docx', label: 'Word Document', icon: FileEarmarkWord, color: 'primary' },
    { value: 'xlsx', label: 'Excel Spreadsheet', icon: FileEarmarkExcel, color: 'success' },
    { value: 'pptx', label: 'PowerPoint', icon: FileEarmarkPpt, color: 'warning' },
    { value: 'mp3', label: 'Audio File', icon: FileEarmarkMusic, color: 'info' },
    { value: 'zip', label: 'ZIP Archive', icon: FileEarmarkZip, color: 'secondary' },
    { value: 'other', label: 'Other', icon: FileEarmark, color: 'dark' }
  ];

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchCategories(),
        fetchFiles(),
        fetchPopularDownloads(),
        fetchDownloadStats()
      ]);

      if (currentUser) {
        await Promise.all([
          fetchDownloadHistory(),
          fetchUserRatings()
        ]);
      }
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await downloadsAPI.getCategories();
      if (response.success) {
        setCategories(response.data);
      }
    } catch (error) {
      toast.error('Failed to load categories');
    }
  };

  const fetchFiles = async () => {
    try {
      const response = await downloadsAPI.getFiles();
      if (response.success) {
        setDownloads(response.data.results || response.data);
      }
    } catch (error) {
      toast.error('Failed to load files');
    }
  };

  const fetchPopularDownloads = async () => {
    try {
      const response = await downloadsAPI.getPopularDownloads();
      if (response.success) {
        setPopularDownloads(response.data);
      }
    } catch (error) {
      console.error('Error fetching popular downloads:', error);
    }
  };

  const fetchDownloadHistory = async () => {
    try {
      const response = await downloadsAPI.getDownloadHistory();
      if (response.success) {
        setDownloadHistory(response.data.results || response.data);
      }
    } catch (error) {
      console.error('Error fetching download history:', error);
    }
  };

  const fetchUserRatings = async () => {
    try {
      const response = await downloadsAPI.getUserRatings();
      if (response.success) {
        setUserRatings(response.data);
      }
    } catch (error) {
      console.error('Error fetching user ratings:', error);
    }
  };

  const fetchDownloadStats = async () => {
    try {
      const response = await downloadsAPI.getDownloadStats();
      if (response.success) {
        setDownloadStats(response.data);
      }
    } catch (error) {
      console.error('Error fetching download stats:', error);
    }
  };

  const hasAccessToFile = (file) => {
    if (!currentUser) return false;
    
    const userRole = currentUser.role;
    const fileRole = file.required_role;
    
    if (fileRole === 'all') return true;
    return userRole === fileRole || currentUser.role === 'admin';
  };

  const getFileIcon = (fileType) => {
    const fileTypeObj = FILE_TYPES.find(ft => ft.value === fileType);
    const IconComponent = fileTypeObj?.icon || FileEarmark;
    const color = fileTypeObj?.color || 'dark';
    
    return <IconComponent className={`me-2 text-${color}`} size={20} />;
  };

  const getCategoryBadge = (categoryId) => {
    const category = categories.find(c => c.id === categoryId);
    if (!category) return <Badge bg="secondary">Unknown</Badge>;
    
    const colors = ['primary', 'success', 'info', 'warning', 'danger', 'secondary'];
    const colorIndex = categoryId % colors.length;
    return <Badge bg={colors[colorIndex]}>{category.name}</Badge>;
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  const getRatingStars = (rating, interactive = false, onRate = null) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      let StarIcon = Star;
      if (i <= Math.floor(rating)) {
        StarIcon = StarFill;
      } else if (i - 0.5 <= rating) {
        StarIcon = StarHalf;
      }

      stars.push(
        <StarIcon
          key={i}
          className={`text-warning ${interactive ? 'cursor-pointer' : ''}`}
          size={interactive ? 24 : 16}
          onClick={() => interactive && onRate && onRate(i)}
          style={{ cursor: interactive ? 'pointer' : 'default' }}
        />
      );
    }
    return (
      <div className="d-flex align-items-center">
        {stars}
        <span className="ms-2 text-muted small">({rating?.toFixed(1) || '0.0'})</span>
      </div>
    );
  };

  const getUserRating = (fileId) => {
    return userRatings.find(r => r.file === fileId)?.rating;
  };

  const filteredDownloads = downloads
    .filter(file => {
      const matchesSearch = searchTerm === '' || 
        file.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        file.description?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesCategory = selectedCategory === 'all' || file.category === parseInt(selectedCategory);
      const hasAccess = hasAccessToFile(file);
      
      return matchesSearch && matchesCategory && hasAccess && file.is_active;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'popular':
          return b.downloads - a.downloads;
        case 'recent':
          return new Date(b.upload_date || 0) - new Date(a.upload_date || 0);
        case 'name':
          return a.name?.localeCompare(b.name);
        case 'rating':
          return b.rating - a.rating;
        default:
          return 0;
      }
    });

  const handleDownload = async (file) => {
    setSelectedFile(file);
    setShowDownloadModal(true);
  };

  const confirmDownload = async () => {
    if (!selectedFile) return;

    try {
      const response = await downloadsAPI.downloadFile(selectedFile.id);
      
      if (response.success) {
        const blob = new Blob([response.data]);
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = selectedFile.name;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        setDownloads(prev => prev.map(f => 
          f.id === selectedFile.id 
            ? { ...f, downloads: (f.downloads || 0) + 1, last_download: new Date().toISOString() }
            : f
        ));

        setPopularDownloads(prev => prev.map(f => 
          f.id === selectedFile.id 
            ? { ...f, downloads: (f.downloads || 0) + 1, last_download: new Date().toISOString() }
            : f
        ));

        if (currentUser) {
          await fetchDownloadHistory();
        }

        toast.success('File downloaded successfully!');
      } else {
        toast.error(response.error?.message || 'Download failed');
      }
    } catch (error) {
      toast.error('Error downloading file');
    } finally {
      setShowDownloadModal(false);
      setSelectedFile(null);
    }
  };

  const handleRateFile = async () => {
    if (!fileToRate) return;

    try {
      const existingRating = userRatings.find(r => r.file === fileToRate.id);
      let response;

      if (existingRating) {
        response = await downloadsAPI.updateFileRating(existingRating.id, ratingValue);
      } else {
        response = await downloadsAPI.rateFile(fileToRate.id, ratingValue);
      }

      if (response.success) {
        toast.success('Rating submitted successfully!');
        await fetchUserRatings();
        
        setDownloads(prev => prev.map(f => {
          if (f.id === fileToRate.id) {
            const ratings = f.ratings || [];
            const total = ratings.reduce((sum, r) => sum + r.rating, 0) + ratingValue;
            const count = ratings.length + (existingRating ? 0 : 1);
            const avgRating = total / count;
            return { ...f, rating: avgRating.toFixed(2) };
          }
          return f;
        }));
      } else {
        toast.error(response.error?.message || 'Failed to submit rating');
      }
    } catch (error) {
      toast.error('Error submitting rating');
    } finally {
      setShowRatingModal(false);
      setFileToRate(null);
      setRatingValue(5);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!newFile.file || !newFile.name.trim()) {
      toast.error('Please provide file and name');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('name', newFile.name);
      formData.append('description', newFile.description);
      formData.append('category', newFile.category);
      formData.append('file', newFile.file);
      formData.append('required_role', newFile.required_role);

      const response = await downloadsAPI.createFile(formData);
      
      if (response.success) {
        toast.success('File uploaded successfully!');
        setShowUploadModal(false);
        setNewFile({
          name: '',
          description: '',
          category: '',
          file: null,
          required_role: 'all'
        });
        await fetchFiles();
        await fetchCategories();
      } else {
        toast.error(response.error?.message || 'Upload failed');
      }
    } catch (error) {
      toast.error('Error uploading file');
    } finally {
      setUploading(false);
    }
  };

  const handleFileDelete = async (fileId) => {
    if (!window.confirm('Are you sure you want to delete this file?')) return;

    try {
      const response = await downloadsAPI.deleteFile(fileId);
      if (response.success) {
        toast.success('File deleted successfully!');
        setDownloads(prev => prev.filter(f => f.id !== fileId));
        setPopularDownloads(prev => prev.filter(f => f.id !== fileId));
      } else {
        toast.error(response.error?.message || 'Delete failed');
      }
    } catch (error) {
      toast.error('Error deleting file');
    }
  };

  const handleClearHistory = async () => {
    if (!window.confirm('Clear all download history?')) return;

    try {
      const response = await downloadsAPI.clearDownloadHistory();
      if (response.success) {
        toast.success('History cleared successfully!');
        setDownloadHistory([]);
      } else {
        toast.error(response.error?.message || 'Clear history failed');
      }
    } catch (error) {
      toast.error('Error clearing history');
    }
  };

  const renderSortIcon = () => {
    switch (sortBy) {
      case 'popular':
        return <GraphUp className="me-2" />;
      case 'recent':
        return <Calendar className="me-2" />;
      case 'name':
        return <SortAlphaDown className="me-2" />;
      case 'rating':
        return <SortNumericDown className="me-2" />;
      default:
        return <Filter className="me-2" />;
    }
  };

  if (loading) {
    return (
      <Container className="mt-5">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-3">Loading downloads...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="py-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h2 mb-1">Downloads Center</h1>
              <p className="text-muted mb-0">
                Access and download school resources and documents
              </p>
            </div>
            <div className="d-flex gap-2">
              {currentUser?.role === 'admin' && (
                <Button 
                  variant="primary"
                  onClick={() => setShowUploadModal(true)}
                >
                  <CloudUpload className="me-2" />
                  Upload File
                </Button>
              )}
              {currentUser && (
                <Button 
                  variant="outline-secondary"
                  onClick={() => setShowHistory(!showHistory)}
                >
                  <ClockHistory className="me-2" />
                  My Downloads ({downloadHistory.length})
                </Button>
              )}
            </div>
          </div>
        </Col>
      </Row>

      {/* Stats Cards */}
      {downloadStats && (
        <Row className="mb-4">
          <Col md={3}>
            <Card className="text-center h-100 border-primary">
              <Card.Body>
                <h2 className="text-primary mb-0">{downloadStats.total_downloads || 0}</h2>
                <p className="text-muted mb-0">Total Downloads</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center h-100 border-success">
              <Card.Body>
                <h2 className="text-success mb-0">{downloads.length}</h2>
                <p className="text-muted mb-0">Available Files</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center h-100 border-info">
              <Card.Body>
                <h2 className="text-info mb-0">{categories.length}</h2>
                <p className="text-muted mb-0">Categories</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center h-100 border-warning">
              <Card.Body>
                <h2 className="text-warning mb-0">
                  {downloads.filter(f => f.downloads > 100).length}
                </h2>
                <p className="text-muted mb-0">Popular Files</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Search and Filters */}
      <Card className="mb-4">
        <Card.Body>
          <Row className="g-3">
            <Col md={5}>
              <InputGroup>
                <InputGroup.Text>
                  <Search />
                </InputGroup.Text>
                <Form.Control
                  type="text"
                  placeholder="Search files..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </InputGroup>
            </Col>
            <Col md={4}>
              <Form.Select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                <option value="all">All Categories</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name} ({category.files_count || 0})
                  </option>
                ))}
              </Form.Select>
            </Col>
            <Col md={3}>
              <Form.Select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="popular">
                  <span className="d-flex align-items-center">
                    <GraphUp className="me-2" size={14} />
                    Most Popular
                  </span>
                </option>
                <option value="recent">
                  <span className="d-flex align-items-center">
                    <Calendar className="me-2" size={14} />
                    Recently Added
                  </span>
                </option>
                <option value="name">
                  <span className="d-flex align-items-center">
                    <SortAlphaDown className="me-2" size={14} />
                    Name (A-Z)
                  </span>
                </option>
                <option value="rating">
                  <span className="d-flex align-items-center">
                    <SortNumericDown className="me-2" size={14} />
                    Highest Rated
                  </span>
                </option>
              </Form.Select>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Download History */}
      <Modal show={showHistory && currentUser} onHide={() => setShowHistory(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>My Download History</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {downloadHistory.length === 0 ? (
            <div className="text-center py-4">
              <Clock className="display-4 text-muted mb-3" />
              <p className="text-muted">No download history yet</p>
            </div>
          ) : (
            <Table hover responsive>
              <thead>
                <tr>
                  <th>File Name</th>
                  <th>Download Date</th>
                  <th>Size</th>
                  <th>Category</th>
                </tr>
              </thead>
              <tbody>
                {downloadHistory.map(record => (
                  <tr key={record.id}>
                    <td>{record.file?.name || 'Unknown File'}</td>
                    <td>{new Date(record.download_date).toLocaleString()}</td>
                    <td>{formatFileSize(record.file?.file_size)}</td>
                    <td>{getCategoryBadge(record.file?.category)}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button 
            variant="outline-danger"
            onClick={handleClearHistory}
            disabled={downloadHistory.length === 0}
          >
            Clear All
          </Button>
          <Button variant="secondary" onClick={() => setShowHistory(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Popular Downloads */}
      {popularDownloads.length > 0 && (
        <Card className="mb-4">
          <Card.Header>
            <h5 className="mb-0 d-flex align-items-center">
              <TrophyFill className="text-warning me-2" />
              Most Popular Downloads
            </h5>
          </Card.Header>
          <Card.Body>
            <Row>
              {popularDownloads.slice(0, 3).map(file => (
                <Col key={file.id} md={4}>
                  <Card className="h-100">
                    <Card.Body className="d-flex flex-column">
                      <div className="text-center mb-3">
                        {getFileIcon(file.file_type)}
                      </div>
                      <Card.Title className="text-center h6">{file.name}</Card.Title>
                      <div className="text-center mb-2">
                        {getCategoryBadge(file.category)}
                      </div>
                      <div className="text-center mb-2">
                        {getRatingStars(file.rating || 0)}
                      </div>
                      <div className="text-center small text-muted mb-3">
                        {formatFileSize(file.file_size)} • {file.downloads || 0} downloads
                      </div>
                      <Card.Text className="small text-muted text-center flex-grow-1">
                        {file.description?.substring(0, 100)}...
                      </Card.Text>
                      <div className="mt-auto">
                        <Button
                          variant="primary"
                          className="w-100"
                          onClick={() => handleDownload(file)}
                        >
                          <Download className="me-1" />
                          Download
                        </Button>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card.Body>
        </Card>
      )}

      {/* All Downloads Table */}
      <Card>
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">All Available Files</h5>
          <span className="text-muted">
            {filteredDownloads.length} files
          </span>
        </Card.Header>
        <Card.Body>
          {filteredDownloads.length === 0 ? (
            <div className="text-center py-5">
              <FolderX className="display-4 text-muted mb-3" />
              <h5>No files found</h5>
              <p className="text-muted">Try adjusting your search or filter criteria</p>
            </div>
          ) : (
            <Table hover responsive>
              <thead>
                <tr>
                  <th>File Name</th>
                  <th>Category</th>
                  <th>Type</th>
                  <th>Size</th>
                  <th>Downloads</th>
                  <th>Rating</th>
                  <th>Last Download</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredDownloads.map(file => (
                  <tr key={file.id}>
                    <td>
                      <div className="d-flex align-items-center">
                        {getFileIcon(file.file_type)}
                        <div>
                          <div className="fw-semibold">{file.name}</div>
                          <small className="text-muted">{file.description?.substring(0, 80)}...</small>
                        </div>
                      </div>
                    </td>
                    <td>{getCategoryBadge(file.category)}</td>
                    <td>
                      <Badge bg="secondary">
                        {file.file_type?.toUpperCase()}
                      </Badge>
                    </td>
                    <td>{formatFileSize(file.file_size)}</td>
                    <td>
                      <div className="d-flex align-items-center">
                        <ProgressBar 
                          now={Math.min((file.downloads || 0) / 10, 100)} 
                          style={{ height: '6px', flex: 1, marginRight: '0.5rem' }}
                          variant="primary"
                        />
                        <span>{file.downloads || 0}</span>
                      </div>
                    </td>
                    <td>
                      <div className="d-flex align-items-center">
                        {getRatingStars(file.rating || 0)}
                        {getUserRating(file.id) && (
                          <CheckCircle className="text-success ms-2" />
                        )}
                      </div>
                    </td>
                    <td>{formatDate(file.last_download)}</td>
                    <td>
                      <div className="d-flex gap-2">
                        <OverlayTrigger
                          overlay={<Tooltip>Download</Tooltip>}
                        >
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => handleDownload(file)}
                          >
                            <Download />
                          </Button>
                        </OverlayTrigger>
                        <OverlayTrigger
                          overlay={<Tooltip>Rate</Tooltip>}
                        >
                          <Button
                            variant="outline-warning"
                            size="sm"
                            onClick={() => {
                              setFileToRate(file);
                              setRatingValue(getUserRating(file.id) || 5);
                              setShowRatingModal(true);
                            }}
                          >
                            <Star />
                          </Button>
                        </OverlayTrigger>
                        {currentUser?.role === 'admin' && (
                          <OverlayTrigger
                            overlay={<Tooltip>Delete</Tooltip>}
                          >
                            <Button
                              variant="outline-danger"
                              size="sm"
                              onClick={() => handleFileDelete(file.id)}
                            >
                              <Trash />
                            </Button>
                          </OverlayTrigger>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>

      {/* Download Confirmation Modal */}
      <Modal show={showDownloadModal} onHide={() => setShowDownloadModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Download</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedFile && (
            <>
              <div className="d-flex align-items-center mb-3">
                {getFileIcon(selectedFile.file_type)}
                <div>
                  <h6 className="mb-0">{selectedFile.name}</h6>
                  <small className="text-muted">
                    {formatFileSize(selectedFile.file_size)} • {selectedFile.file_type?.toUpperCase()}
                  </small>
                </div>
              </div>
              <p>{selectedFile.description}</p>
              <Alert variant="info" className="small">
                <InfoCircle className="me-2" />
                This download will be recorded in your history.
              </Alert>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDownloadModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={confirmDownload}>
            <Download className="me-1" />
            Download Now
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Rating Modal */}
      <Modal show={showRatingModal} onHide={() => setShowRatingModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Rate This File</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {fileToRate && (
            <>
              <div className="text-center mb-4">
                <h5>{fileToRate.name}</h5>
                <p className="text-muted">How would you rate this file?</p>
                
                <div className="d-flex justify-content-center mb-3">
                  {getRatingStars(ratingValue, true, setRatingValue)}
                </div>
                
                <div className="text-muted small">
                  {ratingValue === 5 && 'Excellent - Perfect file!'}
                  {ratingValue === 4 && 'Very Good - Very useful'}
                  {ratingValue === 3 && 'Good - Could be better'}
                  {ratingValue === 2 && 'Fair - Needs improvement'}
                  {ratingValue === 1 && 'Poor - Not helpful'}
                </div>
              </div>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowRatingModal(false)}>
            Cancel
          </Button>
          <Button variant="warning" onClick={handleRateFile}>
            <StarFill className="me-1" />
            Submit Rating
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Upload Modal */}
      <Modal show={showUploadModal} onHide={() => setShowUploadModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Upload New File</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleFileUpload}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>File *</Form.Label>
              <Form.Control
                type="file"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.mp3,.zip"
                onChange={(e) => setNewFile({...newFile, file: e.target.files[0]})}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>File Name *</Form.Label>
              <Form.Control
                type="text"
                value={newFile.name}
                onChange={(e) => setNewFile({...newFile, name: e.target.value})}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={newFile.description}
                onChange={(e) => setNewFile({...newFile, description: e.target.value})}
              />
            </Form.Group>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Category *</Form.Label>
                  <Form.Select
                    value={newFile.category}
                    onChange={(e) => setNewFile({...newFile, category: e.target.value})}
                    required
                  >
                    <option value="">Select Category</option>
                    {categories.map(cat => (
                      <option key={cat.id} value={cat.id}>
                        {cat.name}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Access Level</Form.Label>
                  <Form.Select
                    value={newFile.required_role}
                    onChange={(e) => setNewFile({...newFile, required_role: e.target.value})}
                  >
                    {ROLE_CHOICES.map(role => (
                      <option key={role.value} value={role.value}>
                        {role.label}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Alert variant="info" className="small">
              <InfoCircle className="me-2" />
              Maximum file size: 100MB. Supported formats: PDF, DOC, XLS, PPT, MP3, ZIP
            </Alert>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowUploadModal(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={uploading}>
              {uploading ? (
                <>
                  <Spinner animation="border" size="sm" className="me-2" />
                  Uploading...
                </>
              ) : (
                'Upload File'
              )}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
};

export default Downloads;