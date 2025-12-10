import axios from './axios';

export async function generateEmail(data) {
  const response = await axios.post('/api/generate-email', data);
  return response.data;
}

export async function sendEmail(data) {
  const response = await axios.post('/api/email/send', data);
  return response.data;
}

export async function sendTestEmail(data) {
  const response = await axios.post('/api/email/send-test', data);
  return response.data;
}

export async function connectEmailProvider(data) {
  const response = await axios.post('/api/email-provider/connect', data);
  return response.data;
}

export async function getEmailProvider() {
  const response = await axios.get('/api/email-provider/me');
  return response.data;
}

export async function testEmailProvider(data) {
  const response = await axios.post('/api/email-provider/test', data);
  return response.data;
}

export async function getEmailLogs(leadId) {
  const response = await axios.get(`/api/email/logs?lead_id=${leadId}`);
  return response.data;
}
