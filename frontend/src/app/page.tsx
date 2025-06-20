'use client';

import { useState, useRef, useEffect } from 'react';

export default function Home() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [speechFlaws, setSpeechFlaws] = useState('');
  
  interface NuanceItem {
    alternative: string;
    nuance: string;
  }
  
  const [nuanceInquiry, setNuanceInquiry] = useState<NuanceItem | NuanceItem[] | null>(null);
  const [alternativeExpressions, setAlternativeExpressions] = useState<NuanceItem | NuanceItem[] | null>(null);

  // 音声URLが変更されたら自動再生
  useEffect(() => {
    if (audioUrl && audioRef.current) {
      audioRef.current.play().catch(error => {
        console.error('Error playing audio:', error);
      });
    }
  }, [audioUrl]);

  // コンポーネントのクリーンアップ
  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  // キーボードイベントのハンドリング
  useEffect(() => {
    const handleKeyDown = async (event: KeyboardEvent) => {
      if (event.code === 'Space' && !isRecording && sessionId) {
        event.preventDefault(); // スペースキーのデフォルト動作（スクロール）を防止
        await startRecording();
      }
    };

    const handleKeyUp = (event: KeyboardEvent) => {
      if (event.code === 'Space' && isRecording) {
        event.preventDefault();
        stopRecording();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [isRecording, sessionId]);

  const createSession = async () => {
    const response = await fetch('http://localhost:8000/api/v1/gemini_audio/', {
      method: 'GET',
    });
    const data = await response.json();
    setSessionId(data.session_id);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio_file', audioBlob);

        try {
          const response = await fetch('http://localhost:8000/api/v1/gemini_audio/' + sessionId, {
            method: 'POST',
            body: formData,
          });
          const data = await response.json();
          setTranscript(data.gemini_response[0].transcription);
          setResponse(data.gemini_response[0].response);
          setSpeechFlaws(data.gemini_response[0].speechflaws);
          setNuanceInquiry(data.gemini_response[0].nuanceinquiry);
          setAlternativeExpressions(data.gemini_response[0].alternativeexpressions);
          
          // デバッグ用のログ
          console.log('Nuance Inquiry:', data.gemini_response[0].nuanceinquiry);
          console.log('Alternative Expressions:', data.gemini_response[0].alternativeexpressions);

          // 音声データをBase64からBlobに変換
          const audioContent = data.audio_content;
          try {
            const byteCharacters = atob(audioContent);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
              byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const audioBlob = new Blob([byteArray], { type: 'audio/mp3' });

            // 既存のURLを解放
            if (audioUrl) {
              URL.revokeObjectURL(audioUrl);
            }

            // 新しい音声URLを設定
            const newAudioUrl = URL.createObjectURL(audioBlob);
            setAudioUrl(newAudioUrl);
          } catch (error) {
            console.error('Error decoding audio data:', error);
            console.log('Audio content:', audioContent);
          }
        } catch (error) {
          console.error('Error transcribing audio:', error);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Speech to Text</h1>
        
        <div className="mb-8">
          <h2>{sessionId}</h2>
          <button
            onClick={createSession}
            className={`px-6 py-3 rounded-full font-semibold ${
              sessionId
                ? 'bg-red-500 hover:bg-red-600'
                : 'bg-blue-500 hover:bg-blue-600'
            } text-white transition-colors`}
          >
            {sessionId ? 'Now Conversation' : 'Start Conversation'}
          </button>
          <div className="mt-4 text-center">
            <p className="text-gray-600">
              {sessionId 
                ? 'スペースキーを押している間だけ録音します'
                : '会話を開始してください'}
            </p>
            {isRecording && (
              <div className="mt-2 text-red-500 font-semibold animate-pulse">
                録音中...
              </div>
            )}
          </div>
        </div>

        {transcript && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Transcription:</h2>
            <p className="text-gray-700">{transcript}</p>
            <h2 className="text-xl font-semibold mb-4">Response:</h2>
            <p className="text-gray-700">{response}</p>
            <h2 className="text-xl font-semibold mb-4">Speech Flaws:</h2>
            <p className="text-gray-700">{speechFlaws}</p>
            <h2 className="text-xl font-semibold mb-4">Nuance Inquiry:</h2>
            <ul className="list-disc pl-5 text-gray-700">
              {nuanceInquiry && (Array.isArray(nuanceInquiry) ? (
                nuanceInquiry.map((item, index) => (
                  <li key={index}>
                    {typeof item === 'object' ? (
                      <>
                        <div>Alternative: {item.alternative}</div>
                        <div>Nuance: {item.nuance}</div>
                      </>
                    ) : (
                      item
                    )}
                  </li>
                ))
              ) : (
                <li>
                  {typeof nuanceInquiry === 'object' ? (
                    <>
                      <div>Alternative: {nuanceInquiry.alternative}</div>
                      <div>Nuance: {nuanceInquiry.nuance}</div>
                    </>
                  ) : (
                    JSON.stringify(nuanceInquiry)
                  )}
                </li>
              ))}
            </ul>
            <h2 className="text-xl font-semibold mb-4">Alternative Expressions:</h2>
            <ul className="list-disc pl-5 text-gray-700">
              {alternativeExpressions && (Array.isArray(alternativeExpressions) ? (
                alternativeExpressions.map((item, index) => (
                  <li key={index}>
                    {typeof item === 'object' ? (
                      <>
                        <div>Alternative: {item.alternative}</div>
                        <div>Nuance: {item.nuance}</div>
                      </>
                    ) : (
                      item
                    )}
                  </li>
                ))
              ) : (
                <li>
                  {typeof alternativeExpressions === 'object' ? (
                    <>
                      <div>Alternative: {alternativeExpressions.alternative}</div>
                      <div>Nuance: {alternativeExpressions.nuance}</div>
                    </>
                  ) : (
                    JSON.stringify(alternativeExpressions)
                  )}
                </li>
              ))}
            </ul>
            {audioUrl && (
              <audio
                ref={audioRef}
                src={audioUrl}
                controls
                className="mt-4 w-full"
              />
            )}
          </div>
        )}
      </div>
    </main>
  );
}
