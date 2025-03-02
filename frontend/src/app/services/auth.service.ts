import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor() { }

  login(username: string, password:string): boolean{
    if(username === 'user' && password === 'password'){
      localStorage.setItem('token', 'dummy');
      return true;
    }
    return false;
  }

  logout(): void{
    localStorage.removeItem('token');
  }

  isLoggedIn(): boolean{
    return !!localStorage.getItem('token');
  }
}
