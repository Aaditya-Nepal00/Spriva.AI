import React from 'react';
import { useAppContext } from '../context/AppContext';

const StatusBar = () => {
  const { agentStatus, isLoading, error } = useAppContext();

  if (!agentStatus && !error && !isLoading) return null;

  return (
    <div className={`status-bar ${error ? 'error' : ''}`}>
      <div className="status-content">
        {isLoading && <span className="spinner"></span>}
        <span className="status-text">{error || agentStatus}</span>
      </div>

      <style jsx>{`
        .status-bar {
          position: fixed;
          bottom: 24px;
          right: 24px;
          padding: 8px 16px;
          background: #1a1a1a;
          border: 1px solid var(--border);
          border-radius: var(--radius-sm);
          box-shadow: 0 4px 12px rgba(0,0,0,0.5);
          z-index: 1000;
          font-size: 12px;
          color: var(--text-secondary);
          animation: slideUp 0.3s ease-out;
        }

        .status-bar.error {
          border-color: var(--score-low);
          color: var(--score-low);
          background: #2a0a0a;
        }

        .status-content {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .spinner {
          width: 12px;
          height: 12px;
          border: 2px solid var(--text-muted);
          border-top-color: var(--text-primary);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes slideUp { from { transform: translateY(100%); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
      `}</style>
    </div>
  );
};

export default StatusBar;
