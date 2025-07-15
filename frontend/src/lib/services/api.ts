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

export interface AudioResponse {
  transcription: string;
  response: string;
  audio_content: string;
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
} 