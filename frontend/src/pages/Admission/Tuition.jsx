import React, { useState } from 'react';
import { Container, Row, Col, Card, Table, Badge, Button, Alert, Form } from 'react-bootstrap';

const Tuition = () => {
  const [selectedCurriculum, setSelectedCurriculum] = useState('cbc');

  const feeStructures = {
    cbc: [
      {
        level: 'Grade 1-3',
        tuition: '85,000',
        development: '15,000',
        activities: '5,000',
        total: '105,000',
        term: 'Per Term'
      },
      {
        level: 'Grade 4-6',
        tuition: '95,000',
        development: '15,000',
        activities: '5,000',
        total: '115,000',
        term: 'Per Term'
      },
      {
        level: 'Grade 7-9 (Junior Secondary)',
        tuition: '120,000',
        development: '20,000',
        activities: '8,000',
        total: '148,000',
        term: 'Per Term'
      }
    ],
    cambridge: [
      {
        level: 'IGCSE Years 1-2',
        tuition: '180,000',
        development: '25,000',
        activities: '12,000',
        total: '217,000',
        term: 'Per Term'
      },
      {
        level: 'AS Level',
        tuition: '200,000',
        development: '25,000',
        activities: '12,000',
        total: '237,000',
        term: 'Per Term'
      },
      {
        level: 'A Level',
        tuition: '210,000',
        development: '25,000',
        activities: '12,000',
        total: '247,000',
        term: 'Per Term'
      }
    ]
  };

  const additionalFees = [
    { item: 'Application Fee', amount: '2,000', frequency: 'One-time' },
    { item: 'Registration Fee', amount: '15,000', frequency: 'One-time' },
    { item: 'School Uniform', amount: '12,000 - 18,000', frequency: 'As needed' },
    { item: 'Textbooks & Materials', amount: '8,000 - 15,000', frequency: 'Per year' },
    { item: 'Boarding Fees', amount: '80,000', frequency: 'Per term' },
    { item: 'Transportation', amount: '25,000 - 40,000', frequency: 'Per term' }
  ];

  const paymentPlans = [
    {
      name: 'Full Payment',
      description: 'Pay entire year in advance',
      discount: '5% discount on tuition',
      benefits: ['Priority placement', 'Reduced paperwork', 'Discount benefit']
    },
    {
      name: 'Termly Payment',
      description: 'Pay at beginning of each term',
      discount: 'Standard rates apply',
      benefits: ['Manageable payments', 'Flexible budgeting', 'No extra charges']
    },
    {
      name: 'Monthly Installments',
      description: 'Spread payments over 10 months',
      discount: 'Administrative fee: 3%',
      benefits: ['Budget friendly', 'Automatic deductions', 'Payment reminders']
    }
  ];

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <div className="text-center mb-5">
            <h1>Tuition & Fees</h1>
            <p className="lead">Transparent fee structure for quality education</p>
          </div>

          <Alert variant="info" className="mb-4">
            <Alert.Heading>Fee Information</Alert.Heading>
            All fees are in Kenyan Shillings. Fees are reviewed annually and may be subject to change. 
            The school offers sibling discounts and scholarship opportunities.
          </Alert>

          {/* Curriculum Selector */}
          <Card className="mb-4">
            <Card.Body className="text-center">
              <h5 className="mb-3">Select Curriculum to View Fees</h5>
              <div className="d-flex justify-content-center gap-3">
                <Button
                  variant={selectedCurriculum === 'cbc' ? 'primary' : 'outline-primary'}
                  onClick={() => setSelectedCurriculum('cbc')}
                >
                  CBC Program
                </Button>
                <Button
                  variant={selectedCurriculum === 'cambridge' ? 'primary' : 'outline-primary'}
                  onClick={() => setSelectedCurriculum('cambridge')}
                >
                  Cambridge Program
                </Button>
              </div>
            </Card.Body>
          </Card>

          {/* Fee Structure */}
          <Card className="mb-4">
            <Card.Header>
              <h4 className="mb-0">
                <i className="bi bi-cash-coin text-success me-2"></i>
                {selectedCurriculum === 'cbc' ? 'CBC Program Fees' : 'Cambridge Program Fees'}
              </h4>
            </Card.Header>
            <Card.Body>
              <Table responsive striped>
                <thead>
                  <tr>
                    <th>Grade Level</th>
                    <th>Tuition Fee</th>
                    <th>Development Fee</th>
                    <th>Activities Fee</th>
                    <th>Total</th>
                    <th>Frequency</th>
                  </tr>
                </thead>
                <tbody>
                  {feeStructures[selectedCurriculum].map((fee, index) => (
                    <tr key={index}>
                      <td><strong>{fee.level}</strong></td>
                      <td>KSh {fee.tuition}</td>
                      <td>KSh {fee.development}</td>
                      <td>KSh {fee.activities}</td>
                      <td>
                        <Badge bg="success" className="fs-6">
                          KSh {fee.total}
                        </Badge>
                      </td>
                      <td>{fee.term}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              
              <Alert variant="warning" className="mt-3">
                <strong>Note:</strong> Fees include all standard academic materials, basic stationery, 
                and access to school facilities. Additional costs may apply for specialized programs, 
                field trips, and optional activities.
              </Alert>
            </Card.Body>
          </Card>

          <Row>
            {/* Additional Fees */}
            <Col lg={6}>
              <Card className="mb-4">
                <Card.Header>
                  <h5 className="mb-0">Additional Fees & Charges</h5>
                </Card.Header>
                <Card.Body>
                  <Table responsive>
                    <thead>
                      <tr>
                        <th>Item</th>
                        <th>Amount (KSh)</th>
                        <th>Frequency</th>
                      </tr>
                    </thead>
                    <tbody>
                      {additionalFees.map((fee, index) => (
                        <tr key={index}>
                          <td>{fee.item}</td>
                          <td>
                            <strong>{fee.amount}</strong>
                          </td>
                          <td>
                            <Badge bg="secondary">{fee.frequency}</Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </Col>

            {/* Payment Plans */}
            <Col lg={6}>
              <Card className="mb-4">
                <Card.Header>
                  <h5 className="mb-0">Payment Plans</h5>
                </Card.Header>
                <Card.Body>
                  {paymentPlans.map((plan, index) => (
                    <Card key={index} className="mb-3">
                      <Card.Body>
                        <h6 className="text-primary">{plan.name}</h6>
                        <p className="text-muted mb-2">{plan.description}</p>
                        <Badge bg="warning" className="mb-2">{plan.discount}</Badge>
                        <ul className="small mb-0">
                          {plan.benefits.map((benefit, idx) => (
                            <li key={idx}>{benefit}</li>
                          ))}
                        </ul>
                      </Card.Body>
                    </Card>
                  ))}
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Discounts and Financial Information */}
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Discounts & Financial Assistance</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <h6>Sibling Discounts</h6>
                  <ul>
                    <li>2nd child: 10% tuition discount</li>
                    <li>3rd child: 15% tuition discount</li>
                    <li>4th+ children: 20% tuition discount</li>
                  </ul>
                </Col>
                <Col md={6}>
                  <h6>Payment Information</h6>
                  <ul>
                    <li>Bank transfers accepted</li>
                    <li>MPesa payments available</li>
                    <li>Credit card payments (3% fee)</li>
                    <li>All payments due first week of term</li>
                  </ul>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Fee Calculator */}
          <Card>
            <Card.Header>
              <h5 className="mb-0">Fee Calculator</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Form>
                    <Form.Group className="mb-3">
                      <Form.Label>Select Curriculum</Form.Label>
                      <Form.Select>
                        <option>CBC - Grade 1-3</option>
                        <option>CBC - Grade 4-6</option>
                        <option>CBC - Junior Secondary</option>
                        <option>Cambridge - IGCSE</option>
                        <option>Cambridge - AS Level</option>
                        <option>Cambridge - A Level</option>
                      </Form.Select>
                    </Form.Group>
                    <Form.Group className="mb-3">
                      <Form.Label>Number of Siblings</Form.Label>
                      <Form.Select>
                        <option>0</option>
                        <option>1</option>
                        <option>2</option>
                        <option>3+</option>
                      </Form.Select>
                    </Form.Group>
                    <Form.Group className="mb-3">
                      <Form.Label>Boarding Required?</Form.Label>
                      <Form.Check type="checkbox" label="Yes, include boarding fees" />
                    </Form.Group>
                  </Form>
                </Col>
                <Col md={6}>
                  <Card className="bg-light">
                    <Card.Body>
                      <h6>Estimated Annual Cost</h6>
                      <div className="text-center my-4">
                        <h2 className="text-primary">KSh 315,000</h2>
                        <small className="text-muted">Per year (3 terms)</small>
                      </div>
                      <Button variant="primary" className="w-100">
                        Get Detailed Quote
                      </Button>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Tuition;