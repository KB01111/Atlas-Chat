import { createContext, useContext } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

console.log('[SupabaseProvider] Supabase URL:', supabaseUrl ? supabaseUrl.slice(0, 8) + '...' : 'undefined');
console.log('[SupabaseProvider] Supabase Anon Key:', supabaseAnonKey ? supabaseAnonKey.slice(0, 8) + '...' : 'undefined');

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('[SupabaseProvider] Missing Supabase environment variables');
  throw new Error('Missing Supabase environment variables');
}

const supabase = createClient(supabaseUrl, supabaseAnonKey);
console.log('[SupabaseProvider] Supabase client created successfully');

const SupabaseContext = createContext(supabase);

export const SupabaseProvider = ({ children }) => (
  <SupabaseContext.Provider value={supabase}>
    {children}
  </SupabaseContext.Provider>
);

export const useSupabase = () => useContext(SupabaseContext);