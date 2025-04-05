import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-team-member',
  standalone: true,
  templateUrl: './team-member.component.html',
  styleUrls: ['./team-member.component.css']
})
export class TeamMemberComponent {
  @Input() name!: string;
  @Input() role!: string;
  @Input() image!: string;
}
