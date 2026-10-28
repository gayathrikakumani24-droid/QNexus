import React from 'react';
import { Link } from 'react-router-dom';
import { Layers, Sparkles, ArrowRight, Calendar, Clock } from 'lucide-react';
import LatexRenderer from '../common/LatexRenderer';

const SimilarQuestionsList = ({ similarQuestions, isLoading }) => {
  if (isLoading) {
    return (
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3 animate-pulse">
        <div className="h-4 w-40 bg-slate-800 rounded"></div>
        <div className="space-y-2">
          <div className="h-16 bg-slate-800/60 rounded-xl"></div>
          <div className="h-16 bg-slate-800/60 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (!similarQuestions || similarQuestions.length === 0) {
    return null;
  }

  return (
    <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4 shadow-lg">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center space-x-2">
          <Layers className="h-4 w-4 text-cyan-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-white">
            Semantically Similar PYQs ({similarQuestions.length})
          </h3>
        </div>
        <span className="text-[11px] text-slate-500 font-medium">Vector Matched</span>
      </div>

      <div className="space-y-3">
        {similarQuestions.map((item, idx) => {
          const q = item.question;
          const score = item.similarity_score;

          return (
            <div
              key={q.question_id || idx}
              className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 transition-all space-y-2.5 group"
            >
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    {q.subject || 'JEE Main'}
                  </span>
                  <span className="text-slate-400 font-medium text-[11px]">{q.chapter || ''}</span>
                </div>

                {score && (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-950/60 text-cyan-300 border border-cyan-800/50 flex items-center space-x-1">
                    <Sparkles className="h-2.5 w-2.5" />
                    <span>{Math.round(score * 100)}% Match</span>
                  </span>
                )}
              </div>

              <div className="text-slate-200 text-xs line-clamp-2 leading-relaxed">
                <LatexRenderer content={q.content} />
              </div>

              <div className="pt-2 border-t border-slate-900 flex items-center justify-between text-[11px] text-slate-500">
                <span>{q.year} {q.session || ''} • {q.shift || ''}</span>
                <Link
                  to={`/question/${q.question_id}`}
                  className="text-blue-400 hover:text-blue-300 font-semibold flex items-center space-x-1 group-hover:translate-x-0.5 transition-transform"
                >
                  <span>Practice</span>
                  <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SimilarQuestionsList;
