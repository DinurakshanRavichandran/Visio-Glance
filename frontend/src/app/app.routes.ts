import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { RegisterComponent } from './pages/register/register.component';
import { AuthGuard } from './guards/auth.guard';
import { HomepageComponent } from './pages/homepage/homepage.component';
import { SystemComponent } from './pages/system/system.component';
import { AboutusComponent } from './pages/aboutus/aboutus.component';
import { ChatbotComponent } from './components/chatbot/chatbot.component';
import { FooterComponent } from './components/footer/footer.component';
import { FundusAnalyserComponent } from './components/fundus-analyser/fundus-analyser.component';
import { NavbarComponent } from './components/navbar/navbar.component';
import { OctAnalyserComponent } from './components/oct-analyser/oct-analyser.component';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { SymptomsAnalyserComponent } from './components/symptoms-analyser/symptoms-analyser.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent, title: 'Login' },
  { path: 'register', component: RegisterComponent, title: 'Register' },
  { path: 'home', component: HomepageComponent, title: 'Home' },
  { path: 'aboutus', component: AboutusComponent, title: 'AboutUs' },
  {
    path: 'system',
    component: SystemComponent, // Parent component
    children: [
      { path: 'chatbot', component: ChatbotComponent, title: 'Chatbot' },
      { path: 'oct', component: OctAnalyserComponent, title: 'OCT Analyser' },
      { path: 'fundus', component: FundusAnalyserComponent, title: 'Fundus Analyser' },
      { path: 'symptoms', component: SymptomsAnalyserComponent, title: 'Symptoms Analyser' },
      { path: '', redirectTo: 'chatbot', pathMatch: 'full' }, // Default route for /system
    ],
  },
  { path: 'footer', component: FooterComponent, title: 'Footer' },
  { path: 'navbar', component: NavbarComponent, title: 'Navbar' },
  { path: 'sidebar', component: SidebarComponent, title: 'Sidebar' },
  { path: 'fundus', component: FundusAnalyserComponent, title: 'Fundus' },
  { path: '**', redirectTo: 'login' }, // Redirect unknown routes to login
];

export default routes;