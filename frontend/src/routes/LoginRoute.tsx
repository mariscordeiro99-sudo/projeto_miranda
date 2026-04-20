import { Route } from 'react-router-dom';
import { LoginPage } from '../pages/login';
import { Navigate } from 'react-router-dom';

export const AuthRoutes = (isAuthenticated: boolean) => {
  return (
    <>
      <Route 
        path="/login" 
        element={!isAuthenticated ? <LoginPage /> : <Navigate to="/home" />} 
      />
    </>
  );
};