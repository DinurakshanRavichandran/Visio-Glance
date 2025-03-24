import { Component } from '@angular/core';
import { AboutHeaderComponent } from '../../components/about-header/about-header.component';
import { ImpactComponent } from '../../components/impact/impact.component';
import { VisionComponent } from '../../components/vision/vision.component';
import { TeamComponent } from '../../components/team/team.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [AboutHeaderComponent, ImpactComponent, VisionComponent, TeamComponent],
  template: `
    <app-about-header></app-about-header>
    <app-impact></app-impact>
    <app-vision></app-vision>
    <app-team></app-team>
  `,
  styleUrls: ['./aboutus.component.css']
})
export class AboutusComponent { }
