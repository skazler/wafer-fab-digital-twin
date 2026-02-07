import React, { useState, useEffect } from 'react';
import StatusCard from './components/StatusCard';
import YieldChart from './components/YieldChart';

function App() {
  const [latestData, setLatestData] = useState(null);

  useEffect(() => {
    const fetchLatest = async () => {
      try {
        // fetch the very last point from InfluxDB via FastAPI backend
        const response = await fetch('http://localhost:8000/latest'); 
        const data = await response.json();
        setLatestData(data);
      } catch (error) {
        console.error("Link to Greenfield API severed:", error);
      }
    };

    const interval = setInterval(fetchLatest, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App" style={{ padding: '20px', backgroundColor: '#1a1a1a', minHeight: '100vh', color: 'white' }}>
      <h1>Project Greenfield: Real-Time Fab Monitor</h1>
      <hr style={{ borderColor: '#333' }} />
      
      <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
        <StatusCard 
          title="Tool Status" 
          value={latestData?.status || "CONNECTING..."} 
          // todo: add logic here to turn the card red if status is CRITICAL
        />
        <StatusCard title="Current Wafer" value={latestData?.wafer_id || "---"} />
        <StatusCard 
          title="Chamber Temp" 
          value={latestData ? `${latestData.metrics.temperature} °C` : "0 °C"} 
        />
      </div>

      <div style={{ background: '#252525', padding: '20px', borderRadius: '8px' }}>
        <YieldChart />
      </div>
    </div>
  );
}

export default App;