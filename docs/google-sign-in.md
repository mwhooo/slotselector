# Google Sign-In Setup

SlotSelector uses Supabase Auth for Google sign-in and a row-level-secured Supabase table for signed-in app state. Guest data remains in browser storage.

## Supabase Project

1. Create a Supabase project.
2. In the SQL Editor, run [`../supabase/schema.sql`](../supabase/schema.sql).
3. In Authentication URL Configuration, set the Site URL to `https://slotselector.markbakker.online`.
4. Add redirect URLs for `https://slotselector.markbakker.online/**` and `http://localhost:5173/**`.
5. In Authentication Providers, enable Google and copy the callback URL shown by Supabase.

## Google OAuth Client

1. Create a Web application OAuth client in Google Cloud Console and configure its consent screen.
2. Add the Supabase callback URL from the previous section as an authorized redirect URI. It has the form `https://<project-ref>.supabase.co/auth/v1/callback`.
3. Copy the Google client ID and client secret into the Google provider settings in Supabase. Do not put the Google client secret in this repository or in frontend environment variables.
4. Publish the Google consent screen when ready for general users. While it remains in Testing, only configured test users can sign in.

## Frontend Configuration

Copy `.env.example` to `.env` and set the Supabase project URL and publishable key from the Supabase project API settings. The publishable key is intended for browser use; the database policies in `schema.sql` restrict each user to their own row. Never use a Supabase `service_role` key in the frontend.

Build the Docker image with Compose so these build arguments are included:

```powershell
docker compose build
```

The NUC image must be rebuilt and transferred after the credentials are configured. Add the production hostname to Supabase's allowed redirect URLs. For local Vite development, keep `http://localhost:5173/**` configured.

On first Google sign-in, saved hunts from the current guest browser are merged into the account. Signed-in state is then synced to that account and also cached in a separate browser-storage key. Signing out returns to the guest browser state.