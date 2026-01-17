-- Supabase SQL schema for wine-liquidation
-- (Откройте Supabase Dashboard → SQL Editor → New query → вставьте и выполните)

-- Таблица винных позиций
create table if not exists public.wines (
  id text primary key,
  category text,
  name text not null,
  region text,
  price numeric not null default 0,
  discount_price numeric not null default 0,
  quantity integer not null default 0,
  updated_at timestamptz not null default now()
);

-- Авто-обновление updated_at при изменениях
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists wines_set_updated_at on public.wines;
create trigger wines_set_updated_at
before update on public.wines
for each row execute function public.set_updated_at();

-- ВАЖНО: включаем RLS (Row Level Security)
-- RLS = правила, кто может читать/писать строки таблицы
alter table public.wines enable row level security;

-- Политики (Policies) для безопасного варианта: только залогиненные пользователи
drop policy if exists "wines_read_authenticated" on public.wines;
create policy "wines_read_authenticated"
on public.wines
for select
to authenticated
using (true);

drop policy if exists "wines_write_authenticated" on public.wines;
create policy "wines_write_authenticated"
on public.wines
for all
to authenticated
using (true)
with check (true);

-- ============================
-- История изменений (журнал)
-- ============================
-- В Supabase обычно уже включён pgcrypto, но на всякий случай:
create extension if not exists pgcrypto;

create table if not exists public.wine_events (
  id uuid primary key default gen_random_uuid(),
  wine_id text not null references public.wines(id) on delete cascade,
  event_type text not null, -- sale | restock | adjust
  delta integer not null,
  old_quantity integer not null,
  new_quantity integer not null,
  source text, -- откуда изменение: modal / inline / etc
  actor text, -- кто менял (email из Auth)
  created_at timestamptz not null default now()
);

alter table public.wine_events enable row level security;

drop policy if exists "wine_events_read_authenticated" on public.wine_events;
create policy "wine_events_read_authenticated"
on public.wine_events
for select
to authenticated
using (true);

drop policy if exists "wine_events_insert_authenticated" on public.wine_events;
create policy "wine_events_insert_authenticated"
on public.wine_events
for insert
to authenticated
with check (true);

-- Быстрый “итог” для UI (чипы в списке Истории)
-- Считает суммарное изменение количества (delta_sum) и количество событий (events_count) по каждой позиции.
drop view if exists public.wine_event_summary;
create view public.wine_event_summary as
select
  wine_id,
  count(*)::int as events_count,
  coalesce(sum(delta), 0)::int as delta_sum,
  max(created_at) as last_event_at
from public.wine_events
group by wine_id;

-- Публичный режим без пароля (НЕ рекомендуется для реальных данных).
-- Если когда-нибудь захотите “без логина”, раскомментируйте блок ниже.
--
-- drop policy if exists "wines_read_anon" on public.wines;
-- create policy "wines_read_anon"
-- on public.wines
-- for select
-- to anon
-- using (true);
--
-- drop policy if exists "wines_write_anon" on public.wines;
-- create policy "wines_write_anon"
-- on public.wines
-- for all
-- to anon
-- using (true)
-- with check (true);

