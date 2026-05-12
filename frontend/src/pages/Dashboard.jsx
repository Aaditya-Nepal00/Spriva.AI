import React from 'react';
import { useAppContext } from '../context/AppContext';

const Dashboard = ({ onNavigate }) => {
  const { orgProfile, grants, drafts } = useAppContext();

  if (!orgProfile) {
    return (
      <div className="onboarding-view">
        <div className="centered-empty">
          <h2>Start by setting up your organization</h2>
          <p className="text-secondary">Add your org profile to start finding grants</p>
          <div className="onboarding-actions">
            <button className="btn-primary" onClick={() => onNavigate('intake')}>
              Enter Details Manually
            </button>
            <button className="btn-secondary" onClick={() => onNavigate('intake')}>
              Upload Document
            </button>
          </div>
        </div>

        <style jsx>{`
          .onboarding-view {
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
          }
          .centered-empty {
            text-align: center;
            max-width: 400px;
          }
          .centered-empty h2 {
            font-size: 24px;
            margin-bottom: 8px;
          }
          .centered-empty p {
            margin-bottom: 32px;
          }
          .onboarding-actions {
            display: flex;
            gap: 12px;
            justify-content: center;
          }

          @media (max-width: 768px) {
            .centered-empty {
              padding: 0 16px;
            }
            .centered-empty h2 {
              font-size: 20px;
            }
            .onboarding-actions {
              flex-direction: column;
            }
            .onboarding-actions button {
              width: 100%;
            }
          }
        `}</style>
      </div>
    );
  }

  const bestMatch = grants.length > 0 ? Math.max(...grants.map(g => g.eligibility_score || 0)) : 0;
  const draftCount = Object.keys(drafts).length;

  return (
    <div className="dashboard">
      <div className="welcome-header">
        <h2>Good morning, {orgProfile.name}</h2>
      </div>

      <div className="stats-row">
        <div className="card stat-card">
          <span className="stat-value">{grants.length}</span>
          <span className="stat-label">Grants Found</span>
        </div>
        <div className="card stat-card">
          <span className="stat-value">{bestMatch}%</span>
          <span className="stat-label">Best Match Score</span>
        </div>
        <div className="card stat-card">
          <span className="stat-value">{draftCount}</span>
          <span className="stat-label">Drafts Created</span>
        </div>
        <div className="card stat-card">
          <span className="stat-value">0</span>
          <span className="stat-label">Emails Drafted</span>
        </div>
      </div>

      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="action-buttons">
          <button className="btn-secondary" onClick={() => onNavigate('discovery')}>Find New Grants</button>
          <button className="btn-secondary" onClick={() => onNavigate('drafts')}>Continue Last Draft</button>
          <button className="btn-secondary" onClick={() => onNavigate('assistant')}>Open AI Assistant</button>
        </div>
      </div>

      <style jsx>{`
        .dashboard {
          display: flex;
          flex-direction: column;
          gap: 32px;
        }

        .welcome-header h2 {
          font-size: 20px;
        }

        .stats-row {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 16px;
        }

        .stat-card {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .stat-value {
          font-size: 24px;
          font-weight: 600;
        }

        .stat-label {
          font-size: 12px;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .quick-actions h3 {
          font-size: 15px;
          margin-bottom: 16px;
        }

        .action-buttons {
          display: flex;
          gap: 12px;
        }

        /* ─── Mobile ─── */
        @media (max-width: 768px) {
          .dashboard {
            gap: 24px;
          }

          .stats-row {
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
          }

          .stat-value {
            font-size: 20px;
          }

          .action-buttons {
            flex-direction: column;
          }

          .action-buttons button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default Dashboard;
