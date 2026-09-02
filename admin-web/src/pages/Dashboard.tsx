import React, { useState, useEffect } from 'react';
import { fetchDashboardMetrics, triggerScraper } from '../services/api';
import { Package, Tags, Store, Activity } from 'lucide-react';

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      const data = await fetchDashboardMetrics();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to fetch metrics', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !metrics) {
    return <div style={{ padding: 32 }}>Loading dashboard metrics...</div>;
  }

  const handleTriggerScraper = async (storeName: string) => {
    try {
      await triggerScraper(storeName);
      alert(`Scraper queued for ${storeName}`);
    } catch (err: any) {
      alert(`Failed to trigger scraper: ${err.response?.data?.detail || err.message}`);
    }
  };

  const formatRelativeTime = (isoString: string | null): string => {
    if (!isoString) return 'Never';
    const date = new Date(isoString);
    const diffMins = Math.floor((new Date().getTime() - date.getTime()) / 60000);
    if (diffMins < 60) return `${diffMins} mins ago`;
    return `${Math.floor(diffMins / 60)} hours ago`;
  };

  return (
    <div className="content-scroll">
      <h1 className="page-title" style={{ marginBottom: 32 }}>System Overview</h1>
      
      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Total Products</span>
            <Package color="var(--accent)" size={24} />
          </div>
          <div className="card-value">{metrics.total_products?.toLocaleString()}</div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Tracked Stores</span>
            <Store color="var(--primary)" size={24} />
          </div>
          <div className="card-value">{metrics.store_distribution?.length || 0}</div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Category Breakdown</span>
            <Tags color="var(--text-secondary)" size={20} />
          </div>
          <div>
            {metrics.category_breakdown?.map((item: any, i: number) => (
              <div className="list-item" key={i}>
                <div className="list-item-left">
                  <div style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: 'var(--accent)' }} />
                  <span>{item.category}</span>
                </div>
                <strong>{item.count?.toLocaleString()}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Scraper Status</span>
            <Activity color="var(--text-secondary)" size={20} />
          </div>
          <div>
            {metrics.scraper_status?.map((item: any, i: number) => (
              <div className="list-item" key={i}>
                <div className="list-item-left" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: 4 }}>
                  <span style={{ fontWeight: 600 }}>{item.store}</span>
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                    Last sync: {formatRelativeTime(item.last_scrape)}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span className={`badge badge-${item.status}`}>
                    {item.status}
                  </span>
                  <button 
                    onClick={() => handleTriggerScraper(item.store)}
                    style={{ padding: '6px 12px', background: '#F3F4F6', border: '1px solid #E5E7EB', borderRadius: 6, fontSize: 12, fontWeight: 600, color: '#374151' }}
                  >
                    Trigger
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
