import { useState, useEffect } from "react"
import {
  Search, MapPin, Briefcase, Globe, Clock,
  CheckCircle, AlertCircle, Loader2, ArrowRight,
  History, Linkedin, Mail, Building2, User, ChevronDown, ChevronUp,
  Zap, Database
} from "lucide-react"
import api from "../api/axios"
import Button from "../components/ui/Button"
import Input from "../components/ui/Input"
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "../components/ui/Card"
import Badge from "../components/ui/Badge"
import { Alert, AlertDescription } from "../components/ui/Alert"

//  Helper: decode discoveredDomain row into a person object 
function parsePerson(domain) {
  if (domain.person) return domain.person
  if (domain.company_description) {
    try {
      const m = JSON.parse(domain.company_description)
      if (m && m.first_name !== undefined) return m
    } catch (_) {}
  }
  return null
}

function isPeoplePipeline(discoveredDomains) {
  if (!discoveredDomains || discoveredDomains.length === 0) return false
  return discoveredDomains.some((d) => parsePerson(d) !== null)
}

//  Seniority badge colour 
const SENIORITY_VARIANTS = {
  c_suite: "destructive", founder: "destructive",
  vp: "default", director: "default",
  manager: "secondary", senior: "secondary",
}

//  Person card (Apollo / Snov results) 
function PersonCard({ domain }) {
  const person = parsePerson(domain)
  const email = domain.emails_found || ""
  const linkedin = domain.source_url || person?.linkedin_url || ""

  if (!person && !email) return null

  const name = person
    ? `${person.first_name} ${person.last_name}`.trim()
    : domain.company_name || "Unknown"

  const title = person?.title || domain.company_name || ""
  const company = person?.company || domain.domain || ""
  const seniority = person?.seniority || ""
  const source = person?.source || ""
  const location = person?.location || ""

  return (
    <div className="flex items-start gap-3 p-4 border border-slate-100 rounded-lg bg-white hover:border-blue-200 hover:shadow-sm transition-all">
      {/* Avatar */}
      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-semibold text-sm shrink-0">
        {name.charAt(0).toUpperCase()}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-semibold text-slate-900 text-sm">{name}</span>
          {seniority && (
            <Badge variant={SENIORITY_VARIANTS[seniority] || "outline"} className="text-[10px] px-1.5 py-0 h-4 capitalize">
              {seniority.replace("_", " ")}
            </Badge>
          )}
          {source && (
            <Badge variant="outline" className="text-[10px] px-1.5 py-0 h-4 text-slate-400 border-slate-200">
              {source}
            </Badge>
          )}
        </div>
        {title && <p className="text-xs text-slate-600 mt-0.5 truncate">{title}</p>}
        <div className="flex items-center gap-3 mt-1 flex-wrap">
          {company && (
            <span className="flex items-center gap-1 text-xs text-slate-500">
              <Building2 className="w-3 h-3" />{company}
            </span>
          )}
          {location && (
            <span className="flex items-center gap-1 text-xs text-slate-500">
              <MapPin className="w-3 h-3" />{location}
            </span>
          )}
        </div>
        {email && (
          <div className="flex items-center gap-1 mt-1">
            <Mail className="w-3 h-3 text-green-600" />
            <span className="text-xs text-green-700 font-medium truncate">{email}</span>
          </div>
        )}
      </div>

      {/* LinkedIn */}
      {linkedin && (
        <a
          href={linkedin}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 p-1.5 rounded text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
          title="View LinkedIn profile"
        >
          <Linkedin className="w-4 h-4" />
        </a>
      )}
    </div>
  )
}

//  Source badge 
function SourceBadge({ domains }) {
  if (!domains || domains.length === 0) return null
  const sources = [...new Set(domains.map((d) => parsePerson(d)?.source).filter(Boolean))]
  if (sources.length === 0) return null
  return (
    <div className="flex items-center gap-2 text-xs text-slate-500">
      <span>Source:</span>
      {sources.map((s) => (
        <Badge key={s} variant="outline" className="text-xs capitalize px-2">
          {s === "apollo" ? "Apollo.io" : s === "snov" ? "Snov.io" : s === "pdl" ? "People Data Labs" : s === "icypeas" ? "Icypeas" : s}
        </Badge>
      ))}
    </div>
  )
}

//  Main page 
export default function DiscoverLeadsPage() {
  const [formData, setFormData] = useState({
    keywords: "", location: "", industry: "", job_title: "", seniority: "", max_results: 25,
  })
  const [loading, setLoading] = useState(false)
  const [currentJob, setCurrentJob] = useState(null)
  const [jobStatus, setJobStatus] = useState(null)
  const [error, setError] = useState(null)
  const [recentJobs, setRecentJobs] = useState([])
  const [showAdvanced, setShowAdvanced] = useState(false)

  useEffect(() => {
    if (!currentJob) return
    const poll = setInterval(async () => {
      try {
        const res = await api.get(`/api/lead-discovery/${currentJob.id}`)
        setJobStatus(res.data)
        if (["completed", "failed"].includes(res.data.job.status)) {
          clearInterval(poll)
          setLoading(false)
          fetchRecentJobs()
        }
      } catch (err) {
        console.error("Poll error:", err)
      }
    }, 3000)
    return () => clearInterval(poll)
  }, [currentJob])

  useEffect(() => { fetchRecentJobs() }, [])

  const fetchRecentJobs = async () => {
    try {
      const res = await api.get("/api/lead-discovery/", { params: { limit: 10 } })
      setRecentJobs(res.data)
    } catch (_) {}
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    setJobStatus(null)
    try {
      const payload = { ...formData }
      // Strip empty optional fields
      Object.keys(payload).forEach((k) => { if (payload[k] === "" || payload[k] === null) delete payload[k] })
      const res = await api.post("/api/lead-discovery/start", payload)
      setCurrentJob(res.data)
      setJobStatus({ job: res.data, discovered_domains: [], progress_percent: 0 })
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to start lead discovery")
      setLoading(false)
    }
  }

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value })

  const handleViewJob = async (jobId) => {
    try {
      const res = await api.get(`/api/lead-discovery/${jobId}`)
      setCurrentJob(res.data.job)
      setJobStatus(res.data)
      window.scrollTo({ top: 0, behavior: "smooth" })
    } catch (_) { setError("Failed to load job details") }
  }

  const statusVariant = (s) =>
    s === "completed" ? "success" : s === "failed" ? "destructive" : s === "running" ? "default" : "secondary"

  const peoplePipeline = jobStatus ? isPeoplePipeline(jobStatus.discovered_domains) : false

  return (
    <div className="p-6 space-y-5 max-w-[1400px] mx-auto">
      <div>
        <h1 className="page-title">Discover Leads</h1>
        <p className="page-subtitle mt-0.5">
          Find real professionals from People Data Labs, Apollo, Snov.io, or web search
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/*  Form  */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="w-5 h-5 text-blue-600" />
                Start New Discovery
              </CardTitle>
            </CardHeader>
            <form onSubmit={handleSubmit}>
              <CardContent className="space-y-4">
                <Input
                  label="Search Keywords *"
                  name="keywords"
                  value={formData.keywords}
                  onChange={handleChange}
                  placeholder='e.g. "VP Sales SaaS" or "Growth Lead fintech"'
                  required
                  icon={<Search className="w-4 h-4" />}
                />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Location (optional)"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    placeholder="e.g. India, New York, London"
                    icon={<MapPin className="w-4 h-4" />}
                  />
                  <Input
                    label="Industry (optional)"
                    name="industry"
                    value={formData.industry}
                    onChange={handleChange}
                    placeholder="e.g. SaaS, Fintech, E-commerce"
                    icon={<Briefcase className="w-4 h-4" />}
                  />
                </div>

                {/* Advanced filters */}
                <button
                  type="button"
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className="flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-800 font-medium"
                >
                  {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  {showAdvanced ? "Hide" : "Show"} advanced filters
                </button>

                {showAdvanced && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1 border-t border-slate-100">
                    <Input
                      label="Job Title (optional)"
                      name="job_title"
                      value={formData.job_title}
                      onChange={handleChange}
                      placeholder='e.g. "VP Sales", "CTO", "Head of Marketing"'
                      icon={<User className="w-4 h-4" />}
                    />
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Seniority (optional)</label>
                      <select
                        name="seniority"
                        value={formData.seniority}
                        onChange={handleChange}
                        className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                      >
                        <option value="">Any seniority</option>
                        <option value="founder">Founder / Owner</option>
                        <option value="c_suite">C-Suite (CEO, CTO, CMO)</option>
                        <option value="vp">VP / Vice President</option>
                        <option value="director">Director</option>
                        <option value="manager">Manager</option>
                        <option value="senior">Senior Individual Contributor</option>
                      </select>
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
                  </div>
                )}
              </CardContent>
              <CardFooter className="flex flex-col gap-3">
                <Button type="submit" isLoading={loading} className="w-full" icon={<Zap className="w-4 h-4" />}>
                  {loading ? "Searching for leads" : "Find Leads"}
                </Button>
                <p className="text-xs text-slate-400 text-center">
                  Uses PDL → Icypeas → Apollo → Snov.io → Web Crawl (whichever is configured)
                </p>
              </CardFooter>
            </form>
          </Card>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/*  Job status  */}
          {jobStatus && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    {jobStatus.job.status === "running" && <Loader2 className="w-4 h-4 animate-spin text-blue-600" />}
                    {jobStatus.job.status === "completed" && <CheckCircle className="w-4 h-4 text-green-600" />}
                    {jobStatus.job.status === "failed" && <AlertCircle className="w-4 h-4 text-red-600" />}
                    Discovery Progress
                  </span>
                  <Badge variant={statusVariant(jobStatus.job.status)} className="capitalize">
                    {jobStatus.job.status}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-5">
                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xs text-slate-500 mb-1">{peoplePipeline ? "People Found" : "Domains Found"}</p>
                    <p className="font-semibold text-slate-900 text-lg">{jobStatus.job.domains_found}</p>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xs text-slate-500 mb-1">{peoplePipeline ? "Processed" : "Crawled"}</p>
                    <p className="font-semibold text-slate-900 text-lg">{jobStatus.job.domains_crawled}</p>
                  </div>
                  <div className="p-3 bg-green-50 rounded-lg border border-green-100">
                    <p className="text-xs text-green-600 mb-1">Leads Saved</p>
                    <p className="font-semibold text-green-700 text-lg">{jobStatus.job.leads_created}</p>
                  </div>
                </div>

                {/* Progress bar (only while running) */}
                {jobStatus.job.status === "running" && (
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs text-slate-500">
                      <span>Progress</span><span>{jobStatus.progress_percent}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-500"
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

              {/*  Person cards (Apollo / Snov)  */}
                {peoplePipeline && jobStatus.discovered_domains.length > 0 && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-slate-900">
                        Discovered People ({jobStatus.discovered_domains.length})
                      </h3>
                      <SourceBadge domains={jobStatus.discovered_domains} />
                    </div>
                    <div className="space-y-2 max-h-[520px] overflow-y-auto pr-1">
                      {jobStatus.discovered_domains.map((d) => (
                        <PersonCard key={d.id} domain={d} />
                      ))}
                    </div>
                  </div>
                )}

                {/*  Legacy domain table (SERP crawl)  */}
                {!peoplePipeline && jobStatus.discovered_domains.length > 0 && (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Database className="w-4 h-4 text-slate-400" />
                      <h3 className="text-sm font-semibold text-slate-900">Discovered Domains</h3>
                    </div>
                    <div className="overflow-x-auto border rounded-lg">
                      <table className="w-full text-sm text-left">
                        <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b">
                          <tr>
                            <th className="px-4 py-2 font-medium">Domain</th>
                            <th className="px-4 py-2 font-medium">Company</th>
                            <th className="px-4 py-2 font-medium">Status</th>
                            <th className="px-4 py-2 font-medium">Emails</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {jobStatus.discovered_domains.map((d) => (
                            <tr key={d.id} className="bg-white">
                              <td className="px-4 py-2 text-slate-900">{d.domain}</td>
                              <td className="px-4 py-2 text-slate-600">{d.company_name || "�"}</td>
                              <td className="px-4 py-2">
                                <Badge variant={d.status === "crawled" ? "success" : d.status === "failed" ? "destructive" : "secondary"} className="text-xs">
                                  {d.status}
                                </Badge>
                              </td>
                              <td className="px-4 py-2 text-slate-600">
                                {d.emails_found ? d.emails_found.split(",").length : 0}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {jobStatus.job.status === "completed" && jobStatus.job.leads_created > 0 && (
                  <div className="flex justify-end pt-2">
                    <Button
                      variant="default"
                      className="bg-green-600 hover:bg-green-700"
                      onClick={() => (window.location.href = "/leads")}
                      icon={<ArrowRight className="w-4 h-4" />}
                    >
                      View {jobStatus.job.leads_created} Leads
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/*  Recent jobs sidebar  */}
        <div className="lg:col-span-1">
          <Card className="h-full sticky top-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <History className="w-4 h-4 text-slate-500" />
                Recent Jobs
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {recentJobs.length === 0 ? (
                <div className="p-6 text-center text-slate-500 text-sm">
                  No discovery jobs yet. Start one above!
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {recentJobs.map((job) => (
                    <button
                      key={job.id}
                      className="w-full text-left p-4 hover:bg-slate-50 transition-colors focus:outline-none"
                      onClick={() => handleViewJob(job.id)}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-medium text-slate-900 text-sm truncate max-w-[130px]" title={job.keywords}>
                          {job.keywords}
                        </span>
                        <Badge variant={statusVariant(job.status)} className="text-[10px] px-1.5 h-5 capitalize">
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
                        <span className="text-xs font-semibold text-green-700">
                          {job.leads_created} leads
                        </span>
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
