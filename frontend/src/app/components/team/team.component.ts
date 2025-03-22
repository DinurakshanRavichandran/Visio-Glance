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
    { name: 'Dr. Sarah Johnson', role: 'Ophthalmologist', image: 'assets/team/team.png' },
    { name: 'Mark Lee', role: 'AI Researcher', image: 'assets/team/team.png' },
    { name: 'Emily Carter', role: 'Data Scientist', image: 'assets/team/team.png' },
    { name: 'Dr. John Smith', role: 'Medical Advisor', image: 'assets/team/team.png' }
  ];
}
