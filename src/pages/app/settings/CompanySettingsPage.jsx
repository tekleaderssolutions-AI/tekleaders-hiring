import React from 'react';
import { Input, Button } from '@/components/ui';
export default function CompanySettingsPage() {
  return (
    <div className="settings-page">
      <div className="settings-content">
        <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-8)' }}>Company Settings</h1>
        <div className="settings-section">
          <h3 className="settings-section-title">General Information</h3>
          <Input label="Company Name" placeholder="Acme Inc." />
          <Input label="Website" placeholder="https://acme.com" />
          <Input label="Industry" placeholder="Technology" />
          <Input label="Company Size" placeholder="50-200" />
        </div>
        <div className="settings-section">
          <h3 className="settings-section-title">Branding</h3>
          <Input label="Primary Color" type="color" />
          <Input label="Logo URL" placeholder="https://..." />
        </div>
        <Button variant="primary">Save Changes</Button>
      </div>
    </div>
  );
}
