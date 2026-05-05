import { LoginPage } from '../pages/login';
import { Navigate } from 'react-router-dom';

interface AuthRoutesProps {
  isAuthenticated: boolean;
}

export const AuthRoutes = ({ isAuthenticated }: AuthRoutesProps) => {
  return !isAuthenticated ? <LoginPage /> : <Navigate to="/home" replace />;
};