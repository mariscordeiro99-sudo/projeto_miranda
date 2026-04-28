import { Route, Navigate } from 'react-router-dom';
import { DashboardPage } from '../pages/dashboard';

interface DashRoutesProps {
  isAdmin: boolean;
}

export const DashRoutes = ({ isAdmin }: DashRoutesProps) => {
  return (
    <Route 
      path="/dashboard" 
      element={
        isAdmin ? (
          <DashboardPage />
        ) : (
          <Navigate to="/home" replace />
        )
      } 
    />
  );
};