const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface SessionResponse {
  session_id: string;
}

export interface WebpageRequest {
  url: string;
}

export interface WebpageResponse {
  webpage_data: {
    title: string;
  };
}

export interface Transcription {
  id: number;
  content: string;
}

export interface Response {
  id: number;
  content: string;
}

export interface AudioResponse {
  transcription: Transcription;
  response: Response;
  audio_content: string;
}

export interface AnalysisResult {
  advice: string;
  speechflaws: string;
  nuanceinquiry: string[];
  alternativeexpressions: [string, string][];
  suggestion: string;
}

export interface AnalysisResultResponse {
  analysis_result: AnalysisResult;
}



export class AudioService {
  static async createSession(): Promise<SessionResponse> {
    const response = await fetch(`${API_BASE_URL}/gemini_audio`, {
      method: 'GET',
    });
    console.log(response);
    
    if (!response.ok) {
      throw new Error(`Failed to create session: ${response.statusText}`);
    }
    
    return response.json();
  }

  static async addWebpageToSession(sessionId: string, url: string): Promise<WebpageResponse> {
    const response = await fetch(`${API_BASE_URL}/gemini_audio/${sessionId}/webpage`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url.trim() }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to add webpage');
    }

    return response.json();
  }

  static async processAudio(sessionId: string, audioBlob: Blob): Promise<AudioResponse> {
    const formData = new FormData();
    formData.append('audio_file', audioBlob);

    const response = await fetch(`${API_BASE_URL}/gemini_audio/${sessionId}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to process audio: ${response.statusText}`);
    }

    return response.json();
  }

  static async getAnalysisResult(sessionId: string, conversationId: string): Promise<AnalysisResultResponse> {
    const response = await fetch(`${API_BASE_URL}/get_analysis_result/${sessionId}/${conversationId}`);
    return response.json();
  }
} 
