import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { ImageAnalysisService } from '../../services/image-analysis.service';

@Component({
  selector: 'app-fundus-analyser',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './fundus-analyser.component.html',
  styleUrls: ['./fundus-analyser.component.css'],
  providers: [ImageAnalysisService]
})
export class FundusAnalyserComponent {
  fileName: string | null = null;
  imagePreview: string | null = null;
  isLoading = false;
  diagnosis: string | null = null;
  errorMessage: string | null = null;
  selectedFile: File | null = null;
  limeExplanation: string | null = null;
  gradcamExplanation: string | null = null;
  loadingLime = false;
  loadingGradcam = false;

  constructor(private imageService: ImageAnalysisService) {}

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.resetState();
      this.selectedFile = input.files[0];
      this.fileName = this.selectedFile.name;

      // Create preview
      const reader = new FileReader();
      reader.onload = () => {
        this.imagePreview = reader.result as string;
      };
      reader.readAsDataURL(this.selectedFile);

      this.analyzeImage();
    }
  }

  private resetState(): void {
    // Clean up previous object URLs to prevent memory leaks
    if (this.limeExplanation) {
      URL.revokeObjectURL(this.limeExplanation);
    }
    if (this.gradcamExplanation) {
      URL.revokeObjectURL(this.gradcamExplanation);
    }

    this.diagnosis = null;
    this.errorMessage = null;
    this.limeExplanation = null;
    this.gradcamExplanation = null;
    this.loadingLime = false;
    this.loadingGradcam = false;
  }

  analyzeImage(): void {
    if (!this.selectedFile) {
      this.errorMessage = 'Please select an image first.';
      return;
    }

    this.isLoading = true;
    this.imageService.analyzeImage(this.selectedFile).subscribe({
      next: (response) => {
        this.diagnosis = response.predicted_disease;
        this.getExplanationImages(this.selectedFile!);
      },
      error: (err) => {
        console.error('Analysis error:', err);
        this.errorMessage = err.error?.message || 'Failed to analyze image. Please try again.';
        this.isLoading = false;
      }
    });
  }

  private getExplanationImages(file: File): void {
    const formData = new FormData();
    formData.append('file', file);
  
    // LIME Explanation
    this.loadingLime = true;
    this.imageService.getLimeExplanation(formData).subscribe({
      next: (limeResponse) => {
        this.limeExplanation = URL.createObjectURL(limeResponse);
      },
      error: (err) => {
        console.error('LIME error:', err);
        this.errorMessage = 'Failed to generate LIME explanation.';
      },
      complete: () => this.loadingLime = false
    });
  
    // Grad-CAM Explanation
    this.loadingGradcam = true;
    this.imageService.getGradcamExplanation(formData).subscribe({
      next: (gradcamResponse) => {
        this.gradcamExplanation = URL.createObjectURL(gradcamResponse);
      },
      error: (err) => {
        console.error('Grad-CAM error:', err);
        this.errorMessage = 'Failed to generate Grad-CAM explanation.';
      },
      complete: () => {
        this.loadingGradcam = false;
        this.isLoading = false; // Only complete when both explanations are done
      }
    });
  }

  ngOnDestroy(): void {
    // Clean up object URLs when component is destroyed
    if (this.limeExplanation) {
      URL.revokeObjectURL(this.limeExplanation);
    }
    if (this.gradcamExplanation) {
      URL.revokeObjectURL(this.gradcamExplanation);
    }
  }
}