"use client";

import { useEffect, useState } from "react";

interface EscalationBannerProps {
  show: boolean;
  onDismiss: () => void;
}

export function EscalationBanner({ show, onDismiss }: EscalationBannerProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setVisible(true);
      const timer = setTimeout(() => {
        setVisible(false);
        onDismiss();
      }, 8000);
      return () => clearTimeout(timer);
    } else {
      setVisible(false);
    }
  }, [show, onDismiss]);

  if (!visible) return null;

  return (
    <div className="flex items-center gap-2 px-4 py-2.5 bg-amber-50 border-b border-amber-200 text-amber-800 text-sm animate-slide-up">
      <span className="text-base">⚠️</span>
      <span className="flex-1">
        Your message has been flagged for priority support. A human agent will
        assist you shortly.
      </span>
      <button
        onClick={() => {
          setVisible(false);
          onDismiss();
        }}
        className="text-amber-600 hover:text-amber-800 font-medium text-xs"
      >
        Dismiss
      </button>
    </div>
  );
}