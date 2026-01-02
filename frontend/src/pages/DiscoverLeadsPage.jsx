import { useState, useEffect } from 'react'
import { 
  Search, 
  MapPin, 
  Briefcase, 
  Globe, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  ArrowRight,
  History
} from 'lucide-react'
import api from '../api/axios'

import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import { Alert, AlertDescription } from '../components/ui/Alert'
import LoadingSpinner from '../components/ui/LoadingSpinner'

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
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (err) {
      setError('Failed to load job details')
    }
  }

  const getStatusVariant = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'destructive';
      case 'running': return 'default';
      default: return 'secondary';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Discover Leads</h1>
        <p className="text-slate-500">Find new potential customers using AI-powered search.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Discovery Form */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Start New Discovery</CardTitle>
            </CardHeader>
            <form onSubmit={handleSubmit}>
              <CardContent className="space-y-4">
                <Input
                  label="Keywords"
                  name="keywords"
                  value={formData.keywords}
                  onChange={handleChange}
                  placeholder="e.g., AI software, marketing agency"
                  required
                  icon={<Search className="w-4 h-4" />}
                />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Location (optional)"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    placeholder="e.g., India, USA"
                    icon={<MapPin className="w-4 h-4" />}
                  />

                  <Input
                    label="Industry (optional)"
                    name="industry"
                    value={formData.industry}
                    onChange={handleChange}
                    placeholder="e.g., SaaS, E-commerce"
                    icon={<Briefcase className="w-4 h-4" />}
                  />
                </div>

                <Input
                  label="Max Results"
                  type="number"
                  name="max_results"
                  value={formData.max_results}
                  onChange={handleChange}
                  min="1"
                  max="100"
                />
              </CardContent>
              <CardFooter>
                <Button
                  type="submit"
                  isLoading={loading}
                  className="w-full"
                  icon={<Globe className="w-4 h-4" />}
                >
                  {loading ? 'Discovering...' : 'Discover Leads'}
                </Button>
              </CardFooter>
            </form>
          </Card>

          {/* Error Display */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Job Status */}
          {jobStatus && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Discovery Progress</span>
                  <Badge variant={getStatusVariant(jobStatus.job.status)} className="capitalize">
                    {jobStatus.job.status}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xs text-slate-500 mb-1">Keywords</p>
                    <p className="font-medium text-slate-900 truncate" title={jobStatus.job.keywords}>
                      {jobStatus.job.keywords}
                    </p>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xs text-slate-500 mb-1">Domains Found</p>
                    <p className="font-medium text-slate-900">{jobStatus.job.domains_found}</p>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xs text-slate-500 mb-1">Crawled</p>
                    <p className="font-medium text-slate-900">{jobStatus.job.domains_crawled}</p>
                  </div>
                  <div className="p-3 bg-green-50 rounded-lg border border-green-100">
                    <p className="text-xs text-green-600 mb-1">Leads Created</p>
                    <p className="font-medium text-green-700">{jobStatus.job.leads_created}</p>
                  </div>
                </div>

                {/* Progress Bar */}
                {jobStatus.job.status === 'running' && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs text-slate-500">
                      <span>Progress</span>
                      <span>{jobStatus.progress_percent}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${jobStatus.progress_percent}%` }}
                      />
                    </div>
                  </div>
                )}

                {jobStatus.job.error_message && (
                  <Alert variant="destructive">
                    <AlertDescription>{jobStatus.job.error_message}</AlertDescription>
                  </Alert>
                )}

                {/* Discovered Domains Preview */}
                {jobStatus.discovered_domains.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-sm font-medium text-slate-900">Discovered Domains</h3>
                    <div className="overflow-x-auto border rounded-lg">
                      <table className="w-full text-sm text-left">
                        <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
                          <tr>
                            <th className="px-4 py-2 font-medium">Domain</th>
                            <th className="px-4 py-2 font-medium">Company</th>
                            <th className="px-4 py-2 font-medium">Status</th>
                            <th className="px-4 py-2 font-medium">Emails</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-200">
                          {jobStatus.discovered_domains.map((domain) => (
                            <tr key={domain.id} className="bg-white">
                              <td className="px-4 py-2 text-slate-900">{domain.domain}</td>
                              <td className="px-4 py-2 text-slate-600">{domain.company_name || '-'}</td>
                              <td className="px-4 py-2">
                                <Badge variant={
                                  domain.status === 'crawled' ? 'success' :
                                  domain.status === 'failed' ? 'destructive' : 'secondary'
                                } className="text-xs">
                                  {domain.status}
                                </Badge>
                              </td>
                              <td className="px-4 py-2 text-slate-600">
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
                  <div className="flex justify-end">
                    <Button
                      variant="default"
                      className="bg-green-600 hover:bg-green-700"
                      onClick={() => window.location.href = '/leads'}
                      icon={<ArrowRight className="w-4 h-4" />}
                    >
                      View Leads
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Recent Jobs Sidebar */}
        <div className="lg:col-span-1">
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <History className="w-5 h-5 text-slate-500" />
                Recent Jobs
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {recentJobs.length === 0 ? (
                <div className="p-6 text-center text-slate-500 text-sm">
                  No discovery jobs yet. Start one to find leads!
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {recentJobs.map((job) => (
                    <button
                      key={job.id}
                      className="w-full text-left p-4 hover:bg-slate-50 transition-colors focus:outline-none focus:bg-slate-50"
                      onClick={() => handleViewJob(job.id)}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-medium text-slate-900 text-sm truncate max-w-[120px]" title={job.keywords}>
                          {job.keywords}
                        </span>
                        <Badge variant={getStatusVariant(job.status)} className="text-[10px] px-1.5 py-0.5 h-5">
                          {job.status}
                        </Badge>
                      </div>
                      <div className="flex justify-between items-end">
                        <div className="text-xs text-slate-500">
                          <div className="flex items-center gap-1 mb-0.5">
                            <Clock className="w-3 h-3" />
                            {new Date(job.created_at).toLocaleDateString()}
                          </div>
                          {job.location && <div className="truncate max-w-[100px]">{job.location}</div>}
                        </div>
                        <div className="text-xs font-medium text-slate-700">
                          {job.leads_created} leads
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
