import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Plus,
  Edit2,
  Trash2,
  Clock,
  Bot,
  Sparkles,
  Info,
  CheckCircle,
  AlertCircle,
  Save,
  X,
  Users
} from 'lucide-react';
import { getCampaign, getCampaignLeads } from '../api/campaigns';
import { getSequenceSteps, createSequenceStep, updateSequenceStep, deleteSequenceStep } from '../api/sequenceSteps';

import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import ConfirmDialog from '../components/ui/ConfirmDialog';
import { Card, CardHeader, CardTitle, CardContent, CardFooter, CardDescription } from '../components/ui/Card';
import { SkeletonCard } from '../components/ui/Skeleton';
import Badge from '../components/ui/Badge';
import { Alert, AlertDescription } from '../components/ui/Alert';
import EmptyState from '../components/ui/EmptyState';
import { useToast } from '../context/ToastContext';

const AI_TONE_OPTIONS = [
  { value: 'professional', label: 'Professional' },
  { value: 'friendly', label: 'Friendly' },
  { value: 'casual', label: 'Casual' },
  { value: 'aggressive', label: 'Aggressive' },
];

const STEP_FORM_DEFAULT = {
  step_index: 1,
  subject_template: '',
  body_template: '',
  delay_days: 0,
  use_ai_generation: false,
  ai_tone: 'professional',
  ai_goal: 'schedule a meeting',
  product_description: '',
};

function CampaignEditor() {
  const { campaignId } = useParams();
  const navigate = useNavigate();
  const toast = useToast();

  const [campaign, setCampaign] = useState(null);
  const [steps, setSteps] = useState([]);
  const [enrolledLeads, setEnrolledLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [editingStep, setEditingStep] = useState(null);
  const [stepForm, setStepForm] = useState(STEP_FORM_DEFAULT);
  const [deleteStepId, setDeleteStepId] = useState(null);

  /* ─── Data fetch ────────────────────────────────────────────── */
  const fetchCampaignData = useCallback(async () => {
    try {
      setLoading(true);
      const [campaignData, stepsData, leadsData] = await Promise.all([
        getCampaign(campaignId),
        getSequenceSteps(campaignId),
        getCampaignLeads(campaignId),
      ]);
      setCampaign(campaignData);
      setSteps(stepsData.sort((a, b) => a.step_index - b.step_index));
      setEnrolledLeads(leadsData);
      setError(null);
    } catch {
      setError('Failed to load campaign');
    } finally {
      setLoading(false);
    }
  }, [campaignId]);

  useEffect(() => {
    fetchCampaignData();
  }, [fetchCampaignData]);

  /* ─── Step handlers ─────────────────────────────────────────── */
  const handleSaveStep = async (e) => {
    e.preventDefault();
    if (!stepForm.subject_template.trim() || !stepForm.body_template.trim()) {
      toast.error('Subject and body templates are required');
      return;
    }
    try {
      if (editingStep) {
        await updateSequenceStep(editingStep.id, stepForm);
        toast.success('Step updated successfully');
      } else {
        await createSequenceStep({ ...stepForm, campaign_id: campaignId });
        toast.success('Step created successfully');
      }
      setEditingStep(null);
      setStepForm({ ...STEP_FORM_DEFAULT, step_index: steps.length + 1 });
      await fetchCampaignData();
    } catch {
      toast.error('Failed to save step');
    }
  };

  const handleEditStep = (step) => {
    setEditingStep(step);
    setStepForm({
      step_index: step.step_index,
      subject_template: step.subject_template,
      body_template: step.body_template,
      delay_days: step.delay_days,
      use_ai_generation: step.use_ai_generation || false,
      ai_tone: step.ai_tone || 'professional',
      ai_goal: step.ai_goal || 'schedule a meeting',
      product_description: step.product_description || '',
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleConfirmDelete = async () => {
    try {
      await deleteSequenceStep(deleteStepId);
      await fetchCampaignData();
      toast.success('Step deleted');
    } catch {
      toast.error('Failed to delete step');
    } finally {
      setDeleteStepId(null);
    }
  };

  const handleCancelEdit = () => {
    setEditingStep(null);
    setStepForm({ ...STEP_FORM_DEFAULT, step_index: steps.length + 1 });
  };

  const getStatusVariant = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'paused': return 'warning';
      case 'completed': return 'default';
      default: return 'secondary';
    }
  };

  /* ─── Loading skeleton ──────────────────────────────────────── */
  if (loading) {
    return (
      <div className="p-6 space-y-5 max-w-[1400px] mx-auto">
        <div className="h-6 w-24 bg-ink-100 rounded animate-pulse" />
        <div className="h-8 w-64 bg-ink-100 rounded animate-pulse" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-4">
            {[1, 2, 3].map((i) => <SkeletonCard key={i} />)}
          </div>
          <SkeletonCard />
        </div>
      </div>
    );
  }

  if (error || !campaign) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertCircle className="w-4 h-4" />
          <AlertDescription>{error || 'Campaign not found'}</AlertDescription>
        </Alert>
      </div>
    );
  }

  /* ─── Render ────────────────────────────────────────────────── */
  return (
    <div className="p-6 space-y-5 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="space-y-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/campaigns')}
          icon={<ArrowLeft className="w-3.5 h-3.5" />}
          className="text-ink-500 hover:text-ink-800 pl-0"
        >
          Campaigns
        </Button>

        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div>
            <h1 className="page-title">{campaign.name}</h1>
            <p className="page-subtitle mt-0.5">{campaign.description}</p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <span className="text-sm font-medium text-ink-500">Status:</span>
            <Badge variant={getStatusVariant(campaign.status)} className="capitalize">
              {campaign.status}
            </Badge>
          </div>
        </div>

        <div className="flex items-start gap-3 px-4 py-3 bg-brand-50 border border-brand-100 rounded-xl text-sm">
          <Info className="w-4 h-4 text-brand-600 mt-0.5 shrink-0" />
          <p className="text-ink-600">
            <strong className="text-ink-800">Template Variables:</strong>{' '}
            Use{' '}
            {['{{first_name}}', '{{last_name}}', '{{company}}', '{{title}}', '{{email}}', '{{phone}}']
              .map((v, i) => (
                <code key={i} className="bg-brand-100 text-brand-700 px-1 py-0.5 rounded text-xs mx-0.5 font-mono">
                  {v}
                </code>
              ))}
            {' '}in your templates.
          </p>
        </div>
      </div>

      {/* Steps + Form grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Sequence steps list */}
        <div className="space-y-4">
          <h2 className="text-base font-semibold text-ink-900">
            Sequence Steps{' '}
            <span className="text-ink-400 font-normal">({steps.length})</span>
          </h2>

          {steps.length === 0 ? (
            <EmptyState
              icon={Plus}
              title="No steps yet"
              description="Add your first step to start building your email sequence."
            />
          ) : (
            <div className="space-y-3">
              {steps.map((step) => (
                <Card
                  key={step.id}
                  className={`transition-all ${
                    editingStep?.id === step.id ? 'ring-2 ring-brand-500' : ''
                  }`}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant="secondary">Step {step.step_index}</Badge>
                        {step.delay_days > 0 && (
                          <span className="text-xs text-ink-400 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            Wait {step.delay_days} day{step.delay_days !== 1 ? 's' : ''}
                          </span>
                        )}
                        {step.use_ai_generation && (
                          <Badge variant="outline" className="text-purple-600 border-purple-200 bg-purple-50 text-xs">
                            <Sparkles className="w-3 h-3 mr-1" />
                            AI Personalized
                          </Badge>
                        )}
                      </div>
                      <div className="flex gap-1 shrink-0">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEditStep(step)}
                          icon={<Edit2 className="w-4 h-4" />}
                          className="h-8 w-8 p-0 text-ink-400 hover:text-ink-700"
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDeleteStepId(step.id)}
                          icon={<Trash2 className="w-4 h-4" />}
                          className="h-8 w-8 p-0 text-danger/60 hover:text-danger hover:bg-danger/10"
                        />
                      </div>
                    </div>
                    <div className="space-y-1.5">
                      <p className="text-sm font-medium text-ink-900 truncate">
                        {step.subject_template}
                      </p>
                      <p className="text-sm text-ink-500 line-clamp-2 bg-ink-50 px-3 py-2 rounded-lg border border-ink-100 font-mono text-xs leading-relaxed">
                        {step.body_template}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Add / Edit step form */}
        <div className="space-y-4">
          <h2 className="text-base font-semibold text-ink-900">
            {editingStep ? 'Edit Step' : 'Add New Step'}
          </h2>

          <Card>
            <form onSubmit={handleSaveStep}>
              <CardContent className="space-y-4 pt-6">
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="Step Number"
                    type="number"
                    min="1"
                    value={stepForm.step_index}
                    onChange={(e) =>
                      setStepForm({ ...stepForm, step_index: parseInt(e.target.value) })
                    }
                    required
                  />
                  <Input
                    label="Delay (days)"
                    type="number"
                    min="0"
                    value={stepForm.delay_days}
                    onChange={(e) =>
                      setStepForm({ ...stepForm, delay_days: parseInt(e.target.value) })
                    }
                    required
                    helperText="Days after previous step (0 = immediate)"
                  />
                </div>

                {/* AI Personalization toggle */}
                <div className="border border-ink-100 rounded-xl p-4 bg-ink-50 space-y-4">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      id="use_ai_generation"
                      className="w-4 h-4 text-brand-600 rounded focus:ring-brand-500 border-ink-300"
                      checked={stepForm.use_ai_generation}
                      onChange={(e) =>
                        setStepForm({ ...stepForm, use_ai_generation: e.target.checked })
                      }
                    />
                    <span className="text-sm font-medium text-ink-900 flex items-center gap-2">
                      <Bot className="w-4 h-4 text-purple-600" />
                      Use AI Personalization
                    </span>
                  </label>

                  {stepForm.use_ai_generation && (
                    <div className="space-y-4 pl-7 border-l-2 border-purple-200">
                      <Select
                        label="Email Tone"
                        value={stepForm.ai_tone}
                        onChange={(e) => setStepForm({ ...stepForm, ai_tone: e.target.value })}
                        options={AI_TONE_OPTIONS}
                        required
                      />
                      <Input
                        label="Email Goal"
                        placeholder="e.g., schedule a meeting"
                        value={stepForm.ai_goal}
                        onChange={(e) => setStepForm({ ...stepForm, ai_goal: e.target.value })}
                        required
                      />
                      <div>
                        <label className="block text-xs font-medium text-ink-600 mb-1.5">
                          Product / Service Description
                        </label>
                        <textarea
                          rows="3"
                          className="w-full px-3 py-2.5 bg-surface border border-ink-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500 text-sm text-ink-900 placeholder-ink-400 transition-colors resize-none"
                          placeholder="Describe your offer for AI context..."
                          value={stepForm.product_description}
                          onChange={(e) =>
                            setStepForm({ ...stepForm, product_description: e.target.value })
                          }
                          required
                        />
                      </div>
                    </div>
                  )}
                </div>

                <Input
                  label={
                    stepForm.use_ai_generation
                      ? 'Subject Template (fallback)'
                      : 'Subject Template'
                  }
                  placeholder="Hi {{first_name}}, quick question…"
                  value={stepForm.subject_template}
                  onChange={(e) =>
                    setStepForm({ ...stepForm, subject_template: e.target.value })
                  }
                  required
                />

                <div>
                  <label className="block text-xs font-medium text-ink-600 mb-1.5">
                    {stepForm.use_ai_generation ? 'Body Template (fallback)' : 'Body Template'}
                  </label>
                  <textarea
                    rows="7"
                    className="w-full px-3 py-2.5 bg-surface border border-ink-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500 text-sm text-ink-900 placeholder-ink-400 font-mono leading-relaxed transition-colors resize-none"
                    placeholder={`Hi {{first_name}},\n\nI noticed you work at {{company}}...\n\nBest regards`}
                    value={stepForm.body_template}
                    onChange={(e) =>
                      setStepForm({ ...stepForm, body_template: e.target.value })
                    }
                    required
                  />
                </div>
              </CardContent>

              <CardFooter className="flex gap-2 bg-ink-50 border-t border-ink-100">
                <Button type="submit" className="flex-1" icon={<Save className="w-4 h-4" />}>
                  {editingStep ? 'Update Step' : 'Add Step'}
                </Button>
                {editingStep && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleCancelEdit}
                    icon={<X className="w-4 h-4" />}
                  >
                    Cancel
                  </Button>
                )}
              </CardFooter>
            </form>
          </Card>
        </div>
      </div>

      {/* Enrolled Leads */}
      <div className="space-y-4">
        <h2 className="text-base font-semibold text-ink-900">
          Enrolled Leads{' '}
          <span className="text-ink-400 font-normal">({enrolledLeads.length})</span>
        </h2>

        <Card>
          <CardContent className="p-0">
            {enrolledLeads.length === 0 ? (
              <div className="p-10 text-center">
                <EmptyState
                  icon={Users}
                  title="No leads enrolled"
                  description="Go to the Leads page to add leads to this campaign."
                />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Lead</th>
                      <th>Company</th>
                      <th>Status</th>
                      <th>Current Step</th>
                      <th>Last Sent</th>
                    </tr>
                  </thead>
                  <tbody>
                    {enrolledLeads.map((lead) => (
                      <tr key={lead.id}>
                        <td>
                          <div className="font-medium text-ink-900">
                            {lead.first_name} {lead.last_name}
                          </div>
                          <div className="text-ink-400 text-xs">{lead.email}</div>
                        </td>
                        <td>
                          <div className="text-ink-900">{lead.company || '—'}</div>
                          <div className="text-ink-400 text-xs">{lead.title || '—'}</div>
                        </td>
                        <td>
                          <Badge
                            variant={
                              lead.status === 'completed'
                                ? 'success'
                                : lead.status === 'in_progress'
                                ? 'default'
                                : lead.status === 'stopped'
                                ? 'destructive'
                                : 'secondary'
                            }
                            className="capitalize"
                          >
                            {lead.status.replace('_', ' ')}
                          </Badge>
                        </td>
                        <td className="text-ink-600">
                          {lead.last_step_index > 0 ? `Step ${lead.last_step_index}` : 'Not started'}
                        </td>
                        <td className="text-ink-500 text-sm">
                          {lead.last_sent_at
                            ? new Date(lead.last_sent_at).toLocaleDateString()
                            : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Confirm delete step */}
      <ConfirmDialog
        isOpen={!!deleteStepId}
        onClose={() => setDeleteStepId(null)}
        onConfirm={handleConfirmDelete}
        title="Delete Step"
        description="Are you sure you want to delete this step? This action cannot be undone."
        confirmLabel="Delete Step"
        variant="destructive"
      />
    </div>
  );
}

export default CampaignEditor;
