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
}