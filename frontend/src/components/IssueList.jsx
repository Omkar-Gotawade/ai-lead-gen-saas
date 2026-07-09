import React from 'react';
import { AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function IssueList({ issues = [] }) {
  if (!issues.length) {
    return (
      <div className="rounded-xl border border-success/30 bg-success/10 p-3 flex items-start gap-2">
        <CheckCircle2 className="w-4 h-4 text-success mt-0.5" />
        <p className="text-sm text-success-light">No major spam risks detected.</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-brand-500/30 bg-brand-500/10 p-3">
      <div className="flex items-center gap-2 mb-2">
        <AlertTriangle className="w-4 h-4 text-brand-500" />
        <p className="text-sm font-semibold text-brand-400">Detected issues</p>
      </div>
      <ul className="space-y-1">
        {issues.map((issue, index) => (
          <li key={`${issue}-${index}`} className="text-sm text-brand-300">
            {issue}
          </li>
        ))}
      </ul>
    </div>
  );
}
