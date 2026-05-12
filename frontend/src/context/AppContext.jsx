import React, { createContext, useContext, useState, useEffect } from 'react';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [orgProfile, setOrgProfile] = useState(() => {
    const saved = localStorage.getItem('spriva_org_profile');
    return saved ? JSON.parse(saved) : null;
  });
  
  const [grants, setGrants] = useState([]);
  const [selectedGrant, setSelectedGrant] = useState(null);
  const [drafts, setDrafts] = useState({});
  const [agentStatus, setAgentStatus] = useState('Agent Ready');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (orgProfile) {
      localStorage.setItem('spriva_org_profile', JSON.stringify(orgProfile));
    }
  }, [orgProfile]);

  const value = {
    orgProfile,
    setOrgProfile,
    grants,
    setGrants,
    selectedGrant,
    setSelectedGrant,
    drafts,
    setDrafts,
    agentStatus,
    setAgentStatus,
    isLoading,
    setIsLoading,
    error,
    setError
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};
