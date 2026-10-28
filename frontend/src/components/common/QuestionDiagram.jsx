import React, { useState } from 'react';
import { ZoomIn, X } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const BACKEND_URL = API_BASE_URL.replace('/api/v1', '');

export const QuestionDiagram = ({ imageUrls = [], className = '' }) => {
  const [zoomedImage, setZoomedImage] = useState(null);

  if (!imageUrls || imageUrls.length === 0) return null;

  const getFullUrl = (url) => {
    if (!url) return '';
    return url.startsWith('http') ? url : `${BACKEND_URL}${url}`;
  };

  return (
    <div className={`space-y-2.5 my-3 ${className}`}>
      <div className="flex flex-wrap items-center gap-3">
        {imageUrls.map((url, idx) => {
          const fullUrl = getFullUrl(url);
          return (
            <div
              key={idx}
              className="relative group border border-qnx-border rounded-xl overflow-hidden bg-white shadow-paper-sm max-w-full"
            >
              <img
                src={fullUrl}
                alt={`Question diagram ${idx + 1}`}
                className="max-h-72 sm:max-h-96 object-contain rounded-xl p-2 mx-auto cursor-pointer hover:opacity-95 transition-opacity"
                onClick={() => setZoomedImage(fullUrl)}
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
              <button
                type="button"
                onClick={() => setZoomedImage(fullUrl)}
                className="absolute top-2 right-2 p-1.5 bg-black/60 text-white rounded-lg opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 text-[10px] font-bold"
                title="Expand diagram"
              >
                <ZoomIn className="w-3.5 h-3.5" />
                <span>Zoom</span>
              </button>
            </div>
          );
        })}
      </div>

      {zoomedImage && (
        <div 
          className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={() => setZoomedImage(null)}
        >
          <div 
            className="relative max-w-4xl max-h-[90vh] bg-white rounded-2xl p-4 overflow-auto shadow-2xl" 
            onClick={e => e.stopPropagation()}
          >
            <button
              onClick={() => setZoomedImage(null)}
              className="absolute top-3 right-3 p-1.5 bg-qnx-cream-paper hover:bg-qnx-cream text-qnx-text rounded-full shadow"
              title="Close"
            >
              <X className="w-5 h-5" />
            </button>
            <img src={zoomedImage} alt="Zoomed diagram" className="max-w-full max-h-[80vh] object-contain mx-auto" />
          </div>
        </div>
      )}
    </div>
  );
};

export default QuestionDiagram;
