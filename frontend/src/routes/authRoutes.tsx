import { Route } from 'react-router-dom';
import {LoginPage} from '../pages/login';
import {RegisterPage} from '../pages/register';
import { AppRoutes } from '../routes/types/loginReg';

export const AuthRoutes = [
  <Route key="login" path={AppRoutes.LOGIN} element={<LoginPage />} />,
  <Route key="register" path={AppRoutes.REGISTER} element={<RegisterPage />} />,
];