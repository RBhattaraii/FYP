import React, { useState, useEffect } from 'react';
import { fetchUsers } from '../services/api';
import { Users as UsersIcon, Heart, Bell, ShoppingBag } from 'lucide-react';

export default function Users() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const limit = 20;

  useEffect(() => {
    loadUsers();
  }, [page]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const data = await fetchUsers(page, limit);
      setUsers(data.users || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error('Failed to fetch users', err);
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="content-scroll">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32 }}>
        <h1 className="page-title">User Management</h1>
        <div style={{ background: '#F3F4F6', padding: '8px 16px', borderRadius: 8, fontWeight: 600, color: 'var(--text-secondary)' }}>
          Total Users: {total}
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Role</th>
                <th>Points</th>
                <th style={{ textAlign: 'center' }}>Activity</th>
                <th>Joined</th>
              </tr>
            </thead>
            <tbody>
              {loading && users.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: 32 }}>Loading users...</td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: 32 }}>No users found.</td>
                </tr>
              ) : (
                users.map(user => (
                  <tr key={user.id}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{user.full_name || 'No Name'}</div>
                      <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{user.email}</div>
                    </td>
                    <td>
                      <span className={`badge ${user.role === 'admin' ? 'badge-active' : 'badge-stale'}`} style={{ background: user.role === 'admin' ? '#DBEAFE' : '#F3F4F6', color: user.role === 'admin' ? '#1E40AF' : '#4B5563' }}>
                        {user.role}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600, color: 'var(--accent)' }}>
                      {user.points?.toLocaleString() || 0}
                    </td>
                    <td>
                      <div style={{ display: 'flex', justifyContent: 'center', gap: 16 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--text-secondary)' }} title="Wishlist Items">
                          <Heart size={14} /> {user.wishlist_count || 0}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--text-secondary)' }} title="Price Alerts">
                          <Bell size={14} /> {user.alert_count || 0}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--text-secondary)' }} title="Purchases tracked">
                          <ShoppingBag size={14} /> {user.purchase_count || 0}
                        </div>
                      </div>
                    </td>
                    <td style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 16, marginTop: 24 }}>
          <button 
            className="pagination-btn"
            disabled={page === 1} 
            onClick={() => setPage(p => p - 1)}
          >
            Previous
          </button>
          <span style={{ fontSize: 14, fontWeight: 500, color: 'var(--text-secondary)' }}>
            Page {page} of {totalPages}
          </span>
          <button 
            className="pagination-btn"
            disabled={page >= totalPages} 
            onClick={() => setPage(p => p + 1)}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
