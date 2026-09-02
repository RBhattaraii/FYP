import React, { useState, useEffect } from 'react';
import { getVouchers, createVoucher, deleteVoucher } from '../services/api';
import { Ticket, Plus, Trash2 } from 'lucide-react';

export default function Vouchers() {
  const [vouchers, setVouchers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [code, setCode] = useState('');
  const [discount, setDiscount] = useState('');
  const [pointsCost, setPointsCost] = useState('0');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadVouchers();
  }, []);

  const loadVouchers = async () => {
    try {
      const data = await getVouchers();
      setVouchers(data.vouchers || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      await createVoucher(code.toUpperCase(), parseFloat(discount), parseInt(pointsCost) || 0);
      setCode('');
      setDiscount('');
      setPointsCost('0');
      loadVouchers();
    } catch (err) {
      alert('Failed to create voucher');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this voucher?')) return;
    try {
      await deleteVoucher(id);
      loadVouchers();
    } catch (err) {
      alert('Failed to delete');
    }
  };

  return (
    <div className="content-scroll">
      <h1 className="page-title" style={{ marginBottom: 32 }}>Promotional Vouchers</h1>

      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Create New Voucher</span>
            <Plus size={20} color="var(--primary)" />
          </div>
          <form onSubmit={handleCreate}>
            <div className="form-group">
              <label>Voucher Code</label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="e.g. SUMMER20" 
                value={code}
                onChange={e => setCode(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Discount Amount (Rs)</label>
              <input 
                type="number" 
                className="form-input" 
                placeholder="e.g. 500" 
                value={discount}
                onChange={e => setDiscount(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Points Cost (For Reward Tiers)</label>
              <input 
                type="number" 
                className="form-input" 
                placeholder="0 for regular vouchers" 
                value={pointsCost}
                onChange={e => setPointsCost(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn-primary" disabled={creating}>
              {creating ? 'Creating...' : 'Create Voucher'}
            </button>
          </form>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Active Vouchers</span>
            <Ticket size={20} color="var(--primary)" />
          </div>
          
          {loading ? (
            <p>Loading...</p>
          ) : vouchers.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)' }}>No active vouchers found.</p>
          ) : (
            <div>
              {vouchers.map(v => (
                <div className="list-item" key={v.id}>
                  <div className="list-item-left" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                    <span style={{ fontWeight: 700, fontSize: 18, color: 'var(--primary)' }}>{v.voucher_code}</span>
                    <span style={{ fontSize: 14, color: 'var(--success)' }}>
                      Rs {v.discount_amount} off {v.points_cost > 0 && `(Costs ${v.points_cost} pts)`}
                    </span>
                  </div>
                  <button 
                    onClick={() => handleDelete(v.id)}
                    style={{ padding: 8, background: '#FEE2E2', borderRadius: 8, color: 'var(--danger)' }}
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
