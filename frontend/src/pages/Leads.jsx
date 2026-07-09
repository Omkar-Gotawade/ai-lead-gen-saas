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
            {total > 0 ? (
              <><span className="stat-number" style={{ color: '#f59e0b', fontSize: '0.9rem' }}>{total}</span> contacts in your database</>
            ) : 'Manage your contacts and prospects'}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {selectedLeadIds.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowCampaignModal(true)}
              icon={<Users className="w-3.5 h-3.5" />}
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
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none" style={{ color: '#343a52' }} />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by name, email, company…"
          className="w-full pl-9 pr-8 py-2 text-sm rounded-lg transition-colors focus:outline-none"
          style={{
            background: '#111220',
            border: '1px solid rgba(255,255,255,0.08)',
            color: '#c8cce0',
          }}
          onFocus={e => { e.target.style.borderColor = '#d97706'; e.target.style.boxShadow = '0 0 0 3px rgba(245,158,11,0.12)'; }}
          onBlur={e => { e.target.style.borderColor = 'rgba(255,255,255,0.08)'; e.target.style.boxShadow = 'none'; }}
        />
        {searchQuery && (
          <button
            onClick={() => setSearchQuery('')}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 transition-colors"
            style={{ color: '#343a52' }}
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
                      className="w-3.5 h-3.5 rounded cursor-pointer"
                      style={{ accentColor: '#f59e0b' }}
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
                          className="w-3.5 h-3.5 rounded cursor-pointer"
                          style={{ accentColor: '#f59e0b' }}
                        />
                      </td>
                      <td>
                        <div className="flex items-center gap-2.5">
                          <div
                            className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
                            style={{ background: 'rgba(245,158,11,0.12)', color: '#f59e0b', border: '1px solid rgba(245,158,11,0.2)' }}
                          >
                            {lead.full_name?.[0]?.toUpperCase() || '?'}
                          </div>
                          <span className="font-medium" style={{ color: '#e8eaf5' }}>{lead.full_name}</span>
                        </div>
                      </td>
                      <td style={{ color: '#6b7290' }}>{lead.email}</td>
                      <td style={{ color: '#8b8fa8' }}>{lead.company || <span style={{ color: '#252840' }}>—</span>}</td>
                      <td style={{ color: '#6b7290', fontSize: '0.75rem' }}>{lead.title || <span style={{ color: '#252840' }}>—</span>}</td>
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
                              className="p-1.5 rounded-md transition-colors"
                              style={{ color: '#343a52' }}
                              onMouseEnter={e => { e.currentTarget.style.color = '#06b6d4'; e.currentTarget.style.background = 'rgba(6,182,212,0.08)'; }}
                              onMouseLeave={e => { e.currentTarget.style.color = '#343a52'; e.currentTarget.style.background = 'transparent'; }}
                              title="View LinkedIn profile"
                            >
                              <Linkedin className="w-3.5 h-3.5" />
                            </a>
                          )}
                          <button
                            onClick={() => { setSelectedLead(lead); setShowComposer(true); }}
                            className="p-1.5 rounded-md transition-colors"
                            style={{ color: '#343a52' }}
                            onMouseEnter={e => { e.currentTarget.style.color = '#f59e0b'; e.currentTarget.style.background = 'rgba(245,158,11,0.08)'; }}
                            onMouseLeave={e => { e.currentTarget.style.color = '#343a52'; e.currentTarget.style.background = 'transparent'; }}
                            title="Compose Email"
                          >
                            <Mail className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleEnrichLead(lead.id)}
                            disabled={enrichingLeads.has(lead.id)}
                            className={`p-1.5 rounded-md transition-colors ${
                              enrichingLeads.has(lead.id) ? 'animate-pulse-soft' : ''
                            }`}
                            style={{ color: enrichingLeads.has(lead.id) ? '#f59e0b' : '#343a52' }}
                            onMouseEnter={e => { if (!enrichingLeads.has(lead.id)) { e.currentTarget.style.color = '#f59e0b'; e.currentTarget.style.background = 'rgba(245,158,11,0.08)'; }}}
                            onMouseLeave={e => { if (!enrichingLeads.has(lead.id)) { e.currentTarget.style.color = '#343a52'; e.currentTarget.style.background = 'transparent'; }}}
                            title="Enrich with AI"
                          >
                            <Sparkles className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => { setSelectedLead(lead); setShowEditModal(true); }}
                            className="p-1.5 rounded-md transition-colors"
                            style={{ color: '#343a52' }}
                            onMouseEnter={e => { e.currentTarget.style.color = '#c8cce0'; e.currentTarget.style.background = 'rgba(255,255,255,0.05)'; }}
                            onMouseLeave={e => { e.currentTarget.style.color = '#343a52'; e.currentTarget.style.background = 'transparent'; }}
                            title="Edit"
                          >
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => { setSelectedLead(lead); setShowDeleteModal(true); }}
                            className="p-1.5 rounded-md transition-colors"
                            style={{ color: '#343a52' }}
                            onMouseEnter={e => { e.currentTarget.style.color = '#ef4444'; e.currentTarget.style.background = 'rgba(239,68,68,0.08)'; }}
                            onMouseLeave={e => { e.currentTarget.style.color = '#343a52'; e.currentTarget.style.background = 'transparent'; }}
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
