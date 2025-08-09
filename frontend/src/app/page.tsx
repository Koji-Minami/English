'use client';

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { AudioService } from '@/lib/services/api';
import { AudioRecorder, createAudioUrlFromBase64 } from '@/lib/services/audioRecorder';
import { useKeyboardControls } from '@/lib/hooks/useKeyboardControls';

export default function Component() {
    const [userName, setUserName] = useState("");
    const [url, setUrl] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [talkHistory, setTalkHistory] = useState(["aaaa","bbbb","cccc","dddd","eeee"]);
    const [conversationHistory, setConversationHistory] = useState<Array<{id: number, isUser: boolean, content: string}>>([]);
    const [speechflaws, setSpeechflaws] = useState("");
    const [adviceForExpression, setAdviceForExpression] = useState("");
    const [alternativeExpressions, setAlternativeExpressions] = useState<string[]>([]);
    const [usefulIdioms, setUsefulIdioms] = useState<string[]>([]);
    const [isInvisible, setIsInvisible] = useState(false);
    const audioRecorderRef = useRef<AudioRecorder | null>(null);
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const [isRecording, setIsRecording] = useState(false);
    const [webpageUrl, setWebpageUrl] = useState('');
    const [isAddingWebpage, setIsAddingWebpage] = useState(false);
    const [webpageStatus, setWebpageStatus] = useState<string | null>(null);
    const [transcript, setTranscript] = useState<string>('');
    const [response, setResponse] = useState<string>('');
    const [analysisResults, setAnalysisResults] = useState<{[key: string]: any}>({});
    const [selectedMessageId, setSelectedMessageId] = useState<number | null>(null);
    

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
      const data = await AudioService.createSession(userName);
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
      
      setTranscript(data.transcription.content);
      setResponse(data.response.content);
      setConversationHistory([...conversationHistory, {
        id: data.transcription.id,
        isUser: true,
        content: data.transcription.content,
      },{
        id: data.response.id,
        isUser: false,
        content: data.response.content,
      }]);
      console.log(conversationHistory);
      

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

  const finishSession = async () => {
    try {
      console.log("finish session");
      setSessionId(null);
      setWebpageStatus(null); // セッション作成時にステータスをリセット
      setConversationHistory([]);
      setAnalysisResults({});
      setSelectedMessageId(null);
      setTranscript("");
      setResponse("");
      setSpeechflaws("");
      setAdviceForExpression("");
      setAlternativeExpressions([]);
      setUsefulIdioms([]);
    } catch (error) {
      console.error('Error finishing session:', error);
      setError('セッションの完了に失敗しました');
    }
  };

  const handleMessageClick = async (messageId: number, isUser: boolean) => {
    if (!isUser || !sessionId) return;
    
    try {
      setSelectedMessageId(messageId);
      console.log(messageId);
      const result = await AudioService.getAnalysisResult(sessionId, messageId.toString());
      console.log(result);
      
      // 分析結果を保存
      setAnalysisResults(result);
      
      // 分析結果を表示用のstateに設定
      setAdviceForExpression(result.analysis_result.advice || '');
      setSpeechflaws(result.analysis_result.speechflaws || '');
      setAlternativeExpressions(
        result.analysis_result.alternativeexpressions?.map((expr: [string, string]) => expr[0]) || []
      );
      setUsefulIdioms(
        Array.isArray(result.analysis_result.suggestion) 
          ? result.analysis_result.suggestion 
          : []
      );
    } catch (error) {
      console.error('Error getting analysis result:', error);
      setError('分析結果の取得に失敗しました');
    }
  };

  const toggleInvisibleMode = () => {
    setIsInvisible(!isInvisible);
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-100 via-blue-50 to-indigo-100 overflow-hidden">
    {!userName && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white p-8 rounded-lg shadow-xl text-center">
          <h2 className="text-2xl font-bold text-slate-800 mb-4">Select User</h2>
          <div className="flex flex-col gap-4">
            <Button onClick={() => setUserName("Koji")} className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg hover:shadow-xl transition-all duration-200">
              Koji
            </Button>
            <Button onClick={() => setUserName("Risa")} className="bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200">
              Risa
            </Button>
          </div>
        </div>
      </div>
    )}
      {/* 音声要素（非表示） */}
      <audio ref={audioRef} src={audioUrl || undefined} controls className="hidden"/>
      {/* 左サイドバー */}
      <div className="w-48 bg-gradient-to-b from-slate-800 to-slate-900 p-4 shadow-xl flex-shrink-0">
        <div className="mb-8">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <div className="w-6 h-6 bg-gradient-to-r from-blue-400 to-blue-600 rounded-full"></div>
            Talk History
          </h2>
          <div className="space-y-2">
            {talkHistory.map((_, i) => (
              <div
                key={i}
                className="text-slate-300 text-sm hover:text-white hover:bg-slate-700 p-2 rounded-lg cursor-pointer transition-all duration-200"
              >
                {_}
              </div>
            ))}
          </div>
        </div>

        <div className="border-t border-slate-600 pt-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <div className="w-5 h-5 bg-gradient-to-r from-green-400 to-green-600 rounded-full"></div>
            Words Test
          </h3>
        </div>
      </div>

      {/* メインエリア */}
      <div className="flex-1 flex flex-col p-6 min-w-0">
        {/* ヘッダー部分 */}
        <div className="flex-shrink-0 mb-6">
          <h3 className="text-lg font-bold text-slate-800 mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            ようこそ、{userName}さん
          </h3>
          <h1 className="text-3xl font-bold text-slate-800 mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Talk Theme: Lorem ipsum dolor sit amet, consectetur
          </h1>

          {/* セッション開始ボタン */}
          <div className="mb-4 flex gap-3">
            <Button 
              onClick={createSession}
              disabled={isLoading}
              className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white shadow-lg hover:shadow-xl transition-all duration-200"
            >
              {sessionId ? `ID:${sessionId}` : 'セッションを開始'}
            </Button>
            <Button 
              onClick={finishSession}
              disabled={isLoading}
              className={`bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 ${sessionId ? '' : 'hidden'}`}
            >
              {`finish session`}
            </Button>

          </div>

          <div className="flex gap-3">
              <div className="flex items-center gap-2 bg-white rounded-lg p-3 shadow-md border border-slate-200">
                <span className="text-slate-700 text-sm font-medium">URL:</span>
                <Input
                  value={webpageUrl}
                  onChange={(e) => setWebpageUrl(e.target.value)}
                  placeholder="URLを入力してください"
                  className="w-64 border-slate-300 focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              <Button 
                onClick={addWebpageToSession}
                disabled={!sessionId || isAddingWebpage}
                className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg hover:shadow-xl transition-all duration-200"
              >
                {isAddingWebpage ? '追加中...' : 'Upload'}
              </Button>
            </div>
            {webpageStatus && (
              <div className="mt-2 text-sm text-blue-600">
                {webpageStatus}
              </div>
            )}

        </div>

        {/* 2つのウィンドウを並べる部分 - 残りの高さを全て使用 */}
        <div className="flex gap-6 flex-1 min-h-0">
          {/* Conversations History */}
          <div className="flex-1 bg-white rounded-xl shadow-lg border border-slate-200 flex flex-col min-w-0">
            <div className="flex items-center gap-3 p-6 pb-4 flex-shrink-0">
              <h2 className="text-2xl font-bold text-slate-800">Conversations History</h2>
              <Button
                variant="outline"
                size="sm"
                onClick={toggleInvisibleMode}
                className={`transition-colors duration-200 ${
                  isInvisible 
                    ? 'bg-red-100 border-red-300 text-red-700 hover:bg-red-200' 
                    : 'bg-slate-100 border-slate-300 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {isInvisible ? 'Visible' : 'Invisible'}
              </Button>
            </div>

            <div className="flex-1 px-6 pb-6 overflow-hidden">
              {!isInvisible ? (
                <div className="space-y-4 h-full overflow-y-auto">
                  {conversationHistory.map((message) => (
                    <div key={message.id} className={`flex gap-3 ${message.isUser ? '' : 'flex-row-reverse'}`}>
                      <div className={`w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center shadow-md ${
                        message.isUser 
                          ? 'bg-gradient-to-r from-blue-500 to-blue-600' 
                          : 'bg-gradient-to-r from-green-500 to-green-600'
                      }`}>
                        <span className="text-white text-sm font-bold">
                          {message.isUser ? 'U' : 'AI'}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0 px-2">
                        <div className={`text-sm font-semibold text-slate-700 mb-1 ${
                          message.isUser ? '' : 'text-right'
                        }`}>
                          {message.isUser ? 'User' : 'Models'}
                        </div>
                        <div 
                          className={`rounded-lg p-4 max-w-full text-slate-700 text-sm shadow-sm cursor-pointer transition-all duration-200 ${
                            message.isUser 
                              ? 'bg-blue-50 border border-blue-100 hover:bg-blue-100 hover:border-blue-200' 
                              : 'bg-green-50 border border-green-100'
                          } ${selectedMessageId === message.id ? 'ring-2 ring-blue-500' : ''}`}
                          onClick={() => handleMessageClick(message.id, message.isUser)}
                        >
                          {message.content}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-slate-400">
                  <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                    <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                    </svg>
                  </div>
                  <div className="text-lg font-semibold mb-2">非表示モード</div>
                  <div className="text-sm text-slate-500">メッセージが非表示になっています</div>
                </div>
              )}
            </div>
          </div>

          {/* English Skill-Up Report */}
          <div className="flex-1 bg-white rounded-xl shadow-lg border border-slate-200 flex flex-col min-w-0">
            <div className="flex items-center gap-3 p-6 pb-4 flex-shrink-0">
              <h2 className="text-2xl font-bold text-slate-800">
                English Skill-Up Report
                {selectedMessageId && (
                  <span className="text-sm font-normal text-slate-500 ml-2">
                    (Message ID: {selectedMessageId})
                  </span>
                )}
              </h2>
            </div>

            <div className="flex-1 px-6 pb-6 overflow-hidden">
              <div className="space-y-4 h-full overflow-y-auto">
                {/* Speechflows for Expression */}
                <div>
                  <div className="text-sm font-semibold text-slate-700 mb-2">Speechflaws</div>
                  <div className="bg-blue-50 rounded-lg p-4 text-slate-700 text-sm border border-blue-100 shadow-sm">
                    {speechflaws}
                  </div>
                </div>
                {/* Advice for Expression */}
                <div>
                  <div className="text-sm font-semibold text-slate-700 mb-2">Advice for Expression</div>
                  <div className="bg-orange-50 rounded-lg p-4 text-slate-700 text-sm border border-blue-100 shadow-sm">
                    {adviceForExpression}
                  </div>
                </div>

                {/* Alternative Expressions */}
                <div>
                  <div className="text-sm font-semibold text-slate-700 mb-2">Alternative Expressions</div>
                  <div className="bg-green-50 rounded-lg p-4 text-slate-700 text-sm border border-green-100 shadow-sm">
                    <ul className="space-y-1">
                      {alternativeExpressions.map((expression) => (
                        <li key={expression}>{expression}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Useful Idioms */}
                <div>
                  <div className="text-sm font-semibold text-slate-700 mb-2">Useful Idioms</div>
                  <div className="bg-purple-50 rounded-lg p-4 text-slate-700 text-sm border border-purple-100 shadow-sm">
                    <ul className="space-y-1">
                      {usefulIdioms.map((idiom) => (
                        <li key={idiom}>{idiom}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
