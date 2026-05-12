import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';

const DocumentIntake = ({ onComplete }) => {
  const { orgProfile, setOrgProfile, setIsLoading, isLoading, setError, error } = useAppContext();
  const [activeTab, setActiveTab] = useState('manual');
  const [pastedText, setPastedText] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  
  const [formData, setFormData] = useState(orgProfile || {
    name: '',
    mission: '',
    focus_areas: '',
    location: '',
    budget: ''
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    try {
      // For now, we simulate the save and call the search
      setOrgProfile(formData);
      
      const response = await fetch('/api/grants/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (!response.ok) throw new Error('Failed to fetch grants');
      
      onComplete(); // Navigate to discovery
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAIExtract = async () => {
    if (!pastedText.trim()) return;
    
    setIsLoading(true);
    setStatusMessage('Agent is reading your document...');
    setError(null);
    
    try {
      const response = await fetch('/api/intake/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: pastedText, filename: 'pasted_document.txt' })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        const extracted = {
          name: data.org_name || '',
          mission: data.mission || '',
          focus_areas: data.focus_areas || '',
          location: data.location || '',
          budget: data.budget_range || ''
        };
        setFormData(extracted);
        setStatusMessage('Profile extracted. Review and save.');
        setActiveTab('manual');
      } else {
        throw new Error('AI extraction failed. Please try manual entry.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="document-intake">
      <div className="tab-header">
        <button 
          className={`tab-btn ${activeTab === 'manual' ? 'active' : ''}`}
          onClick={() => setActiveTab('manual')}
        >
          Manual Entry
        </button>
        <button 
          className={`tab-btn ${activeTab === 'paste' ? 'active' : ''}`}
          onClick={() => setActiveTab('paste')}
        >
          Paste Document
        </button>
      </div>

      <div className="tab-content">
        {error && <div className="error-box">{error}</div>}
        {statusMessage && <div className="status-box">{statusMessage}</div>}

        {activeTab === 'manual' ? (
          <div className="form-container">
            <form onSubmit={handleManualSubmit}>
              <div className="form-group">
                <label>Organization Name</label>
                <input 
                  type="text" 
                  name="name" 
                  value={formData.name} 
                  onChange={handleInputChange}
                  required 
                />
              </div>

              <div className="form-group">
                <label>Mission Statement</label>
                <textarea 
                  name="mission" 
                  rows="4" 
                  value={formData.mission} 
                  onChange={handleInputChange}
                  required 
                />
              </div>

              <div className="form-group">
                <label>Focus Areas</label>
                <input 
                  type="text" 
                  name="focus_areas" 
                  value={formData.focus_areas} 
                  onChange={handleInputChange}
                  placeholder="Education, Health, Climate"
                  required 
                />
              </div>

              <div className="form-group">
                <label>Location</label>
                <input 
                  type="text" 
                  name="location" 
                  value={formData.location} 
                  onChange={handleInputChange}
                  required 
                />
              </div>

              <div className="form-group">
                <label>Annual Budget</label>
                <input 
                  type="text" 
                  name="budget" 
                  value={formData.budget} 
                  onChange={handleInputChange}
                  placeholder="$50,000"
                  required 
                />
              </div>

              <button type="submit" className="btn-primary submit-btn" disabled={isLoading}>
                {isLoading ? 'Saving...' : 'Save Profile & Find Grants'}
              </button>
            </form>
          </div>
        ) : (
          <div className="paste-container">
            <label>Paste your annual report, past grant application, or any organization document</label>
            <textarea 
              rows="10" 
              value={pastedText} 
              onChange={(e) => setPastedText(e.target.value)}
              placeholder="Paste content here..."
            />
            <button 
              className="btn-primary submit-btn" 
              onClick={handleAIExtract}
              disabled={isLoading || !pastedText.trim()}
            >
              {isLoading ? 'Agent is reading your document...' : 'Extract Profile with AI'}
            </button>
          </div>
        )}
      </div>

      <style jsx>{`
        .document-intake {
          max-width: 800px;
        }

        .tab-header {
          display: flex;
          gap: 16px;
          border-bottom: 1px solid var(--border);
          margin-bottom: 24px;
        }

        .tab-btn {
          height: 40px;
          background: transparent;
          color: var(--text-secondary);
          border-bottom: 2px solid transparent;
          border-radius: 0;
          font-weight: 500;
          min-height: 40px;
        }

        .tab-btn.active {
          color: var(--text-primary);
          border-bottom-color: var(--text-primary);
        }

        .form-container, .paste-container {
          max-width: 600px;
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
        }

        .error-box {
          padding: 12px;
          background: #2a0a0a;
          border: 1px solid var(--score-low);
          color: var(--score-low);
          border-radius: var(--radius-sm);
          font-size: 13px;
          margin-bottom: 16px;
        }

        .status-box {
          padding: 12px;
          background: #0f2618;
          border: 1px solid var(--score-high);
          color: var(--score-high);
          border-radius: var(--radius-sm);
          font-size: 13px;
          margin-bottom: 16px;
        }

        /* ─── Mobile ─── */
        @media (max-width: 768px) {
          .document-intake {
            max-width: 100%;
          }

          .form-container, .paste-container {
            max-width: 100%;
          }

          .form-container form {
            display: flex;
            flex-direction: column;
            gap: 16px;
          }

          textarea {
            min-height: 120px;
          }

          .submit-btn {
            width: 100%;
            height: 48px;
          }
        }
      `}</style>
    </div>
  );
};

export default DocumentIntake;
