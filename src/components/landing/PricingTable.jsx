import React from 'react';
import { Check } from 'lucide-react';
import { Button } from '@/components/ui';

const plans = [
  { name:'Starter', price:'$49', period:'/mo', desc:'For small teams getting started', features:['Up to 5 active jobs','AI screening (100/mo)','Email support','Basic analytics'], cta:'Start Free Trial' },
  { name:'Professional', price:'$149', period:'/mo', desc:'For growing teams', features:['Unlimited active jobs','AI screening (unlimited)','Priority support','Advanced analytics','API access','Custom pipelines'], cta:'Get Started', popular:true },
  { name:'Enterprise', price:'Custom', period:'', desc:'For large organizations', features:['Everything in Pro','SSO / SAML','Dedicated CSM','SLA guarantee','Custom integrations','On-prem deployment'], cta:'Contact Sales' },
];

export default function PricingTable() {
  return (
    <section style={{ padding:'var(--spacing-24) var(--spacing-6)', background:'var(--color-bg-secondary)' }}>
      <div style={{ maxWidth:1200, margin:'0 auto' }}>
        <div style={{ textAlign:'center', marginBottom:'var(--spacing-16)' }}>
          <span style={{ fontSize:'var(--text-sm)', fontWeight:'var(--weight-semibold)', color:'var(--color-primary)', textTransform:'uppercase', letterSpacing:'0.05em' }}>Pricing</span>
          <h2 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-4xl)', fontWeight:'var(--weight-bold)', marginTop:'var(--spacing-3)' }}>Simple, transparent pricing</h2>
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(300px, 1fr))', gap:'var(--spacing-6)', alignItems:'stretch' }}>
          {plans.map((plan) => (
            <div key={plan.name} className="card" style={{ padding:'var(--spacing-8)', display:'flex', flexDirection:'column', border: plan.popular ? '2px solid var(--color-primary)' : undefined, position:'relative' }}>
              {plan.popular && <div style={{ position:'absolute', top:-12, left:'50%', transform:'translateX(-50%)', background:'var(--gradient-primary)', color:'#fff', fontSize:'var(--text-xs)', fontWeight:'var(--weight-semibold)', padding:'4px 16px', borderRadius:'var(--radius-full)' }}>Most Popular</div>}
              <h3 style={{ fontSize:'var(--text-xl)', fontWeight:'var(--weight-bold)', marginBottom:'var(--spacing-2)' }}>{plan.name}</h3>
              <p style={{ fontSize:'var(--text-sm)', color:'var(--color-text-muted)', marginBottom:'var(--spacing-4)' }}>{plan.desc}</p>
              <div style={{ marginBottom:'var(--spacing-6)' }}>
                <span style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-4xl)', fontWeight:'var(--weight-extrabold)' }}>{plan.price}</span>
                <span style={{ color:'var(--color-text-muted)', fontSize:'var(--text-sm)' }}>{plan.period}</span>
              </div>
              <div style={{ flex:1, marginBottom:'var(--spacing-6)' }}>
                {plan.features.map((f) => (
                  <div key={f} style={{ display:'flex', alignItems:'center', gap:'var(--spacing-2)', marginBottom:'var(--spacing-3)', fontSize:'var(--text-sm)', color:'var(--color-text-secondary)' }}>
                    <Check size={16} style={{ color:'var(--color-success)', flexShrink:0 }} />{f}
                  </div>
                ))}
              </div>
              <Button variant={plan.popular ? 'primary' : 'secondary'} style={{ width:'100%' }}>{plan.cta}</Button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
