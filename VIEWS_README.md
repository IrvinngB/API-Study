# Documentación de las Vistas SQL relacionadas con Task y Calificaciones

Este documento describe las vistas SQL implementadas en el backend para la gestión de tareas (tasks), eventos de calendario y calificaciones (grades), así como los endpoints de la API que exponen estos datos a los clientes.

## Índice
- [Introducción](#introducción)
- [Vistas SQL](#vistas-sql)
  - [vw_calendar_with_grades](#vw_calendar_with_grades)
  - [vw_grades_by_category](#vw_grades_by_category)
  - [vw_grades_by_course](#vw_grades_by_course)
  - [vw_calendar_grades_linked](#vw_calendar_grades_linked)
  - [vw_events_with_tasks](#vw_events_with_tasks)
  - [vw_user_dashboard](#vw_user_dashboard)
- [Endpoints de la API](#endpoints-de-la-api)
- [Modelos de Respuesta](#modelos-de-respuesta)

---

## Introducción

Las vistas SQL permiten consultar información compleja y relacionada entre eventos de calendario, tareas y calificaciones de manera eficiente. Estas vistas se utilizan en los endpoints de la API para entregar datos listos para el consumo de la aplicación frontend.

---

## Vistas SQL

### 1. vw_calendar_with_grades
- **Descripción:** Devuelve todos los eventos de calendario y, si existe, la calificación asociada (solo grades activas, es decir, `value = 1`).
- **Uso típico:** Mostrar eventos con posibles calificaciones vinculadas.
- **Campos relevantes:**
  - Datos del evento (id, title, start_datetime, etc.)
  - Datos de la calificación asociada (grade_id, grade_title, score, etc.)

### 2. vw_grades_by_category
- **Descripción:** Devuelve solo las calificaciones activas agrupadas por categoría.
- **Uso típico:** Mostrar el rendimiento del usuario por categoría de calificación.
- **Campos relevantes:**
  - grade_id, user_id, class_id, category_id
  - category_name, category_percentage
  - score, max_score, graded_at

### 3. vw_grades_by_course
- **Descripción:** Devuelve solo las calificaciones activas agrupadas por curso (class_id).
- **Uso típico:** Mostrar el rendimiento del usuario por curso.
- **Campos relevantes:**
  - grade_id, user_id, class_id, class_name
  - score, max_score, graded_at

### 4. vw_calendar_grades_linked
- **Descripción:** Devuelve solo los eventos de calendario que tienen una calificación asociada (grades activas).
- **Uso típico:** Listar eventos que están directamente relacionados con una calificación.
- **Campos relevantes:**
  - Datos del evento y de la calificación asociada

### 5. vw_events_with_tasks
- **Descripción:** Muestra todos los eventos de calendario y, si existe, la tarea asociada (por user_id, class_id y fechas aproximadas).
- **Uso típico:** Relacionar eventos de calendario con tareas y calificaciones.
- **Campos relevantes:**
  - calendar_event_id, event_title, start_datetime
  - task_id, task_title, due_date, status
  - grade_id, grade_value

### 6. vw_user_dashboard
- **Descripción:** Resumen para el usuario: próximos eventos, tareas pendientes y últimas calificaciones.
- **Uso típico:** Dashboard/resumen en la app.
- **Campos relevantes:**
  - next_event_id, next_task_id, last_grade_id, etc.

---

## Endpoints de la API

Los siguientes endpoints de FastAPI exponen las vistas anteriores:

- `GET /vw/calendar-with-grades` → Devuelve la vista `vw_calendar_with_grades` para el usuario autenticado.
- `GET /vw/grades-by-category` → Devuelve la vista `vw_grades_by_category` para el usuario autenticado.
- `GET /vw/grades-by-course` → Devuelve la vista `vw_grades_by_course` para el usuario autenticado.
- `GET /vw/calendar-grades-linked` → Devuelve la vista `vw_calendar_grades_linked` para el usuario autenticado.

Todos estos endpoints requieren autenticación y filtran los resultados por el `user_id` del usuario autenticado.

---

## Modelos de Respuesta

Cada endpoint utiliza un modelo de respuesta basado en Pydantic, que refleja la estructura de la vista SQL correspondiente. Ejemplo de modelos:


Estos modelos se encuentran en `models.py` y aseguran que los datos devueltos sean consistentes y tipados.


## Modelos y Relaciones

Las vistas y endpoints mencionados utilizan los siguientes modelos de Pydantic, que reflejan la estructura de las tablas y relaciones en la base de datos. A continuación se describen los modelos principales y cómo se relacionan entre sí:

### Diagrama de Relaciones Simplificado

```
UserProfile (user_id)
   │
   ├───┬────────────┐
   │   │            │
Class  CalendarEvent  CategoryGrade
   │        │             │
   │        │             │
   └────┬───┘             │
        │                 │
      Grade ──────────────┘
        │
      (relaciona class_id, category_id, calendar_event_id)
```

### Modelos Clave

#### CalendarWithGrades
Representa un evento de calendario con información de una calificación asociada (si existe).
- Incluye campos de evento (`id`, `title`, `start_datetime`, etc.) y de calificación (`grade_id`, `score`, `category_id`, etc.).
- Relaciona: `CalendarEvent` ←→ `Grade` (por `calendar_event_id`)

#### GradeByCategory
Representa una calificación agrupada por categoría.
- Incluye información de la categoría (`category_id`, `category_name`, `category_percentage`) y de la calificación.
- Relaciona: `Grade` ←→ `CategoryGrade` (por `category_id`)

#### GradeByCourse
Representa una calificación agrupada por curso.
- Incluye información del curso (`class_id`, `class_name`) y de la calificación.
- Relaciona: `Grade` ←→ `Class` (por `class_id`)

#### CalendarGradesLinked
Representa eventos de calendario que tienen una calificación asociada obligatoriamente.
- Similar a `CalendarWithGrades`, pero solo incluye eventos con calificación.

### Campos y Relaciones Importantes

- **user_id**: Presente en casi todos los modelos, asegura que los datos sean filtrados por usuario.
- **class_id**: Relaciona eventos, calificaciones y categorías con una clase específica.
- **category_id**: Relaciona calificaciones con una categoría de calificación.
- **calendar_event_id**: Relaciona calificaciones con eventos de calendario.
- **value**: Campo en `Grade` que indica si la calificación está activa (1) o completada (0).

### Ejemplo de Modelo: CalendarWithGrades

```python
class CalendarWithGrades(BaseModel):
    id: UUID
    user_id: UUID
    class_id: Optional[UUID]
    title: str
    description: Optional[str]
    start_datetime: datetime
    end_datetime: datetime
    location: Optional[str]
    google_calendar_id: Optional[str]
    event_type: Optional[str]
    is_recurring: Optional[bool]
    recurrence_pattern: Optional[Dict[str, Any]]
    reminder_minutes: Optional[int]
    external_calendar_sync: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    grade_id: Optional[UUID]
    grade_title: Optional[str]
    grade_description: Optional[str]
    score: Optional[float]
    max_score: Optional[float]
    graded_at: Optional[datetime]
    category_id: Optional[UUID]
    grade_value: Optional[float]
```

Puedes consultar todos los modelos completos en el archivo `models.py`.

---

## Desglose de Modelos y Campos

A continuación se describen los modelos principales utilizados en las vistas y sus campos más relevantes:

### 1. UserProfile
**Descripción:** Representa al usuario de la plataforma.
- `id`: UUID único del usuario.
- `email`: Correo electrónico.
- `full_name`, `avatar_url`, `timezone`, `subscription_tier`, `preferences`, `created_at`, `updated_at`.

### 2. Class
**Descripción:** Representa una clase o curso.
- `id`: UUID único de la clase.
- `user_id`: Usuario propietario.
- `name`, `code`, `instructor`, `color`, `credits`, `semester`, `description`, `syllabus_url`, `is_active`, `created_at`, `updated_at`.

### 3. CalendarEvent
**Descripción:** Evento de calendario (clase, examen, recordatorio, etc.).
- `id`, `user_id`, `class_id`, `title`, `description`, `start_datetime`, `end_datetime`, `event_type`, `is_recurring`, `recurrence_pattern`, `location`, `reminder_minutes`, `google_calendar_id`, `external_calendar_sync`, `created_at`, `updated_at`.

### 4. CategoryGrade
**Descripción:** Categoría de calificación (por ejemplo, "Exámenes", "Tareas").
- `id`, `user_id`, `class_id`, `name`, `percentage`, `created_at`, `updated_at`.

### 5. Grade
**Descripción:** Calificación obtenida por el usuario en una categoría y clase específica.
- `id`, `user_id`, `class_id`, `category_id`, `title`, `description`, `score`, `max_score`, `calendar_event_id`, `event_type`, `graded_at`, `created_at`, `updated_at`, `value` (1=activa, 0=completada).

### 6. Task (tarea)
**Descripción:** Tarea asociada a un usuario, clase y fecha límite.
- `id`, `user_id`, `class_id`, `title`, `due_date`, `status`, `completion_percentage`.

---

## Ejemplo de Relación entre Modelos

Supongamos que un usuario tiene una clase de Matemáticas. En esa clase hay una categoría de calificación llamada "Exámenes" (20%). El usuario tiene un evento de calendario para el examen final, y una calificación asociada a ese evento. Además, hay una tarea para estudiar para ese examen.

```
UserProfile ──┬─> Class ──┬─> CategoryGrade ──┬─> Grade ──┬─> CalendarEvent
              │          │                   │           └─> Task
              │          │                   └─> Task
              │          └─> CalendarEvent
              └─> Task
```

---

## Ejemplo de Consulta y Respuesta

**Consulta:**
```http
GET /vw/calendar-with-grades
Authorization: Bearer <token>
```

**Respuesta:**
```json
[
  {
    "id": "...",
    "user_id": "...",
    "class_id": "...",
    "title": "Examen Final",
    "start_datetime": "2025-07-30T08:00:00Z",
    "end_datetime": "2025-07-30T10:00:00Z",
    "grade_id": "...",
    "grade_title": "Examen Final",
    "score": 95,
    "max_score": 100,
    "category_id": "...",
    "grade_value": 1
    // ...otros campos
  }
]
```

---

## Buenas Prácticas y Recomendaciones

- Utiliza los endpoints de vistas para obtener datos agregados y evitar lógica compleja en el frontend.
- Filtra siempre por `user_id` para garantizar la privacidad y seguridad de los datos.
- Usa los modelos de respuesta para validar y tipar los datos en el frontend.
- Marca las calificaciones como completadas usando el endpoint PATCH (`/tasks/{grade_id}/complete`) en vez de borrarlas.
- Consulta el archivo `models.py` para ver la definición completa y actualizada de los modelos.

---

## Glosario de Campos Clave

- **id**: Identificador único universal (UUID).
- **user_id**: Usuario propietario del registro.
- **class_id**: Clase o curso relacionado.
- **category_id**: Categoría de calificación.
- **calendar_event_id**: Evento de calendario relacionado.
- **score**: Puntuación obtenida.
- **max_score**: Puntuación máxima posible.
- **value**: Estado de la calificación (1=activa, 0=completada).
- **reminder_minutes**: Minutos antes del evento para enviar recordatorio.
- **is_recurring**: Si el evento es recurrente.
- **external_calendar_sync**: Información de sincronización con calendarios externos.

---

## Créditos y Contacto

**Autor:** Equipo StudyVault  
**Contacto:** soporte@studyvault.com  
**Última actualización:** Julio 2025

---

## Guía para Crear una Pantalla de Tareas (Task) en el Frontend

### 1. Selección de la Vista SQL
Para mostrar una pantalla de tareas enriquecida, puedes aprovechar la vista `vw_events_with_tasks`, que ya une eventos de calendario, tareas y calificaciones. Esto permite mostrar en una sola consulta:
- El evento de calendario (clase, examen, etc.)
- La tarea asociada (si existe)
- La calificación asociada (si existe)

### 2. Ejemplo de Flujo de Datos en el Frontend
1. **Consulta la vista:**
   - Realiza un fetch a `/vw/events-with-tasks` filtrando por el usuario autenticado.
2. **Renderiza la lista:**
   - Muestra cada evento de calendario como un ítem principal.
   - Si existe una tarea asociada, muéstrala anidada o relacionada al evento.
   - Si existe una calificación asociada, muestra el score y la categoría (ver punto 4).
3. **Permite acciones rápidas:**
   - Marcar tarea como completada.
   - Acceder al detalle del evento, tarea o calificación.

### 3. Ejemplo de Estructura de Componente (React/React Native)

```jsx
// Pseudocódigo para un componente TaskScreen
import { useEffect, useState } from 'react';

function TaskScreen() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    fetch('/api/vw/events-with-tasks', { headers: { Authorization: 'Bearer ...' } })
      .then(res => res.json())
      .then(setItems);
  }, []);

  return (
    <View>
      {items.map(ev => (
        <EventCard key={ev.calendar_event_id} event={ev} />
      ))}
    </View>
  );
}

function EventCard({ event }) {
  return (
    <View>
      <Text>{event.event_title}</Text>
      {event.task_id && (
        <Text>Tarea: {event.task_title} - Estado: {event.status}</Text>
      )}
      {event.grade_id && (
        <Text>Calificación: {event.score} / {event.max_score}</Text>
      )}
    </View>
  );
}
```

### 4. Resolviendo el Conflicto: Categorías en Grades vs Calendar

**Problema:**
- Las calificaciones (`grades`) tienen una relación explícita con categorías (`category_id`), pero los eventos de calendario (`calendar_events`) no.

**Solución recomendada:**
1. Cuando muestres un evento con calificación, si el campo `category_id` está presente en la respuesta, realiza una consulta adicional (o usa un join en el backend) para obtener el nombre y porcentaje de la categoría desde la tabla `categories_grades`.
2. Puedes enriquecer la UI mostrando la categoría junto a la calificación, por ejemplo:
   - "Examen Final (Exámenes - 20%)"
3. Si necesitas mostrar la categoría directamente en la pantalla de eventos, puedes modificar la vista SQL para incluir el join con `categories_grades` (como ya hace `vw_grades_by_category`).

**Ejemplo de enriquecimiento en el frontend:**
```js
// Si tienes category_id, puedes buscar la categoría en un store global o hacer fetch a /categories_grades
const category = categories.find(cat => cat.id === event.category_id);
<Text>Calificación: {event.score} ({category?.name})</Text>
```

### 5. Recomendaciones de UX
- Permite filtrar tareas por clase, fecha o estado.
- Muestra claramente si una tarea está asociada a un evento de calendario y/o calificación.
- Usa colores o iconos para diferenciar tipos de eventos, tareas y calificaciones.
- Ofrece acciones rápidas (marcar como completada, ver detalles, editar).

---

**Resumen:**
Puedes construir una pantalla de tareas potente y contextualizada usando la vista `vw_events_with_tasks` y enriqueciendo los datos de categoría desde la tabla `categories_grades`. Así aprovechas al máximo las relaciones y evitas inconsistencias entre eventos, tareas y calificaciones.
