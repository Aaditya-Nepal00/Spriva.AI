import React from 'react';

const GrantCard = ({ grant, isBest, onViewDetails }) => {
  const score = grant.eligibility_score || 0;
  
  const getScoreClass = (s) => {
    if (s >= 70) return 'badge-high';
    if (s >= 50) return 'badge-mid';
    return 'badge-low';
  };

  return (
    <div className="grant-card card">
      <div className="card-top">
        <h4 className="grant-title">{grant.title}</h4>
        <div className={`score-badge pill ${getScoreClass(score)}`}>
          {score}%
        </div>
      </div>

      <div className="funder-row">
        <span className="funder-name">{grant.funder}</span>
        <span className="pill funder-type">{grant.type || 'Foundation'}</span>
      </div>

      <div className="meta-row">
        <span className="amount">{grant.amount_text || grant.amount || 'Flexible'}</span>
        <span className="deadline text-muted">Due {grant.deadline || 'Oct 3, 2026'}</span>
      </div>

      <p className="reasoning text-muted italic">
        Why this fits: {grant.reasoning_snippet || 'Strategic alignment with mission objectives.'}
      </p>

      <div className="card-bottom">
        {isBest && (
          <div className="best-match-banner badge-high">
            Best Match
          </div>
        )}
        <div className="actions">
          <button className="btn-secondary view-btn" onClick={onViewDetails}>
            View Details
          </button>
        </div>
      </div>

      <style jsx>{`
        .grant-card {
          display: flex;
          flex-direction: column;
          gap: 12px;
          position: relative;
          padding-bottom: 56px; /* Space for bottom actions */
        }

        .card-top {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 12px;
        }

        .grant-title {
          font-size: 15px;
          font-weight: 600;
          line-height: 1.3;
        }

        .score-badge {
          font-weight: 700;
          font-size: 12px;
          flex-shrink: 0;
        }

        .funder-row {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .funder-name {
          font-size: 13px;
          color: var(--text-secondary);
        }

        .funder-type {
          font-size: 11px;
          background: #1a1a1a;
          border-color: #2a2a2a;
        }

        .meta-row {
          display: flex;
          justify-content: space-between;
          font-size: 13px;
        }

        .amount {
          color: var(--score-high);
          font-weight: 500;
        }

        .reasoning {
          font-size: 12px;
          font-style: italic;
          line-height: 1.4;
        }

        .card-bottom {
          position: absolute;
          bottom: 20px;
          left: 20px;
          right: 20px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .best-match-banner {
          flex: 1;
          height: 28px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 11px;
          font-weight: 600;
          border-radius: var(--radius-sm);
        }

        .actions {
          display: flex;
          justify-content: flex-end;
          flex: 1;
        }

        .view-btn {
          height: 28px;
          padding: 0 12px;
          font-size: 12px;
          border-color: #2a2a2a;
        }

        .view-btn:hover {
          border-color: white;
          color: white;
        }
      `}</style>
    </div>
  );
};

export default GrantCard;
