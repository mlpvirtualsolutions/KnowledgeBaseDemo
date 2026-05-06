
- create different project for all companies and use that db
- come up with list of columns for user info table
- create user info table like with modified query below
create table public.users (
  id            uuid primary key references auth.users,
  first_name    text,
  last_name     text
);
- ask claude now that table is created how fetch user_info 
- run a login flow with user loging in and display user_info
- use url dictionary mapper to set n8n url based on user_info's user_group



-------------------------------------------
- add a create user flow
- add an admin page to edit users
- add a forgot password option