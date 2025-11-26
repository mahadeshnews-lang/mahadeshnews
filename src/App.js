import React, { useState, useEffect } from 'react';

function App() {
  const [status, setStatus] = useState('Loading...');

  useEffect(() => {
    // Backend API Check
    fetch('/api/')
      .then(res => res.json())
      .then(data => setStatus(data.message))
      .catch(err => setStatus('Backend connecting...'));
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-red-700 text-white p-4 shadow-md">
        <div className="container mx-auto">
          <h1 className="text-2xl font-bold">Mahadesh News | महादेश न्यूज़</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto p-4 mt-4">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">System Status</h2>
          <p className="text-gray-700">Backend Status: <span className="font-bold text-blue-600">{status}</span></p>
          <p className="mt-4 text-sm text-gray-500">
            Website is currently under construction. News feed coming soon.
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;
