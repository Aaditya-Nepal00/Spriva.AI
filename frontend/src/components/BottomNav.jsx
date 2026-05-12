import React from 'react';

const BottomNav = ({ activeTab, onTabChange }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path> },
    { id: 'intake', label: 'Intake', icon: <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4m4-5l5 5 5-5m-5 5V3"></path> },
    { id: 'discovery', label: 'Discovery', icon: <><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></> },
    { id: 'drafts', label: 'Drafts', icon: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></> },
    { id: 'assistant', label: 'Assistant', icon: <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path> },
  ];

  return (
    <nav className="bottom-nav">
      {navItems.map((item) => (
        <button
          key={item.id}
          className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
          onClick={() => onTabChange(item.id)}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {item.icon}
          </svg>
          <span>{item.label}</span>
        </button>
      ))}

      <style jsx>{`
        .bottom-nav {
          display: none;
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          height: 56px;
          background: #111111;
          border-top: 1px solid #1f1f1f;
          z-index: 1000;
          padding-bottom: env(safe-area-inset-bottom);
        }

        @media (max-width: 768px) {
          .bottom-nav {
            display: flex;
            justify-content: space-around;
            align-items: center;
          }
        }

        .nav-item {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 4px;
          background: transparent;
          color: var(--text-muted);
          height: 100%;
          border-radius: 0;
          padding: 0;
          min-height: auto;
        }

        .nav-item span {
          font-size: 10px;
          font-weight: 500;
        }

        .nav-item.active {
          color: white;
        }

        .nav-item.active svg {
          stroke: white;
        }
      `}</style>
    </nav>
  );
};

export default BottomNav;
