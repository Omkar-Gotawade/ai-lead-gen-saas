import { useState } from 'react';
import { createPortal } from 'react-dom';
import { RotateCcw, Wrench } from 'lucide-react';
import { checkSpam, generateEmail, sendTestEmail } from '../api/email';
import SpamScoreCard from './SpamScoreCard';
import IssueList from './IssueList';

export default function EmailComposer({ lead, onClose, onSend, emailProviderConfigured = false }) {
  const [tone, setTone] = useState('professional');
  const [goal, setGoal] = useState('schedule a meeting');
  const [productDescription, setProductDescription] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [loadingGenerate, setLoadingGenerate] = useState(false);
  const [loadingSend, setLoadingSend] = useState(false);
  const [checkingSpam, setCheckingSpam] = useState(false);
  const [applyingFixes, setApplyingFixes] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [spamResult, setSpamResult] = useState(null);

  const runSpamAnalysis = async (emailBody) => {
    setCheckingSpam(true);
    try {
      const result = await checkSpam({
        email_body: emailBody,
        lead_id: lead?.id || null,
        campaign_id: null,
      });
      setSpamResult(result);
      return result;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to run spam check');
      return null;
    } finally {
      setCheckingSpam(false);
    }
  };

  const handleGenerate = async () => {
    setLoadingGenerate(true);
    setError('');
    
    try {
      const data = await generateEmail({
        lead_id: lead.id,
        tone,
        goal,
        product_description: productDescription || 'our product or service'
      });
      
      setSubject(data.subject);
      setBody(data.body);
      const spam = await runSpamAnalysis(data.body);

      if (spam?.level === 'critical') {
        setSuccess('Email generated, but spam risk is critical. Apply fixes or regenerate.');
      } else if (spam?.level === 'warning') {
        setSuccess('Email generated with warnings. Review issues before sending.');
      } else {
        setSuccess('Email generated successfully!');
      }
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate email');
    } finally {
      setLoadingGenerate(false);
    }
  };

  const handleApplyFixes = async () => {
    if (!body) {
      return;
    }

    setApplyingFixes(true);
    setError('');

    try {
      const replacements = {
        free: 'complimentary',
        guarantee: 'aim to',
        urgent: 'timely',
        win: 'improve',
      };

      let fixed = body;

      Object.entries(replacements).forEach(([word, replacement]) => {
        fixed = fixed.replace(new RegExp(`\\b${word}\\b`, 'gi'), replacement);
      });

      fixed = fixed.replace(/!{2,}/g, '!');

      let linkSeen = false;
      fixed = fixed.replace(/(https?:\/\/\S+|www\.\S+)/gi, (match) => {
        if (!linkSeen) {
          linkSeen = true;
          return match;
        }
        return '';
      });

      if (lead?.company && !fixed.toLowerCase().includes(lead.company.toLowerCase())) {
        fixed += `\n\nP.S. I put this together specifically for ${lead.company}.`;
      }

      setBody(fixed);
      await runSpamAnalysis(fixed);

      setSuccess('Applied spam-safety fixes. Please review the updated draft.');
      setTimeout(() => setSuccess(''), 3000);
    } finally {
      setApplyingFixes(false);
    }
  };

  const handleSendTest = async () => {
    if (!subject || !body) {
      setError('Please generate an email first');
      return;
    }

    setLoadingSend(true);
    setError('');
    
    try {
      await sendTestEmail({
        to_email: lead.email,
        subject,
        body
      });
      
      setSuccess('Test email sent successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send test email');
    } finally {
      setLoadingSend(false);
    }
  };

  const handleSave = () => {
    if (onSend) {
      onSend({ subject, body });
    }
  };

  return createPortal(
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[1000] p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Email Composer</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Lead Info */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-3">Lead Information</h3>
              <div className="space-y-2 text-sm">
                <p><span className="font-medium">Name:</span> {lead.first_name} {lead.last_name}</p>
                <p><span className="font-medium">Email:</span> {lead.email}</p>
                {lead.title && <p><span className="font-medium">Title:</span> {lead.title}</p>}
                {lead.company && <p><span className="font-medium">Company:</span> {lead.company}</p>}
                {lead.industry && <p><span className="font-medium">Industry:</span> {lead.industry}</p>}
              </div>
            </div>

            {/* Generation Options */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tone
                </label>
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="professional">Professional</option>
                  <option value="friendly">Friendly</option>
                  <option value="casual">Casual</option>
                  <option value="formal">Formal</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Goal
                </label>
                <input
                  type="text"
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  placeholder="e.g., book a demo, get a reply"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Product Description
                </label>
                <textarea
                  value={productDescription}
                  onChange={(e) => setProductDescription(e.target.value)}
                  placeholder="Brief description of your product or service"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                onClick={handleGenerate}
                disabled={loadingGenerate}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {loadingGenerate ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </>
                ) : (
                  '✨ Generate Email with AI'
                )}
              </button>

              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={handleApplyFixes}
                  disabled={applyingFixes || !body}
                  className="w-full border border-amber-300 text-amber-800 py-2 px-3 rounded-md hover:bg-amber-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm"
                >
                  <Wrench className="w-4 h-4" />
                  {applyingFixes ? 'Fixing...' : 'Fix'}
                </button>
                <button
                  onClick={handleGenerate}
                  disabled={loadingGenerate}
                  className="w-full border border-blue-300 text-blue-800 py-2 px-3 rounded-md hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm"
                >
                  <RotateCcw className="w-4 h-4" />
                  Regenerate
                </button>
              </div>

              {checkingSpam && (
                <p className="text-xs text-slate-500">Running spam check...</p>
              )}
            </div>
          </div>

          {/* Error/Success Messages */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
              {error}
            </div>
          )}
          {success && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md text-green-700 text-sm">
              {success}
            </div>
          )}

          {spamResult && (
            <div className="mb-4 space-y-3">
              <SpamScoreCard score={spamResult.score} level={spamResult.level} />
              <IssueList issues={spamResult.issues} />
            </div>
          )}

          {/* Email Preview/Edit */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subject
              </label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Email subject line"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Body
              </label>
              <textarea
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder="Email body text"
                rows={12}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 mt-6">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSendTest}
              disabled={loadingSend || !subject || !body}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loadingSend ? 'Sending...' : 'Send Test'}
            </button>
            <button
              onClick={handleSave}
              disabled={!subject || !body}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              Save Draft
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
}
