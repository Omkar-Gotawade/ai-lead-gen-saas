import React, { useState, useEffect, useCallback } from 'react';
import {
  User,
  Mail,
  Lock,
  Save,
  Server,
  CheckCircle,
  AlertCircle,
  Key,
  Shield,
  Brain,
  Trash2
} from 'lucide-react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardDescription,
  CardFooter,
} from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import PasswordInput from '../components/ui/PasswordInput';
import ConfirmDialog from '../components/ui/ConfirmDialog';
import { Tabs, TabList, Tab, TabPanel } from '../components/ui/Tabs';
import { useToast } from '../context/ToastContext';
import api from '../api';

const Settings = () => {
  const toast = useToast();
  const [loading, setLoading] = useState(false);

  // Profile State
  const [profile, setProfile] = useState({ email: '', full_name: '', role: '' });

  // Password State
  const [passwords, setPasswords] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
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
    from_name: '',
  });
  const [showDeleteProvider, setShowDeleteProvider] = useState(false);

  // AI Configuration State
  const [aiConfig, setAiConfig] = useState({ api_key: '', has_key: false });

  /* ─── Data fetching ─────────────────────────────────────────── */
  const fetchProfile = useCallback(async () => {
    try {
      const res = await api.get('/auth/me');
      setProfile({
        email: res.data.email,
        full_name: res.data.full_name || '',
        role: res.data.role || 'user',
      });
    } catch {
      // Silently handled — user session is validated by ProtectedRoute
    }
  }, []);

  const fetchEmailProvider = useCallback(async () => {
    try {
      const res = await api.get('/api/email-provider/me');
      if (res.data) {
        setEmailProvider(res.data);
        setProviderForm({
          type: res.data.provider_type || 'smtp',
          smtp_server: res.data.smtp_server || '',
          smtp_port: res.data.smtp_port || 587,
          smtp_username: res.data.smtp_username || '',
          smtp_password: '',
          sendgrid_api_key: '',
          from_email: res.data.from_email || '',
          from_name: res.data.from_name || '',
        });
      }
    } catch {
      // No provider configured yet — that's fine
    }
  }, []);

  const fetchAiConfig = useCallback(async () => {
    try {
      const res = await api.get('/api/ai-config/me');
      if (res.data) {
        setAiConfig({ api_key: '', has_key: !!res.data.api_key });
      }
    } catch {
      // No AI config yet
    }
  }, []);

  useEffect(() => {
    fetchProfile();
    fetchEmailProvider();
    fetchAiConfig();
  }, [fetchProfile, fetchEmailProvider, fetchAiConfig]);

  /* ─── Handlers ──────────────────────────────────────────────── */
  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.put('/auth/profile', {
        full_name: profile.full_name,
        email: profile.email,
      });
      toast.success('Profile updated successfully');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (passwords.new_password !== passwords.confirm_password) {
      toast.error('New passwords do not match');
      return;
    }
    setLoading(true);
    try {
      await api.post('/auth/change-password', {
        current_password: passwords.current_password,
        new_password: passwords.new_password,
      });
      toast.success('Password changed successfully');
      setPasswords({ current_password: '', new_password: '', confirm_password: '' });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const handleProviderSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = { provider_type: providerForm.type };

      if (providerForm.type === 'smtp') {
        payload.smtp_host = providerForm.smtp_server;
        payload.smtp_port = providerForm.smtp_port;
        payload.smtp_username = providerForm.smtp_username;
        if (providerForm.smtp_password) {
          payload.smtp_password = providerForm.smtp_password;
        } else if (!emailProvider) {
          toast.error('Password is required for new SMTP configuration');
          setLoading(false);
          return;
        }
      } else if (providerForm.type === 'sendgrid') {
        if (providerForm.sendgrid_api_key) {
          payload.sendgrid_api_key = providerForm.sendgrid_api_key;
        } else if (!emailProvider) {
          toast.error('API key is required for new SendGrid configuration');
          setLoading(false);
          return;
        }
      }

      payload.from_email = providerForm.from_email;
      payload.from_name = providerForm.from_name;

      await api.post('/api/email-provider/connect', payload);
      toast.success('Email provider configured successfully');
      await fetchEmailProvider();
    } catch (error) {
      const detail = error.response?.data?.detail;
      const msg =
        typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
          ? detail.map((e) => e.msg || e).join(', ')
          : 'Failed to configure email provider';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProvider = async () => {
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
        from_name: '',
      });
      toast.success('Email provider removed');
    } catch {
      toast.error('Failed to remove provider');
    } finally {
      setLoading(false);
      setShowDeleteProvider(false);
    }
  };

  const handleAiConfigSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {};
      if (aiConfig.api_key) {
        payload.api_key = aiConfig.api_key;
      } else if (!aiConfig.has_key) {
        toast.error('API key is required for AI configuration');
        setLoading(false);
        return;
      }
      await api.post('/api/ai-config/configure', payload);
      toast.success('AI configuration saved successfully');
      fetchAiConfig();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save AI configuration');
    } finally {
      setLoading(false);
    }
  };

  /* ─── Render ────────────────────────────────────────────────── */
  return (
    <div className="p-6 space-y-5 max-w-[1400px] mx-auto">
      <div>
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle mt-0.5">Manage your account and application preferences</p>
      </div>

      <Tabs defaultTab="profile">
        <TabList>
          <Tab id="profile" icon={User}>Profile</Tab>
          <Tab id="security" icon={Shield}>Security</Tab>
          <Tab id="email" icon={Mail}>Email Provider</Tab>
          <Tab id="ai" icon={Brain}>AI Configuration</Tab>
        </TabList>

        {/* ── Profile ── */}
        <TabPanel id="profile" className="pt-5">
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
                  className="bg-ink-50"
                />
              </CardContent>
              <CardFooter>
                <Button type="submit" isLoading={loading} icon={<Save className="w-4 h-4" />}>
                  Save Changes
                </Button>
              </CardFooter>
            </form>
          </Card>
        </TabPanel>

        {/* ── Security ── */}
        <TabPanel id="security" className="pt-5">
          <Card>
            <CardHeader>
              <CardTitle>Password</CardTitle>
              <CardDescription>Change your account password.</CardDescription>
            </CardHeader>
            <form onSubmit={handlePasswordChange}>
              <CardContent className="space-y-4">
                <PasswordInput
                  label="Current Password"
                  value={passwords.current_password}
                  onChange={(e) => setPasswords({ ...passwords, current_password: e.target.value })}
                  required
                />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <PasswordInput
                    label="New Password"
                    value={passwords.new_password}
                    onChange={(e) => setPasswords({ ...passwords, new_password: e.target.value })}
                    required
                  />
                  <PasswordInput
                    label="Confirm New Password"
                    value={passwords.confirm_password}
                    onChange={(e) =>
                      setPasswords({ ...passwords, confirm_password: e.target.value })
                    }
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
        </TabPanel>

        {/* ── Email Provider ── */}
        <TabPanel id="email" className="pt-5">
          <div className="space-y-6">
            {emailProvider && (
              <div className="flex items-center gap-2.5 px-4 py-3 bg-success/10 border border-success/25 rounded-xl text-sm">
                <CheckCircle className="h-4 w-4 text-success shrink-0" />
                <span className="text-ink-700">
                  Active Provider:{' '}
                  <strong className="text-ink-900">
                    {emailProvider.provider_type?.toUpperCase() || 'N/A'}
                  </strong>
                  {emailProvider.smtp_host && ` — ${emailProvider.smtp_host}`}
                  {!emailProvider.smtp_host && emailProvider.from_email && ` — ${emailProvider.from_email}`}
                </span>
              </div>
            )}

            <Card>
              <CardHeader>
                <CardTitle>Email Provider Configuration</CardTitle>
                <CardDescription>Configure SMTP or SendGrid for email sending.</CardDescription>
              </CardHeader>
              <form onSubmit={handleProviderSave}>
                <CardContent className="space-y-4">
                  {/* Provider selector */}
                  <div>
                    <label className="block text-xs font-medium text-ink-600 mb-2">
                      Provider Type
                    </label>
                    <div className="flex gap-4">
                      {[
                        { value: 'smtp', label: 'SMTP Server' },
                        { value: 'sendgrid', label: 'SendGrid' },
                      ].map(({ value, label }) => (
                        <label key={value} className="flex items-center gap-2 cursor-pointer group">
                          <input
                            type="radio"
                            name="provider_type"
                            value={value}
                            checked={providerForm.type === value}
                            onChange={(e) =>
                              setProviderForm({ ...providerForm, type: e.target.value })
                            }
                            className="text-brand-600 border-ink-300 focus:ring-brand-500"
                          />
                          <span className="text-sm font-medium text-ink-700 group-hover:text-ink-900 transition-colors">
                            {label}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* SMTP fields */}
                  {providerForm.type === 'smtp' && (
                    <>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Input
                          label="SMTP Server"
                          value={providerForm.smtp_server}
                          onChange={(e) =>
                            setProviderForm({ ...providerForm, smtp_server: e.target.value })
                          }
                          placeholder="smtp.gmail.com"
                          required
                        />
                        <Input
                          label="SMTP Port"
                          type="number"
                          value={providerForm.smtp_port}
                          onChange={(e) =>
                            setProviderForm({
                              ...providerForm,
                              smtp_port: parseInt(e.target.value),
                            })
                          }
                          placeholder="587"
                          required
                        />
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Input
                          label="Username"
                          value={providerForm.smtp_username}
                          onChange={(e) =>
                            setProviderForm({ ...providerForm, smtp_username: e.target.value })
                          }
                          placeholder="user@example.com"
                          required
                        />
                        <PasswordInput
                          label="Password"
                          value={providerForm.smtp_password}
                          onChange={(e) =>
                            setProviderForm({ ...providerForm, smtp_password: e.target.value })
                          }
                          placeholder={emailProvider ? '••••••••' : 'Enter password'}
                          helperText={emailProvider ? 'Leave blank to keep current password' : ''}
                          required={!emailProvider}
                        />
                      </div>
                    </>
                  )}

                  {/* SendGrid fields */}
                  {providerForm.type === 'sendgrid' && (
                    <PasswordInput
                      label="SendGrid API Key"
                      value={providerForm.sendgrid_api_key}
                      onChange={(e) =>
                        setProviderForm({ ...providerForm, sendgrid_api_key: e.target.value })
                      }
                      placeholder={emailProvider ? '••••••••' : 'SG.xxxxxxxxxxxxxxxxxxxxx'}
                      helperText={
                        emailProvider
                          ? 'Leave blank to keep current API key'
                          : 'Get your API key from SendGrid dashboard'
                      }
                      required={!emailProvider}
                    />
                  )}

                  {/* Common fields */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label="From Email"
                      type="email"
                      value={providerForm.from_email}
                      onChange={(e) =>
                        setProviderForm({ ...providerForm, from_email: e.target.value })
                      }
                      placeholder="sender@example.com"
                      required
                    />
                    <Input
                      label="From Name"
                      value={providerForm.from_name}
                      onChange={(e) =>
                        setProviderForm({ ...providerForm, from_name: e.target.value })
                      }
                      placeholder="My Company"
                    />
                  </div>
                </CardContent>
                <CardFooter className="flex justify-between">
                  <Button
                    type="submit"
                    isLoading={loading}
                    icon={<Server className="w-4 h-4" />}
                  >
                    Save Configuration
                  </Button>
                  {emailProvider && (
                    <Button
                      type="button"
                      variant="destructive"
                      onClick={() => setShowDeleteProvider(true)}
                      disabled={loading}
                      icon={<Trash2 className="w-4 h-4" />}
                    >
                      Remove Provider
                    </Button>
                  )}
                </CardFooter>
              </form>
            </Card>
          </div>
        </TabPanel>

        {/* ── AI Configuration ── */}
        <TabPanel id="ai" className="pt-5">
          <div className="space-y-6">
            <div className="flex items-start gap-3 px-4 py-3 bg-brand-50 border border-brand-100 rounded-xl text-sm">
              <Brain className="h-4 w-4 text-brand-600 mt-0.5 shrink-0" />
              <p className="text-ink-600">
                Configure AI providers for email personalization and content generation. API keys
                are encrypted and stored securely.
              </p>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>AI Provider Configuration</CardTitle>
                <CardDescription>Configure API keys for AI-powered email generation.</CardDescription>
              </CardHeader>
              <form onSubmit={handleAiConfigSave}>
                <CardContent className="space-y-4">
                  <PasswordInput
                    label="AI API Key"
                    value={aiConfig.api_key}
                    onChange={(e) => setAiConfig({ ...aiConfig, api_key: e.target.value })}
                    placeholder={aiConfig.has_key ? '••••••••' : 'Enter your API key'}
                    helperText={
                      aiConfig.has_key
                        ? '✓ Configured — Leave blank to keep current key'
                        : 'Enter your Gemini, OpenAI, or Anthropic API key'
                    }
                    required={!aiConfig.has_key}
                  />
                  <div className="bg-ink-50 p-4 rounded-xl border border-ink-100">
                    <h4 className="text-sm font-semibold text-ink-900 mb-2">
                      How API Keys Are Used
                    </h4>
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
        </TabPanel>
      </Tabs>

      {/* Confirm remove provider dialog */}
      <ConfirmDialog
        isOpen={showDeleteProvider}
        onClose={() => setShowDeleteProvider(false)}
        onConfirm={handleDeleteProvider}
        title="Remove Email Provider"
        description="Are you sure you want to remove this email provider? Your campaigns will stop sending emails until you configure a new provider."
        confirmLabel="Remove Provider"
        variant="destructive"
      />
    </div>
  );
};

export default Settings;
