import React, { useEffect, useState } from 'react';
import { Clock, AlertTriangle } from 'lucide-react';

export const Timer = ({ initialMinutes = 30, onTimeUp, isRunning = true }) => {
  const [secondsLeft, setSecondsLeft] = useState(initialMinutes * 60);

  useEffect(() => {
    setSecondsLeft(initialMinutes * 60);
  }, [initialMinutes]);

  useEffect(() => {
    if (!isRunning || secondsLeft <= 0) {
      if (secondsLeft <= 0 && onTimeUp) onTimeUp();
      return;
    }

    const interval = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          if (onTimeUp) onTimeUp();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isRunning, secondsLeft, onTimeUp]);

  const minutes = Math.floor(secondsLeft / 60);
  const seconds = secondsLeft % 60;
  const isUrgent = secondsLeft < 300; // < 5 mins

  return (
    <div
      className={`px-3.5 py-1.5 rounded-xl border flex items-center gap-2 font-mono text-xs font-bold transition-all shadow-paper-sm ${
        isUrgent
          ? 'bg-qnx-terracotta-soft text-qnx-terracotta border-qnx-terracotta-soft animate-pulse'
          : 'bg-white border-qnx-border text-qnx-text'
      }`}
    >
      {isUrgent ? (
        <AlertTriangle className="w-4 h-4 text-qnx-terracotta shrink-0" />
      ) : (
        <Clock className="w-4 h-4 text-qnx-olive shrink-0" />
      )}
      <span>
        {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
      </span>
    </div>
  );
};

export default Timer;
