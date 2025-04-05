import { Component, OnInit, HostListener } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ApiService, SymptomsPredictionResponse } from '../../services/api.service';

@Component({
  selector: 'app-symptoms-analyser',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './symptoms-analyser.component.html',
  styleUrls: ['./symptoms-analyser.component.css']
})
export class SymptomsAnalyserComponent implements OnInit {
  symptomsForm!: FormGroup;
  dropdownVisible = false;
  selectedSymptoms: string[] = [];

  predictionResult: SymptomsPredictionResponse | null = null;
  xaiImageUrl: string | null = null;
  errorMessage: string | null = null;
  warningMessage: string | null = null;

  allSymptoms: string[] = [
    'Tunnel vision', 'Halos around lights', 'Redness in the eye', 'Blurred vision',
    'Frequent changes in vision', 'No visible symptoms', 'Blotches of dark vision',
    'Fluffy white patches in vision', 'Occasional blurred vision', 'Small dark spots in vision',
    'Seeing dark spots', 'Sudden vision loss', 'Distorted vision', 'Lines appear wavy',
    'Mild eye strain', 'Difficulty reading', 'Floaters', 'Color vision changes',
    'Blind spots', 'Light sensitivity', 'Night vision problems'
  ];

  constructor(private fb: FormBuilder, private apiService: ApiService) {}

  ngOnInit(): void {
    this.symptomsForm = this.fb.group({
      age: ['', [Validators.required, Validators.min(1), Validators.max(100)]],
      iop: ['', [Validators.min(10), Validators.max(25)]],
      cdr: ['', [Validators.min(0.3), Validators.max(0.8)]],
      pachymetry: ['', [Validators.min(500.01), Validators.max(599.99)]],
      retinalThickness: ['', [Validators.min(57.181233), Validators.max(500)]],
      visualAcuity: [''],
      lensOpacity: [''],
      glare: [''],
      uv: [''],
      diabetes: [''],
      microaneurysms: ['', [Validators.min(0), Validators.max(12)]],
      hemorrhages: ['', [Validators.min(0), Validators.max(11)]],
      lensStatus: [''],
      oct: [''],
      fluorescein: [''],
      smoking: [''],
      bmi: ['', [Validators.min(9.1), Validators.max(50)]],
      bp: ['', [Validators.min(110), Validators.max(200)]],
      cholesterol: ['', [Validators.min(150), Validators.max(250)]]
    });
  }
  

  toggleSymptomsDropdown(event: MouseEvent): void {
    event.stopPropagation();
    this.dropdownVisible = !this.dropdownVisible;
  }

  onSymptomToggle(symptom: string): void {
    const index = this.selectedSymptoms.indexOf(symptom);
    if (index > -1) {
      this.selectedSymptoms.splice(index, 1);
    } else {
      this.selectedSymptoms.push(symptom);
    }
  }

  onSubmit(): void {
    this.warningMessage = null;

    const ageControl = this.symptomsForm.get('age');
    const isAgeValid = ageControl?.valid;
    const hasSymptoms = this.selectedSymptoms.length > 0;

    // 🔒 Full form validation check
    if (this.symptomsForm.invalid) {
      alert('❌ Please Enter Valid Data within the Given Ranges.');
      this.symptomsForm.markAllAsTouched();
      return;
    }

    if (!isAgeValid || !hasSymptoms) {
      alert('❌ Please fill in the required fields: Age and Visual Symptoms.');
      return;
    }

    const raw = this.symptomsForm.value;
    const ageValue = parseFloat(raw.age);
    const formattedAge = parseFloat(ageValue.toFixed(1));

    const defaultNumericValues: Record<string, number> = {
      iop: 19.0,
      cdr: 0.55,
      pachymetry: 549.335,
      retinalThickness: 248.16244677258328,
      microaneurysms: 2.0,
      hemorrhages: 3.0,
      bmi: 28.132697211774943,
      bp: 144.0,
      cholesterol: 200.0
    };

    const finalData: { [key: string]: any } = {
      Age: formattedAge
    };

    let filledCount = 0;
    for (const field in defaultNumericValues) {
      const val = raw[field];
      const parsed = val !== '' && val !== null && !isNaN(parseFloat(val)) ? parseFloat(val) : defaultNumericValues[field];
      finalData[this.camelToLabel(field)] = parsed;
      if (val !== '' && val !== null) filledCount++;
    }

    const binaryFields: string[] = [
      'visualAcuity', 'lensOpacity', 'glare', 'uv',
      'diabetes', 'lensStatus', 'oct', 'fluorescein', 'smoking'
    ];

    for (const field of binaryFields) {
      const isSelected = !!raw[field];
      const label = this.getOneHotFieldLabel(field, raw[field]);
      finalData[label] = isSelected ? 1.0 : 0.0;
      if (isSelected) filledCount++;
    }

    for (const symptom of this.allSymptoms) {
      const key = `Visual Symptoms_${symptom.toLowerCase()}`;
      finalData[key] = this.selectedSymptoms.includes(symptom) ? 1.0 : 0.0;
    }

    if (filledCount === 0) {
      const warningText = '⚠️ Warning! Prediction may be less accurate due to limited input.';
      alert(warningText);
      this.warningMessage = warningText;
    }

    console.log('📤 Final input data:', finalData);

    this.apiService.submitSymptoms(finalData).subscribe({
      next: (response) => {
        this.predictionResult = response;
        this.errorMessage = null;

        if (response?.diagnosis === 'Warning') {
          this.warningMessage = response.message || '⚠️ Prediction may be less accurate.';
        }

        this.xaiImageUrl = response?.xai_image
          ? `${this.apiService['apiUrl']}/static/xai/${response.xai_image}`
          : null;

        console.log('✅ Prediction Result:', response);
      },

      error: (error) => {
        this.predictionResult = null;
        this.xaiImageUrl = null;
        this.errorMessage = error;
        console.error('❌ Prediction error:', error);
      }
    });
    
  }

    // 🔁 Reset method
    onReset(): void {
      this.symptomsForm.reset();
      this.selectedSymptoms = [];
      this.predictionResult = null;
      this.xaiImageUrl = null;
      this.errorMessage = null;
      this.warningMessage = null;
    }

  camelToLabel(field: string): string {
    switch (field) {
      case 'iop': return 'Intraocular Pressure (IOP)';
      case 'cdr': return 'Cup-to-Disc Ratio (CDR)';
      case 'pachymetry': return 'Pachymetry';
      case 'retinalThickness': return 'Retinal Thickness';
      case 'microaneurysms': return 'Microaneurysms Count';
      case 'hemorrhages': return 'Hemorrhages Count';
      case 'bmi': return 'BMI';
      case 'bp': return 'Blood Pressure';
      case 'cholesterol': return 'Cholesterol Levels';
      default: return field;
    }
  }

  getOneHotFieldLabel(field: string, value: string): string {
    if (!value) return `${this.fieldMap[field] || field}_none`;

    const cleanValue = value.toString().trim().replace(/_/g, ' ').replace(/ +/g, ' ');

    switch (field) {
      case 'visualAcuity': return `Visual Acuity Test Results_${cleanValue}`;
      case 'lensOpacity': return `Lens Opacity_${cleanValue}`;
      case 'glare': return `Glare Sensitivity_${cleanValue}`;
      case 'uv': return `UV Exposure_${cleanValue}`;
      case 'diabetes': return 'History of Diabetes';
      case 'smoking': return 'Smoking Status';
      case 'lensStatus': return `Lens Status_${this.capitalize(cleanValue)}`;
      case 'oct': return `Optical Coherence Tomography (OCT) Results_${this.capitalize(cleanValue)}`;
      case 'fluorescein': return `Fluorescein Angiography Results_${this.capitalize(cleanValue)}`;
      default: return field;
    }
  }

  capitalize(text: string): string {
    return text
      .toLowerCase()
      .split(' ')
      .map(word => word[0].toUpperCase() + word.slice(1))
      .join(' ');
  }

  fieldMap: Record<string, string> = {
    diabetes: 'History of Diabetes',
    smoking: 'Smoking Status'
  };

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (!target.closest('.symptoms-multi-select')) {
      this.dropdownVisible = false;
    }
  }
}
