import React from 'react';
import Badge from './ui/Badge';

function getLevelBadge(level) {
  if (level === 'safe') return 'success';
  if (level === 'warning') return 'warning';
  return 'danger';
}

function getLevelLabel(level) {
  return String(level || 'safe').toUpperCase();
}

export default function SpamScoreCard({ score = 0, level = 'safe' }) {
  const clamped = Math.max(0, Math.min(100, Number(score) || 0));
  const ringColor = level === 'safe' ? '#10b981' : level === 'warning' ? '#f59e0b' : '#ef4444';

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-slate-800">Spam Risk Score</h4>
        <Badge variant={getLevelBadge(level)} size="xs" className="uppercase tracking-wide">
          {getLevelLabel(level)}
        </Badge>
      </div>

      <div className="flex items-center gap-4">
        <div
          className="relative h-20 w-20 rounded-full"
          style={{
            background: `conic-gradient(${ringColor} ${clamped}%, #e2e8f0 ${clamped}% 100%)`,
          }}
        >
          <div className="absolute inset-2 rounded-full bg-white flex items-center justify-center">
            <span className="text-lg font-bold text-slate-900">{clamped}</span>
          </div>
        </div>
        <p className="text-xs text-slate-600">
          0 is safest. 100 is highest risk.
        </p>
      </div>
    </div>
  );
}
