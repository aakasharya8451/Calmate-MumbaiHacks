export interface User {
  id?: string;
  name: string;
  email: string;
  phone_number: string;
  branch: string;
  department: string;
  context?: string;
  dob?: string; // YYYY-MM-DD
  created_at?: string;
}

export interface Admin {
  id: string;
  email: string;
  // password_hash is never exposed to client
}

export interface AuthSession {
  token: string;
  adminEmail: string;
}

export interface SortConfig {
  key: keyof User;
  direction: 'asc' | 'desc';
}

export interface ExcelRow {
  name: string;
  email: string;
  phone_number: string;
  branch: string;
  department: string;
  context: string;
  dob: string | number;
  [key: string]: any;
}
