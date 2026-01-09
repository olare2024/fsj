import React, { useState } from 'react';
import { 
  Container, Row, Col, Card, Button, Alert, 
  Form, Table, ProgressBar 
} from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { financeAPI } from '../../../services/financeAPI.js';
import { Upload, Download, FileText } from 'react-bootstrap-icons'; // Using react-bootstrap-icons

const BulkReceiptUpload = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [uploadResults, setUploadResults] = useState(null);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
      ];
      
      if (!validTypes.includes(selectedFile.type)) {
        setError('Please select a valid Excel file (.xlsx or .xls)');
        return;
      }

      // Validate file size (5MB max)
      if (selectedFile.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB');
        return;
      }

      setFile(selectedFile);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await financeAPI.bulkUploadReceipts(formData, {
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(progress);
        }
      });

      setUploadResults(response.data);
      setSuccess(`Successfully processed ${response.data.created_receipts.length} receipts`);
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed. Please check your file format.');
    } finally {
      setUploading(false);
    }
  };

  const downloadTemplate = async () => {
    try {
      const response = await financeAPI.downloadReceiptTemplate();
      // Create a blob from the response data
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      
      // Create a temporary URL and trigger download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'receipt_upload_template.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download template');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount);
  };

  return (
    <Container fluid className="mt-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h3 mb-1">Bulk Receipt Upload</h1>
              <p className="text-muted mb-0">Upload multiple receipts using Excel template</p>
            </div>
            <Button 
              variant="outline-secondary" 
              onClick={() => navigate('/finance/receipts')}
            >
              Back to Receipts
            </Button>
          </div>
        </Col>
      </Row>

      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}

      <Row>
        <Col lg={8}>
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h5 className="mb-0">Upload File</h5>
            </Card.Header>
            <Card.Body>
              {/* File Upload Area */}
              <div 
                className="border-2 border-dashed rounded p-5 text-center"
                style={{ 
                  border: '2px dashed #dee2e6', 
                  borderRadius: '0.375rem',
                  backgroundColor: uploading ? '#f8f9fa' : 'white'
                }}
              >
                {uploading ? (
                  <div>
                    <div className="spinner-border text-primary mb-3" role="status">
                      <span className="visually-hidden">Uploading...</span>
                    </div>
                    <h5>Uploading File...</h5>
                    <ProgressBar 
                      now={uploadProgress} 
                      label={`${uploadProgress}%`}
                      className="mb-3"
                    />
                    <p className="text-muted">
                      Processing your file. Please don't close this window.
                    </p>
                  </div>
                ) : (
                  <>
                    <Upload size={48} className="text-muted mb-3" />
                    <h5>Drag & Drop your Excel file here</h5>
                    <p className="text-muted mb-3">
                      or click to browse your files
                    </p>
                    <Form.Group>
                      <Form.Control
                        type="file"
                        accept=".xlsx,.xls"
                        onChange={handleFileSelect}
                        className="d-none"
                        id="file-upload"
                      />
                      <Button
                        variant="primary"
                        onClick={() => document.getElementById('file-upload').click()}
                      >
                        Select File
                      </Button>
                    </Form.Group>
                    {file && (
                      <div className="mt-3">
                        <FileText className="me-2" />
                        <strong>{file.name}</strong>
                        <small className="text-muted ms-2">
                          ({(file.size / 1024 / 1024).toFixed(2)} MB)
                        </small>
                      </div>
                    )}
                  </>
                )}
              </div>

              {/* Upload Button */}
              {file && !uploading && (
                <div className="text-center mt-4">
                  <Button
                    variant="primary"
                    onClick={handleUpload}
                    disabled={uploading}
                    size="lg"
                  >
                    {uploading ? 'Uploading...' : 'Upload Receipts'}
                  </Button>
                </div>
              )}
            </Card.Body>
          </Card>

          {/* Upload Results */}
          {uploadResults && (
            <Card className="border-0 shadow-sm mt-4">
              <Card.Header className="bg-white border-0 py-3">
                <h5 className="mb-0">Upload Results</h5>
              </Card.Header>
              <Card.Body>
                <Row className="mb-4">
                  <Col md={4}>
                    <Card className="bg-success bg-opacity-10 border-0">
                      <Card.Body className="text-center">
                        <h4 className="text-success">
                          {uploadResults.created_receipts.length}
                        </h4>
                        <p className="mb-0">Successfully Created</p>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={4}>
                    <Card className="bg-warning bg-opacity-10 border-0">
                      <Card.Body className="text-center">
                        <h4 className="text-warning">
                          {uploadResults.skipped?.length || 0}
                        </h4>
                        <p className="mb-0">Skipped (Duplicates)</p>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={4}>
                    <Card className="bg-danger bg-opacity-10 border-0">
                      <Card.Body className="text-center">
                        <h4 className="text-danger">
                          {uploadResults.not_created?.length || 0}
                        </h4>
                        <p className="mb-0">Failed</p>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>

                {/* Created Receipts */}
                {uploadResults.created_receipts.length > 0 && (
                  <div className="mb-4">
                    <h6>Successfully Created Receipts</h6>
                    <Table responsive bordered size="sm">
                      <thead>
                        <tr>
                          <th>Receipt #</th>
                          <th>Student</th>
                          <th>Amount</th>
                        </tr>
                      </thead>
                      <tbody>
                        {uploadResults.created_receipts.map((receiptNumber, index) => (
                          <tr key={index}>
                            <td>{receiptNumber}</td>
                            <td>N/A</td>
                            <td>N/A</td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </div>
                )}

                {/* Errors */}
                {uploadResults.not_created && uploadResults.not_created.length > 0 && (
                  <div>
                    <h6 className="text-danger">Errors</h6>
                    <Table responsive bordered size="sm">
                      <thead>
                        <tr>
                          <th>Row</th>
                          <th>Error</th>
                          <th>Data</th>
                        </tr>
                      </thead>
                      <tbody>
                        {uploadResults.not_created.map((error, index) => (
                          <tr key={index}>
                            <td>{error.row}</td>
                            <td className="text-danger">{error.error}</td>
                            <td>
                              <small>
                                {JSON.stringify(error.data)}
                              </small>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </div>
                )}
              </Card.Body>
            </Card>
          )}
        </Col>

        <Col lg={4}>
          {/* Instructions Card */}
          <Card className="border-0 shadow-sm mb-4">
            <Card.Header className="bg-white border-0 py-3">
              <h6 className="mb-0">Instructions</h6>
            </Card.Header>
            <Card.Body>
              <h6>File Requirements:</h6>
              <ul className="small">
                <li>Excel format (.xlsx or .xls)</li>
                <li>Maximum file size: 5MB</li>
                <li>Follow the template structure</li>
                <li>Required fields must be filled</li>
              </ul>

              <h6>Required Fields:</h6>
              <ul className="small">
                <li><strong>payer_name</strong> - Payer's full name</li>
                <li><strong>student_admission_number</strong> - Student admission number</li>
                <li><strong>paid_for</strong> - Payment purpose</li>
                <li><strong>amount</strong> - Payment amount</li>
                <li><strong>date</strong> - Payment date (YYYY-MM-DD)</li>
                <li><strong>term</strong> - Term name</li>
              </ul>

              <div className="d-grid">
                <Button
                  variant="outline-primary"
                  onClick={downloadTemplate}
                >
                  <Download className="me-2" />
                  Download Template
                </Button>
              </div>
            </Card.Body>
          </Card>

          {/* Quick Tips Card */}
          <Card className="border-0 shadow-sm">
            <Card.Header className="bg-white border-0 py-3">
              <h6 className="mb-0">Quick Tips</h6>
            </Card.Header>
            <Card.Body>
              <div className="small">
                <p><strong>Payment Methods:</strong></p>
                <ul>
                  <li>M-Pesa</li>
                  <li>Bank Transfer</li>
                  <li>Cash</li>
                  <li>Cheque</li>
                </ul>

                <p><strong>Common Payment Purposes:</strong></p>
                <ul>
                  <li>Tuition Fee</li>
                  <li>Activity Fee</li>
                  <li>Examination Fee</li>
                  <li>Boarding Fee</li>
                  <li>Transport Fee</li>
                </ul>

                <p className="text-muted">
                  Need help? Contact the finance department for assistance.
                </p>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default BulkReceiptUpload;