import { ApiResponse, MeetingDetails } from '../types';

const API_BASE_URL = import.meta.env.PROD 
  ? '' 
  : 'http://localhost:5000';

// Helper to get the full URL for the current environment
const getFullUrl = (path: string): string => {
  if (import.meta.env.PROD) {
    return path; // In production, use relative paths
  } else {
    return `http://localhost:5000${path}`; // In development, use full URL
  }
};

interface UploadResponse {
  success: boolean;
  session_id?: string;
  video_file?: string;
  audio_file?: string;
  transcript_file?: string;
  pdf_file?: string;
  email_sent?: boolean;
  processing_time?: number;
  transcript?: string;
  language?: string;
  duration?: number;
  output_file?: string;
  error?: string;
}

interface ChatResponse {
  success: boolean;
  response?: string;
  error?: string;
}

interface SessionResponse {
  success: boolean;
  session_id?: string;
  message?: string;
  error?: string;
}

interface TTSResponse {
  success: boolean;
  audio_url?: string;
  message?: string;
  error?: string;
}

interface PDFResponse {
  success: boolean;
  pdf_file?: string;
  download_url?: string;
  error?: string;
}

class ApiService {
  private async makeRequest<T>(
    url: string, 
    options: RequestInit = {}
  ): Promise<T> {
    try {
      console.log(`🔄 Making API request to: ${API_BASE_URL}${url}`);
      const response = await fetch(`${API_BASE_URL}${url}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      console.log(`📡 Response status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API error: ${response.status} - ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log(`✅ API response:`, data);
      return data;
    } catch (error) {
      console.error('❌ API request failed:', error);
      
      // Check for specific browser extension errors
      if (error instanceof Error) {
        if (error.message.includes('Could not establish connection') || 
            error.message.includes('Receiving end does not exist')) {
          throw new Error('Browser extension interference detected. Please disable extensions and try again.');
        }
        if (error.message.includes('Failed to fetch') || 
            error.message.includes('NetworkError')) {
          throw new Error('Network connection failed. Please check if the server is running.');
        }
      }
      
      throw error;
    }
  }

  private async makeFormRequest<T>(
    url: string, 
    formData: FormData
  ): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API form request failed:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    return this.makeRequest('/health');
  }

  // File processing endpoints
  async processVideo(
    file: File, 
    recipients: string[], 
    meetingDetails?: Partial<MeetingDetails>
  ): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('video_file', file);
    formData.append('recipients', recipients.join(','));
    
    if (meetingDetails?.title) formData.append('meeting_title', meetingDetails.title);
    if (meetingDetails?.date) formData.append('meeting_date', meetingDetails.date);
    if (meetingDetails?.companyName) formData.append('company_name', meetingDetails.companyName);
    if (meetingDetails?.customMessage) formData.append('custom_message', meetingDetails.customMessage);

    return this.makeFormRequest('/process-video', formData);
  }

  async processAudio(
    file: File, 
    recipients: string[], 
    meetingDetails?: Partial<MeetingDetails>
  ): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('audio_file', file);
    formData.append('recipients', recipients.join(','));
    
    if (meetingDetails?.title) formData.append('meeting_title', meetingDetails.title);
    if (meetingDetails?.date) formData.append('meeting_date', meetingDetails.date);
    if (meetingDetails?.companyName) formData.append('company_name', meetingDetails.companyName);
    if (meetingDetails?.customMessage) formData.append('custom_message', meetingDetails.customMessage);

    return this.makeFormRequest('/process-audio', formData);
  }

  async processTranscript(
    transcript: string,
    recipients: string[],
    meetingDetails?: Partial<MeetingDetails>
  ): Promise<UploadResponse> {
    return this.makeRequest('/process-transcript', {
      method: 'POST',
      body: JSON.stringify({
        transcript,
        recipients,
        meeting_title: meetingDetails?.title,
        meeting_date: meetingDetails?.date,
        company_name: meetingDetails?.companyName,
        custom_message: meetingDetails?.customMessage,
      }),
    });
  }

  async transcribeOnly(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    const isVideo = file.type.startsWith('video/');
    formData.append(isVideo ? 'video_file' : 'audio_file', file);

    return this.makeFormRequest('/transcribe-only', formData);
  }

  // Chat endpoints
  async startChatSession(transcript: string): Promise<SessionResponse> {
    return this.makeRequest('/chat/start', {
      method: 'POST',
      body: JSON.stringify({ transcript }),
    });
  }

  async sendChatMessage(sessionId: string, message: string): Promise<ChatResponse> {
    return this.makeRequest(`/chat/${sessionId}/message`, {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  async generateMinutes(
    sessionId: string, 
    meetingDetails: MeetingDetails
  ): Promise<PDFResponse> {
    // Convert frontend field names to backend expected format
    const backendData = {
      meeting_title: meetingDetails.title,
      meeting_date: meetingDetails.date,
      company_name: meetingDetails.companyName,
      custom_message: meetingDetails.customMessage,
    };
    
    return this.makeRequest(`/chat/${sessionId}/generate-minutes`, {
      method: 'POST',
      body: JSON.stringify(backendData),
    });
  }

  async sendEmail(
    sessionId: string, 
    meetingDetails: MeetingDetails
  ): Promise<ApiResponse> {
    // Convert frontend field names to backend expected format
    const backendData = {
      meeting_title: meetingDetails.title,
      meeting_date: meetingDetails.date,
      company_name: meetingDetails.companyName,
      recipients: meetingDetails.recipients,
      custom_message: meetingDetails.customMessage,
    };
    
    console.log('📧 sendEmail called with:', {
      sessionId,
      backendData
    });
    
    try {
      const response = await this.makeRequest(`/chat/${sessionId}/send-email`, {
        method: 'POST',
        body: JSON.stringify(backendData),
      }) as any;
      
      console.log('📧 sendEmail response:', response);
      
      // The backend returns a different format, so we need to adapt it
      if (response.success) {
        return {
          success: true,
          data: response
        };
      } else {
        return {
          success: false,
          error: response.error || 'Unknown error'
        };
      }
    } catch (error) {
      console.error('📧 sendEmail error:', error);
      throw error;
    }
  }

  async generateTTS(sessionId: string, text: string): Promise<TTSResponse> {
    return this.makeRequest(`/chat/${sessionId}/tts`, {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
  }

  // Utility endpoints
  async getSupportedFormats() {
    return this.makeRequest('/supported-formats');
  }

  // File download helper
  getDownloadUrl(filename: string): string {
    return getFullUrl(`/download/${filename}`);
  }

  getAudioUrl(filename: string): string {
    return getFullUrl(`/audio/${filename}`);
  }
}

export const apiService = new ApiService();
export default apiService;
