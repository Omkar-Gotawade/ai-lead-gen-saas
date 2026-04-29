import React, { useState, useMemo } from 'react';
import {
  Plus,
  Upload,
  Users,
  Search,
  Mail,
  Edit2,
  Trash2,
  Sparkles,
  Linkedin,
  ChevronLeft,
  ChevronRight,
  X,
} from 'lucide-react';

import { useLeads } from '../hooks/useLeads';
import { useToast } from '../context/ToastContext';

import CreateLeadModal from '../components/CreateLeadModal';
import EditLeadModal from '../components/EditLeadModal';
import DeleteLeadModal from '../components/DeleteLeadModal';
import CSVUploadModal from '../components/CSVUploadModal';
import EmailComposer from '../components/EmailComposer';
import AddToCampaignModal from '../components/AddToCampaignModal';

import Button from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { Alert, AlertDescription } from '../components/ui/Alert';

const Leads = () => {
  const toast = useToast();
  const {
    leads, total, page, pageSize, loading, error,
    emailProviderConfigured, enrichingLeads,
    canGoPrev, canGoNext,
    setPage,
    createLead, updateLead, deleteLead, uploadCSV, enrichLead,
  } = useLeads();

  /* ── Modal + selection state ─────────────────────────────── */
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showCSVModal, setShowCSVModal] = useState(false);
  const [showComposer, setShowComposer] = useState(false);
  const [showCampaignModal, setShowCampaignModal] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);
  const [selectedLeadIds, setSelectedLeadIds] = useState([]);

  /* ── Client-side search ───────────────────────────────────── */
  const [searchQuery, setSearchQuery] = useState('');

  const filteredLeads = useMemo(() => {
    if (!searchQuery.trim()) return leads;
    const q = searchQuery.toLowerCase();
    return leads.filter(
      (l) =>
        l.full_name?.toLowerCase().includes(q) ||
        l.email?.toLowerCase().includes(q) ||
        l.company?.toLowerCase().includes(q) ||
        l.title?.toLowerCase().includes(q),
    );
  }, [leads, searchQuery]);

  /* ── Handlers ─────────────────────────────────────────────── */
  const handleCreateLead = async (data) => {
    try {
      await createLead(data);
      setShowCreateModal(false);
      toast.success('Lead added successfully.');
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to create lead');
    }
  };

  const handleEditLead = async (data) => {
    try {
      await updateLead(selectedLead.id, data);
      setShowEditModal(false);
      setSelectedLead(null);
      toast.success('Lead updated.');
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to update lead');
    }
  };

  const handleDeleteLead = async () => {
    try {
      await deleteLead(selectedLead.id);
      setShowDeleteModal(false);
      setSelectedLead(null);
      toast.success('Lead deleted.');
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to delete lead');
    }
  };

  const handleCSVUpload = async (file) => {
    try {
      await uploadCSV(file);
      setShowCSVModal(false);
      toast.success('CSV imported successfully.');
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to upload CSV');
    }
  };

  const handleEnrichLead = async (leadId) => {
    try {
      await enrichLead(leadId);
    } catch {
      toast.error('Failed to enrich lead. Please try again.');
    }
  };

  const handleSelectAll = (e) => {
    setSelectedLeadIds(e.target.checked ? filteredLeads.map((l) => l.id) : []);
  };

  const handleSelectLead = (leadId) => {
    setSelectedLeadIds((prev) =>
      prev.includes(leadId) ? prev.filter((id) => id !== leadId) : [...prev, leadId],
    );
  };

  const withProtocol = (url) => {
    if (!url) return '';
    return url.startsWith('http://') || url.startsWith('https://') ? url : `https://${url}`;
  };

  const totalPages = Math.ceil(total / pageSize);

  /* ── Render ───────────────────────────────────────────────── */
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

      {/* Search bar */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-400 pointer-events-none" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by name, email, company…"
          className="w-full pl-9 pr-8 py-2 text-sm border border-ink-200 rounded-lg bg-surface text-ink-800 placeholder-ink-400
                     focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500 transition-colors"
        />
        {searchQuery && (
          <button
            onClick={() => setSearchQuery('')}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-ink-400 hover:text-ink-700 transition-colors"
            aria-label="Clear search"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Table card */}
      <Card className="overflow-hidden">
        {loading ? (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th className="w-10 px-4 py-3" />
                  <th>Name</th><th>Email</th><th>Company</th>
                  <th>Title</th><th>Source</th>
                  <th className="text-right pr-5">Actions</th>
                </tr>
              </thead>
              <tbody>
                {Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i} className="border-b border-ink-50">
                    <td className="px-4 py-3 w-10"><div className="skeleton h-3.5 w-3.5 rounded" /></td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2.5">
                        <div className="skeleton w-7 h-7 rounded-full shrink-0" />
                        <div className="skeleton h-4 w-28 rounded" />
                      </div>
                    </td>
                    <td className="px-4 py-3"><div className="skeleton h-4 w-36 rounded" /></td>
                    <td className="px-4 py-3"><div className="skeleton h-4 w-24 rounded" /></td>
                    <td className="px-4 py-3"><div className="skeleton h-3 w-20 rounded" /></td>
                    <td className="px-4 py-3"><div className="skeleton h-5 w-14 rounded-full" /></td>
                    <td className="px-4 py-3 text-right pr-4"><div className="skeleton h-4 w-20 rounded ml-auto" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th className="w-10 px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedLeadIds.length === filteredLeads.length && filteredLeads.length > 0}
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
                {filteredLeads.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="py-16 text-center text-ink-400">
                      <div className="flex flex-col items-center gap-3">
                        <Users className="w-10 h-10 text-ink-200" />
                        <div>
                          <p className="font-medium text-ink-600">
                            {searchQuery ? 'No matching leads' : 'No leads yet'}
                          </p>
                          <p className="text-sm mt-0.5">
                            {searchQuery
                              ? 'Try a different search term'
                              : 'Add a lead manually or import a CSV'}
                          </p>
                        </div>
                      </div>
                    </td>
                  </tr>
                ) : (
                  filteredLeads.map((lead) => (
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
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page - 1)}
              disabled={!canGoPrev}
              icon={<ChevronLeft className="w-3.5 h-3.5" />}
            >
              Prev
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page + 1)}
              disabled={!canGoNext}
              iconEnd={<ChevronRight className="w-3.5 h-3.5" />}
            >
              Next
            </Button>
          </div>
        </div>
      )}

      {/* Modals */}
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
        onSuccess={() => setSelectedLeadIds([])}
      />
    </div>
  );
};

export default Leads;
