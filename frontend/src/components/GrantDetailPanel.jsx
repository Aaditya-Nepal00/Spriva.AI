import React from 'react';
import { useAppContext } from '../context/AppContext';
import ScoreBreakdown from './ScoreBreakdown';

const GrantDetailPanel = ({ grant, onClose }) => {
  const { setSelectedGrant, setAgentStatus } = useAppContext();
  
  const score = grant.eligibility_score || 0;
  const breakdown = grant.score_breakdown || {
    mission_alignment: 25,
    location: 15,
    budget: 18,
    focus_areas: 27
  };

  const handleDraftApplication = () => {
    setSelectedGrant(grant);
    setAgentStatus('Drafting Application...');
    onClose();
    // In App.jsx, if selectedGrant is set and we switch to drafts, it will handle it
  };

  const handleDraftEmail = async () => {
    setAgentStatus('Drafting Outreach Email...');
    try {
      await fetch('/api/pipeline/from-profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(grant)
      });
      setAgentStatus('Email Drafted');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="detail-overlay">
      <div className="detail-panel">
        <header className="panel-header">
          <button className="close-btn" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
          <div className="header-content">
            <h2 className="grant-title">{grant.title}</h2>
            <div className="funder-name">{grant.funder}</div>
            <div className={`score-badge pill ${score >= 70 ? 'badge-high' : score >= 50 ? 'badge-mid' : 'badge-low'}`}>
              {score}% Match
            </div>
          </div>
        </header>

        <div className="panel-body">
          <div className="info-grid">
            <div className="info-item">
              <label>Amount</label>
              <div className="info-val">{grant.amount_text || grant.amount || 'Flexible'}</div>
            </div>
            <div className="info-item">
              <label>Deadline</label>
              <div className="info-val">{grant.deadline || 'Rolling'}</div>
            </div>
            <div className="info-item">
              <label>Location</label>
              <div className="info-val">{grant.location_focus || 'Global'}</div>
            </div>
            <div className="info-item">
              <label>Funder Type</label>
              <div className="info-val">{grant.type || 'Foundation'}</div>
            </div>
          </div>

          <section className="breakdown-section">
            <h3>Eligibility Breakdown</h3>
            <ScoreBreakdown breakdown={breakdown} />
            <div className="total-score">
              <span>Total Score</span>
              <span className="bold">{score}/100</span>
            </div>
          </section>

          <section className="description-section">
            <p className="text-secondary">
              {grant.description || 'This grant supports high-impact initiatives aligned with community development and strategic sustainability goals.'}
            </p>
          </section>

          <section className="contact-section">
            <h3>Funder Contact</h3>
            <div className="contact-links">
              <a href={grant.website || '#'} target="_blank" rel="noopener noreferrer">Website</a>
              <a href={`mailto:${grant.email || 'info@funder.org'}`}>Email Program Officer</a>
            </div>
            <div className="officer text-muted font-12">
              Officer: {grant.program_officer || 'Not listed'}
            </div>
          </section>
        </div>

        <footer className="panel-footer">
          <button className="btn-primary full-width" onClick={handleDraftApplication}>
            Draft Application
          </button>
          <button className="btn-secondary full-width" onClick={handleDraftEmail}>
            Draft Outreach Email
          </button>
        </footer>
      </div>

      <style jsx>{`
        .detail-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.4);
          z-index: 200;
          display: flex;
          justify-content: flex-end;
        }

        .detail-panel {
          width: 480px;
          height: 100%;
          background: var(--bg-secondary);
          border-left: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
          from { transform: translateX(100%); }
          to { transform: translateX(0); }
        }

        .panel-header {
          padding: 24px;
          border-bottom: 1px solid var(--border);
          position: relative;
        }

        .close-btn {
          position: absolute;
          top: 24px;
          right: 24px;
          background: transparent;
          color: var(--text-muted);
          min-height: auto;
        }

        .close-btn:hover {
          color: var(--text-primary);
        }

        .grant-title {
          font-size: 18px;
          margin-bottom: 4px;
          padding-right: 32px;
        }

        .funder-name {
          color: var(--text-secondary);
          font-size: 14px;
          margin-bottom: 12px;
        }

        .panel-body {
          flex: 1;
          overflow-y: auto;
          padding: 24px;
          display: flex;
          flex-direction: column;
          gap: 32px;
        }

        .info-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }

        .info-val {
          font-weight: 500;
          margin-top: 4px;
        }

        section h3 {
          font-size: 13px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--text-muted);
          margin-bottom: 16px;
        }

        .total-score {
          display: flex;
          justify-content: space-between;
          margin-top: 16px;
          padding-top: 12px;
          border-top: 1px solid var(--border);
          font-size: 15px;
        }

        .bold { font-weight: 700; }

        .contact-links {
          display: flex;
          gap: 16px;
          margin-bottom: 8px;
        }

        .contact-links a {
          font-size: 13px;
          text-decoration: underline;
        }

        .panel-footer {
          padding: 24px;
          border-top: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .full-width { width: 100%; height: 40px; }

        /* ─── Mobile: full-screen overlay ─── */
        @media (max-width: 768px) {
          .detail-overlay {
            justify-content: stretch;
          }

          .detail-panel {
            width: 100%;
            border-left: none;
            animation: slideUp 0.3s ease-out;
          }

          @keyframes slideUp {
            from { transform: translateY(100%); }
            to { transform: translateY(0); }
          }

          .close-btn {
            top: 16px;
            right: 16px;
            width: 44px;
            height: 44px;
            min-height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
          }

          .panel-header {
            padding: 16px;
          }

          .panel-body {
            padding: 16px;
            gap: 24px;
          }

          .panel-footer {
            padding: 16px;
            padding-bottom: calc(16px + env(safe-area-inset-bottom));
          }

          .full-width {
            height: 48px;
          }
        }
      `}</style>
    </div>
  );
};

export default GrantDetailPanel;
