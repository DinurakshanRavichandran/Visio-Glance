import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FundusAnalyserComponent } from './fundus-analyser.component';

describe('FundusAnalyserComponent', () => {
  let component: FundusAnalyserComponent;
  let fixture: ComponentFixture<FundusAnalyserComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FundusAnalyserComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FundusAnalyserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
