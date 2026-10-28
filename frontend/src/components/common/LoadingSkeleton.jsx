import React from 'react';

export const QuestionCardSkeleton = () => (
  <div className="bg-white border border-qnx-border rounded-card p-6 shadow-paper-sm animate-pulse space-y-4">
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="h-5 w-20 bg-qnx-sage-soft rounded-badge"></div>
        <div className="h-5 w-28 bg-qnx-border-light rounded-badge"></div>
      </div>
      <div className="h-5 w-24 bg-qnx-border-light rounded-badge"></div>
    </div>
    <div className="space-y-2 py-2">
      <div className="h-4 bg-qnx-border-light rounded w-full"></div>
      <div className="h-4 bg-qnx-border-light rounded w-5/6"></div>
      <div className="h-4 bg-qnx-border-light rounded w-3/4"></div>
    </div>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-qnx-border-light">
      <div className="h-4 bg-qnx-border-light rounded"></div>
      <div className="h-4 bg-qnx-border-light rounded"></div>
      <div className="h-4 bg-qnx-border-light rounded"></div>
      <div className="h-4 bg-qnx-border-light rounded"></div>
    </div>
  </div>
);

export const CardSkeleton = () => (
  <div className="bg-white border border-qnx-border rounded-card p-6 shadow-paper-sm animate-pulse space-y-3">
    <div className="h-5 bg-qnx-border-light rounded w-1/3"></div>
    <div className="h-8 bg-qnx-sage-soft rounded w-1/2"></div>
    <div className="h-4 bg-qnx-border-light rounded w-2/3"></div>
  </div>
);

export const TableSkeleton = ({ rows = 5 }) => (
  <div className="bg-white border border-qnx-border rounded-card p-4 shadow-paper-sm animate-pulse space-y-3">
    <div className="h-6 bg-qnx-border-light rounded w-1/4 mb-4"></div>
    {Array.from({ length: rows }).map((_, idx) => (
      <div key={idx} className="flex items-center justify-between py-2 border-b border-qnx-border-light last:border-0">
        <div className="h-4 bg-qnx-border-light rounded w-1/3"></div>
        <div className="h-4 bg-qnx-border-light rounded w-1/6"></div>
        <div className="h-4 bg-qnx-border-light rounded w-1/6"></div>
      </div>
    ))}
  </div>
);

export default QuestionCardSkeleton;
