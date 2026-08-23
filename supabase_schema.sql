-- SnapClass schema - run this in Supabase SQL Editor

create table public.teachers (
  teacher_id bigint generated always as identity primary key,
  username text unique not null,
  password text not null,
  name text not null
);

create table public.students (
  student_id bigint generated always as identity primary key,
  name text not null,
  face_embedding jsonb,
  voice_embedding jsonb
);

create table public.subjects (
  subject_id bigint generated always as identity primary key,
  subject_code text unique not null,
  name text not null,
  section text,
  teacher_id bigint references public.teachers (teacher_id)
);

create table public.subject_students (
  student_id bigint references public.students (student_id),
  subject_id bigint references public.subjects (subject_id),
  primary key (student_id, subject_id)
);

create table public.attendance_logs (
  log_id bigint generated always as identity primary key,
  student_id bigint references public.students (student_id),
  subject_id bigint references public.subjects (subject_id),
  timestamp timestamptz not null,
  is_present boolean not null
);

-- App uses the raw API key without user auth, so allow access
alter table public.teachers enable row level security;
alter table public.students enable row level security;
alter table public.subjects enable row level security;
alter table public.subject_students enable row level security;
alter table public.attendance_logs enable row level security;

create policy "allow all teachers" on public.teachers for all using (true) with check (true);
create policy "allow all students" on public.students for all using (true) with check (true);
create policy "allow all subjects" on public.subjects for all using (true) with check (true);
create policy "allow all enrollments" on public.subject_students for all using (true) with check (true);
create policy "allow all logs" on public.attendance_logs for all using (true) with check (true);
