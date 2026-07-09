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
    <div className="rounded-xl border border-white/10 bg-canvas p-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-white">Spam Risk Score</h4>
        <Badge variant={getLevelBadge(level)} size="xs" className="uppercase tracking-wide">
          {getLevelLabel(level)}
        </Badge>
      </div>

      <div className="flex items-center gap-4">
        <div
          className="relative h-20 w-20 rounded-full"
          style={{
            background: `conic-gradient(${ringColor} ${clamped}%, #1e2130 ${clamped}% 100%)`,
          }}
        >
          <div className="absolute inset-2 rounded-full bg-surface flex items-center justify-center">
            <span className="text-lg font-bold text-white">{clamped}</span>
          </div>
        </div>
        <p className="text-xs text-ink-400">
          0 is safest. 100 is highest risk.
        </p>
      </div>
    </div>
  );
}
