import { useState, useEffect } from 'react'
import { leadsAPI } from '../api'
import { getEmailProvider } from '../api/email'
import CreateLeadModal from '../components/CreateLeadModal'
import EditLeadModal from '../components/EditLeadModal'
import DeleteLeadModal from '../components/DeleteLeadModal'
import CSVUploadModal from '../components/CSVUploadModal'
import EmailComposer from '../components/EmailComposer'
import AddToCampaignModal from '../components/AddToCampaignModal'

const Leads = () => {
  const [leads, setLeads] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(50)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [emailProviderConfigured, setEmailProviderConfigured] = useState(false)
  
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showCSVModal, setShowCSVModal] = useState(false)
  const [showComposer, setShowComposer] = useState(false)
  const [showCampaignModal, setShowCampaignModal] = useState(false)
  const [selectedLead, setSelectedLead] = useState(null)
  const [enrichingLeads, setEnrichingLeads] = useState(new Set())
  const [selectedLeadIds, setSelectedLeadIds] = useState([])

  useEffect(() => {
    fetchLeads()
    checkEmailProvider()
  }, [page])

  const fetchLeads = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await leadsAPI.getLeads(page, pageSize)
      setLeads(response.data.leads)
      setTotal(response.data.total)
    } catch (err) {
      setError('Failed to fetch leads')
    } finally {
      setLoading(false)
    }
  }

  const checkEmailProvider = async () => {
    try {
      await getEmailProvider()
      setEmailProviderConfigured(true)
    } catch (err) {
      setEmailProviderConfigured(false)
    }
  }

  const handleCreateLead = async (data) => {
    try {
      await leadsAPI.createLead(data)
      setShowCreateModal(false)
      fetchLeads()
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to create lead')
    }
  }

  const handleEditLead = async (data) => {
    try {
      await leadsAPI.updateLead(selectedLead.id, data)
      setShowEditModal(false)
      setSelectedLead(null)
      fetchLeads()
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to update lead')
    }
  }

  const handleDeleteLead = async () => {
    try {
      await leadsAPI.deleteLead(selectedLead.id)
      setShowDeleteModal(false)
      setSelectedLead(null)
      fetchLeads()
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to delete lead')
    }
  }

  const handleCSVUpload = async (file) => {
    try {
      await leadsAPI.uploadCSV(file)
      setShowCSVModal(false)
      fetchLeads()
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to upload CSV')
    }
  }

  const handleEnrichLead = async (leadId) => {
    setEnrichingLeads(prev => new Set(prev).add(leadId))
    try {
      await leadsAPI.enrichLead(leadId)
      // Show success message
      setTimeout(() => {
        fetchLeads()
        setEnrichingLeads(prev => {
          const newSet = new Set(prev)
          newSet.delete(leadId)
          return newSet
        })
      }, 3000)
    } catch (err) {
      setEnrichingLeads(prev => {
        const newSet = new Set(prev)
        newSet.delete(leadId)
        return newSet
      })
      alert('Failed to enrich lead')
    }
  }

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedLeadIds(leads.map(lead => lead.id))
    } else {
      setSelectedLeadIds([])
    }
  }

  const handleSelectLead = (leadId) => {
    setSelectedLeadIds(prev => {
      if (prev.includes(leadId)) {
        return prev.filter(id => id !== leadId)
      } else {
        return [...prev, leadId]
      }
    })
  }

  const handleCampaignSuccess = () => {
    setSelectedLeadIds([])
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Leads</h1>
          <p className="mt-2 text-sm text-gray-700">
            A list of all leads in your account including their name, email, and company.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none space-x-2">
          {selectedLeadIds.length > 0 && (
            <button
              onClick={() => setShowCampaignModal(true)}
              className="inline-flex items-center justify-center rounded-md border border-transparent bg-green-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            >
              Add {selectedLeadIds.length} to Campaign
            </button>
          )}
          <button
            onClick={() => setShowCSVModal(true)}
            className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Upload CSV
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Add lead
          </button>
        </div>
      </div>

      {error && (
        <div className="mt-4 rounded-md bg-red-50 p-4">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      )}

      {loading ? (
        <div className="mt-8 text-center">
          <div className="text-lg">Loading...</div>
        </div>
      ) : (
        <>
          <div className="mt-8 flex flex-col">
            <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
              <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
                <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                  <table className="min-w-full divide-y divide-gray-300">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-3.5 text-left">
                          <input
                            type="checkbox"
                            checked={selectedLeadIds.length === leads.length && leads.length > 0}
                            onChange={handleSelectAll}
                            className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                          />
                        </th>
                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                          Name
                        </th>
                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                          Email
                        </th>
                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                          Company
                        </th>
                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                          Source
                        </th>
                        <th className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                          <span className="sr-only">Actions</span>
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 bg-white">
                      {leads.map((lead) => (
                        <tr key={lead.id}>
                          <td className="px-3 py-4">
                            <input
                              type="checkbox"
                              checked={selectedLeadIds.includes(lead.id)}
                              onChange={() => handleSelectLead(lead.id)}
                              className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                            />
                          </td>
                          <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-900">
                            {lead.full_name}
                          </td>
                          <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                            {lead.email}
                          </td>
                          <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                            {lead.company || '-'}
                          </td>
                          <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                            {lead.source || '-'}
                          </td>
                          <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                            <button
                              onClick={() => {
                                setSelectedLead(lead)
                                setShowComposer(true)
                              }}
                              className="text-blue-600 hover:text-blue-900 mr-4"
                            >
                              Compose
                            </button>
                            <button
                              onClick={() => handleEnrichLead(lead.id)}
                              disabled={enrichingLeads.has(lead.id)}
                              className="text-green-600 hover:text-green-900 mr-4 disabled:opacity-50"
                            >
                              {enrichingLeads.has(lead.id) ? 'Enriching...' : 'Enrich'}
                            </button>
                            <button
                              onClick={() => {
                                setSelectedLead(lead)
                                setShowEditModal(true)
                              }}
                              className="text-indigo-600 hover:text-indigo-900 mr-4"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => {
                                setSelectedLead(lead)
                                setShowDeleteModal(true)
                              }}
                              className="text-red-600 hover:text-red-900"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          {/* Pagination */}
          <div className="mt-4 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing <span className="font-medium">{(page - 1) * pageSize + 1}</span> to{' '}
              <span className="font-medium">
                {Math.min(page * pageSize, total)}
              </span>{' '}
              of <span className="font-medium">{total}</span> results
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page >= totalPages}
                className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </>
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
          setShowEditModal(false)
          setSelectedLead(null)
        }}
        onSubmit={handleEditLead}
        lead={selectedLead}
      />
      <DeleteLeadModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false)
          setSelectedLead(null)
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
            setShowComposer(false)
            setSelectedLead(null)
          }}
          onSend={(emailData) => {
            console.log('Email drafted:', emailData)
            setShowComposer(false)
            setSelectedLead(null)
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
  )
}

export default Leads
