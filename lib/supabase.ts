/**
 * Supabase Client - Singleton client for Supabase PostgreSQL.
 * Replaces the DynamoDB client from the Python backend.
 */

import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    "Missing Supabase environment variables. Copy .env.local.example to .env.local and fill in your Supabase credentials."
  );
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);