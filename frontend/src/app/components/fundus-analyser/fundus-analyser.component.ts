import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http'; // ✅ Import HttpClientModule
import { ImageAnalysisService } from '../../services/image-analysis.service';

@Component({
  selector: 'app-fundus-analyser',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule], // ✅ Add HttpClientModule
  templateUrl: './fundus-analyser.component.html',
  styleUrls: ['./fundus-analyser.component.css'],
  providers: [ImageAnalysisService] // ✅ Provide service
})
export class FundusAnalyserComponent {
  fileName: string | null = null;
  imagePreview: string | null = null;
  isLoading = false;
  diagnosis: string | null = null;
  processedImage: string | null = null;
  selectedFile: File | null = null;
  limeExplanation: string | null = null;
  gradcamExplanation: string | null = null;

  constructor(private imageService: ImageAnalysisService) {}

  onFileSelected(event: Event): void {
    console.log("hk")
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
      this.fileName = this.selectedFile.name;

      const reader = new FileReader();
      reader.onload = () => {
        this.imagePreview = reader.result as string;
      };
      reader.readAsDataURL(this.selectedFile);
    }
    this.analyzeImage()
  }

  analyzeImage(): void {
    console.log("hk")
    if (!this.selectedFile) {
      alert('Please select an image first.');
      return;
    }

    this.isLoading = true;
    this.diagnosis = null;
    this.processedImage = null;
    this.limeExplanation = null;
    this.gradcamExplanation = null

    this.imageService.analyzeImage(this.selectedFile).subscribe({
      next: (response) => {
        this.diagnosis = response.predicted_disease;
        
        // Then get the explanation images
        this.getExplanationImages(this.selectedFile!);
      },
      error: (err) => {
        console.error(err);
        this.diagnosis = 'Error analyzing image. Try again.';
        this.isLoading = false;
      }
    });
  }

  private getExplanationImages(file: File): void {
    const formData = new FormData();
    formData.append('file', file);
  
    // Get LIME explanation
    this.imageService.getLimeExplanation(formData).subscribe({
      next: (limeResponse) => {
        this.limeExplanation = URL.createObjectURL(limeResponse);
      },
      error: (err) => console.error('LIME error:', err)
    });
  
    // Get Grad-CAM explanation
    this.imageService.getGradcamExplanation(formData).subscribe({
      next: (gradcamResponse) => {
        this.gradcamExplanation = URL.createObjectURL(gradcamResponse);
        this.isLoading = false;
        console.log(gradcamResponse)
      },
      error: (err) => console.error('Grad-CAM error:', err)
    });
  }
}
