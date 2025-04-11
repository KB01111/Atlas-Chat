import { createClient, SupabaseClient } from '@supabase/supabase-js';
import React, { createContext, useContext } from 'react';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || '';
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || '';

const supabase = createClient(supabaseUrl, supabaseAnonKey);

const SupabaseContext = createContext<SupabaseClient | null>(null);

export const useSupabase = () => {
  const context = useContext(SupabaseContext);
  if (!context) {
    throw new Error('useSupabase must be used within a SupabaseProvider');
  }
  return context;
};

const SupabaseProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <SupabaseContext.Provider value={supabase}>{children}</SupabaseContext.Provider>
);

export default SupabaseProvider;
