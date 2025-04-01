import { Component, OnInit, HostListener } from '@angular/core'
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms'
import { CommonModule } from '@angular/common'

@Component({
  selector: 'app-symptoms-analyser',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './symptoms-analyser.component.html',
  styleUrls: ['./symptoms-analyser.component.css']
})

export class SymptomsAnalyserComponent implements OnInit {
  symptomsForm!: FormGroup
  dropdownVisible = false
  selectedSymptoms: string[] = []

  allSymptoms: string[] = [
    'Tunnel vision', 'Halos around lights', 'Redness in the eye', 'Blurred vision',
    'Frequent changes in vision', 'No visible symptoms', 'Blotches of dark vision',
    'Fluffy white patches in vision', 'Occasional blurred vision', 'Small dark spots in vision',
    'Seeing dark spots', 'Sudden vision loss', 'Distorted vision', 'Lines appear wavy',
    'Mild eye strain', 'Difficulty reading', 'Floaters', 'Color vision changes',
    'Blind spots', 'Light sensitivity', 'Night vision problems'
  ]

  constructor(private fb: FormBuilder) {}

  ngOnInit(): void {
    this.symptomsForm = this.fb.group({
      age: ['', Validators.required],
      iop: [''],
      cdr: [''],
      pachymetry: [''],
      retinalThickness: [''],
      visualAcuity: [''],
      lensOpacity: [''],
      glare: [''],
      uv: [''],
      diabetes: [''],
      microaneurysms: [''],
      hemorrhages: [''],
      lensStatus: [''],
      oct: [''],
      fluorescein: [''],
      smoking: [''],
      bmi: [''],
      bp: [''],
      cholesterol: ['']
    })
  }

  toggleSymptomsDropdown(event: MouseEvent): void {
    event.stopPropagation()
    this.dropdownVisible = !this.dropdownVisible
  }  

  onSymptomToggle(symptom: string): void {
    const index = this.selectedSymptoms.indexOf(symptom)
    if (index > -1) {
      this.selectedSymptoms.splice(index, 1)
    } else {
      this.selectedSymptoms.push(symptom)
    }
  }

  onSubmit(): void {
    const ageControl = this.symptomsForm.get('age')
    const isAgeValid = ageControl?.valid
    const hasSymptoms = this.selectedSymptoms.length > 0

    if (!isAgeValid || !hasSymptoms) {
      alert('❌ Please fill in the required fields: Age and Visual Symptoms.')
      return
    }

    const finalData = {
      ...this.symptomsForm.value,
      visualSymptoms: this.selectedSymptoms
    }

    console.log('✅ Form submitted:', finalData)
    alert('Form submitted successfully!')

    this.symptomsForm.reset()
    this.selectedSymptoms = []
  }

  @HostListener('document:click', ['$event'])
onDocumentClick(event: MouseEvent): void {
  const target = event.target as HTMLElement
  if (!target.closest('.symptoms-multi-select')) {
    this.dropdownVisible = false
  }
}

}
