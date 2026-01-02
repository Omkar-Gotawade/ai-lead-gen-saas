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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Leads</h1>
          <p className="text-slate-500">Manage and track your potential customers.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {selectedLeadIds.length > 0 && (
            <Button
              variant="outline"
              onClick={() => setShowCampaignModal(true)}
              className="text-green-600 border-green-200 hover:bg-green-50"
              icon={<Users className="w-4 h-4" />}
            >
              Add {selectedLeadIds.length} to Campaign
            </Button>
          )}
          <Button
            variant="outline"
            onClick={() => setShowCSVModal(true)}
            icon={<Upload className="w-4 h-4" />}
          >
            Import CSV
          </Button>
          <Button
            onClick={() => setShowCreateModal(true)}
            icon={<Plus className="w-4 h-4" />}
          >
            Add Lead
          </Button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-12 flex justify-center">
              <LoadingSpinner size="lg" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-4 w-4">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={selectedLeadIds.length === leads.length && leads.length > 0}
                          onChange={handleSelectAll}
                          className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                        />
                      </div>
                    </th>
                    <th className="px-6 py-4 font-medium">Name</th>
                    <th className="px-6 py-4 font-medium">Email</th>
                    <th className="px-6 py-4 font-medium">Company</th>
                    <th className="px-6 py-4 font-medium">Source</th>
                    <th className="px-6 py-4 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {leads.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-12 text-center text-slate-500">
                        No leads found. Add a new lead or import a CSV to get started.
                      </td>
                    </tr>
                  ) : (
                    leads.map((lead) => (
                      <tr key={lead.id} className="bg-white hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center">
                            <input
                              type="checkbox"
                              checked={selectedLeadIds.includes(lead.id)}
                              onChange={() => handleSelectLead(lead.id)}
                              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                            />
                          </div>
                        </td>
                        <td className="px-6 py-4 font-medium text-slate-900">
                          {lead.full_name}
                        </td>
                        <td className="px-6 py-4 text-slate-600">
                          {lead.email}
                        </td>
                        <td className="px-6 py-4 text-slate-600">
                          {lead.company || <span className="text-slate-400">-</span>}
                        </td>
                        <td className="px-6 py-4">
                          <Badge variant="secondary" className="capitalize">
                            {lead.source || 'Manual'}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => {
                                setSelectedLead(lead);
                                setShowComposer(true);
                              }}
                              className="p-1 text-slate-400 hover:text-blue-600 transition-colors"
                              title="Compose Email"
                            >
                              <Mail className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleEnrichLead(lead.id)}
                              disabled={enrichingLeads.has(lead.id)}
                              className={`p-1 transition-colors ${
                                enrichingLeads.has(lead.id) 
                                  ? 'text-blue-600 animate-pulse' 
                                  : 'text-slate-400 hover:text-purple-600'
                              }`}
                              title="Enrich Lead"
                            >
                              <Sparkles className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => {
                                setSelectedLead(lead);
                                setShowEditModal(true);
                              }}
                              className="p-1 text-slate-400 hover:text-slate-900 transition-colors"
                              title="Edit"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => {
                                setSelectedLead(lead);
                                setShowDeleteModal(true);
                              }}
                              className="p-1 text-slate-400 hover:text-red-600 transition-colors"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
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
        </CardContent>
      </Card>

      {/* Pagination */}
      {!loading && total > 0 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-slate-500">
            Showing <span className="font-medium text-slate-900">{(page - 1) * pageSize + 1}</span> to{' '}
            <span className="font-medium text-slate-900">
              {Math.min(page * pageSize, total)}
            </span>{' '}
            of <span className="font-medium text-slate-900">{total}</span> results
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page - 1)}
              disabled={page === 1}
              icon={<ChevronLeft className="w-4 h-4" />}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page + 1)}
              disabled={page >= totalPages}
            >
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      )}

      {/* Modals */}
      <CreateLeadModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateLead}
      />
      <EditLeadModal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setSelectedLead(null);
        }}
        onSubmit={handleEditLead}
        lead={selectedLead}
      />
      <DeleteLeadModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setSelectedLead(null);
        }}
        onConfirm={handleDeleteLead}
        lead={selectedLead}
      />
      <CSVUploadModal
        isOpen={showCSVModal}
        onClose={() => setShowCSVModal(false)}
        onUpload={handleCSVUpload}
      />
      {showComposer && selectedLead && (
        <EmailComposer
          lead={selectedLead}
          emailProviderConfigured={emailProviderConfigured}
          onClose={() => {
            setShowComposer(false);
            setSelectedLead(null);
          }}
          onSend={(emailData) => {
            console.log('Email drafted:', emailData);
            setShowComposer(false);
            setSelectedLead(null);
          }}
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
