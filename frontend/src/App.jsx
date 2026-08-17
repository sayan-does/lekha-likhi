import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AuthGate from './components/AuthGate';
import Dashboard from './components/Dashboard';
import SharedPage from './components/SharedPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <AuthGate>
              <Dashboard />
            </AuthGate>
          }
        />
        <Route path="/shared/:token" element={<SharedPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
