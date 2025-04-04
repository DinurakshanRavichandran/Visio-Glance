import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface OctClassificationResponse {
  classification: {
    prediction: string;
    confidence: number;
  };
  explanations: {
    lime: string;
    shap: string;
  };
}

interface ChatResponse {
  response: string;
}
// Note: The ChatResponse interface is a placeholder. Adjust it according to your actual API response structure.

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:5000';

  constructor(private http: HttpClient) { }

  // OCT-specific methods
  oct_classifyImage(image: File): Observable<OctClassificationResponse> {
    const formData = new FormData();
    formData.append('image', image);
    formData.append('model_type', 'oct');

    return this.http.post<OctClassificationResponse>(
      `${this.apiUrl}/analyze`, 
      formData
    ).pipe(
      catchError(this.oct_handleError)
    );
  }

  sendChatMessage(message: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(
      `${this.apiUrl}/api/ml/chat`,
      { message: message }
    ).pipe(catchError(this.handleError));
  }

  oct_getXaiImage(imageUrl: string): Observable<Blob> {
    return this.http.get(imageUrl, { responseType: 'blob' });
  }

  private oct_handleError(error: HttpErrorResponse) {
    console.error('OCT Analysis Error:', error.message);
    return throwError('OCT analysis failed. Please try again.');
  }

  // General error handler (optional)
  private handleError(error: HttpErrorResponse) {
    console.error('API Error:', error.message);
    return throwError('Something went wrong. Please try again.');
  }

  // Inside your existing ApiService class
// Add these authentication methods:

login(email: string, password: string): Observable<any> {
  return this.http.post<any>(
    `${this.apiUrl}/auth/login`,
    { email, password }
  ).pipe(
    catchError(this.handleAuthError)
  );
}

register(username: string, email: string, password: string): Observable<any> {
  return this.http.post<any>(
    `${this.apiUrl}/auth/register`,
    { username, email, password }
  ).pipe(
    catchError(this.handleAuthError)
  );
}

private handleAuthError(error: HttpErrorResponse) {
  let errorMessage = 'Authentication failed. Please try again.';
  if (error.error?.error) {
    errorMessage = error.error.error; // Use backend error message
  }
  return throwError(errorMessage);
}
}