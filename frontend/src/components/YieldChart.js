import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const YieldChart = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch('http://localhost:8000/history');
        const result = await response.json();
        
        // transform the data
        const chartPoints = result.history
          .filter(item => item.metric === 'temperature') // match backend field name
          .map(item => ({
            time: new Date(item.time).toLocaleTimeString(),
            temp: item.value
          }));
          
        setData(chartPoints);
      } catch (error) {
        console.error("Error fetching Greenfield telemetry:", error);
      }
    };

    fetchHistory(); // run immediately on load
    const interval = setInterval(fetchHistory, 5000); 
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ width: '100%', height: 400, backgroundColor: '#252525', padding: '20px', borderRadius: '10px' }}>
      <h3 style={{ color: '#00ff00', marginBottom: '20px' }}>Thermal Trend Analysis (Chamber A)</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis dataKey="time" stroke="#888" />
          <YAxis domain={[175, 195]} stroke="#888" />
          <Tooltip contentStyle={{ backgroundColor: '#333', border: 'none' }} />
          <Line 
            type="monotone" 
            dataKey="temp" 
            stroke="#00ff00" 
            strokeWidth={3} 
            dot={false}
            animationDuration={300}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default YieldChart;