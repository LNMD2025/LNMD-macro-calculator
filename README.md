# Cadence

Social fitness, coach programming, and free nutrition tools. This repository is the installable web app for [cdncapp.com](https://cdncapp.com).

## What this build fixes

- Feed, stories, and comments no longer call an undefined `supabase` client (they use the shared `sb` client).
- Repost no longer crashes on a removed `renderFeed()` helper.
- The app is a real PWA: manifest, icons, service worker, install prompt, Add to Home Screen on iOS.
- Mobile shell uses safe-area insets, 16px inputs (no iOS zoom), and a bottom tab bar that clears the home indicator.
- Macro Calculator includes Katch-McArdle targets for training days and rest days, meals per day, per-session two-a-day details, and optional save to `macro_profiles`.
- Supabase public tables now have RLS. Catalog data stays readable. Nutrition and personal logs are owner-only.
- `handle_new_user()` can no longer be called as a public RPC.

## Run locally

Open `index.html` from a local static server (required for the service worker and install prompt):

```bash
python3 -m http.server 4173
```

Then visit `http://localhost:4173`. Use Chrome DevTools → Application → Manifest to confirm installability.

## Deploy

Host the repo root on Cloudflare Pages or GitHub Pages.

- Cloudflare: `_redirects` and `_headers` are already included.
- Point the production domain at this build when you are ready to replace the live prototype.

## Backend

Supabase project `doughbros-training` (`stezlxsdtjxieckqvhba`). The browser uses the publishable/anon key only. Row-level security is the access control layer.
