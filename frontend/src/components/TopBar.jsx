import React from 'react';
import { useAppContext } from '../context/AppContext';

const TopBar = ({ title }) => {
  const { orgProfile } = useAppContext();

  return (
    <header className="top-bar">
      <div className="top-bar-left">
        <div className="mobile-logo">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
          </svg>
          <span className="mobile-logo-text">Spriva AI</span>
        </div>
        <h1 className="page-title">{title}</h1>
      </div>
      <div className="top-bar-right">
        {orgProfile && (
          <div className="pill org-pill">
            {orgProfile.name}
          </div>
        )}
      </div>

      <style jsx>{`
        .top-bar {
          height: 56px;
          padding: 0 24px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid #1f1f1f;
          background: var(--bg-primary);
          position: sticky;
          top: 0;
          z-index: 90;
        }

        .top-bar-left {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .page-title {
          font-size: 15px;
          font-weight: 600;
        }

        .org-pill {
          color: var(--text-secondary);
          background: #161616;
        }

        .mobile-logo {
          display: none;
          align-items: center;
          gap: 8px;
        }

        .mobile-logo-text {
          font-weight: 600;
          font-size: 15px;
        }

        /* ─── Mobile ─── */
        @media (max-width: 768px) {
          .top-bar {
            height: 48px;
            padding: 0 16px;
          }

          .mobile-logo {
            display: flex;
          }

          .page-title {
            display: none;
          }
        }
      `}</style>
    </header>
  );
};

export default TopBar;
