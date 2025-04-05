import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TeamMemberComponent } from '../team-member/team-member.component';

@Component({
  selector: 'app-team',
  standalone: true,
  imports: [CommonModule, TeamMemberComponent],
  templateUrl: './team.component.html',
  styleUrls: ['./team.component.css']
})

// TODO: implement logic for get images for users
export class TeamComponent {
  teamMembers = [  // Ensure the property name matches the one used in HTML
    { name: 'Sakuna Sankalpa', role: 'Data Scientist', image: '../../../assets/team/sakuna.jpg' },
    { name: 'Dinurakshan Ravichandran', role: 'AI Researcher', image: '../../../assets/team/dinurakshan.jpg' },
    { name: 'Surakkitha Galappathy', role: 'Data Scientist', image: '../../../assets/team/Surakkitha.jpg' },
    { name: 'Yehan Manodya', role: 'Data Scientist', image: '../../../assets/team/yehan.jpg' }
  ];
}
