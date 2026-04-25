import { Route } from 'react-router-dom';
import { DashPage } from '../pages/dashboard';
import { Navigate } from 'react-router-dom';

export const DashRoutes = (isAdmin: boolean) => {
  return (
    <>
      <Route 
        path="/dashboard" 
        element={!isAdmin ? <DashPage /> : <Navigate to="/home" />} 
      />
    </>
  );
};