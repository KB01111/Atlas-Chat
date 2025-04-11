import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
// eslint-disable-next-line no-undef
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'YOUR_SUPABASE_URL_PLACEHOLDER';
// eslint-disable-next-line no-undef
const supabaseAnonKey =
  process.env.REACT_APP_SUPABASE_ANON_KEY || 'YOUR_SUPABASE_ANON_KEY_PLACEHOLDER';

if (!supabaseUrl || supabaseUrl === 'YOUR_SUPABASE_URL_PLACEHOLDER') {
  console.error('Supabase URL is missing or using placeholder. Check environment variables.');
}
if (!supabaseAnonKey || supabaseAnonKey === 'YOUR_SUPABASE_ANON_KEY_PLACEHOLDER') {
  console.error('Supabase Anon Key is missing or using placeholder. Check environment variables.');
}

export const supabase =
  supabaseUrl &&
  supabaseAnonKey &&
  supabaseUrl !== 'YOUR_SUPABASE_URL_PLACEHOLDER' &&
  supabaseAnonKey !== 'YOUR_SUPABASE_ANON_KEY_PLACEHOLDER'
    ? createClient(supabaseUrl, supabaseAnonKey)
    : null;

// Import data-provider API and hooks
export * from 'librechat-data-provider'; // Adjusted path assuming it's a direct dependency now
export * from 'librechat-data-provider/react-query';

// Example: custom API call combining Supabase and data-provider
export async function fetchUserProfile(userId) {
  if (!supabase) {
    console.error('Supabase client not initialized.');
    return null;
  }

  const { data, error } = await supabase.from('profiles').select('*').eq('id', userId).single();

  if (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
  return data;
}
