import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthGate from './components/AuthGate';
import HomePage from './components/HomePage';
import ArchivePage from './components/ArchivePage';
import Dashboard from './components/Dashboard';
import SharedPage from './components/SharedPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AuthGate />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/archive" element={<ArchivePage />} />
          <Route path="/write" element={<Dashboard />} />
        </Route>
        <Route path="/shared/:token" element={<SharedPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
