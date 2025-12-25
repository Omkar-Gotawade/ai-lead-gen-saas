import { useState, useEffect } from 'react'
import api from '../api/axios'

export default function DiscoverLeadsPage() {
  const [formData, setFormData] = useState({
    keywords: '',
    location: '',
    industry: '',
    max_results: 20
  })
  const [loading, setLoading] = useState(false)
  const [currentJob, setCurrentJob] = useState(null)
  const [jobStatus, setJobStatus] = useState(null)
  const [error, setError] = useState(null)
  const [recentJobs, setRecentJobs] = useState([])

  // Poll job status
  useEffect(() => {
    if (!currentJob) return

    const pollInterval = setInterval(async () => {
      try {
        const response = await api.get(`/api/lead-discovery/${currentJob.id}`)
        setJobStatus(response.data)

        // Stop polling if job is completed or failed
        if (['completed', 'failed'].includes(response.data.job.status)) {
          clearInterval(pollInterval)
          setLoading(false)
          // Refresh recent jobs
          fetchRecentJobs()
        }
      } catch (err) {
        console.error('Failed to fetch job status:', err)
      }
    }, 3000) // Poll every 3 seconds

    return () => clearInterval(pollInterval)
  }, [currentJob])

  // Load recent jobs on mount
  useEffect(() => {
    fetchRecentJobs()
  }, [])

  const fetchRecentJobs = async () => {
    try {
      const response = await api.get('/api/lead-discovery/', { params: { limit: 10 } })
      setRecentJobs(response.data)
    } catch (err) {
      console.error('Failed to fetch recent jobs:', err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const response = await api.post('/api/lead-discovery/start', formData)
      setCurrentJob(response.data)
      setJobStatus({ job: response.data, discovered_domains: [], progress_percent: 0 })
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start lead discovery')
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleViewJob = async (jobId) => {
    try {
      const response = await api.get(`/api/lead-discovery/${jobId}`)
      setCurrentJob(response.data.job)
      setJobStatus(response.data)
    } catch (err) {
      setError('Failed to load job details')
    }
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Discover Leads</h1>

      {/* Discovery Form */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Start New Discovery</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Keywords *
            </label>
            <input
              type="text"
              name="keywords"
              value={formData.keywords}
              onChange={handleChange}
              placeholder="e.g., AI software, marketing agency"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location (optional)
              </label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="e.g., India, USA"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Industry (optional)
              </label>
              <input
                type="text"
                name="industry"
                value={formData.industry}
                onChange={handleChange}
                placeholder="e.g., SaaS, E-commerce"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Results
            </label>
            <input
              type="number"
              name="max_results"
              value={formData.max_results}
              onChange={handleChange}
              min="1"
              max="100"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Discovering...' : 'Discover Leads'}
          </button>
        </form>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {/* Job Status */}
      {jobStatus && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Discovery Progress</h2>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Status:</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                jobStatus.job.status === 'completed' ? 'bg-green-100 text-green-800' :
                jobStatus.job.status === 'failed' ? 'bg-red-100 text-red-800' :
                jobStatus.job.status === 'running' ? 'bg-blue-100 text-blue-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {jobStatus.job.status}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-gray-600">Keywords:</span>
              <span className="font-medium">{jobStatus.job.keywords}</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-gray-600">Domains Found:</span>
              <span className="font-medium">{jobStatus.job.domains_found}</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-gray-600">Domains Crawled:</span>
              <span className="font-medium">{jobStatus.job.domains_crawled}</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-gray-600">Leads Created:</span>
              <span className="font-medium text-green-600">{jobStatus.job.leads_created}</span>
            </div>

            {/* Progress Bar */}
            {jobStatus.job.status === 'running' && (
              <div className="mt-4">
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                    style={{ width: `${jobStatus.progress_percent}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-1 text-center">
                  {jobStatus.progress_percent}% complete
                </p>
              </div>
            )}

            {jobStatus.job.error_message && (
              <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded">
                <p className="text-sm text-red-700">{jobStatus.job.error_message}</p>
              </div>
            )}
          </div>

          {/* Discovered Domains Preview */}
          {jobStatus.discovered_domains.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-3">Discovered Domains</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Domain</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Emails</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {jobStatus.discovered_domains.map((domain) => (
                      <tr key={domain.id}>
                        <td className="px-4 py-2 text-sm">{domain.domain}</td>
                        <td className="px-4 py-2 text-sm">{domain.company_name || '-'}</td>
                        <td className="px-4 py-2">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            domain.status === 'crawled' ? 'bg-green-100 text-green-800' :
                            domain.status === 'failed' ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {domain.status}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-sm">
                          {domain.emails_found ? domain.emails_found.split(',').length : 0}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {jobStatus.job.status === 'completed' && jobStatus.job.leads_created > 0 && (
            <div className="mt-4">
              <a
                href="/leads"
                className="inline-block bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
              >
                View Leads →
              </a>
            </div>
          )}
        </div>
      )}

      {/* Recent Jobs */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Discovery Jobs</h2>
        
        {recentJobs.length === 0 ? (
          <p className="text-gray-500">No discovery jobs yet. Start one above!</p>
        ) : (
          <div className="space-y-3">
            {recentJobs.map((job) => (
              <div
                key={job.id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                onClick={() => handleViewJob(job.id)}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">{job.keywords}</p>
                    <p className="text-sm text-gray-500">
                      {job.location && `${job.location} • `}
                      {new Date(job.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      job.status === 'completed' ? 'bg-green-100 text-green-800' :
                      job.status === 'failed' ? 'bg-red-100 text-red-800' :
                      job.status === 'running' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {job.status}
                    </span>
                    <p className="text-sm text-gray-600 mt-1">
                      {job.leads_created} leads
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
