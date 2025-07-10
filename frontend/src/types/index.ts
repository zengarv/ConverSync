export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export interface SessionData {
  id: string;
  transcript: string;
  isActive: boolean;
}

export interface MeetingDetails {
  title: string;
  date: string;
  companyName: string;
  recipients?: string[];
  customMessage?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface UploadProgress {
  isUploading: boolean;
  progress: number;
  status: 'idle' | 'uploading' | 'processing' | 'complete' | 'error';
}