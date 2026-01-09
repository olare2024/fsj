import React from 'react';
import { Card, Badge } from 'react-bootstrap';

const CurriculumInfo = ({ curriculum }) => {
  const curriculumData = {
    cbc: {
      name: 'CBC (Competency Based Curriculum)',
      description: 'Kenya\'s new education system focusing on competencies and skills development',
      levels: ['Pre-Primary (PP1-PP2)', 'Lower Primary (Grade 1-3)', 'Upper Primary (Grade 4-6)', 'Junior Secondary (Grade 7-9)', 'Senior Secondary (Grade 10-12)'],
      features: ['Competency-based', 'Flexible learning paths', 'Focus on skills', 'Digital literacy']
    },
    igcse: {
      name: 'IGCSE (Cambridge)',
      description: 'International General Certificate of Secondary Education - globally recognized qualification',
      levels: ['Lower Secondary (Year 7-9)', 'IGCSE (Year 10-11)', 'A-Levels (Year 12-13)'],
      features: ['International recognition', 'Broad curriculum', 'University preparation', 'Global perspective']
    },
    ib: {
      name: 'International Baccalaureate (IB)',
      description: 'Comprehensive international education program promoting intercultural understanding',
      levels: ['Primary Years Programme (PYP)', 'Middle Years Programme (MYP)', 'Diploma Programme (DP)'],
      features: ['International mindedness', 'Holistic education', 'Critical thinking', 'Research skills']
    },
    american: {
      name: 'American Curriculum',
      description: 'US-based education system with standardized testing and college preparation',
      levels: ['Elementary School', 'Middle School', 'High School'],
      features: ['Standardized testing', 'College prep', 'Elective courses', 'AP classes']
    }
  };

  if (!curriculum || !curriculumData[curriculum]) {
    return null;
  }

  const data = curriculumData[curriculum];

  return (
    <Card className="mt-2 border-info">
      <Card.Header className="bg-info text-white py-2">
        <strong>{data.name}</strong>
      </Card.Header>
      <Card.Body className="p-3">
        <p className="mb-2">{data.description}</p>
        
        <div className="mb-2">
          <strong>Education Levels:</strong>
          <ul className="mb-1">
            {data.levels.map((level, index) => (
              <li key={index} style={{ fontSize: '0.9rem' }}>{level}</li>
            ))}
          </ul>
        </div>

        <div>
          <strong>Key Features:</strong>
          <div className="mt-1">
            {data.features.map((feature, index) => (
              <Badge key={index} bg="outline-info" text="dark" className="me-1 mb-1">
                {feature}
              </Badge>
            ))}
          </div>
        </div>
      </Card.Body>
    </Card>
  );
};

export default CurriculumInfo;