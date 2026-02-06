import React from 'react';

const StatusCard = ({ title, value }) => (
  <div style={{ 
    border: '1px solid #444', 
    padding: '15px', 
    borderRadius: '8px', 
    minWidth: '150px',
    backgroundColor: '#2d2d2d' 
  }}>
    <h3 style={{ fontSize: '12px', color: '#888' }}>{title}</h3>
    <p style={{ fontSize: '20px', fontWeight: 'bold' }}>{value}</p>
  </div>
);

export default StatusCard;
