import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import BottomNav from './components/BottomNav';
import Dashboard from './pages/Dashboard';
import DocumentIntake from './pages/DocumentIntake';
import GrantDiscovery from './pages/GrantDiscovery';
import ApplicationDrafts from './pages/ApplicationDrafts';
import AIAssistant from './pages/AIAssistant';
import { useAppContext } from './context/AppContext';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const { orgProfile } = useAppContext();

  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard onNavigate={setActiveTab} />;
      case 'intake':
        return <DocumentIntake onComplete={() => setActiveTab('discovery')} />;
      case 'discovery':
        return <GrantDiscovery />;
      case 'drafts':
        return <ApplicationDrafts />;
      case 'assistant':
        return <AIAssistant />;
      default:
        return <Dashboard />;
    }
  };

  const getTitle = () => {
    const titles = {
      dashboard: 'Dashboard',
      intake: 'Document Intake',
      discovery: 'Grant Discovery',
      drafts: 'Application Drafts',
      assistant: 'AI Assistant'
    };
    return titles[activeTab] || 'Spriva AI';
  };

  return (
    <div className="shell">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="main-area">
        <TopBar title={getTitle()} />
        <div className="content-viewport">
          {renderPage()}
        </div>
      </main>
      <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />

      <style jsx>{`
        .shell {
          display: flex;
          width: 100vw;
          height: 100vh;
        }

        .main-area {
          margin-left: 240px;
          flex: 1;
          height: 100vh;
          display: flex;
          flex-direction: column;
          background: var(--bg-primary);
          overflow: hidden;
        }

        .content-viewport {
          flex: 1;
          overflow-y: auto;
          padding: 24px;
        }

        /* ─── Tablet: collapsed sidebar ─── */
        @media (max-width: 1024px) and (min-width: 769px) {
          .main-area {
            margin-left: 56px;
          }
        }

        /* ─── Mobile: no sidebar, bottom nav ─── */
        @media (max-width: 768px) {
          .main-area {
            margin-left: 0;
            padding-bottom: 72px;
          }

          .content-viewport {
            padding: 16px;
          }
        }
      `}</style>
    </div>
  );
}

export default App;
