import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { RegisterComponent } from './pages/register/register.component';

import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent, title: 'Login' },
  { path: 'register', component: RegisterComponent, title: 'Register' },
  
  { path: '**', redirectTo: 'login' } // Redirect unknown routes to login
];
export default routes;