import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import KanbanBoard from '@/components/jobs/KanbanBoard';
import CandidateDrawer from '@/components/jobs/CandidateDrawer';

const mockCandidates = [
  { id:1, name:'Sarah Chen', role:'Frontend Dev', stage:'screening', aiScore:92, email:'sarah@test.com', location:'Remote' },
  { id:2, name:'James Wilson', role:'Frontend Dev', stage:'screening', aiScore:85, email:'james@test.com', location:'NYC' },
  { id:3, name:'Emily Ross', role:'Frontend Dev', stage:'interview', aiScore:78, email:'emily@test.com', location:'London' },
  { id:4, name:'Alex Kumar', role:'Frontend Dev', stage:'applied', aiScore:65, email:'alex@test.com', location:'Berlin' },
  { id:5, name:'Maria Garcia', role:'Frontend Dev', stage:'assessment', aiScore:88, email:'maria@test.com', location:'Remote' },
  { id:6, name:'David Park', role:'Frontend Dev', stage:'offer', aiScore:95, email:'david@test.com', location:'SF' },
  { id:7, name:'Lisa Wang', role:'Frontend Dev', stage:'applied', aiScore:72, email:'lisa@test.com', location:'Toronto' },
];

export default function JobPipelinePage() {
  const { id } = useParams();
  const [selected, setSelected] = useState(null);
  return (
    <div style={{ padding:'var(--spacing-6)' }}>
      <div style={{ marginBottom:'var(--spacing-6)' }}>
        <h1 style={{ fontSize:'var(--text-2xl)', fontWeight:'var(--weight-bold)' }}>Pipeline — Job #{id}</h1>
        <p style={{ color:'var(--color-text-muted)', fontSize:'var(--text-sm)', marginTop:4 }}>{mockCandidates.length} candidates in pipeline</p>
      </div>
      <KanbanBoard candidates={mockCandidates} onCardClick={setSelected} />
      {selected && <CandidateDrawer candidate={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
