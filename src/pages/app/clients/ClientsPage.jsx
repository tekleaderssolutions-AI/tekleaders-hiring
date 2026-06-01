import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Building2, Phone, Mail, User, Edit2, Check, X } from 'lucide-react';
import api from '@/lib/api';

function useClients() {
  return useQuery({
    queryKey: ['clients'],
    queryFn: () => api.get('/clients').then(r => r.data),
  });
}

function useCreateClient() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post('/clients', data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['clients'] }),
  });
}

function useUpdateClient() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }) => api.patch(`/clients/${id}`, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['clients'] }),
  });
}

const STATUS_COLOR = { active: '#059669', inactive: '#9ca3af' };

export default function ClientsPage() {
  const { data: clients = [], isLoading } = useClients();
  const createClient = useCreateClient();
  const updateClient = useUpdateClient();
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({ name: '', contact_name: '', contact_email: '', contact_phone: '' });
  const [editForm, setEditForm] = useState({});

  const handleCreate = async () => {
    if (!form.name.trim()) return;
    await createClient.mutateAsync(form);
    setForm({ name: '', contact_name: '', contact_email: '', contact_phone: '' });
    setShowForm(false);
  };

  const handleEdit = (client) => {
    setEditingId(client.id);
    setEditForm({ name: client.name, contact_name: client.contact_name || '', contact_email: client.contact_email || '', contact_phone: client.contact_phone || '' });
  };

  const handleSave = async (id) => {
    await updateClient.mutateAsync({ id, ...editForm });
    setEditingId(null);
  };

  return (
    <div style={{ padding: '32px 40px', maxWidth: 900, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: '#111827', margin: 0 }}>Clients</h1>
          <p style={{ color: '#6b7280', marginTop: 4, fontSize: 14 }}>Manage your recruitment clients</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          style={{ display: 'flex', alignItems: 'center', gap: 8, background: 'var(--color-primary, #00756a)', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 18px', fontSize: 14, fontWeight: 600, cursor: 'pointer' }}
        >
          <Plus size={16} /> Add Client
        </button>
      </div>

      {/* Create Form */}
      {showForm && (
        <div style={{ background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 12, padding: 24, marginBottom: 24 }}>
          <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16, color: '#111827' }}>New Client</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Client Name *</label>
              <input
                value={form.name}
                onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                placeholder="e.g. Accenture"
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 14, boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Contact Name</label>
              <input
                value={form.contact_name}
                onChange={e => setForm(f => ({ ...f, contact_name: e.target.value }))}
                placeholder="Point of contact"
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 14, boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Email</label>
              <input
                value={form.contact_email}
                onChange={e => setForm(f => ({ ...f, contact_email: e.target.value }))}
                placeholder="contact@client.com"
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 14, boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label style={{ fontSize: 12, fontWeight: 600, color: '#374151', display: 'block', marginBottom: 4 }}>Phone</label>
              <input
                value={form.contact_phone}
                onChange={e => setForm(f => ({ ...f, contact_phone: e.target.value }))}
                placeholder="+91 9876543210"
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 14, boxSizing: 'border-box' }}
              />
            </div>
          </div>
          <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
            <button
              onClick={handleCreate}
              disabled={createClient.isPending}
              style={{ background: '#00756a', color: '#fff', border: 'none', borderRadius: 6, padding: '8px 20px', fontSize: 14, fontWeight: 600, cursor: 'pointer' }}
            >
              {createClient.isPending ? 'Saving...' : 'Save Client'}
            </button>
            <button
              onClick={() => { setShowForm(false); setForm({ name: '', contact_name: '', contact_email: '', contact_phone: '' }); }}
              style={{ background: '#fff', color: '#374151', border: '1px solid #d1d5db', borderRadius: 6, padding: '8px 20px', fontSize: 14, cursor: 'pointer' }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Clients List */}
      {isLoading ? (
        <div style={{ textAlign: 'center', color: '#9ca3af', padding: 48 }}>Loading clients...</div>
      ) : clients.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#9ca3af', padding: 64, border: '2px dashed #e5e7eb', borderRadius: 12 }}>
          <Building2 size={40} style={{ opacity: 0.3, marginBottom: 12 }} />
          <div style={{ fontSize: 16, fontWeight: 600 }}>No clients yet</div>
          <div style={{ fontSize: 13, marginTop: 4 }}>Add your first client to get started</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {clients.map(client => (
            <div key={client.id} style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: '20px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              {editingId === client.id ? (
                <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginRight: 16 }}>
                  <input value={editForm.name} onChange={e => setEditForm(f => ({ ...f, name: e.target.value }))} placeholder="Name" style={{ padding: '6px 10px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 13 }} />
                  <input value={editForm.contact_name} onChange={e => setEditForm(f => ({ ...f, contact_name: e.target.value }))} placeholder="Contact" style={{ padding: '6px 10px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 13 }} />
                  <input value={editForm.contact_email} onChange={e => setEditForm(f => ({ ...f, contact_email: e.target.value }))} placeholder="Email" style={{ padding: '6px 10px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 13 }} />
                  <input value={editForm.contact_phone} onChange={e => setEditForm(f => ({ ...f, contact_phone: e.target.value }))} placeholder="Phone" style={{ padding: '6px 10px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 13 }} />
                </div>
              ) : (
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                    <Building2 size={18} color="#00756a" />
                    <span style={{ fontSize: 16, fontWeight: 700, color: '#111827' }}>{client.name}</span>
                    <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 20, background: STATUS_COLOR[client.status] + '20', color: STATUS_COLOR[client.status], fontWeight: 600, textTransform: 'uppercase' }}>
                      {client.status}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
                    {client.contact_name && (
                      <span style={{ fontSize: 13, color: '#6b7280', display: 'flex', alignItems: 'center', gap: 4 }}>
                        <User size={13} /> {client.contact_name}
                      </span>
                    )}
                    {client.contact_email && (
                      <span style={{ fontSize: 13, color: '#6b7280', display: 'flex', alignItems: 'center', gap: 4 }}>
                        <Mail size={13} /> {client.contact_email}
                      </span>
                    )}
                    {client.contact_phone && (
                      <span style={{ fontSize: 13, color: '#6b7280', display: 'flex', alignItems: 'center', gap: 4 }}>
                        <Phone size={13} /> {client.contact_phone}
                      </span>
                    )}
                  </div>
                </div>
              )}
              <div style={{ display: 'flex', gap: 8 }}>
                {editingId === client.id ? (
                  <>
                    <button onClick={() => handleSave(client.id)} style={{ background: '#059669', color: '#fff', border: 'none', borderRadius: 6, padding: '6px 14px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}>
                      <Check size={14} /> Save
                    </button>
                    <button onClick={() => setEditingId(null)} style={{ background: '#fff', color: '#374151', border: '1px solid #d1d5db', borderRadius: 6, padding: '6px 10px', cursor: 'pointer' }}>
                      <X size={14} />
                    </button>
                  </>
                ) : (
                  <button onClick={() => handleEdit(client)} style={{ background: '#f9fafb', color: '#374151', border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 12px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4, fontSize: 13 }}>
                    <Edit2 size={13} /> Edit
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
