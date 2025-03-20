import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OctAnalyserComponent } from './oct-analyser.component';

describe('OctAnalyserComponent', () => {
  let component: OctAnalyserComponent;
  let fixture: ComponentFixture<OctAnalyserComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OctAnalyserComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OctAnalyserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
