import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import GrantCard from '../components/GrantCard';
import GrantDetailPanel from '../components/GrantDetailPanel';

const GrantDiscovery = () => {
  const { orgProfile, grants, setGrants, setIsLoading, isLoading, setError, error } = useAppContext();
  const [filter, setFilter] = useState('all');
  const [showDetail, setShowDetail] = useState(false);
  const [localSelectedGrant, setLocalSelectedGrant] = useState(null);

  const fetchGrants = async () => {
    if (!orgProfile) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/grants/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orgProfile)
      });
      const data = await response.json();
      setGrants(data.grants || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (grants.length === 0 && orgProfile) {
      fetchGrants();
    }
  }, []);

  const filteredGrants = grants.filter(grant => {
    const score = grant.eligibility_score || 0;
    if (filter === 'all') return true;
    if (filter === 'high') return score >= 70;
    if (filter === 'mid') return score >= 50 && score < 70;
    if (filter === 'low') return score < 50;
    return true;
  });

  const handleViewDetails = (grant) => {
    setLocalSelectedGrant(grant);
    setShowDetail(true);
  };

  return (
    <div className="grant-discovery">
      <div className="discovery-header">
        <div className="header-actions">
          <button className="btn-primary" onClick={fetchGrants} disabled={isLoading}>
            {isLoading ? 'Searching...' : 'Search Grants'}
          </button>
          <div className="filter-tabs">
            {['all', 'high', 'mid', 'low'].map(f => (
              <button 
                key={f}
                className={`filter-btn ${filter === f ? 'active' : ''}`}
                onClick={() => setFilter(f)}
              >
                {f === 'all' ? 'All' : f === 'high' ? 'Strong Match' : f === 'mid' ? 'Good' : 'Weak'}
              </button>
            ))}
          </div>
        </div>
        <div className="grant-count text-muted">
          {grants.length} grants found
        </div>
      </div>

      {isLoading ? (
        <div className="loading-grid">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="card skeleton-card animate-pulse"></div>
          ))}
        </div>
      ) : error ? (
        <div className="error-view">{error}</div>
      ) : (
        <div className="grant-grid">
          {filteredGrants.map((grant, index) => (
            <GrantCard 
              key={grant.id || index} 
              grant={grant} 
              isBest={index === 0 && filter === 'all'}
              onViewDetails={() => handleViewDetails(grant)}
            />
          ))}
        </div>
      )}

      {showDetail && localSelectedGrant && (
        <GrantDetailPanel 
          grant={localSelectedGrant} 
          onClose={() => setShowDetail(false)} 
        />
      )}

      <style jsx>{`
        .grant-discovery {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }

        .discovery-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .header-actions {
          display: flex;
          align-items: center;
          gap: 24px;
        }

        .filter-tabs {
          display: flex;
          border: 1px solid var(--border);
          border-radius: var(--radius-sm);
          overflow: hidden;
        }

        .filter-btn {
          height: 32px;
          padding: 0 12px;
          background: transparent;
          color: var(--text-secondary);
          border-radius: 0;
          font-size: 12px;
          border-right: 1px solid var(--border);
          min-height: 32px;
        }

        .filter-btn:last-child {
          border-right: none;
        }

        .filter-btn.active {
          background: var(--bg-tertiary);
          color: var(--text-primary);
        }

        .grant-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
        }

        .loading-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
        }

        .skeleton-card {
          height: 180px;
          border-style: dashed;
        }

        .error-view {
          padding: 24px;
          color: var(--score-low);
          text-align: center;
        }

        /* ─── Mobile ─── */
        @media (max-width: 768px) {
          .discovery-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
          }

          .header-actions {
            flex-direction: column;
            align-items: stretch;
            gap: 12px;
            width: 100%;
          }

          .header-actions .btn-primary {
            width: 100%;
          }

          .filter-tabs {
            width: 100%;
          }

          .filter-btn {
            flex: 1;
            text-align: center;
            min-height: 44px;
          }

          .grant-grid,
          .loading-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default GrantDiscovery;
