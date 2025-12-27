import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://zbjqzktppxnhydpmcety.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpianF6a3RwcHhuaHlkcG1jZXR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4NTM3MDYsImV4cCI6MjA4MjQyOTcwNn0.Ei4ZqWmjxTJ2pqi42UjdRga5x2UnFlnN3igy6WBJ8ns';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
