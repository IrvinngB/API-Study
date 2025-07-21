-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.calendar_events (
  user_id uuid NOT NULL,
  class_id uuid,
  title text NOT NULL,
  description text,
  start_datetime timestamp with time zone NOT NULL,
  end_datetime timestamp with time zone NOT NULL,
  location text,
  google_calendar_id text,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  event_type text DEFAULT 'class'::text,
  is_recurring boolean DEFAULT false,
  recurrence_pattern jsonb DEFAULT '{}'::jsonb,
  reminder_minutes integer DEFAULT 15,
  external_calendar_sync jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT calendar_events_pkey PRIMARY KEY (id),
  CONSTRAINT calendar_events_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id),
  CONSTRAINT calendar_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.categories_grades (
  class_id uuid NOT NULL,
  name text NOT NULL,
  percentage numeric NOT NULL,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT categories_grades_pkey PRIMARY KEY (id),
  CONSTRAINT categories_grades_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id)
);
CREATE TABLE public.classes (
  user_id uuid NOT NULL,
  name text NOT NULL,
  code text,
  instructor text,
  credits integer,
  semester text,
  description text,
  syllabus_url text,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  color text DEFAULT '#3B82F6'::text,
  is_active boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT classes_pkey PRIMARY KEY (id),
  CONSTRAINT classes_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.grades (
  description text,
  value numeric,
  calendar_event_id uuid,
  event_type character varying,
  user_id uuid NOT NULL,
  class_id uuid NOT NULL,
  title text,
  score numeric NOT NULL,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  max_score numeric DEFAULT 100,
  graded_at timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  category_id uuid NOT NULL,
  CONSTRAINT grades_pkey PRIMARY KEY (id),
  CONSTRAINT grades_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id),
  CONSTRAINT fk_grades_calendar_event_id FOREIGN KEY (calendar_event_id) REFERENCES public.calendar_events(id),
  CONSTRAINT grades_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories_grades(id),
  CONSTRAINT grades_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.notes (
  user_id uuid NOT NULL,
  class_id uuid NOT NULL,
  title text NOT NULL,
  content text NOT NULL,
  ai_summary text,
  lesson_date date,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  tags ARRAY DEFAULT '{}'::text[],
  local_files_path text DEFAULT 'StudyFiles'::text,
  attachments jsonb DEFAULT '[]'::jsonb,
  is_favorite boolean DEFAULT false,
  last_edited timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT notes_pkey PRIMARY KEY (id),
  CONSTRAINT notes_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id),
  CONSTRAINT notes_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.notifications (
  user_id uuid NOT NULL,
  title text NOT NULL,
  message text NOT NULL,
  action_url text,
  scheduled_for timestamp with time zone,
  sent_at timestamp with time zone,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  type text DEFAULT 'info'::text,
  is_read boolean DEFAULT false,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT notifications_pkey PRIMARY KEY (id),
  CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.tasks (
  user_id uuid NOT NULL,
  class_id uuid,
  title text NOT NULL,
  description text,
  due_date timestamp with time zone,
  estimated_duration integer,
  device_created text,
  completed_at timestamp with time zone,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  priority integer DEFAULT 2 CHECK (priority >= 1 AND priority <= 3),
  status text DEFAULT 'pending'::text,
  completion_percentage integer DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
  tags ARRAY DEFAULT '{}'::text[],
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT tasks_pkey PRIMARY KEY (id),
  CONSTRAINT tasks_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id),
  CONSTRAINT tasks_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id)
);
CREATE TABLE public.user_devices (
  user_id uuid NOT NULL,
  device_id text NOT NULL,
  device_name text,
  device_type text,
  last_sync timestamp with time zone DEFAULT now(),
  is_active boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_devices_pkey PRIMARY KEY (user_id, device_id),
  CONSTRAINT user_devices_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.user_profiles (
  email text NOT NULL UNIQUE,
  full_name text,
  avatar_url text,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  timezone text DEFAULT 'America/Panama'::text,
  subscription_tier text DEFAULT 'free'::text,
  preferences jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_profiles_pkey PRIMARY KEY (id)
);