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

    this.imageService.analyzeImage(this.selectedFile).subscribe({
      next: (response) => {
        this.diagnosis = response.predicted_disease;
        this.isLoading = false;
      },
      error: (err) => {
        console.error(err);
        this.diagnosis = 'Error analyzing image. Try again.';
        this.isLoading = false;
      }
    });
  }
}
