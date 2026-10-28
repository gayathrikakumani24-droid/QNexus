import React from 'react';
import { InlineMath, BlockMath } from 'react-katex';

/**
 * Parses mixed text containing LaTeX expressions ($...$, $$...$$, \(...\), \[...\])
 * and renders inline and block KaTeX math gracefully with error fallback.
 */
export const LatexRenderer = ({ content, className = '' }) => {
  if (!content) return null;

  // Split content by $$...$$ or $...$
  const regex = /(\$\$[\s\S]*?\$\$|\$[^\$\n]+?\$)/g;
  const parts = content.split(regex);

  return (
    <div className={`leading-relaxed ${className}`}>
      {parts.map((part, index) => {
        if (!part) return null;

        // Block math: $$ ... $$
        if (part.startsWith('$$') && part.endsWith('$$')) {
          const math = part.slice(2, -2).trim();
          return (
            <div key={index} className="my-2 overflow-x-auto py-1">
              <BlockMath math={math} errorColor="#f43f5e" />
            </div>
          );
        }

        // Inline math: $ ... $
        if (part.startsWith('$') && part.endsWith('$')) {
          const math = part.slice(1, -1).trim();
          return <InlineMath key={index} math={math} errorColor="#f43f5e" />;
        }

        // Standard text
        return <span key={index}>{part}</span>;
      })}
    </div>
  );
};

export default LatexRenderer;
