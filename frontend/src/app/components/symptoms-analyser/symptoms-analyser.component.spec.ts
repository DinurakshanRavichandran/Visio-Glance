import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SymptomsAnalyserComponent } from './symptoms-analyser.component';

describe('SymptomsAnalyserComponent', () => {
  let component: SymptomsAnalyserComponent;
  let fixture: ComponentFixture<SymptomsAnalyserComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SymptomsAnalyserComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SymptomsAnalyserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
