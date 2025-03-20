import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { CommonEngine } from '@angular/ssr/node';

@Component({
  selector: 'app-navbar',
  imports: [CommonModule, RouterModule],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent {
  constructor(private router: Router){

  }
  isLoggedIn(): boolean{
    return !!localStorage.getItem('token');
  }

  logout()
  {
    localStorage.removeItem('token');
    this.router.navigate(['/login']);
  }
}
