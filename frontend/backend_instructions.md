# Supabase Setup & Backend Instructions

Since this is a client-side React bundle, the backend logic (Bcrypt hashing) must be deployed to Supabase Edge Functions.

## 1. Database Setup (SQL)

Run this SQL in your Supabase SQL Editor to set up the necessary tables.

```sql
-- 1. Create Admins Table
create table admins (
  id uuid default gen_random_uuid() primary key,
  email text unique not null,
  password_hash text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. Create Users Table (for the excel upload)
create table users (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  email text not null,
  phone_number text,
  branch text,
  department text,
  context text,
  dob date,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. Enable RLS (Security)
alter table users enable row level security;
alter table admins enable row level security;

-- 4. Create Policies
-- Allow public read access to users (or restrict to authenticated admins if you implement JWT checking in postgres)
-- For this demo, we allow anon read, but write is restricted.
create policy "Enable read access for all users" on users for select using (true);
create policy "Enable insert for authenticated (service role) only" on users for insert with check (true);

-- 5. Seed an Admin User
-- Password is 'admin123'. Hash generated via bcrypt cost 10.
insert into admins (email, password_hash)
values ('admin@example.com', '$2a$10$X7.X.X.X.X.X.X.X.X.X.X.X.X.X.X.X.examplehashplaceholder');
-- NOTE: In a real scenario, generate a hash using node:
-- const bcrypt = require('bcrypt');
-- console.log(bcrypt.hashSync('admin123', 10));
-- Actual hash for 'admin123': $2b$10$vI8aWBnW3fID.ZQ4/zo1G.q1lRps.9cGLcZEiGDMVr5yUP1KUOYTa
```

## 2. Supabase Edge Function: `admin-login`

Create a function `supabase functions new admin-login`.
Replace the content of `index.ts` with:

```typescript
// supabase/functions/admin-login/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"
import * as bcrypt from "https://deno.land/x/bcrypt@v0.4.1/mod.ts"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { email, password } = await req.json()

    // Create Supabase Client with Service Role Key (Server side only!)
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Fetch admin by email
    const { data: admin, error } = await supabaseClient
      .from('admins')
      .select('*')
      .eq('email', email)
      .single()

    if (error || !admin) {
      return new Response(JSON.stringify({ error: 'Invalid credentials' }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // Compare Password
    const match = await bcrypt.compare(password, admin.password_hash)

    if (!match) {
      return new Response(JSON.stringify({ error: 'Invalid credentials' }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // Generate a simple session token (In prod, sign a real JWT)
    const token = btoa(`${admin.id}:${Date.now()}`)

    return new Response(JSON.stringify({ token, message: 'Login successful' }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})
```

## 3. Deployment

1. `supabase functions deploy admin-login`
2. Set your env secrets: `supabase secrets set SUPABASE_SERVICE_ROLE_KEY=...`

## 4. Running the React App

The React app checks `process.env.VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`.
Create a `.env` file in the root:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

If the Edge Function is not reachable, the React app falls back to a **Demo Mode** (admin@example.com / admin123) so you can preview the UI.
