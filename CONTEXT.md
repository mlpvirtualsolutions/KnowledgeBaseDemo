# Logidex Platform — Claude Code Context

## What this is
A multi-tenant SaaS web app where companies pay for employees
to log in and chat with their AI-powered department handbook.
Each company has its own n8n workflow with its own webhook URL.
The platform routes each logged-in user to their company's
specific workflow so they only ever query their own data.

## Current state
- Chat interface exists and works for the Meridian demo company
- n8n RAG workflow is working — ingests Google Drive docs,
  answers questions via AI, returns responses to the chat UI
- Supabase is set up BUT currently connected to the Meridian
  project — this is wrong and needs to be updated
- Auth is partially built but the users table lives inside the
  Meridian Supabase project — it needs to move to a new
  dedicated Platform Supabase project
- The n8n webhook URL is currently hardcoded — needs to be
  dynamic and per-company

## Supabase setup — TWO separate projects
1. PLATFORM PROJECT (new — needs to be created)
   Holds: companies table, users table
   Used for: auth, session management, company routing
   Env vars: SUPABASE_PLATFORM_URL, SUPABASE_PLATFORM_ANON_KEY
   This is the project the VS Code app connects to for all
   auth and routing logic.

2. MERIDIAN PROJECT (existing — do not touch)
   Holds: Meridian's vector/document data
   Used by: Meridian's n8n workflow only
   The VS Code app does NOT directly query this project.
   n8n handles it internally.

Current code is pointed at the Meridian project for auth —
this must be updated to point to the Platform project.

## Target database schema (Platform project)

### companies table
- id (uuid, primary key)
- name (text)
- n8n_webhook_url (text) — stored server-side only, never
  sent to browser
- seat_limit (integer)
- subscription_status (text, default 'active')
- stripe_customer_id (text, nullable)
- created_at (timestamp)

### users table
- id (uuid, primary key)
- email (text, unique)
- role (text — values: employee, company_admin, super_admin)
- company_id (uuid, FK to companies — NULL for super_admin)
- department_id (text, nullable — e.g. 'sales', 'ops')
- seat_active (boolean, default true)
- created_at (timestamp)

department_id is passed with every chat query to n8n so the
workflow filters retrieved content to only that department's
data. Super admin has department_id = NULL.

## Auth flow
1. User enters email + password on /login
2. Supabase Auth (Platform project) verifies credentials
3. Session is created storing: user_id, company_id, role,
   department_id
4. Role-based routing:
   - employee → /chat
   - company_admin → /admin/users
   - super_admin → /superadmin

## Forgot password flow
- "Forgot password?" link on the login page
- User enters email, receives a reset link via email
- Reset link is single-use, expires after 1 hour
- Use Supabase Auth's built-in password recovery
- Do NOT build this from scratch

## Chat message routing flow
1. User sends message in chat UI
2. Backend reads company_id + role + department_id from session
3. If role is NOT super_admin:
   - Check seat_active = true
   - Check company subscription_status = 'active'
   - If either fails, return: "Your access is currently
     inactive. Please contact your administrator."
4. Query companies table: SELECT n8n_webhook_url WHERE
   id = company_id
5. POST to that webhook URL with: user message + company_id
   + department_id
6. Stream n8n response back to chat UI

## Super admin behavior
- role = 'super_admin', company_id = NULL, department_id = NULL
- Bypasses ALL checks (stripe, seat_active, department)
- On /superadmin page load, backend queries the companies table
  and returns all companies (id + name only — not webhook URL)
  to populate a company selector dropdown
- Super admin picks a company from the dropdown before sending
  a message
- Chat endpoint: if role = super_admin, reads company_id from
  the request body (the dropdown selection) instead of session.
  Webhook URL is never sent to the frontend — only the
  company_id is passed in the chat request body, and the
  backend does the webhook lookup server-side
- Super admin is NEVER added to individual company accounts
- There is one super admin account: mlpvirtualsolutions@gmail.com

## Webhook URL security
n8n_webhook_url is stored in the companies table but is
server-side only — it is never returned to the browser or
exposed in any API response to the client. Backend reads it
and uses it internally only.

## What is NOT being built right now (do not implement)
- Stripe integration
- User invite / email flow
- Company admin dashboard with analytics
- Self-serve onboarding
- Anything not listed in the Bucket 1 steps below

## Bucket 1 — the only goal
1. New Platform Supabase project with correct schema
2. VS Code app auth pointed at Platform project
3. Session carries company_id + role + department_id
4. Chat routing is dynamic per company via webhook URL lookup
5. Super admin page with company selector and company management
6. Forgot password flow
7. Full end-to-end test: two different company users each
   routed to their own n8n workflow