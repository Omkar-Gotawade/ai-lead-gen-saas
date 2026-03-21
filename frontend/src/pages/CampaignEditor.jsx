import React, { useState, useEffect } from 'react';
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
  Play,
  Pause,
  Save,
  X
} from 'lucide-react';
import { getCampaign, getCampaignLeads } from '../api/campaigns';
import { getSequenceSteps, createSequenceStep, updateSequenceStep, deleteSequenceStep } from '../api/sequenceSteps';

import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent, CardFooter, CardDescription } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { Alert, AlertDescription } from '../components/ui/Alert';
import LoadingSpinner from '../components/ui/LoadingSpinner';

function CampaignEditor() {
  const { campaignId } = useParams();
  const navigate = useNavigate();
  
  const [campaign, setCampaign] = useState(null);
  const [steps, setSteps] = useState([]);
  const [enrolledLeads, setEnrolledLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  
  // Form state for adding/editing steps
  const [editingStep, setEditingStep] = useState(null);
  const [stepForm, setStepForm] = useState({
    step_index: 1,
    subject_template: '',
    body_template: '',
    delay_days: 0,
    use_ai_generation: false,
    ai_tone: 'professional',
    ai_goal: 'schedule a meeting',
    product_description: ''
  });

  useEffect(() => {
    fetchCampaignData();
  }, [campaignId]);

  const fetchCampaignData = async () => {
    try {
      setLoading(true);
      const [campaignData, stepsData, leadsData] = await Promise.all([
        getCampaign(campaignId),
        getSequenceSteps(campaignId),
        getCampaignLeads(campaignId)
      ]);
      
      setCampaign(campaignData);
      setSteps(stepsData.sort((a, b) => a.step_index - b.step_index));
      setEnrolledLeads(leadsData);
      setError(null);
    } catch (err) {
      console.error('Error fetching campaign data:', err);
      setError('Failed to load campaign');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveStep = async (e) => {
    e.preventDefault();
    setMessage(null);

    if (!stepForm.subject_template.trim() || !stepForm.body_template.trim()) {
      setMessage({ type: 'error', text: 'Subject and body templates are required' });
      return;
    }

    try {
      if (editingStep) {
        // Update existing step
        await updateSequenceStep(editingStep.id, stepForm);
        setMessage({ type: 'success', text: 'Step updated successfully' });
      } else {
        // Create new step
        await createSequenceStep({
          ...stepForm,
          campaign_id: campaignId
        });
        setMessage({ type: 'success', text: 'Step created successfully' });
      }
      
      // Reset form and refresh
      setEditingStep(null);
      setStepForm({
        step_index: steps.length + 1,
        subject_template: '',
        body_template: '',
        delay_days: 0,
        use_ai_generation: false,
        ai_tone: 'professional',
        ai_goal: 'schedule a meeting',
        product_description: ''
      });
      await fetchCampaignData();
    } catch (err) {
      console.error('Error saving step:', err);
      setMessage({ type: 'error', text: 'Failed to save step' });
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
      product_description: step.product_description || ''
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDeleteStep = async (stepId) => {
    if (!window.confirm('Are you sure you want to delete this step?')) {
      return;
    }

    try {
      await deleteSequenceStep(stepId);
      await fetchCampaignData();
      setMessage({ type: 'success', text: 'Step deleted successfully' });
    } catch (err) {
      console.error('Error deleting step:', err);
      setMessage({ type: 'error', text: 'Failed to delete step' });
    }
  };

  const handleCancelEdit = () => {
    setEditingStep(null);
    setStepForm({
      step_index: steps.length + 1,
      subject_template: '',
      body_template: '',
      delay_days: 0,
      use_ai_generation: false,
      ai_tone: 'professional',
      ai_goal: 'schedule a meeting',
      product_description: ''
    });
  };

  const getStatusVariant = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'paused': return 'warning';
      case 'completed': return 'default';
      default: return 'secondary';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !campaign) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error || 'Campaign not found'}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="p-6 space-y-5 max-w-[1400px] mx-auto">
      {/* Campaign Header */}
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
          
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-slate-600">Status:</span>
            <Badge variant={getStatusVariant(campaign.status)} className="capitalize">
              {campaign.status}
            </Badge>
          </div>
        </div>
          
        <Alert className="bg-blue-50 border-blue-200 text-blue-800">
          <Info className="w-4 h-4 text-blue-600" />
          <AlertDescription>
            <strong>Template Variables:</strong> Use {`{{first_name}}`}, {`{{last_name}}`}, {`{{company}}`}, {`{{title}}`}, {`{{email}}`}, {`{{phone}}`} in your templates
          </AlertDescription>
        </Alert>
      </div>

      {message && (
        <Alert variant={message.type === 'error' ? 'destructive' : 'default'}>
          {message.type === 'success' ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}

      {/* Sequence Steps Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Sequence Steps List */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-slate-900">Sequence Steps ({steps.length})</h2>
          
          {steps.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center text-slate-500">
                No steps yet. Add your first step to start building your sequence.
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {steps.map((step) => (
                <Card key={step.id} className={`transition-all ${editingStep?.id === step.id ? 'ring-2 ring-blue-500' : ''}`}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary">Step {step.step_index}</Badge>
                        {step.delay_days > 0 && (
                          <span className="text-xs text-slate-500 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            Wait {step.delay_days} day{step.delay_days !== 1 ? 's' : ''}
                          </span>
                        )}
                        {step.use_ai_generation && (
                          <Badge variant="outline" className="text-purple-600 border-purple-200 bg-purple-50">
                            <Sparkles className="w-3 h-3 mr-1" />
                            AI Personalized
                          </Badge>
                        )}
                      </div>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEditStep(step)}
                          icon={<Edit2 className="w-4 h-4" />}
                          className="h-8 w-8 p-0"
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteStep(step.id)}
                          icon={<Trash2 className="w-4 h-4" />}
                          className="h-8 w-8 p-0 text-red-500 hover:text-red-600 hover:bg-red-50"
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <p className="font-medium text-slate-900 text-sm">
                        Subject: {step.subject_template}
                      </p>
                      <p className="text-slate-600 text-sm line-clamp-2 bg-slate-50 p-2 rounded border border-slate-100">
                        {step.body_template}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Add/Edit Step Form */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-slate-900">
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
                    onChange={(e) => setStepForm({ ...stepForm, step_index: parseInt(e.target.value) })}
                    required
                  />
                  <Input
                    label="Delay (days)"
                    type="number"
                    min="0"
                    value={stepForm.delay_days}
                    onChange={(e) => setStepForm({ ...stepForm, delay_days: parseInt(e.target.value) })}
                    required
                    helperText="Days after previous step (0 for immediate)"
                  />
                </div>

                {/* AI Personalization Toggle */}
                <div className="border rounded-lg p-4 bg-slate-50 space-y-4">
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      id="use_ai_generation"
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500 border-gray-300"
                      checked={stepForm.use_ai_generation}
                      onChange={(e) => setStepForm({ ...stepForm, use_ai_generation: e.target.checked })}
                    />
                    <label htmlFor="use_ai_generation" className="text-sm font-medium text-slate-900 flex items-center gap-2">
                      <Bot className="w-4 h-4 text-purple-600" />
                      Use AI Personalization
                    </label>
                  </div>
                  
                  {stepForm.use_ai_generation && (
                    <div className="space-y-4 pl-7 border-l-2 border-purple-200">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                          Email Tone
                        </label>
                        <select
                          className="w-full px-3 py-2 bg-white border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                          value={stepForm.ai_tone}
                          onChange={(e) => setStepForm({ ...stepForm, ai_tone: e.target.value })}
                          required={stepForm.use_ai_generation}
                        >
                          <option value="professional">Professional</option>
                          <option value="friendly">Friendly</option>
                          <option value="casual">Casual</option>
                          <option value="aggressive">Aggressive</option>
                        </select>
                      </div>

                      <Input
                        label="Email Goal"
                        placeholder="e.g., schedule a meeting"
                        value={stepForm.ai_goal}
                        onChange={(e) => setStepForm({ ...stepForm, ai_goal: e.target.value })}
                        required={stepForm.use_ai_generation}
                      />

                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                          Product/Service Description
                        </label>
                        <textarea
                          rows="3"
                          className="w-full px-3 py-2 bg-white border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                          placeholder="Describe your offer for AI context..."
                          value={stepForm.product_description}
                          onChange={(e) => setStepForm({ ...stepForm, product_description: e.target.value })}
                          required={stepForm.use_ai_generation}
                        />
                      </div>
                    </div>
                  )}
                </div>

                <Input
                  label={
                    <span className="flex items-center gap-2">
                      Subject Template
                      {!stepForm.use_ai_generation && <span className="text-xs font-normal text-slate-500">(Fallback)</span>}
                    </span>
                  }
                  placeholder="e.g., Hi {{first_name}}, quick question"
                  value={stepForm.subject_template}
                  onChange={(e) => setStepForm({ ...stepForm, subject_template: e.target.value })}
                  required
                />

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    <span className="flex items-center gap-2">
                      Body Template
                      {!stepForm.use_ai_generation && <span className="text-xs font-normal text-slate-500">(Fallback)</span>}
                    </span>
                  </label>
                  <textarea
                    rows="6"
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-mono"
                    placeholder={`Hi {{first_name}},\n\nI noticed you work at {{company}}...\n\nBest regards`}
                    value={stepForm.body_template}
                    onChange={(e) => setStepForm({ ...stepForm, body_template: e.target.value })}
                    required
                  />
                </div>
              </CardContent>
              <CardFooter className="flex gap-2 bg-slate-50 border-t border-slate-100">
                <Button
                  type="submit"
                  className="flex-1"
                  icon={<Save className="w-4 h-4" />}
                >
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

      {/* Enrolled Leads Section */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-slate-900">Enrolled Leads ({enrolledLeads.length})</h2>
        
        <Card>
          <CardContent className="p-0">
            {enrolledLeads.length === 0 ? (
              <div className="p-8 text-center text-slate-500">
                No leads enrolled yet. Go to Leads page to add leads to this campaign.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
                    <tr>
                      <th className="px-6 py-4 font-medium">Lead</th>
                      <th className="px-6 py-4 font-medium">Company</th>
                      <th className="px-6 py-4 font-medium">Status</th>
                      <th className="px-6 py-4 font-medium">Current Step</th>
                      <th className="px-6 py-4 font-medium">Last Sent</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {enrolledLeads.map((lead) => (
                      <tr key={lead.id} className="bg-white hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="font-medium text-slate-900">
                            {lead.first_name} {lead.last_name}
                          </div>
                          <div className="text-slate-500 text-xs">{lead.email}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-slate-900">{lead.company || '-'}</div>
                          <div className="text-slate-500 text-xs">{lead.title || '-'}</div>
                        </td>
                        <td className="px-6 py-4">
                          <Badge variant={
                            lead.status === 'completed' ? 'success' :
                            lead.status === 'in_progress' ? 'default' :
                            lead.status === 'stopped' ? 'destructive' : 'secondary'
                          } className="capitalize">
                            {lead.status.replace('_', ' ')}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 text-slate-600">
                          {lead.last_step_index > 0 ? `Step ${lead.last_step_index}` : 'Not started'}
                        </td>
                        <td className="px-6 py-4 text-slate-600">
                          {lead.last_sent_at ? new Date(lead.last_sent_at).toLocaleDateString() : '-'}
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
    </div>
  );
}

export default CampaignEditor;
