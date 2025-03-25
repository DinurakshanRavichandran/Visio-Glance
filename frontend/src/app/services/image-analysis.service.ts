import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ImageAnalysisService {
  private backendUrl = 'https://studious-space-parakeet-7vrw4jqw9gxqhprqg-5000.app.github.dev/'; // Replace with your actual backend URL

  constructor(private http: HttpClient) {}

  analyzeImage(file: File): Observable<{ predicted_disease: string, processed_image_url: string }> {
    // this.getBackendStatus()
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{ predicted_disease: string, processed_image_url: string }>(this.backendUrl + 'api/image/predict', formData).pipe(
      catchError(this.handleError)
    );
  }

  // testing
  getBackendStatus(): void {
    this.http.get(this.backendUrl, { 
      responseType: 'text',
      withCredentials: true  
    }).subscribe({
      next: (response) => {
        console.log('Backend Response:', response);
      },
      error: (error) => {
        console.error('Error fetching backend status:', error);
      }
    });
    console.log("done")
  }

  private handleError(error: HttpErrorResponse) {
    console.error('Error occurred:', error);
    return throwError(() => new Error('Image analysis failed. Please try again.'));
  }
}
