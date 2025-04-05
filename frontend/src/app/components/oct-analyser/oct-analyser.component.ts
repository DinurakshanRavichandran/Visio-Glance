import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { HttpClientModule } from '@angular/common/http';

interface OctClassificationResponse {
  classification: {
    prediction: string;
    confidence: number;
  };
  explanations: {
    lime: string;
    shap: string;
  };
}

@Component({
  selector: 'app-oct-analyser',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './oct-analyser.component.html',
  styleUrls: ['./oct-analyser.component.css']
})
export class OctAnalyserComponent {
  fileName: string | null = null;
  imagePreview: string | null = null;
  isLoading = false;
  diagnosis: string | null = null;
  confidence: number | null = null;
  errorMessage: string | null = null;
  shapImage: string | null = null;
  limeImage: string | null = null;
  loadingShap = false;
  loadingLime = false;

  constructor(private apiService: ApiService) {}

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) {
      const file = input.files[0];
      this.resetState();
      this.fileName = file.name;
      
      // Preview image
      const reader = new FileReader();
      reader.onload = () => this.imagePreview = reader.result as string;
      reader.readAsDataURL(file);

      this.analyzeImage(file);
    }
  }

  private resetState(): void {
    this.errorMessage = null;
    this.diagnosis = null;
    this.confidence = null;
    this.shapImage = null;
    this.limeImage = null;
    this.loadingShap = false;
    this.loadingLime = false;
  }

  analyzeImage(file: File): void {
    this.isLoading = true;
    
    this.apiService.oct_classifyImage(file).subscribe({
      next: (response: OctClassificationResponse) => {
        this.diagnosis = response.classification.prediction;
        this.confidence = response.classification.confidence;
        this.loadXaiImages(response.explanations.shap, response.explanations.lime);
      },
      error: (err: any) => {
        console.error('Analysis error:', err);
        this.errorMessage = err.error?.message || err.message || 'Failed to analyze image. Please try again.';
        this.isLoading = false;
      }
    });
  }

  private loadXaiImages(shapUrl: string, limeUrl: string): void {
    this.loadingShap = true;
    this.loadingLime = true;

    this.apiService.oct_getXaiImage(shapUrl).subscribe({
      next: (blob: Blob) => {
        this.shapImage = URL.createObjectURL(blob);
      },
      error: (err) => {
        console.error('SHAP image load error:', err);
        this.errorMessage = 'Failed to load SHAP explanation.';
        this.loadingShap = false;
      },
      complete: () => this.loadingShap = false
    });

    this.apiService.oct_getXaiImage(limeUrl).subscribe({
      next: (blob: Blob) => {
        this.limeImage = URL.createObjectURL(blob);
      },
      error: (err) => {
        console.error('LIME image load error:', err);
        this.errorMessage = 'Failed to load LIME explanation.';
        this.loadingLime = false;
      },
      complete: () => {
        this.loadingLime = false;
        this.isLoading = false; // Only set to false when both images are done loading
      }
    });
  }
}