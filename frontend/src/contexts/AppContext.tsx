'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AnalysisResult, apiService } from '@/services/api';

interface AppContextType {
  sessionId: string | null;
  analyses: AnalysisResult[];
  isLoading: boolean;
  error: string | null;
  addAnalysis: (analysis: AnalysisResult) => void;
  loadSessionAnalyses: (sessionId: string) => Promise<void>;
  clearError: () => void;
  generateNewSession: () => string;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateNewSession = (): string => {
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
    localStorage.setItem('fii_session_id', newSessionId);
    return newSessionId;
  };

  const addAnalysis = (analysis: AnalysisResult) => {
    setAnalyses(prev => {
      const existingIndex = prev.findIndex(
        a => a.fund_info.ticker === analysis.fund_info.ticker
      );
      
      if (existingIndex >= 0) {
        const updated = [...prev];
        updated[existingIndex] = analysis;
        return updated;
      } else {
        return [...prev, analysis];
      }
    });
  };

  const loadSessionAnalyses = async (sessionId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getSessionAnalyses(sessionId);
      const formattedAnalyses: AnalysisResult[] = response.analyses.map(analysis => ({
        session_id: response.session_id,
        fund_info: analysis.fund_info,
        financial_metrics: analysis.financial_metrics,
        detailed_analysis: analysis.detailed_analysis
      }));
      
      setAnalyses(formattedAnalyses);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar análises');
    } finally {
      setIsLoading(false);
    }
  };

  const clearError = () => setError(null);

  useEffect(() => {
    const savedSessionId = localStorage.getItem('fii_session_id');
    if (savedSessionId) {
      setSessionId(savedSessionId);
      loadSessionAnalyses(savedSessionId);
    } else {
      generateNewSession();
    }
  }, []);

  const value: AppContextType = {
    sessionId,
    analyses,
    isLoading,
    error,
    addAnalysis,
    loadSessionAnalyses,
    clearError,
    generateNewSession
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}