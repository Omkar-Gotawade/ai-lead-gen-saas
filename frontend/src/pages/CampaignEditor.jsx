import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getCampaign, getCampaignLeads } from '../api/campaigns';
import { getSequenceSteps, createSequenceStep, updateSequenceStep, deleteSequenceStep } from '../api/sequenceSteps';

function CampaignEditor() {
  const { campaignId } = useParams();
  const navigate = useNavigate();
  
  const [campaign, setCampaign] = useState(null);
  const [steps, setSteps] = useState([]);
  const [enrolledLeads, setEnrolledLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
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

    if (!stepForm.subject_template.trim() || !stepForm.body_template.trim()) {
      alert('Subject and body templates are required');
      return;
    }

    try {
      if (editingStep) {
        // Update existing step
        await updateSequenceStep(editingStep.id, stepForm);
        alert('Step updated successfully');
      } else {
        // Create new step
        await createSequenceStep({
          ...stepForm,
          campaign_id: campaignId
        });
        alert('Step created successfully');
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
      alert('Failed to save step');
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
  };

  const handleDeleteStep = async (stepId) => {
    if (!confirm('Are you sure you want to delete this step?')) {
      return;
    }

    try {
      await deleteSequenceStep(stepId);
      await fetchCampaignData();
      alert('Step deleted successfully');
    } catch (err) {
      console.error('Error deleting step:', err);
      alert('Failed to delete step');
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

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="mt-2 text-gray-600">Loading campaign...</p>
      </div>
    );
  }

  if (error || !campaign) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
        {error || 'Campaign not found'}
      </div>
    );
  }

  return (
    <div className="px-4 py-8">
      {/* Campaign Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/campaigns')}
          className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
        >
          <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Campaigns
        </button>

        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">{campaign.name}</h1>
            <p className="text-gray-600 mt-1">{campaign.description}</p>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-600">Status:</span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              campaign.status === 'active' ? 'bg-green-100 text-green-800' :
              campaign.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
            </span>
          </div>
        </div>
          
        <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-3 rounded">
          <p className="text-sm">
            <strong>Template Variables:</strong> Use {`{{first_name}}`}, {`{{last_name}}`}, {`{{company}}`}, {`{{title}}`}, {`{{email}}`}, {`{{phone}}`} in your templates
          </p>
        </div>
      </div>

      {/* Sequence Steps Section */}
      <div className="mb-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Sequence Steps List */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Sequence Steps ({steps.length})</h2>
            
            {steps.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-8 text-center">
                <p className="text-gray-600">No steps yet. Add your first step to start building your sequence.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {steps.map((step, index) => (
                  <div key={step.id} className="bg-white rounded-lg shadow p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center">
                        <span className="bg-blue-100 text-blue-800 font-semibold px-2 py-1 rounded text-sm mr-2">
                          Step {step.step_index}
                        </span>
                        {step.delay_days > 0 && (
                          <span className="text-gray-600 text-sm">
                            (Wait {step.delay_days} day{step.delay_days !== 1 ? 's' : ''})
                          </span>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleEditStep(step)}
                          className="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteStep(step.id)}
                          className="text-red-600 hover:text-red-800 text-sm"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                    <div className="text-sm">
                      <p className="font-medium text-gray-900 mb-1">
                        {step.subject_template}
                      </p>
                      <p className="text-gray-600 line-clamp-2">
                        {step.body_template}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Add/Edit Step Form */}
          <div>
            <h2 className="text-xl font-semibold mb-4">
              {editingStep ? 'Edit Step' : 'Add New Step'}
            </h2>
            
            <form onSubmit={handleSaveStep} className="bg-white rounded-lg shadow p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Step Number
                </label>
                <input
                  type="number"
                  min="1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={stepForm.step_index}
                  onChange={(e) => setStepForm({ ...stepForm, step_index: parseInt(e.target.value) })}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Delay (days after previous step)
                </label>
                <input
                  type="number"
                  min="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={stepForm.delay_days}
                  onChange={(e) => setStepForm({ ...stepForm, delay_days: parseInt(e.target.value) })}
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Set to 0 for immediate sending (first step)
                </p>
              </div>

              {/* AI Personalization Toggle */}
              <div className="border-t border-gray-200 pt-4">
                <div className="flex items-center gap-3 mb-4">
                  <input
                    type="checkbox"
                    id="use_ai_generation"
                    className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    checked={stepForm.use_ai_generation}
                    onChange={(e) => setStepForm({ ...stepForm, use_ai_generation: e.target.checked })}
                  />
                  <label htmlFor="use_ai_generation" className="text-sm font-medium text-gray-700">
                    🤖 Use AI Personalization (Each lead gets a unique email)
                  </label>
                </div>
                
                {stepForm.use_ai_generation && (
                  <div className="space-y-4 pl-7 border-l-2 border-blue-200">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Email Tone *
                      </label>
                      <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Email Goal *
                      </label>
                      <input
                        type="text"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., schedule a meeting, book a demo, get a reply"
                        value={stepForm.ai_goal}
                        onChange={(e) => setStepForm({ ...stepForm, ai_goal: e.target.value })}
                        required={stepForm.use_ai_generation}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Product/Service Description *
                      </label>
                      <textarea
                        rows="4"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Describe what you're offering. AI will use this to personalize emails for each lead based on their profile (name, title, company, industry, etc.)"
                        value={stepForm.product_description}
                        onChange={(e) => setStepForm({ ...stepForm, product_description: e.target.value })}
                        required={stepForm.use_ai_generation}
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        💡 AI will automatically personalize emails using lead data (name, title, company, industry, LinkedIn info)
                      </p>
                    </div>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subject Template * {!stepForm.use_ai_generation && <span className="text-xs text-gray-500">(Used as fallback if AI disabled)</span>}
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Hi {{first_name}}, quick question"
                  value={stepForm.subject_template}
                  onChange={(e) => setStepForm({ ...stepForm, subject_template: e.target.value })}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Body Template * {!stepForm.use_ai_generation && <span className="text-xs text-gray-500">(Used as fallback if AI disabled)</span>}
                </label>
                <textarea
                  rows="8"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder={`Hi {{first_name}},\n\nI noticed you work at {{company}}...\n\nBest regards`}
                  value={stepForm.body_template}
                  onChange={(e) => setStepForm({ ...stepForm, body_template: e.target.value })}
                  required
                />
              </div>

              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  {editingStep ? 'Update Step' : 'Add Step'}
                </button>
                {editingStep && (
                  <button
                    type="button"
                    onClick={handleCancelEdit}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* Enrolled Leads Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Enrolled Leads ({enrolledLeads.length})</h2>
        
        {enrolledLeads.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600">No leads enrolled yet. Go to Leads page to add leads to this campaign.</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Lead
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Current Step
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Sent
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {enrolledLeads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {lead.first_name} {lead.last_name}
                        </div>
                        <div className="text-sm text-gray-500">{lead.email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{lead.company || '-'}</div>
                        <div className="text-sm text-gray-500">{lead.title || '-'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          lead.status === 'completed' ? 'bg-green-100 text-green-800' :
                          lead.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                          lead.status === 'stopped' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {lead.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {lead.last_step_index > 0 ? `Step ${lead.last_step_index}` : 'Not started'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {lead.last_sent_at ? new Date(lead.last_sent_at).toLocaleDateString() : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CampaignEditor;
