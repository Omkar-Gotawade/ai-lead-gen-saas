import React from 'react';
import { AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function IssueList({ issues = [] }) {
  if (!issues.length) {
    return (
      <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 flex items-start gap-2">
        <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5" />
        <p className="text-sm text-emerald-800">No major spam risks detected.</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-3">
      <div className="flex items-center gap-2 mb-2">
        <AlertTriangle className="w-4 h-4 text-amber-700" />
        <p className="text-sm font-semibold text-amber-800">Detected issues</p>
      </div>
      <ul className="space-y-1">
        {issues.map((issue, index) => (
          <li key={`${issue}-${index}`} className="text-sm text-amber-900">
            {issue}
          </li>
        ))}
      </ul>
    </div>
  );
}
