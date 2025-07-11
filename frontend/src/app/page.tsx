'use client';

import { useState, useRef, useEffect } from 'react';
import { AudioService } from '@/lib/services/api';
import { AudioRecorder, createAudioUrlFromBase64 } from '@/lib/services/audioRecorder';
import { useKeyboardControls } from '@/lib/hooks/useKeyboardControls';

export default function Home() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const audioRecorderRef = useRef<AudioRecorder | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [speechFlaws, setSpeechFlaws] = useState('');
  const [webpageUrl, setWebpageUrl] = useState('');
  const [isAddingWebpage, setIsAddingWebpage] = useState(false);
  const [webpageStatus, setWebpageStatus] = useState<string | null>(null);
  
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

  const createSession = async () => {
    try {
      const data = await AudioService.createSession();
      setSessionId(data.session_id);
      setWebpageStatus(null); // セッション作成時にステータスをリセット
    } catch (error) {
      console.error('Error creating session:', error);
      setError('セッションの作成に失敗しました');
    }
  };

  const addWebpageToSession = async () => {
    if (!sessionId || !webpageUrl.trim()) {
      setWebpageStatus('セッションIDまたはURLが無効です');
      return;
    }

    setIsAddingWebpage(true);
    setWebpageStatus('Webページを読み込み中...');

    try {
      const data = await AudioService.addWebpageToSession(sessionId, webpageUrl);
      setWebpageStatus(`✅ ${data.webpage_data.title} を追加しました`);
      setWebpageUrl(''); // 入力フィールドをクリア
    } catch (error) {
      console.error('Error adding webpage:', error);
      setWebpageStatus(`❌ エラー: ${error instanceof Error ? error.message : 'Webページの追加に失敗しました'}`);
    } finally {
      setIsAddingWebpage(false);
    }
  };

  const startRecording = async () => {
    try {
      if (!audioRecorderRef.current) {
        audioRecorderRef.current = new AudioRecorder();
      }
      
      await audioRecorderRef.current.startRecording();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      setError('録音の開始に失敗しました');
    }
  };

  const stopRecording = async () => {
    if (!audioRecorderRef.current || !isRecording) return;

    try {
      const audioBlob = await audioRecorderRef.current.stopRecording();
      setIsRecording(false);

      if (!sessionId) {
        setError('セッションIDがありません');
        return;
      }

      const data = await AudioService.processAudio(sessionId, audioBlob);
      
      setTranscript(data.transcription);
      setResponse(data.response);

      // 音声データをBase64からBlobに変換
      try {
        // 既存のURLを解放
        if (audioUrl) {
          URL.revokeObjectURL(audioUrl);
        }

        // 新しい音声URLを設定
        const newAudioUrl = createAudioUrlFromBase64(data.audio_content);
        setAudioUrl(newAudioUrl);
      } catch (error) {
        console.error('Error decoding audio data:', error);
      }
    } catch (error) {
      console.error('Error processing audio:', error);
      setError('音声の処理に失敗しました');
    }
  };

  // キーボードイベントのハンドリング
  useKeyboardControls({
    isRecording,
    sessionId,
    onStartRecording: startRecording,
    onStopRecording: stopRecording,
  });

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Speech to Text</h1>
        
        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
            <button
              onClick={() => setError(null)}
              className="ml-2 text-red-500 hover:text-red-700"
            >
              ✕
            </button>
          </div>
        )}
        
        <div className="mb-8">
          <h2 className="text-lg font-semibold mb-2">Session ID: {sessionId || 'Not created'}</h2>
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
          
          {/* WebページURL入力フォーム */}
          {sessionId && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-3">📄 会話の題材を追加</h3>
              <div className="flex gap-2 mb-3">
                <input
                  type="url"
                  value={webpageUrl}
                  onChange={(e) => setWebpageUrl(e.target.value)}
                  placeholder="https://example.com/article"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isAddingWebpage}
                />
                <button
                  onClick={addWebpageToSession}
                  disabled={!webpageUrl.trim() || isAddingWebpage}
                  className={`px-4 py-2 rounded-md font-semibold ${
                    !webpageUrl.trim() || isAddingWebpage
                      ? 'bg-gray-300 cursor-not-allowed'
                      : 'bg-green-500 hover:bg-green-600 text-white'
                  } transition-colors`}
                >
                  {isAddingWebpage ? '追加中...' : '追加'}
                </button>
              </div>
              {webpageStatus && (
                <div className={`text-sm ${
                  webpageStatus.includes('✅') ? 'text-green-600' : 
                  webpageStatus.includes('❌') ? 'text-red-600' : 
                  'text-blue-600'
                }`}>
                  {webpageStatus}
                </div>
              )}
              <p className="text-xs text-gray-500 mt-2">
                Webページの内容を参考にした会話ができるようになります
              </p>
            </div>
          )}
          
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
            {/* <h2 className="text-xl font-semibold mb-4">Speech Flaws:</h2>
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
            </ul> */}
            {/* <h2 className="text-xl font-semibold mb-4">Alternative Expressions:</h2>
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
            </ul> */}
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
