import { createClient } from '@supabase/supabase-js';

// NOTE: In a real environment, these should be in process.env
// For this demo to be runnable in some sandboxes, we check for them or use placeholders
const SUPABASE_URL = process.env.VITE_SUPABASE_URL 
const SUPABASE_ANON_KEY = process.env.VITE_SUPABASE_ANON_KEY;

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
