import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ZaloBotService, ZaloConfig, BotStatus, Message, SentMessage } from '../../services/zalo-bot.service';

@Component({
  selector: 'app-zalo-bot',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="min-h-screen bg-gray-50 p-6">
      <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-xl font-semibold text-gray-800">
              <i class="fas fa-robot mr-2 text-blue-600"></i>
              Zalo Bot Manager
            </h3>
          </div>
          <div class="p-6">
            <div class="flex justify-between items-center mb-4">
              <div class="flex gap-2">
                <button class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed" 
                        (click)="startAllBots()"
                        [disabled]="loading">
                  <i class="fas fa-play mr-1"></i> Start All Bots
                </button>
                <button class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed" 
                        (click)="stopAllBots()"
                        [disabled]="loading">
                  <i class="fas fa-stop mr-1"></i> Stop All Bots
                </button>
                <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors" 
                        (click)="refreshConfigs()">
                  <i class="fas fa-refresh mr-1"></i> Refresh
                </button>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-xs text-gray-500" *ngIf="autoRefreshEnabled">
                  <i class="fas fa-sync-alt fa-spin mr-1"></i> Auto-refresh
                </span>
                <button class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-xs font-medium transition-colors" 
                        (click)="toggleAutoRefresh()">
                  <i class="fas mr-1" [ngClass]="autoRefreshEnabled ? 'fa-pause' : 'fa-play'"></i>
                  {{ autoRefreshEnabled ? 'Pause' : 'Start' }} Auto-refresh
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Configs List -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div class="px-6 py-4 border-b border-gray-200">
            <h5 class="text-lg font-semibold text-gray-800">
              Bot Configs ({{ configs.length }})
            </h5>
          </div>
          <div class="p-6">
            <div *ngIf="loading && configs.length === 0" class="text-center py-8">
              <i class="fas fa-spinner fa-spin text-2xl text-gray-400"></i>
              <p class="mt-2 text-gray-500">Loading...</p>
            </div>
            
            <div *ngIf="!loading && configs.length === 0" class="text-center py-8">
              <i class="fas fa-inbox text-3xl text-gray-300"></i>
              <p class="mt-2 text-gray-500">No configs found</p>
            </div>

            <div class="grid gap-4" *ngIf="configs.length > 0">
              <div *ngFor="let config of configs" 
                   class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-3">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                      <h6 class="text-lg font-semibold text-gray-800">{{ config.name }}</h6>
                      <span *ngIf="config.is_default" 
                            class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        Default
                      </span>
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                            [ngClass]="getStatusClass(config.status)">
                        {{ config.status }}
                      </span>
                    </div>
                    <p class="text-sm text-gray-500">ID: {{ config.id }} | IMEI: {{ config.imei }}</p>
                    <p class="text-xs text-gray-400 mt-1" *ngIf="config.created_at">
                      Created: {{ config.created_at | date:'medium' }}
                    </p>
                  </div>
                  <div class="flex gap-2">
                    <button class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed" 
                            (click)="viewBotDetails(config)"
                            [disabled]="loading">
                      <i class="fas fa-info-circle mr-1"></i> Details
                    </button>
                    <button *ngIf="!config.running" 
                            class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed" 
                            (click)="startBot(config.id)"
                            [disabled]="loading">
                      <i class="fas fa-play mr-1"></i> Start
                    </button>
                    <button *ngIf="config.running" 
                            class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed" 
                            (click)="stopBot(config.id)"
                            [disabled]="loading">
                      <i class="fas fa-stop mr-1"></i> Stop
                    </button>
                    <button class="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed" 
                            (click)="cleanupBot(config.id)"
                            [disabled]="loading">
                      <i class="fas fa-broom mr-1"></i> Cleanup
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Bot Details Modal -->
        <div *ngIf="selectedConfig" 
             class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
             (click)="closeDetails()">
          <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
               (click)="$event.stopPropagation()">
            <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h4 class="text-xl font-semibold text-gray-800">
                Bot Details: {{ selectedConfig.name }}
              </h4>
              <button class="text-gray-400 hover:text-gray-600" (click)="closeDetails()">
                <i class="fas fa-times text-xl"></i>
              </button>
            </div>
            
            <div class="p-6">
              <!-- Status Info -->
              <div class="mb-6 bg-gray-50 rounded-lg p-4">
                <h6 class="font-semibold text-gray-800 mb-3">Status Information</h6>
                <div class="grid md:grid-cols-2 gap-4">
                  <div>
                    <p class="text-sm"><span class="font-medium">Running:</span> 
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                            [ngClass]="botStatus?.running ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                        {{ botStatus?.running ? 'Yes' : 'No' }}
                      </span>
                    </p>
                    <p class="text-sm mt-2"><span class="font-medium">Status:</span> 
                      <span class="ml-2" [ngClass]="getStatusClass(botStatus?.status || '')">
                        {{ botStatus?.status || 'N/A' }}
                      </span>
                    </p>
                  </div>
                  <div>
                    <p class="text-sm"><span class="font-medium">Start Time:</span> {{ botStatus?.stats?.start_time || 'N/A' }}</p>
                    <p class="text-sm mt-2"><span class="font-medium">Last Message:</span> {{ botStatus?.stats?.last_message_time || 'N/A' }}</p>
                  </div>
                </div>
                <div class="mt-4 grid md:grid-cols-2 gap-4">
                  <div>
                    <p class="text-sm"><span class="font-medium">Messages Received:</span> {{ botStatus?.stats?.messages_received || 0 }}</p>
                  </div>
                  <div>
                    <p class="text-sm"><span class="font-medium">Messages Sent:</span> {{ botStatus?.stats?.messages_sent || 0 }}</p>
                  </div>
                </div>
              </div>

              <!-- Send Message -->
              <div class="mb-6 border border-gray-200 rounded-lg p-4">
                <h6 class="font-semibold text-gray-800 mb-3">Send Message</h6>
                <div class="space-y-3">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Recipient ID</label>
                    <input type="text" 
                           [(ngModel)]="sendMessageData.recipientId"
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                           placeholder="Enter recipient ID">
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Thread Type</label>
                    <select [(ngModel)]="sendMessageData.threadType"
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                      <option value="USER">USER</option>
                      <option value="GROUP">GROUP</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Message Content</label>
                    <textarea [(ngModel)]="sendMessageData.content"
                              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                              rows="3"
                              placeholder="Enter message content"></textarea>
                  </div>
                  <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          (click)="sendMessage()"
                          [disabled]="loading || !sendMessageData.recipientId || !sendMessageData.content">
                    <i class="fas fa-paper-plane mr-1"></i> Send Message
                  </button>
                </div>
              </div>

              <!-- Recent Messages -->
              <div class="mb-6 border border-gray-200 rounded-lg p-4">
                <div class="flex justify-between items-center mb-3">
                  <h6 class="font-semibold text-gray-800">Recent Messages</h6>
                  <button class="text-sm text-blue-600 hover:text-blue-700" (click)="loadBotMessages()">
                    <i class="fas fa-refresh mr-1"></i> Refresh
                  </button>
                </div>
                <div *ngIf="recentMessages.length === 0" class="text-center py-4 text-gray-500">
                  No recent messages
                </div>
                <div *ngIf="recentMessages.length > 0" class="space-y-2 max-h-60 overflow-y-auto">
                  <div *ngFor="let msg of recentMessages" 
                       class="bg-gray-50 rounded p-2 text-sm">
                    <div class="flex justify-between">
                      <span class="font-medium">{{ msg.sender }}</span>
                      <span class="text-gray-500">{{ msg.time }}</span>
                    </div>
                    <p class="mt-1 text-gray-700">{{ msg.content }}</p>
                  </div>
                </div>
              </div>

              <!-- Sent Messages -->
              <div class="border border-gray-200 rounded-lg p-4">
                <div class="flex justify-between items-center mb-3">
                  <h6 class="font-semibold text-gray-800">Sent Messages</h6>
                  <button class="text-sm text-blue-600 hover:text-blue-700" (click)="loadSentMessages()">
                    <i class="fas fa-refresh mr-1"></i> Refresh
                  </button>
                </div>
                <div *ngIf="sentMessages.length === 0" class="text-center py-4 text-gray-500">
                  No sent messages
                </div>
                <div *ngIf="sentMessages.length > 0" class="space-y-2 max-h-60 overflow-y-auto">
                  <div *ngFor="let msg of sentMessages" 
                       class="bg-blue-50 rounded p-2 text-sm">
                    <div class="flex justify-between">
                      <span class="font-medium">To: {{ msg.recipient_name }} ({{ msg.recipient_id }})</span>
                      <span class="text-gray-500">{{ msg.sent_at | date:'short' }}</span>
                    </div>
                    <p class="mt-1 text-gray-700">{{ msg.content }}</p>
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium mt-1"
                          [ngClass]="msg.status === 'sent' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'">
                      {{ msg.status }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class ZaloBotComponent implements OnInit, OnDestroy {
  configs: ZaloConfig[] = [];
  selectedConfig: ZaloConfig | null = null;
  botStatus: BotStatus | null = null;
  recentMessages: Message[] = [];
  sentMessages: SentMessage[] = [];
  loading = false;
  autoRefreshEnabled = false;
  autoRefreshInterval: any;

  sendMessageData = {
    recipientId: '',
    content: '',
    threadType: 'USER' as 'USER' | 'GROUP'
  };

  constructor(private zaloBotService: ZaloBotService) {}

  ngOnInit() {
    this.loadConfigs();
  }

  ngOnDestroy() {
    if (this.autoRefreshInterval) {
      clearInterval(this.autoRefreshInterval);
    }
  }

  loadConfigs() {
    this.loading = true;
    this.zaloBotService.getConfigs().subscribe({
      next: (response) => {
        if (response.success && response.configs) {
          this.configs = response.configs;
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading configs:', error);
        this.loading = false;
      }
    });
  }

  refreshConfigs() {
    this.loadConfigs();
    if (this.selectedConfig) {
      this.loadBotStatus();
      this.loadBotMessages();
      this.loadSentMessages();
    }
  }

  toggleAutoRefresh() {
    this.autoRefreshEnabled = !this.autoRefreshEnabled;
    if (this.autoRefreshEnabled) {
      this.autoRefreshInterval = setInterval(() => {
        this.refreshConfigs();
      }, 5000); // Refresh every 5 seconds
    } else {
      if (this.autoRefreshInterval) {
        clearInterval(this.autoRefreshInterval);
      }
    }
  }

  startBot(configId: number) {
    this.loading = true;
    this.zaloBotService.startBot(configId).subscribe({
      next: (response) => {
        if (response.success) {
          this.loadConfigs();
          if (this.selectedConfig?.id === configId) {
            this.loadBotStatus();
          }
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Error starting bot:', error);
        this.loading = false;
      }
    });
  }

  stopBot(configId: number) {
    this.loading = true;
    this.zaloBotService.stopBot(configId).subscribe({
      next: (response) => {
        if (response.success) {
          this.loadConfigs();
          if (this.selectedConfig?.id === configId) {
            this.loadBotStatus();
          }
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Error stopping bot:', error);
        this.loading = false;
      }
    });
  }

  cleanupBot(configId: number) {
    if (!confirm('Are you sure you want to cleanup this bot? This will stop and remove the bot instance.')) {
      return;
    }
    this.loading = true;
    this.zaloBotService.cleanupBot(configId).subscribe({
      next: (response) => {
        if (response.success) {
          this.loadConfigs();
          if (this.selectedConfig?.id === configId) {
            this.closeDetails();
          }
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cleaning up bot:', error);
        this.loading = false;
      }
    });
  }

  startAllBots() {
    if (!confirm('Are you sure you want to start all bots?')) {
      return;
    }
    this.loading = true;
    this.zaloBotService.startAllBots().subscribe({
      next: (response) => {
        if (response.success) {
          this.loadConfigs();
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Error starting all bots:', error);
        this.loading = false;
      }
    });
  }

  stopAllBots() {
    if (!confirm('Are you sure you want to stop all bots?')) {
      return;
    }
    this.loading = true;
    this.zaloBotService.stopAllBots().subscribe({
      next: (response) => {
        if (response.success) {
          this.loadConfigs();
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Error stopping all bots:', error);
        this.loading = false;
      }
    });
  }

  viewBotDetails(config: ZaloConfig) {
    this.selectedConfig = config;
    this.loadBotStatus();
    this.loadBotMessages();
    this.loadSentMessages();
    this.sendMessageData = {
      recipientId: '',
      content: '',
      threadType: 'USER'
    };
  }

  closeDetails() {
    this.selectedConfig = null;
    this.botStatus = null;
    this.recentMessages = [];
    this.sentMessages = [];
  }

  loadBotStatus() {
    if (!this.selectedConfig) return;
    this.zaloBotService.getBotStatus(this.selectedConfig.id).subscribe({
      next: (response) => {
        if (response.success && response.data) {
          this.botStatus = response.data;
        }
      },
      error: (error) => {
        console.error('Error loading bot status:', error);
      }
    });
  }

  loadBotMessages() {
    if (!this.selectedConfig) return;
    this.zaloBotService.getBotMessages(this.selectedConfig.id).subscribe({
      next: (response) => {
        if (response.success && response.messages) {
          this.recentMessages = response.messages;
        }
      },
      error: (error) => {
        console.error('Error loading bot messages:', error);
      }
    });
  }

  loadSentMessages() {
    if (!this.selectedConfig) return;
    this.zaloBotService.getSentMessages(this.selectedConfig.id).subscribe({
      next: (response) => {
        if (response.success && response.messages) {
          this.sentMessages = response.messages;
        }
      },
      error: (error) => {
        console.error('Error loading sent messages:', error);
      }
    });
  }

  sendMessage() {
    if (!this.selectedConfig || !this.sendMessageData.recipientId || !this.sendMessageData.content) {
      return;
    }
    this.loading = true;
    this.zaloBotService.sendMessage(
      this.selectedConfig.id,
      this.sendMessageData.recipientId,
      this.sendMessageData.content,
      this.sendMessageData.threadType
    ).subscribe({
      next: (response) => {
        if (response.success) {
          alert('Message sent successfully!');
          this.sendMessageData = {
            recipientId: '',
            content: '',
            threadType: 'USER'
          };
          this.loadSentMessages();
          this.loadBotStatus();
        } else {
          alert('Error: ' + (response.message || 'Failed to send message'));
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Error sending message:', error);
        alert('Error sending message: ' + (error.error?.message || error.message));
        this.loading = false;
      }
    });
  }

  getStatusClass(status: string): string {
    switch (status?.toLowerCase()) {
      case 'listening':
      case 'running':
        return 'bg-green-100 text-green-800';
      case 'stopped':
        return 'bg-gray-100 text-gray-800';
      case 'starting':
        return 'bg-yellow-100 text-yellow-800';
      case 'stopping':
        return 'bg-orange-100 text-orange-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }
}

