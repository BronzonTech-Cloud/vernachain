import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from '../components/layout/MainLayout';
import LoadingSkeleton from '../components/common/LoadingSkeleton';

// Lazy load components
const Dashboard = lazy(() => import('../pages/Dashboard'));
const Network = lazy(() => import('../pages/Network'));
const Validators = lazy(() => import('../pages/Validators'));
const Shards = lazy(() => import('../pages/Shards'));
const Transactions = lazy(() => import('../pages/Transactions'));
const Settings = lazy(() => import('../pages/Settings'));
const NotFound = lazy(() => import('../pages/NotFound'));

// Loading fallback component
const PageLoader = () => (
  <LoadingSkeleton type="detail" />
);

const AppRoutes = () => {
  return (
    <MainLayout>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/network" element={<Network />} />
          <Route path="/validators" element={<Validators />} />
          <Route path="/shards" element={<Shards />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/settings" element={<Settings />} />
          
          {/* Detail Routes */}
          <Route path="/validator/:address" element={<Validators />} />
          <Route path="/transaction/:hash" element={<Transactions />} />
          <Route path="/block/:index" element={<Dashboard />} />
          <Route path="/address/:address" element={<Dashboard />} />
          
          {/* Fallback routes */}
          <Route path="/404" element={<NotFound />} />
          <Route path="*" element={<Navigate to="/404" replace />} />
        </Routes>
      </Suspense>
    </MainLayout>
  );
};

export default AppRoutes; 