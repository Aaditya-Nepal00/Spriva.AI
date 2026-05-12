import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';

const ApplicationDrafts = () => {
  const { selectedGrant, orgProfile, setAgentStatus, isLoading, setIsLoading } = useAppContext();
  const [activeTab, setActiveTab] = useState('Executive Summary');
  const [localDraft, setLocalDraft] = useState({});
  const [grantInfoOpen, setGrantInfoOpen] = useState(false);

  const sections = [
    'Executive Summary', 'Org Background', 'Project Description', 
    'Goals', 'Budget', 'Evaluation', 'Conclusion'
  ];

  const generateDraft = async () => {
    if (!selectedGrant || !orgProfile) return;
    
    setIsLoading(true);
    setAgentStatus('Agent is drafting your application...');
    
    try {
      const response = await fetch('/api/grants/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ org_profile: orgProfile, grant: selectedGrant })
      });
      const data = await response.json();
      
      // We assume the backend returns sections we can split, or a single block
      // For this demo, let's map the text to sections if possible, 
      // or just put it in the first section.
      const draftText = data.application || '';
      const splitDraft = {};
      sections.forEach((s, i) => {
        splitDraft[s] = i === 0 ? draftText : '';
      });
      setLocalDraft(splitDraft);
      setAgentStatus('Draft Generated');
    } catch (err) {
      console.error(err);
      setAgentStatus('Drafting Failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextChange = (section, text) => {
    setLocalDraft(prev => ({ ...prev, [section]: text }));
  };

  if (!selectedGrant) {
    return (
      <div className="empty-state">
        <div className="centered-content">
          <p>Select a grant from Discovery to generate a draft</p>
        </div>
        <style jsx>{`
          .empty-state { height: 100%; display: flex; align-items: center; justify-content: center; color: var(--text-muted); }
        `}</style>
      </div>
    );
  }

  return (
    <div className="application-drafts">
      <div className="split-layout">
        <div className="left-panel">
          <div className="grant-ref">
            <div className="mobile-collapse-header" onClick={() => setGrantInfoOpen(!grantInfoOpen)}>
              <span className="font-11 text-muted uppercase">Reference</span>
              <svg className="collapse-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ transform: grantInfoOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s ease' }}>
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            <h2 className="font-15">{selectedGrant.title}</h2>
            <div className="funder text-secondary font-13">{selectedGrant.funder}</div>
            
            <div className="collapsible-content">
              <div className="ref-grid">
                <div className="ref-item">
                  <label>Amount</label>
                  <div className="font-13">{selectedGrant.amount_text || selectedGrant.amount}</div>
                </div>
                <div className="ref-item">
                  <label>Deadline</label>
                  <div className="font-13">{selectedGrant.deadline}</div>
                </div>
              </div>

              <section className="req-section">
                <h3>Requirements</h3>
                <ul className="text-secondary font-13">
                  <li>Nonprofit 501(c)(3) status</li>
                  <li>Project alignment with local community needs</li>
                  <li>Budget within $50k-$250k range</li>
                  <li>Proven impact metrics from previous year</li>
                </ul>
              </section>

              <section className="priority-section">
                <h3>Funder Priorities</h3>
                <p className="text-secondary font-13">
                  {selectedGrant.description || 'Focus on sustainable development and local capacity building.'}
                </p>
              </section>
            </div>
          </div>
        </div>

        <div className="right-panel">
          <header className="draft-header">
            <div className="breadcrumb text-muted font-12">
              Discovery / {selectedGrant.title}
            </div>
            <div className="header-actions">
              <button className="btn-primary" onClick={generateDraft} disabled={isLoading}>
                {isLoading ? 'Agent is drafting...' : 'Generate Draft'}
              </button>
              <button className="btn-secondary">Save to Drive</button>
            </div>
          </header>

          {isLoading ? (
            <div className="loading-state animate-pulse">
              Agent is drafting your application...
            </div>
          ) : (
            <div className="editor-container">
              <div className="section-tabs">
                {sections.map(s => (
                  <button 
                    key={s}
                    className={`tab-btn ${activeTab === s ? 'active' : ''}`}
                    onClick={() => setActiveTab(s)}
                  >
                    {s}
                  </button>
                ))}
              </div>

              <div className="document-view card">
                <div 
                  className="editor-area"
                  contentEditable
                  suppressContentEditableWarning
                  onBlur={(e) => handleTextChange(activeTab, e.currentTarget.textContent)}
                >
                  {localDraft[activeTab] || 'Click Generate Draft to begin...'}
                </div>
                <div className="char-count text-muted font-11">
                  {(localDraft[activeTab] || '').length} characters
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .application-drafts { height: 100%; overflow: hidden; }
        .split-layout { display: flex; height: 100%; }

        .left-panel {
          width: 40%;
          border-right: 1px solid var(--border);
          padding-right: 24px;
          overflow-y: auto;
          position: sticky;
          top: 0;
        }

        .right-panel {
          width: 60%;
          padding-left: 24px;
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .grant-ref { display: flex; flex-direction: column; gap: 16px; }
        .uppercase { text-transform: uppercase; letter-spacing: 0.05em; }
        .ref-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        
        section h3 { font-size: 11px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px; }
        ul { padding-left: 16px; }
        li { margin-bottom: 4px; }

        .draft-header { display: flex; justify-content: space-between; align-items: center; }
        .header-actions { display: flex; gap: 12px; }

        .editor-container { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
        .section-tabs { display: flex; overflow-x: auto; border-bottom: 1px solid var(--border); margin-bottom: 16px; }
        .tab-btn { 
          padding: 8px 12px; 
          background: transparent; 
          color: var(--text-secondary); 
          border-radius: 0; 
          border-bottom: 2px solid transparent;
          white-space: nowrap;
          font-size: 12px;
          min-height: 36px;
        }
        .tab-btn.active { color: var(--text-primary); border-bottom-color: var(--text-primary); }

        .document-view { flex: 1; display: flex; flex-direction: column; background: var(--bg-primary); padding: 32px; border-radius: 0; border: 1px solid var(--border); }
        .editor-area { flex: 1; outline: none; font-size: 14px; line-height: 1.7; color: var(--text-primary); }
        .char-count { margin-top: 24px; border-top: 1px solid var(--border); padding-top: 12px; }

        .loading-state { height: 100%; display: flex; align-items: center; justify-content: center; color: var(--text-muted); }

        .mobile-collapse-header {
          display: none;
        }

        .collapse-chevron {
          display: none;
        }

        /* ─── Mobile ─── */
        @media (max-width: 768px) {
          .split-layout {
            flex-direction: column;
            overflow-y: auto;
          }

          .left-panel {
            width: 100%;
            border-right: none;
            border-bottom: 1px solid var(--border);
            padding-right: 0;
            padding-bottom: 16px;
            position: relative;
          }

          .right-panel {
            width: 100%;
            padding-left: 0;
            padding-top: 16px;
          }

          .mobile-collapse-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            padding: 8px 0;
          }

          .collapse-chevron {
            display: block;
          }

          .collapsible-content {
            display: none;
          }

          .left-panel:has(.mobile-collapse-header) .collapsible-content {
            display: none;
          }

          .draft-header {
            flex-direction: column;
            gap: 12px;
            align-items: stretch;
          }

          .header-actions {
            flex-direction: column;
          }

          .header-actions button {
            width: 100%;
          }

          .section-tabs {
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
          }

          .section-tabs::-webkit-scrollbar {
            display: none;
          }

          .tab-btn {
            min-height: 44px;
          }

          .document-view {
            padding: 16px;
          }
        }
      `}</style>
    </div>
  );
};

export default ApplicationDrafts;
