import { useEffect } from 'react';

interface KeyboardControlsProps {
  isRecording: boolean;
  sessionId: string | null;
  onStartRecording: () => Promise<void>;
  onStopRecording: () => void;
}

export function useKeyboardControls({
  isRecording,
  sessionId,
  onStartRecording,
  onStopRecording,
}: KeyboardControlsProps) {
  useEffect(() => {
    const handleKeyDown = async (event: KeyboardEvent) => {
      if (event.code === 'Space' && !isRecording && sessionId) {
        event.preventDefault(); // スペースキーのデフォルト動作（スクロール）を防止
        await onStartRecording();
      }
    };

    const handleKeyUp = (event: KeyboardEvent) => {
      if (event.code === 'Space' && isRecording) {
        event.preventDefault();
        onStopRecording();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [isRecording, sessionId, onStartRecording, onStopRecording]);
} 