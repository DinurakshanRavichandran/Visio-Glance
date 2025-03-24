import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-fundus-analyser',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './fundus-analyser.component.html',
  styleUrls: ['./fundus-analyser.component.css']
})

export class FundusAnalyserComponent {
  fileName: string | null = null;
  imagePreview: string | null = null;
  isLoading = false;
  diagnosis: string | null = null;
  processedImage: string | null = null;

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      this.fileName = file.name;

      const reader = new FileReader();
      reader.onload = () => {
        this.imagePreview = reader.result as string;
      };
      reader.readAsDataURL(file);

      this.analyzeImage(file);
    }
  }

  analyzeImage(file: File): void {
    this.isLoading = true;
    this.diagnosis = null;
    this.processedImage = null;

    // Simulate an AI analysis process
    setTimeout(() => {
      this.isLoading = false;
      this.diagnosis = this.generateMockDiagnosis();
      this.processedImage = this.imagePreview; // Placeholder for processed image
    }, 2000);
  }

  private generateMockDiagnosis(): string {
    const conditions = [
      'No signs of diabetic retinopathy detected.',
      'Mild signs of diabetic retinopathy detected.',
      'Moderate signs of diabetic retinopathy detected.',
      'Severe signs of diabetic retinopathy detected.'
    ];
    return conditions[Math.floor(Math.random() * conditions.length)];
  }
}