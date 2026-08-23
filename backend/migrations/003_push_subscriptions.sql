-- Migration 003: Web Push subscriptions and reminder state

create table push_subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  endpoint text not null,
  p256dh text not null,
  auth_key text not null,
  timezone text not null default 'UTC',
  created_at timestamptz not null default now(),
  unique (user_id, endpoint)
);

alter table users add column if not exists reminders_enabled boolean not null default false;
alter table users add column if not exists reminder_last_sent_at timestamptz;

create index push_subscriptions_user_id_idx on push_subscriptions(user_id);

-- RLS for push_subscriptions (defense-in-depth; backend uses service role)
alter table push_subscriptions enable row level security;

create policy "Users can view their own push subscriptions"
  on push_subscriptions
  for select
  using (auth.uid() = user_id);

create policy "Users can insert their own push subscriptions"
  on push_subscriptions
  for insert
  with check (auth.uid() = user_id);

create policy "Users can delete their own push subscriptions"
  on push_subscriptions
  for delete
  using (auth.uid() = user_id);
