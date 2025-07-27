-- Primero eliminamos todas las vistas existentes
DROP VIEW IF EXISTS public.vw_user_dashboard;
DROP VIEW IF EXISTS public.vw_events_with_tasks;
DROP VIEW IF EXISTS public.vw_calendar_grades_linked;
DROP VIEW IF EXISTS public.vw_grades_by_course;
DROP VIEW IF EXISTS public.vw_grades_by_category;
DROP VIEW IF EXISTS public.vw_calendar_with_grades;

-- View: vw_calendar_with_grades
-- Trae todos los eventos de calendario y, si existe, la calificación asociada (solo grades activas)
CREATE VIEW public.vw_calendar_with_grades AS
SELECT
    ce.*,
    g.id AS grade_id,
    g.title AS grade_title,
    g.description AS grade_description,
    g.score,
    g.max_score,
    g.graded_at,
    g.category_id,
    g.value AS grade_value
FROM public.calendar_events ce
LEFT JOIN public.grades g ON g.calendar_event_id = ce.id AND g.value = 1;

-- View: vw_grades_by_category
-- Trae solo las calificaciones activas agrupadas por categoría
CREATE VIEW public.vw_grades_by_category AS
SELECT
    g.id AS grade_id,
    g.user_id,
    g.class_id,
    g.category_id,
    cg.name AS category_name,
    cg.percentage AS category_percentage,
    g.title AS grade_title,
    g.description AS grade_description,
    g.score,
    g.max_score,
    g.graded_at,
    g.calendar_event_id,
    g.value AS grade_value
FROM public.grades g
LEFT JOIN public.categories_grades cg ON g.category_id = cg.id
WHERE g.value = 1;

-- View: vw_grades_by_course
-- Trae solo las calificaciones activas agrupadas por curso (class_id)
CREATE VIEW public.vw_grades_by_course AS
SELECT
    g.id AS grade_id,
    g.user_id,
    g.class_id,
    c.name AS class_name,
    g.title AS grade_title,
    g.description AS grade_description,
    g.score,
    g.max_score,
    g.graded_at,
    g.category_id,
    g.calendar_event_id,
    g.value AS grade_value
FROM public.grades g
LEFT JOIN public.classes c ON g.class_id = c.id
WHERE g.value = 1;

-- View: vw_calendar_grades_linked
-- Solo los eventos de calendario que tienen calificación asociada (grades activas)
CREATE VIEW public.vw_calendar_grades_linked AS
SELECT
    ce.*,
    g.id AS grade_id,
    g.title AS grade_title,
    g.description AS grade_description,
    g.score,
    g.max_score,
    g.graded_at,
    g.category_id,
    g.value AS grade_value
FROM public.calendar_events ce
INNER JOIN public.grades g ON g.calendar_event_id = ce.id AND g.value = 1;

-- View: vw_events_with_tasks
-- Muestra todos los eventos de calendario y, si existe, la tarea asociada (por user_id, class_id y fechas aproximadas)
CREATE VIEW public.vw_events_with_tasks AS
SELECT
    ce.id AS calendar_event_id,
    ce.user_id,
    ce.class_id,
    ce.title AS event_title,
    ce.start_datetime,
    ce.end_datetime,
    ce.location,
    ce.event_type,
    t.id AS task_id,
    t.title AS task_title,
    t.due_date,
    t.status,
    t.completion_percentage,
    g.id AS grade_id,
    g.value AS grade_value
FROM public.calendar_events ce
LEFT JOIN public.tasks t ON t.user_id = ce.user_id
    AND (t.class_id = ce.class_id OR t.class_id IS NULL)
    AND (
        t.due_date BETWEEN ce.start_datetime - INTERVAL '1 day' AND ce.end_datetime + INTERVAL '1 day'
        OR t.due_date IS NULL
    )
LEFT JOIN public.grades g ON g.calendar_event_id = ce.id AND g.value = 1;

-- View: vw_user_dashboard
-- Resumen para el usuario: próximos eventos, tareas pendientes y últimas calificaciones
CREATE VIEW public.vw_user_dashboard AS
SELECT
    u.id AS user_id,
    u.email,
    ce.id AS next_event_id,
    ce.title AS next_event_title,
    ce.start_datetime AS next_event_start,
    t.id AS next_task_id,
    t.title AS next_task_title,
    t.due_date AS next_task_due,
    g.id AS last_grade_id,
    g.title AS last_grade_title,
    g.score AS last_grade_score,
    g.graded_at AS last_grade_date,
    g.value AS last_grade_value
FROM public.user_profiles u
LEFT JOIN LATERAL (
    SELECT * FROM public.calendar_events ce2 
    WHERE ce2.user_id = u.id 
    AND ce2.start_datetime > now() 
    ORDER BY ce2.start_datetime ASC 
    LIMIT 1
) ce ON TRUE
LEFT JOIN LATERAL (
    SELECT * FROM public.tasks t2 
    WHERE t2.user_id = u.id 
    AND t2.status = 'pending' 
    ORDER BY t2.due_date ASC 
    LIMIT 1
) t ON TRUE
LEFT JOIN LATERAL (
    SELECT * FROM public.grades g2 
    WHERE g2.user_id = u.id 
    AND g2.value = 1 
    ORDER BY g2.graded_at DESC 
    LIMIT 1
) g ON TRUE;