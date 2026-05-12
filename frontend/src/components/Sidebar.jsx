import React from 'react';
import { useAppContext } from '../context/AppContext';

const Sidebar = ({ activeTab, onTabChange }) => {
  const { agentStatus } = useAppContext();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path> },
    { id: 'intake', label: 'Document Intake', icon: <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4m4-5l5 5 5-5m-5 5V3"></path> },
    { id: 'discovery', label: 'Grant Discovery', icon: <><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></> },
    { id: 'drafts', label: 'Application Drafts', icon: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></> },
    { id: 'assistant', label: 'AI Assistant', icon: <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path> },
  ];

  return (
    <aside className="sidebar">
      <div className="logo-area">
        <svg className="logo-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
        </svg>
        <span className="logo-wordmark">Spriva AI</span>
      </div>

      <nav className="nav-list">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => onTabChange(item.id)}
            title={item.label}
          >
            <svg className="nav-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {item.icon}
            </svg>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="status-indicator">
          <span className="dot"></span>
          <span className="status-text">{agentStatus}</span>
        </div>
        <div className="version">v1.0</div>
      </div>

      <style jsx>{`
        .sidebar {
          width: 240px;
          height: 100vh;
          position: fixed;
          left: 0;
          top: 0;
          background: #111111;
          border-right: 1px solid #1f1f1f;
          display: flex;
          flex-direction: column;
          z-index: 100;
        }

        .logo-area {
          height: 56px;
          padding: 0 16px;
          display: flex;
          align-items: center;
          gap: 10px;
          border-bottom: 1px solid #1f1f1f;
        }

        .logo-wordmark {
          font-weight: 600;
          font-size: 15px;
          letter-spacing: -0.01em;
        }

        .nav-list {
          flex: 1;
          padding: 16px 0;
          display: flex;
          flex-direction: column;
        }

        .nav-item {
          height: 40px;
          padding: 0 16px;
          justify-content: flex-start;
          background: transparent;
          color: var(--text-secondary);
          border-radius: 0;
          font-size: 13px;
          font-weight: 500;
          min-height: 40px;
        }

        .nav-item:hover {
          background: #161616;
          color: var(--text-primary);
        }

        .nav-item.active {
          background: #1a1a1a;
          color: var(--text-primary);
          border-left: 2px solid white;
        }

        .sidebar-bottom {
          padding: 16px;
          border-top: 1px solid #1f1f1f;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 12px;
          color: var(--text-secondary);
        }

        .dot {
          width: 6px;
          height: 6px;
          background: var(--score-high);
          border-radius: 50%;
          flex-shrink: 0;
        }

        .version {
          font-size: 11px;
          color: var(--text-muted);
        }

        /* ─── Tablet: collapsed sidebar ─── */
        @media (max-width: 1024px) and (min-width: 769px) {
          .sidebar {
            width: 56px;
          }

          .logo-area {
            justify-content: center;
            padding: 0;
          }

          .logo-wordmark {
            display: none;
          }

          .nav-item {
            justify-content: center;
            padding: 0;
          }

          .nav-label {
            display: none;
          }

          .nav-icon {
            width: 20px;
            height: 20px;
          }

          .sidebar-bottom {
            align-items: center;
            padding: 12px 8px;
          }

          .status-text {
            display: none;
          }

          .version {
            display: none;
          }
        }

        /* ─── Mobile: hide sidebar completely ─── */
        @media (max-width: 768px) {
          .sidebar {
            display: none;
          }
        }
      `}</style>
    </aside>
  );
};

export default Sidebar;
