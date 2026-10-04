create table if not exists public.slotselector_user_state (
  user_id uuid primary key references auth.users (id) on delete cascade,
  state jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.slotselector_user_state enable row level security;

drop policy if exists "Users can read their own SlotSelector state" on public.slotselector_user_state;
create policy "Users can read their own SlotSelector state"
  on public.slotselector_user_state
  for select
  to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "Users can create their own SlotSelector state" on public.slotselector_user_state;
create policy "Users can create their own SlotSelector state"
  on public.slotselector_user_state
  for insert
  to authenticated
  with check ((select auth.uid()) = user_id);

drop policy if exists "Users can update their own SlotSelector state" on public.slotselector_user_state;
create policy "Users can update their own SlotSelector state"
  on public.slotselector_user_state
  for update
  to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "Users can delete their own SlotSelector state" on public.slotselector_user_state;
create policy "Users can delete their own SlotSelector state"
  on public.slotselector_user_state
  for delete
  to authenticated
  using ((select auth.uid()) = user_id);

grant select, insert, update, delete on public.slotselector_user_state to authenticated;