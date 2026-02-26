-- Enable RLS on all three tables
ALTER TABLE public.account_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.outbox ENABLE ROW LEVEL SECURITY;

-- account_metadata: authenticated users can read their own row
CREATE POLICY "Users can read own account metadata"
  ON public.account_metadata
  FOR SELECT
  TO authenticated
  USING (account_id = auth.uid());

-- profiles: authenticated users can read their own profile
CREATE POLICY "Users can read own profile"
  ON public.profiles
  FOR SELECT
  TO authenticated
  USING (account_id = auth.uid());

-- outbox: only admins can read
CREATE POLICY "Admins can read outbox"
  ON public.outbox
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.account_metadata
      WHERE account_metadata.account_id = auth.uid()
        AND account_metadata.role IN ('ADMIN', 'SUPER_ADMIN')
    )
  );
