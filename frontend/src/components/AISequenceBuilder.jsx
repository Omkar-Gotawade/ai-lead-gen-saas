import React, { useState, useEffect } from 'react';
import { X, Sparkles, Bot, AlertCircle } from 'lucide-react';
import Button from './ui/Button';
import Input from './ui/Input';
import Select from './ui/Select';
import { generateAISequence } from '../api/campaigns';
import { useToast } from '../context/ToastContext';

const AI_TONE_OPTIONS = [
  { value: 'Founder style', label: 'Founder style (direct, casual)' },
  { value: 'Professional', label: 'Professional (standard B2B)' },
  { value: 'Casual', label: 'Casual (friendly, relaxed)' },
  { value: 'Direct', label: 'Direct (to the point, no fluff)' },
];

const CAMPAIGN_GOAL_OPTIONS = [
  { value: 'Book a meeting', label: 'Book a meeting' },
  { value: 'Schedule demo', label: 'Schedule demo' },
  { value: 'Get a reply', label: 'Get a reply' },
  { value: 'Partnership', label: 'Partnership' },
  { value: 'Recruitment outreach', label: 'Recruitment outreach' },
  { value: 'Custom', label: 'Custom' },
];

function AISequenceBuilder({ isOpen, onClose, onSuccess }) {
  const toast = useToast();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    product_name: '',
    product_description: '',
    target_audience: '',
    campaign_goal: 'Book a meeting',
    tone: 'Founder style',
    number_of_steps: 3,
    campaign_name: ''
  });

  // Auto-suggest campaign name when product or goal changes
  useEffect(() => {
    if (!formData.campaign_name && formData.product_name) {
      setFormData(prev => ({
        ...prev,
        campaign_name: `${prev.product_name} - ${prev.campaign_goal}`
      }));
    }
  }, [formData.product_name, formData.campaign_goal]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await generateAISequence(formData);
      toast.success('AI Sequence generated successfully!');
      onSuccess(response.campaign_id);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate sequence. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm p-4 sm:p-6 animate-in fade-in duration-200">
      <div 
        className="bg-canvas border border-brand-500/30 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] animate-in slide-in-from-bottom-8 sm:slide-in-from-bottom-4 duration-300"
        style={{ boxShadow: '0 0 40px rgba(245, 158, 11, 0.1)' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-surface relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-amber-500/10 to-transparent pointer-events-none" />
          <div className="flex items-center gap-3 relative z-10">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-500">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-ink-900">AI SDR Campaign Builder</h2>
              <p className="text-sm text-ink-500">Describe your offer, AI writes the sequence.</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            disabled={loading}
            className="p-2 text-ink-400 hover:text-ink-600 rounded-lg hover:bg-ink-100 transition-colors z-10"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto p-6 scrollbar-thin">
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-danger/10 border border-danger/20 flex items-start gap-3 text-danger">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          <form id="ai-builder-form" onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <Input
                label="Product / Service Name"
                placeholder="e.g. Prosario"
                value={formData.product_name}
                onChange={(e) => setFormData({ ...formData, product_name: e.target.value })}
                required
                disabled={loading}
              />
              <Input
                label="Target Audience"
                placeholder="e.g. SaaS Founders"
                value={formData.target_audience}
                onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
                required
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-ink-300 mb-1.5">
                Product Description <span className="text-danger">*</span>
              </label>
              <textarea
                className="w-full px-4 py-3 bg-surface border border-ink-200 text-ink-900 placeholder-ink-400 rounded-xl transition-colors resize-none focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500/50"
                rows="3"
                placeholder="What exactly do you do? e.g. We help B2B companies automate cold outreach with AI agents."
                value={formData.product_description}
                onChange={(e) => setFormData({ ...formData, product_description: e.target.value })}
                required
                disabled={loading}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <Select
                label="Campaign Goal"
                options={CAMPAIGN_GOAL_OPTIONS}
                value={formData.campaign_goal}
                onChange={(e) => setFormData({ ...formData, campaign_goal: e.target.value })}
                required
                disabled={loading}
              />
              <Select
                label="Tone"
                options={AI_TONE_OPTIONS}
                value={formData.tone}
                onChange={(e) => setFormData({ ...formData, tone: e.target.value })}
                required
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-ink-300 mb-2">
                Number of Sequence Steps
              </label>
              <div className="flex gap-3">
                {[1, 2, 3, 4, 5].map(num => (
                  <button
                    key={num}
                    type="button"
                    disabled={loading}
                    onClick={() => setFormData({ ...formData, number_of_steps: num })}
                    className={`flex-1 py-2 rounded-lg font-medium transition-colors border ${
                      formData.number_of_steps === num
                        ? 'bg-amber-500/10 border-amber-500 text-amber-700'
                        : 'bg-surface border-ink-200 text-ink-600 hover:bg-ink-50'
                    }`}
                  >
                    {num} {num === 1 ? 'Step' : 'Steps'}
                  </button>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-white/5">
              <Input
                label="Campaign Name"
                placeholder="Name for this new campaign"
                value={formData.campaign_name}
                onChange={(e) => setFormData({ ...formData, campaign_name: e.target.value })}
                required
                disabled={loading}
              />
            </div>
          </form>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-white/5 bg-surface flex items-center justify-between">
          <p className="text-xs text-ink-500 flex items-center gap-1.5">
            <Bot className="w-4 h-4" />
            AI writes the sequence, you review before sending.
          </p>
          <div className="flex gap-3">
            <Button variant="ghost" onClick={onClose} disabled={loading}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              form="ai-builder-form" 
              disabled={loading}
              className="bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-white border-none shadow-[0_0_15px_rgba(245,158,11,0.3)]"
            >
              {loading ? (
                <>
                  <Sparkles className="w-4 h-4 mr-2 animate-pulse" />
                  Writing Sequence...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Generate AI Sequence
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AISequenceBuilder;
