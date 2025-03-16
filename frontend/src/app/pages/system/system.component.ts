import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { NavbarComponent } from "../../components/navbar/navbar.component";
import { ChatbotComponent } from '../../components/chatbot/chatbot.component';
import { OctAnalyserComponent } from '../../components/oct-analyser/oct-analyser.component';
import { FundusAnalyserComponent } from '../../components/fundus-analyser/fundus-analyser.component';
import { MatSidenavModule } from '@angular/material/sidenav';
import { RouterModule } from '@angular/router';
import { SidebarComponent } from '../../components/sidebar/sidebar.component';
import { FooterComponent } from '../../components/footer/footer.component';

@Component({
  selector: 'app-system',
  imports: [NavbarComponent, CommonModule, MatSidenavModule, RouterModule, SidebarComponent, FooterComponent],
  templateUrl: './system.component.html',
  styleUrl: './system.component.css'
})
export class SystemComponent {

}
