import { useState } from 'react';
import { generateEmail, sendTestEmail } from '../api/email';

export default function EmailComposer({ lead, onClose, onSend, emailProviderConfigured = false }) {
  const [tone, setTone] = useState('professional');
  const [goal, setGoal] = useState('schedule a meeting');
  const [productDescription, setProductDescription] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [loadingGenerate, setLoadingGenerate] = useState(false);
  const [loadingSend, setLoadingSend] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

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
      setSuccess('Email generated successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate email');
    } finally {
      setLoadingGenerate(false);
    }
  };

  const handleSendTest = async () => {
    if (!subject || !body) {
      setError('Please generate an email first');
      return;
    }

    if (!emailProviderConfigured) {
      setError('Please configure email provider in Settings first');
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

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
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
    </div>
  );
}
