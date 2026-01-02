import api from './axios'

// Authentication API
export const authAPI = {
  register: (email, password) =>
    api.post('/auth/register', { email, password }),
  
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
}

// Leads API
export const leadsAPI = {
  getLeads: (page = 1, pageSize = 50) =>
    api.get('/leads', { params: { page, page_size: pageSize } }),
  
  getLead: (id) =>
    api.get(`/leads/${id}`),
  
  createLead: (data) =>
    api.post('/leads', data),
  
  updateLead: (id, data) =>
    api.put(`/leads/${id}`, data),
  
  deleteLead: (id) =>
    api.delete(`/leads/${id}`),
  
  uploadCSV: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/leads/upload_csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  
  enrichLead: (id) =>
    api.post(`/leads/${id}/enrich`),
}

export default api
