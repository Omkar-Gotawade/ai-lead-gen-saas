import React, { useState, useEffect } from 'react';
import { 
  User, 
  Mail, 
  Lock, 
  Save, 
  Server, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  Key,
  Shield,
  Brain
} from 'lucide-react';
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent, 
  CardDescription, 
  CardFooter 
} from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { Alert, AlertDescription } from '../components/ui/Alert';
import api from '../api';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  // Profile State
  const [profile, setProfile] = useState({
    email: '',
    full_name: '',
    role: ''
  });

  // Password State
  const [passwords, setPasswords] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  // Email Provider State
  const [emailProvider, setEmailProvider] = useState(null);
  const [providerForm, setProviderForm] = useState({
    type: 'smtp',
    smtp_server: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    sendgrid_api_key: '',
    from_email: '',
    from_name: ''
  });

  // AI Configuration State
  const [aiConfig, setAiConfig] = useState({
    api_key: '',
    has_key: false
  });

  useEffect(() => {
    fetchProfile();
    fetchEmailProvider();
    fetchAiConfig();
    // Clear any existing messages when component mounts
    setMessage({ type: '', text: '' });
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await api.get('/auth/me');
      setProfile({
        email: res.data.email,
        full_name: res.data.full_name || '',
        role: res.data.role || 'user'
      });
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const fetchEmailProvider = async () => {
    try {
      const res = await api.get('/api/email-provider/me');
      if (res.data) {
        console.log('Fetched email provider:', res.data);
        setEmailProvider(res.data);
        setProviderForm({
          type: res.data.provider_type || 'smtp',
          smtp_server: res.data.smtp_server || '',
          smtp_port: res.data.smtp_port || 587,
          smtp_username: res.data.smtp_username || '',
          smtp_password: '', // Don't show existing password
          sendgrid_api_key: '', // Don't show existing API key
          from_email: res.data.from_email || '',
          from_name: res.data.from_name || ''
        });
        // Clear any error messages when provider is loaded successfully
        setMessage({ type: '', text: '' });
      }
    } catch (error) {
      // It's okay if no provider exists yet - don't show error message
      console.log('No email provider configured');
      // Don't set an error message here
    }
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });
    
    try {
      await api.put('/auth/profile', {
        full_name: profile.full_name,
        email: profile.email
      });
      setMessage({ type: 'success', text: 'Profile updated successfully' });
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to update profile' });
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (passwords.new_password !== passwords.confirm_password) {
      setMessage({ type: 'error', text: 'New passwords do not match' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      await api.post('/auth/change-password', {
        current_password: passwords.current_password,
        new_password: passwords.new_password
      });
      setMessage({ type: 'success', text: 'Password changed successfully' });
      setPasswords({ current_password: '', new_password: '', confirm_password: '' });
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to change password' });
    } finally {
      setLoading(false);
    }
  };

  const handleProviderSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const payload = { provider_type: providerForm.type };
      
      if (providerForm.type === 'smtp') {
        payload.smtp_host = providerForm.smtp_server;
        payload.smtp_port = providerForm.smtp_port;
        payload.smtp_username = providerForm.smtp_username;
        // Only send password if it's not empty (for updates)
        if (providerForm.smtp_password) {
          payload.smtp_password = providerForm.smtp_password;
        } else if (!emailProvider) {
          // Password is required for new SMTP configuration
          setMessage({ type: 'error', text: 'Password is required for new SMTP configuration' });
          setLoading(false);
          return;
        }
      } else if (providerForm.type === 'sendgrid') {
        // Only send API key if it's not empty (for updates)
        if (providerForm.sendgrid_api_key) {
          payload.sendgrid_api_key = providerForm.sendgrid_api_key;
        } else if (!emailProvider) {
          // API key is required for new SendGrid configuration
          setMessage({ type: 'error', text: 'API key is required for new SendGrid configuration' });
          setLoading(false);
          return;
        }
      }
      
      // Common fields
      payload.from_email = providerForm.from_email;
      payload.from_name = providerForm.from_name;

      console.log('Sending payload:', { ...payload, smtp_password: payload.smtp_password ? '****' : undefined, sendgrid_api_key: payload.sendgrid_api_key ? '****' : undefined });
      
      const response = await api.post('/api/email-provider/connect', payload);
      setMessage({ type: 'success', text: 'Email provider configured successfully' });
      
      // Reload the provider data after successful save
      await fetchEmailProvider();
    } catch (error) {
      console.error('Error configuring provider:', error);
      const errorDetail = error.response?.data?.detail;
      const errorMessage = typeof errorDetail === 'string' 
        ? errorDetail 
        : (Array.isArray(errorDetail) ? errorDetail.map(e => e.msg || e).join(', ') : 'Failed to configure email provider');
      setMessage({ type: 'error', text: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProvider = async () => {
    if (!window.confirm('Are you sure you want to remove this email provider?')) return;
    
    setLoading(true);
    try {
      await api.delete('/api/email-provider/me');
      setEmailProvider(null);
      setProviderForm({
        type: 'smtp',
        smtp_server: '',
        smtp_port: 587,
        smtp_username: '',
        smtp_password: '',
        sendgrid_api_key: '',
        from_email: '',
        from_name: ''
      });
      setMessage({ type: 'success', text: 'Email provider removed' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to remove provider' });
    } finally {
      setLoading(false);
    }
  };

  const fetchAiConfig = async () => {
    try {
      const res = await api.get('/api/ai-config/me');
      if (res.data) {
        console.log('Fetched AI config:', { has_key: !!res.data.api_key });
        setAiConfig({
          api_key: '', // Don't show existing key
          has_key: !!res.data.api_key
        });
      }
    } catch (error) {
      console.log('No AI configuration found');
    }
  };

  const handleAiConfigSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const payload = {};
      
      // Only send API key if it's not empty
      if (aiConfig.api_key) {
        payload.api_key = aiConfig.api_key;
      } else if (!aiConfig.has_key) {
        setMessage({ type: 'error', text: 'API key is required for AI configuration' });
        setLoading(false);
        return;
      }

      console.log('Saving AI config');
      
      await api.post('/api/ai-config/configure', payload);
      setMessage({ type: 'success', text: 'AI configuration saved successfully' });
      fetchAiConfig();
    } catch (error) {
      console.error('Error saving AI config:', error);
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to save AI configuration' });
    } finally {
      setLoading(false);
    }
  };

  const TabButton = ({ id, label, icon: Icon }) => (
    <button
      onClick={() => setActiveTab(id)}
      className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px ${
        activeTab === id
          ? 'border-brand-600 text-brand-700'
          : 'border-transparent text-ink-500 hover:text-ink-800 hover:border-ink-200'
      }`}
    >
      <Icon className="h-3.5 w-3.5" />
      {label}
    </button>
  );

  return (
    <div className="p-6 space-y-5 max-w-[1400px] mx-auto">
      <div>
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle mt-0.5">Manage your account and application preferences</p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 border-b border-ink-100 pb-0">
        <TabButton id="profile" label="Profile" icon={User} />
        <TabButton id="security" label="Security" icon={Shield} />
        <TabButton id="email" label="Email Provider" icon={Mail} />
        <TabButton id="ai" label="AI Configuration" icon={Brain} />
      </div>

      {/* Messages */}
      {message.text && (
        <Alert variant={message.type === 'error' ? 'destructive' : 'default'}>
          {message.type === 'success' ? <CheckCircle className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <Card>
          <CardHeader>
            <CardTitle>Profile Information</CardTitle>
            <CardDescription>Update your personal details.</CardDescription>
          </CardHeader>
          <form onSubmit={handleProfileUpdate}>
            <CardContent className="space-y-4">
              <Input
                label="Full Name"
                value={profile.full_name}
                onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                placeholder="John Doe"
              />
              <Input
                label="Email Address"
                type="email"
                value={profile.email}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                disabled
                helperText="Email address cannot be changed directly."
              />
              <Input
                label="Role"
                value={profile.role}
                disabled
                className="bg-slate-50"
              />
            </CardContent>
            <CardFooter>
              <Button type="submit" isLoading={loading} icon={<Save className="w-4 h-4" />}>
                Save Changes
              </Button>
            </CardFooter>
          </form>
        </Card>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <Card>
          <CardHeader>
            <CardTitle>Password</CardTitle>
            <CardDescription>Change your account password.</CardDescription>
          </CardHeader>
          <form onSubmit={handlePasswordChange}>
            <CardContent className="space-y-4">
              <Input
                label="Current Password"
                type="password"
                value={passwords.current_password}
                onChange={(e) => setPasswords({ ...passwords, current_password: e.target.value })}
                required
              />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="New Password"
                  type="password"
                  value={passwords.new_password}
                  onChange={(e) => setPasswords({ ...passwords, new_password: e.target.value })}
                  required
                />
                <Input
                  label="Confirm New Password"
                  type="password"
                  value={passwords.confirm_password}
                  onChange={(e) => setPasswords({ ...passwords, confirm_password: e.target.value })}
                  required
                />
              </div>
            </CardContent>
            <CardFooter>
              <Button type="submit" isLoading={loading} icon={<Lock className="w-4 h-4" />}>
                Update Password
              </Button>
            </CardFooter>
          </form>
        </Card>
      )}

      {/* Email Provider Tab */}
      {activeTab === 'email' && (
        <div className="space-y-6">
          {emailProvider && (
            <Alert className="bg-green-50 border-green-200 text-green-800">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription>
                Active Provider: <strong>{emailProvider.provider_type?.toUpperCase() || 'N/A'}</strong>
                {emailProvider.provider_type === 'sendgrid' && emailProvider.from_email && ` (${emailProvider.from_email})`}
                {emailProvider.provider_type === 'smtp' && emailProvider.smtp_server && ` (${emailProvider.smtp_server})`}
                {emailProvider.provider_type === 'smtp' && !emailProvider.smtp_server && emailProvider.from_email && ` (${emailProvider.from_email})`}
              </AlertDescription>
            </Alert>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Email Provider Configuration</CardTitle>
              <CardDescription>Configure SMTP or SendGrid for email sending.</CardDescription>
            </CardHeader>
            <form onSubmit={handleProviderSave}>
              <CardContent className="space-y-4">
                {/* Provider Type Selector */}
                <div>
                  <label className="block text-xs font-medium text-ink-600 mb-2">Provider Type</label>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-2 cursor-pointer group">
                      <input
                        type="radio"
                        name="provider_type"
                        value="smtp"
                        checked={providerForm.type === 'smtp'}
                        onChange={(e) => setProviderForm({ ...providerForm, type: e.target.value })}
                        className="text-brand-600 border-ink-300 focus:ring-brand-500"
                      />
                      <span className="text-sm font-medium text-ink-700 group-hover:text-ink-900 transition-colors">SMTP Server</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer group">
                      <input
                        type="radio"
                        name="provider_type"
                        value="sendgrid"
                        checked={providerForm.type === 'sendgrid'}
                        onChange={(e) => setProviderForm({ ...providerForm, type: e.target.value })}
                        className="text-brand-600 border-ink-300 focus:ring-brand-500"
                      />
                      <span className="text-sm font-medium text-ink-700 group-hover:text-ink-900 transition-colors">SendGrid</span>
                    </label>
                  </div>
                </div>

                {/* SMTP Fields */}
                {providerForm.type === 'smtp' && (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Input
                        label="SMTP Server"
                        value={providerForm.smtp_server}
                        onChange={(e) => setProviderForm({ ...providerForm, smtp_server: e.target.value })}
                        placeholder="smtp.gmail.com"
                        required
                      />
                      <Input
                        label="SMTP Port"
                        type="number"
                        value={providerForm.smtp_port}
                        onChange={(e) => setProviderForm({ ...providerForm, smtp_port: parseInt(e.target.value) })}
                        placeholder="587"
                        required
                      />
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Input
                        label="Username"
                        value={providerForm.smtp_username}
                        onChange={(e) => setProviderForm({ ...providerForm, smtp_username: e.target.value })}
                        placeholder="user@example.com"
                        required
                      />
                      <Input
                        label="Password"
                        type="password"
                        value={providerForm.smtp_password}
                        onChange={(e) => setProviderForm({ ...providerForm, smtp_password: e.target.value })}
                        placeholder={emailProvider && emailProvider.type === 'smtp' ? "••••••••" : "Enter password"}
                        helperText={emailProvider && emailProvider.type === 'smtp' ? "Leave blank to keep current password" : ""}
                        required={!emailProvider || emailProvider.type !== 'smtp'}
                      />
                    </div>
                  </>
                )}

                {/* SendGrid Fields */}
                {providerForm.type === 'sendgrid' && (
                  <div>
                    <Input
                      label="SendGrid API Key"
                      type="password"
                      value={providerForm.sendgrid_api_key}
                      onChange={(e) => setProviderForm({ ...providerForm, sendgrid_api_key: e.target.value })}
                      placeholder={emailProvider && emailProvider.type === 'sendgrid' ? "••••••••" : "SG.xxxxxxxxxxxxxxxxxxxxx"}
                      helperText={emailProvider && emailProvider.type === 'sendgrid' ? "Leave blank to keep current API key" : "Get your API key from SendGrid dashboard"}
                      required={!emailProvider || emailProvider.type !== 'sendgrid'}
                    />
                  </div>
                )}

                {/* Common Fields */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="From Email"
                    type="email"
                    value={providerForm.from_email}
                    onChange={(e) => setProviderForm({ ...providerForm, from_email: e.target.value })}
                    placeholder="sender@example.com"
                    required
                  />
                  <Input
                    label="From Name"
                    value={providerForm.from_name}
                    onChange={(e) => setProviderForm({ ...providerForm, from_name: e.target.value })}
                    placeholder="My Company"
                  />
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button type="submit" isLoading={loading} icon={<Server className="w-4 h-4" />}>
                  Save Configuration
                </Button>
                {emailProvider && (
                  <Button 
                    type="button" 
                    variant="destructive" 
                    onClick={handleDeleteProvider}
                    disabled={loading}
                  >
                    Remove Provider
                  </Button>
                )}
              </CardFooter>
            </form>
          </Card>
        </div>
      )}

      {/* AI Configuration Tab */}
      {activeTab === 'ai' && (
        <div className="space-y-6">
          <Alert className="bg-blue-50 border-blue-200 text-blue-800">
            <Brain className="h-4 w-4 text-blue-600" />
            <AlertDescription>
              Configure AI providers for email personalization and content generation. API keys are encrypted and stored securely.
            </AlertDescription>
          </Alert>

          <Card>
            <CardHeader>
              <CardTitle>AI Provider Configuration</CardTitle>
              <CardDescription>Configure API keys for AI-powered email generation.</CardDescription>
            </CardHeader>
            <form onSubmit={handleAiConfigSave}>
              <CardContent className="space-y-4">
                {/* API Key */}
                <Input
                  label="AI API Key"
                  type="password"
                  value={aiConfig.api_key}
                  onChange={(e) => setAiConfig({ ...aiConfig, api_key: e.target.value })}
                  placeholder={aiConfig.has_key ? "••••••••" : "Enter your API key"}
                  helperText={aiConfig.has_key ? "✓ Configured - Leave blank to keep current key" : "Enter your Gemini, OpenAI, or Anthropic API key"}
                  required={!aiConfig.has_key}
                />

                <div className="bg-ink-50 p-4 rounded-xl border border-ink-100">
                  <h4 className="text-sm font-semibold text-ink-900 mb-2">How API Keys Are Used</h4>
                  <ul className="text-sm text-ink-500 space-y-1 list-disc list-inside">
                    <li>Generate personalized email content based on lead information</li>
                    <li>Create follow-up sequences with AI assistance</li>
                    <li>Optimize subject lines and email bodies</li>
                    <li>All API keys are encrypted before storage</li>
                  </ul>
                </div>
              </CardContent>
              <CardFooter>
                <Button type="submit" isLoading={loading} icon={<Save className="w-4 h-4" />}>
                  Save AI Configuration
                </Button>
              </CardFooter>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
};

export default Settings;
