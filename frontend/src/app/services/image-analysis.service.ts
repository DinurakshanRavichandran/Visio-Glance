import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ImageAnalysisService {
  private backendUrl = environment.backendUrl;

  constructor(private http: HttpClient) {}

  analyzeImage(file: File): Observable<{ predicted_disease: string, processed_image_url: string }> {
    // this.getBackendStatus()
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{ predicted_disease: string, processed_image_url: string }>(this.backendUrl + 'api/image/predict', formData).pipe(
      catchError(this.handleError)
    );
  }

  getLimeExplanation(formData: FormData): Observable<Blob> {
    return this.http.post<{lime_url: string}>(
      this.backendUrl + 'api/image/lime', 
      formData
    ).pipe(
      switchMap(response => {
        // Fetch the actual image from the returned URL
        return this.http.get(this.backendUrl + response.lime_url, { responseType: 'blob' });
      })
    );
  }
  
  getGradcamExplanation(formData: FormData): Observable<Blob> {
    return this.http.post<{gradcam_url: string}>(
      this.backendUrl + 'api/image/gradcam', 
      formData
    ).pipe(
      switchMap(response => {
        // Fetch the actual image from the returned URL
        return this.http.get(this.backendUrl + response.gradcam_url, { responseType: 'blob' });
      })
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
