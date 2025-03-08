import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  registerForm: FormGroup;
  submitted = false;

  constructor(private fb: FormBuilder, private router: Router) {
    this.registerForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]]
    });

    // Apply custom password match validator
    this.registerForm.get('confirmPassword')?.setValidators([
      Validators.required,
      this.passwordMatchValidator.bind(this)
    ]);
  }

  // Custom validator to check if passwords match
  passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const password = this.registerForm?.get('password')?.value;
    const confirmPassword = control.value;
    return password === confirmPassword ? null : { mismatch: true };
  }

  onRegister() {
    this.submitted = true;

    if (this.registerForm.invalid) {
      return; // Stop execution if form is invalid
    }

    console.log('Registration Successful:', this.registerForm.value);
    alert('Registration Successful!');

    // Simulating a small delay before navigating (UX improvement)
    setTimeout(() => {
      this.router.navigate(['/login']);
    }, 1000);
  }

  // Helper function to get form controls
  get form() {
    return this.registerForm.controls;
  }
}
