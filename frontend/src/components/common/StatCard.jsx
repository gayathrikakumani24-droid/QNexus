import React from 'react';

export const StatCard = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'olive', // 'olive' | 'sage' | 'mustard' | 'terracotta' | 'blue'
  trend,
  className = ''
}) => {
  const variantStyles = {
    olive: {
      bg: 'bg-white',
      border: 'border-qnx-border',
      iconBg: 'bg-qnx-sage-soft text-qnx-olive',
      valueColor: 'text-qnx-olive',
      badge: 'bg-qnx-sage-light text-qnx-olive border-qnx-sage/40'
    },
    sage: {
      bg: 'bg-white',
      border: 'border-qnx-border',
      iconBg: 'bg-qnx-sage-light text-qnx-sage',
      valueColor: 'text-qnx-olive',
      badge: 'bg-qnx-sage-soft text-qnx-olive border-qnx-sage/30'
    },
    mustard: {
      bg: 'bg-white',
      border: 'border-qnx-mustard-soft',
      iconBg: 'bg-qnx-mustard-soft text-[#946E14]',
      valueColor: 'text-[#946E14]',
      badge: 'bg-qnx-mustard-light text-[#946E14] border-qnx-mustard-soft'
    },
    terracotta: {
      bg: 'bg-white',
      border: 'border-qnx-terracotta-soft',
      iconBg: 'bg-qnx-terracotta-soft text-qnx-terracotta',
      valueColor: 'text-qnx-terracotta',
      badge: 'bg-qnx-terracotta-light text-qnx-terracotta border-qnx-terracotta-soft'
    },
    blue: {
      bg: 'bg-white',
      border: 'border-qnx-blue-soft',
      iconBg: 'bg-qnx-blue-soft text-qnx-blue',
      valueColor: 'text-[#38679E]',
      badge: 'bg-qnx-blue-light text-[#38679E] border-qnx-blue-soft'
    }
  };

  const style = variantStyles[variant] || variantStyles.olive;

  return (
    <div className={`p-5 rounded-card border ${style.border} ${style.bg} shadow-paper-sm hover:shadow-paper transition-all hover:-translate-y-0.5 ${className}`}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-semibold tracking-wider text-qnx-muted uppercase">{title}</p>
          <p className={`font-serif text-3xl font-bold ${style.valueColor}`}>{value}</p>
          {subtitle && <p className="text-xs text-qnx-muted">{subtitle}</p>}
        </div>
        {Icon && (
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${style.iconBg}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      {trend && (
        <div className="mt-3 pt-3 border-t border-qnx-border-light flex items-center gap-1.5 text-xs">
          <span className={`px-2 py-0.5 rounded-full border text-[11px] font-medium ${style.badge}`}>
            {trend}
          </span>
        </div>
      )}
    </div>
  );
};

export default StatCard;
