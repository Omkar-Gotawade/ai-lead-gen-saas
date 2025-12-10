import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getCampaign, updateCampaign } from '../api/campaigns';
import { getSequenceSteps, createSequenceStep, updateSequenceStep, deleteSequenceStep } from '../api/sequenceSteps';

function CampaignEditor() {
  const { campaignId } = useParams();
  const navigate = useNavigate();
  
  const [campaign, setCampaign] = useState(null);
  const [steps, setSteps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Form state for adding/editing steps
  const [editingStep, setEditingStep] = useState(null);
  const [stepForm, setStepForm] = useState({
    step_index: 1,
    subject_template: '',
    body_template: '',
    delay_days: 0
  });

  useEffect(() => {
    fetchCampaignData();
  }, [campaignId]);

  const fetchCampaignData = async () => {
    try {
      setLoading(true);
      const [campaignData, stepsData] = await Promise.all([
        getCampaign(campaignId),
        getSequenceSteps(campaignId)
      ]);
      
      setCampaign(campaignData);
      setSteps(stepsData.sort((a, b) => a.step_index - b.step_index));
      setError(null);
    } catch (err) {
      console.error('Error fetching campaign data:', err);
      setError('Failed to load campaign');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateCampaignStatus = async (newStatus) => {
    try {
      await updateCampaign(campaignId, { ...campaign, status: newStatus });
      setCampaign({ ...campaign, status: newStatus });
      alert(`Campaign ${newStatus === 'active' ? 'activated' : 'paused'}`);
    } catch (err) {
      console.error('Error updating campaign status:', err);
      alert('Failed to update campaign status');
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
        delay_days: 0
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
      delay_days: step.delay_days
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
      delay_days: 0
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
          <div className="flex items-center justify-between mb-4">
            <div>
              <button
                onClick={() => navigate('/campaigns')}
                className="text-blue-600 hover:text-blue-800 mb-2 flex items-center"
              >
                <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Back to Campaigns
              </button>
              <h1 className="text-3xl font-bold text-gray-900">{campaign.name}</h1>
              <p className="text-gray-600 mt-1">{campaign.description}</p>
            </div>
            <div className="flex gap-2">
              {campaign.status === 'draft' || campaign.status === 'paused' ? (
                <button
                  onClick={() => handleUpdateCampaignStatus('active')}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  Activate Campaign
                </button>
              ) : (
                <button
                  onClick={() => handleUpdateCampaignStatus('paused')}
                  className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700"
                >
                  Pause Campaign
                </button>
              )}
            </div>
          </div>
          
          <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-3 rounded">
            <p className="text-sm">
              <strong>Template Variables:</strong> Use {`{{first_name}}`}, {`{{last_name}}`}, {`{{company}}`}, {`{{title}}`}, {`{{email}}`}, {`{{phone}}`} in your templates
            </p>
          </div>
        </div>

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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subject Template *
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
                  Body Template *
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
  );
}

export default CampaignEditor;
