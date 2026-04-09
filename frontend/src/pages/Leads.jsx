import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Upload, 
  Users, 
  Search, 
  Filter, 
  MoreHorizontal, 
  Mail, 
  Edit2, 
  Trash2, 
  Sparkles,
  Linkedin,
  CheckSquare,
  Square,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { leadsAPI } from '../api';
import { getEmailProvider } from '../api/email';
import CreateLeadModal from '../components/CreateLeadModal';
import EditLeadModal from '../components/EditLeadModal';
import DeleteLeadModal from '../components/DeleteLeadModal';
import CSVUploadModal from '../components/CSVUploadModal';
import EmailComposer from '../components/EmailComposer';
import AddToCampaignModal from '../components/AddToCampaignModal';

import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { Card, CardContent } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { Alert, AlertDescription } from '../components/ui/Alert';
import LoadingSpinner from '../components/ui/LoadingSpinner';

const Leads = () => {
  const [leads, setLeads] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [emailProviderConfigured, setEmailProviderConfigured] = useState(false);
  
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showCSVModal, setShowCSVModal] = useState(false);
  const [showComposer, setShowComposer] = useState(false);
  const [showCampaignModal, setShowCampaignModal] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);
  const [enrichingLeads, setEnrichingLeads] = useState(new Set());
  const [selectedLeadIds, setSelectedLeadIds] = useState([]);

  useEffect(() => {
    fetchLeads();
    checkEmailProvider();
  }, [page]);

  const fetchLeads = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await leadsAPI.getLeads(page, pageSize);
      setLeads(response.data.leads);
      setTotal(response.data.total);
    } catch (err) {
      setError('Failed to fetch leads');
    } finally {
      setLoading(false);
    }
  };

  const checkEmailProvider = async () => {
    try {
      await getEmailProvider();
      setEmailProviderConfigured(true);
    } catch (err) {
      setEmailProviderConfigured(false);
    }
  };

  const handleCreateLead = async (data) => {
    try {
      await leadsAPI.createLead(data);
      setShowCreateModal(false);
      fetchLeads();
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to create lead');
    }
  };

  const handleEditLead = async (data) => {
    try {
      await leadsAPI.updateLead(selectedLead.id, data);
      setShowEditModal(false);
      setSelectedLead(null);
      fetchLeads();
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to update lead');
    }
  };

  const handleDeleteLead = async () => {
    try {
      await leadsAPI.deleteLead(selectedLead.id);
      setShowDeleteModal(false);
      setSelectedLead(null);
      fetchLeads();
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to delete lead');
    }
  };

  const handleCSVUpload = async (file) => {
    try {
      await leadsAPI.uploadCSV(file);
      setShowCSVModal(false);
      fetchLeads();
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to upload CSV');
    }
  };

  const handleEnrichLead = async (leadId) => {
    setEnrichingLeads(prev => new Set(prev).add(leadId));
    try {
      await leadsAPI.enrichLead(leadId);
      setTimeout(() => {
        fetchLeads();
        setEnrichingLeads(prev => {
          const newSet = new Set(prev);
          newSet.delete(leadId);
          return newSet;
        });
      }, 3000);
    } catch (err) {
      setEnrichingLeads(prev => {
        const newSet = new Set(prev);
        newSet.delete(leadId);
        return newSet;
      });
      alert('Failed to enrich lead');
    }
  };

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedLeadIds(leads.map(lead => lead.id));
    } else {
      setSelectedLeadIds([]);
    }
  };

  const handleSelectLead = (leadId) => {
    setSelectedLeadIds(prev => {
      if (prev.includes(leadId)) {
        return prev.filter(id => id !== leadId);
      } else {
        return [...prev, leadId];
      }
    });
  };

  const handleCampaignSuccess = () => {
    setSelectedLeadIds([]);
  };

  const totalPages = Math.ceil(total / pageSize);

  const withProtocol = (url) => {
    if (!url) return '';
    if (url.startsWith('http://') || url.startsWith('https://')) return url;
    return `https://${url}`;
  };

  return (
    <div className="p-6 space-y-5 max-w-[1400px] mx-auto">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="page-title">Leads</h1>
          <p className="page-subtitle mt-0.5">
            {total > 0 ? `${total} contacts in your database` : 'Manage your contacts and prospects'}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {selectedLeadIds.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowCampaignModal(true)}
              icon={<Users className="w-3.5 h-3.5" />}
              className="border-success/30 text-emerald-700 hover:bg-success/8"
            >
              Add {selectedLeadIds.length} to Campaign
            </Button>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowCSVModal(true)}
            icon={<Upload className="w-3.5 h-3.5" />}
          >
            Import CSV
          </Button>
          <Button
            size="sm"
            onClick={() => setShowCreateModal(true)}
            icon={<Plus className="w-3.5 h-3.5" />}
          >
            Add Lead
          </Button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Table card */}
      <Card className="overflow-hidden">
        {loading ? (
          <LoadingSpinner size="md" text="Loading leads…" />
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th className="w-10 px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedLeadIds.length === leads.length && leads.length > 0}
                      onChange={handleSelectAll}
                      className="w-3.5 h-3.5 rounded border-ink-300 text-brand-600 focus:ring-brand-500 cursor-pointer"
                    />
                  </th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Company</th>
                  <th>Title</th>
                  <th>Source</th>
                  <th className="text-right pr-5">Actions</th>
                </tr>
              </thead>
              <tbody>
                {leads.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="py-16 text-center text-ink-400">
                      <div className="flex flex-col items-center gap-3">
                        <Users className="w-10 h-10 text-ink-200" />
                        <div>
                          <p className="font-medium text-ink-600">No leads yet</p>
                          <p className="text-sm mt-0.5">Add a lead manually or import a CSV</p>
                        </div>
                      </div>
                    </td>
                  </tr>
                ) : (
                  leads.map((lead) => (
                    <tr key={lead.id}>
                      <td className="w-10 px-4">
                        <input
                          type="checkbox"
                          checked={selectedLeadIds.includes(lead.id)}
                          onChange={() => handleSelectLead(lead.id)}
                          className="w-3.5 h-3.5 rounded border-ink-300 text-brand-600 focus:ring-brand-500 cursor-pointer"
                        />
                      </td>
                      <td>
                        <div className="flex items-center gap-2.5">
                          <div className="w-7 h-7 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 text-xs font-semibold shrink-0">
                            {lead.full_name?.[0]?.toUpperCase() || '?'}
                          </div>
                          <span className="font-medium text-ink-800">{lead.full_name}</span>
                        </div>
                      </td>
                      <td className="text-ink-500">{lead.email}</td>
                      <td className="text-ink-600">{lead.company || <span className="text-ink-300">—</span>}</td>
                      <td className="text-ink-500 text-xs">{lead.title || <span className="text-ink-300">—</span>}</td>
                      <td>
                        <Badge variant="default" size="xs" className="capitalize">
                          {lead.source || 'Manual'}
                        </Badge>
                      </td>
                      <td className="text-right pr-4">
                        <div className="flex items-center justify-end gap-1">
                          {lead.linkedin_url && (
                            <a
                              href={withProtocol(lead.linkedin_url)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="p-1.5 rounded-md text-ink-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                              title="View LinkedIn profile"
                            >
                              <Linkedin className="w-3.5 h-3.5" />
                            </a>
                          )}
                          <button
                            onClick={() => { setSelectedLead(lead); setShowComposer(true); }}
                            className="p-1.5 rounded-md text-ink-400 hover:text-brand-600 hover:bg-brand-50 transition-colors"
                            title="Compose Email"
                          >
                            <Mail className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleEnrichLead(lead.id)}
                            disabled={enrichingLeads.has(lead.id)}
                            className={`p-1.5 rounded-md transition-colors ${
                              enrichingLeads.has(lead.id)
                                ? 'text-brand-500 animate-pulse-soft'
                                : 'text-ink-400 hover:text-purple-600 hover:bg-purple-50'
                            }`}
                            title="Enrich with AI"
                          >
                            <Sparkles className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => { setSelectedLead(lead); setShowEditModal(true); }}
                            className="p-1.5 rounded-md text-ink-400 hover:text-ink-700 hover:bg-ink-100 transition-colors"
                            title="Edit"
                          >
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => { setSelectedLead(lead); setShowDeleteModal(true); }}
                            className="p-1.5 rounded-md text-ink-400 hover:text-danger hover:bg-danger/8 transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Pagination */}
      {!loading && total > 0 && (
        <div className="flex items-center justify-between text-sm">
          <p className="text-ink-400">
            Showing{' '}
            <span className="font-semibold text-ink-700">{(page - 1) * pageSize + 1}</span>
            {' – '}
            <span className="font-semibold text-ink-700">{Math.min(page * pageSize, total)}</span>
            {' of '}
            <span className="font-semibold text-ink-700">{total}</span>
          </p>
          <div className="flex gap-1.5">
            <Button variant="outline" size="sm" onClick={() => setPage(page - 1)} disabled={page === 1} icon={<ChevronLeft className="w-3.5 h-3.5" />}>
              Prev
            </Button>
            <Button variant="outline" size="sm" onClick={() => setPage(page + 1)} disabled={page >= Math.ceil(total / pageSize)}>
              Next <ChevronRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </div>
        </div>
      )}

      {/* Modals — unchanged logic */}
      <CreateLeadModal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} onSubmit={handleCreateLead} />
      <EditLeadModal
        isOpen={showEditModal}
        onClose={() => { setShowEditModal(false); setSelectedLead(null); }}
        onSubmit={handleEditLead}
        lead={selectedLead}
      />
      <DeleteLeadModal
        isOpen={showDeleteModal}
        onClose={() => { setShowDeleteModal(false); setSelectedLead(null); }}
        onConfirm={handleDeleteLead}
        lead={selectedLead}
      />
      <CSVUploadModal isOpen={showCSVModal} onClose={() => setShowCSVModal(false)} onUpload={handleCSVUpload} />
      {showComposer && selectedLead && (
        <EmailComposer
          lead={selectedLead}
          emailProviderConfigured={emailProviderConfigured}
          onClose={() => { setShowComposer(false); setSelectedLead(null); }}
          onSend={() => { setShowComposer(false); setSelectedLead(null); }}
        />
      )}
      <AddToCampaignModal
        isOpen={showCampaignModal}
        onClose={() => setShowCampaignModal(false)}
        selectedLeadIds={selectedLeadIds}
        onSuccess={handleCampaignSuccess}
      />
    </div>
  );
};

export default Leads;

