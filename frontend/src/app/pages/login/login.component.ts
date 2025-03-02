import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule], 
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  loginForm: FormGroup;
  errorMessage: string = '';

  constructor(private fb: FormBuilder, private router: Router) {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]], // Added min length validation
      password: ['', [Validators.required, Validators.minLength(6)]] // Password must have min 6 chars
    });
  }

  onSubmit() {
    if (this.loginForm.valid) {
      console.log('Login Data:', this.loginForm.value);
      // Future authentication logic here
      this.router.navigate(['/dashboard']); // Example: Navigate to dashboard after login
    } else {
      this.errorMessage = 'Please fill in all fields correctly.';
    }
  }
}
