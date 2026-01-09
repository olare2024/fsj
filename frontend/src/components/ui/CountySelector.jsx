import React from 'react';
import { Form } from 'react-bootstrap';

const CountySelector = ({ value, onChange, isInvalid, disabled, required }) => {
  const kenyanCounties = [
    { value: 'nairobi', label: 'Nairobi', region: 'Central' },
    { value: 'mombasa', label: 'Mombasa', region: 'Coast' },
    { value: 'kisumu', label: 'Kisumu', region: 'Nyanza' },
    { value: 'nakuru', label: 'Nakuru', region: 'Rift Valley' },
    { value: 'eldoret', label: 'Eldoret', region: 'Rift Valley' },
    { value: 'meru', label: 'Meru', region: 'Eastern' },
    { value: 'kiambu', label: 'Kiambu', region: 'Central' },
    { value: 'kakamega', label: 'Kakamega', region: 'Western' },
    { value: 'kisii', label: 'Kisii', region: 'Nyanza' },
    { value: 'nyeri', label: 'Nyeri', region: 'Central' },
    { value: 'machakos', label: 'Machakos', region: 'Eastern' },
    { value: 'thika', label: 'Thika', region: 'Central' },
    { value: 'malindi', label: 'Malindi', region: 'Coast' },
    { value: 'garissa', label: 'Garissa', region: 'North Eastern' }
  ];

  return (
    <Form.Select
      name="county"
      value={value}
      onChange={onChange}
      isInvalid={isInvalid}
      required={required}
      disabled={disabled}
    >
      <option value="">Select County</option>
      {kenyanCounties.map(county => (
        <option key={county.value} value={county.value}>
          {county.label} ({county.region})
        </option>
      ))}
    </Form.Select>
  );
};

export default CountySelector;