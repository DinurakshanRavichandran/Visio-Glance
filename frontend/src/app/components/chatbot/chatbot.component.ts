import { Component, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-chatbot',
  standalone: true,
  imports: [
    CommonModule,  // For *ngFor and *ngIf
    FormsModule     // For [(ngModel)]
  ],
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css']
})
export class ChatbotComponent implements AfterViewChecked {
  messages: Array<{ content: string, isUser: boolean }> = [
    { 
      content: 'Hello! I\'m your medical AI assistant. How can I help you today?',
      isUser: false 
    }
  ];
  
  userInput = '';
  isLoading = false;

  @ViewChild('chatWindow') private chatWindow!: ElementRef;  // Changed to match template

  constructor(private apiService: ApiService) { }

  ngAfterViewChecked() {        
    this.scrollToBottom();        
  } 

  private scrollToBottom(): void {
    try {
      this.chatWindow.nativeElement.scrollTop = this.chatWindow.nativeElement.scrollHeight;
    } catch(err) { 
      console.error('Scroll error:', err); 
    }                 
  }

  sendMessage(): void {
    if (!this.userInput.trim()) return;

    const question = this.userInput.trim();
    this.addMessage(question, true);
    this.userInput = '';
    this.isLoading = true;

    this.apiService.sendChatMessage(question).subscribe({
      next: (response) => this.handleResponse(response),
      error: (error) => this.handleError(error),
      complete: () => this.isLoading = false
    });
  }

  private addMessage(content: string, isUser: boolean): void {
    this.messages.push({ content, isUser });
  }

  private handleResponse(response: any): void {
    const content = response?.response || 'Could not understand the response';
    this.addMessage(content, false);
  }

  private handleError(error: any): void {
    console.error('Chat error:', error);
    this.addMessage('Sorry, I\'m having trouble connecting to the server.', false);
  }
}