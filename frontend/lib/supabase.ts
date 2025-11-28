import { createClient } from '@supabase/supabase-js';

// NOTE: In a real environment, these should be in process.env
// For this demo to be runnable in some sandboxes, we check for them or use placeholders
const SUPABASE_URL = process.env.VITE_SUPABASE_URL || 'https://bllgrficwfwpolqdnugs.supabase.co';
const SUPABASE_ANON_KEY = process.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJsbGdyZmljd2Z3cG9scWRudWdzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNTYyNDEsImV4cCI6MjA3OTYzMjI0MX0.wz4QkNQtHPg0Vg1utGH2NO0xz4KUJSAuHeZrSbdgG9w';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
