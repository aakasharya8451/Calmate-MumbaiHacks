import { supabase } from '../lib/supabase';
import { AuthSession } from '../types';
import bcrypt from 'bcryptjs';

export const authService = {
  /**
   * Logs in the admin user.
   * In a real production app, this invokes a Supabase Edge Function to 
   * securely compare the bcrypt hash on the server side.
   */
  login: async (email: string, password: string): Promise<AuthSession> => {
    try {
      // 1. Query the admins table directly
      const { data: adminData, error } = await supabase
        .from('admin')
        .select('*')
        .eq('email', email)
        .limit(1);

      const admin = adminData?.[0];

      console.log('Supabase Query Result:', { admin, error });

      if (error || !admin) {
        console.error('User not found or query error');
        throw new Error('Invalid credentials');
      }

      // 2. Verify password using bcryptjs
      console.log('Verifying password...');
      const isValid = await bcrypt.compare(password, admin.password);
      console.log('Password valid:', isValid);

      if (!isValid) {
        console.error('Password mismatch');
        throw new Error('Invalid credentials');
      }

      // 3. Return session
      return {
        token: btoa(`${admin.id}:${Date.now()}`), // Simple token generation
        adminEmail: email
      };

    } catch (err: any) {
      console.error('Login error:', err);
      throw new Error(err.message || 'Login failed');
    }
  },

  logout: () => {
    localStorage.removeItem('admin_session');
    window.location.href = '/';
  }
};
