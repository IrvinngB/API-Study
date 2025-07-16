# StudyVault API 📚

Backend API para StudyVault - Una aplicación integral de productividad estudiantil construida con FastAPI y Supabase.

## 🏗️ Arquitectura

### Stack Tecnológico
- **Framework**: FastAPI (Python)
- **Base de Datos**: Supabase (PostgreSQL)
- **Autenticación**: JWT + Supabase Auth
- **Despliegue**: Railway
- **Tiempo Real**: Supabase Realtime

### Estructura del Proyecto
```
Api-Study/
├── main.py                 # Punto de entrada de la aplicación FastAPI
├── database.py             # Configuración del cliente Supabase
├── models.py               # Modelos Pydantic para validación de datos
├── auth_middleware.py      # Middleware de autenticación JWT
├── routers/                # Manejadores de rutas API
│   ├── auth.py            # Endpoints de autenticación
│   ├── classes.py         # Gestión de clases
│   ├── tasks.py           # Gestión de tareas
│   ├── calendar.py        # Eventos del calendario
│   ├── habits.py          # Seguimiento de hábitos
│   ├── sync.py            # Sincronización de datos
│   └── analytics.py       # Análisis de productividad
├── requirements.txt        # Dependencias de Python
├── Procfile               # Configuración de despliegue Railway
└── railway.json           # Configuración de construcción Railway
```

## 🚀 Características

- **Autenticación**: Registro, inicio de sesión y gestión de perfiles de usuario
- **Gestión de Clases**: Crear, actualizar y eliminar clases académicas
- **Gestión de Tareas**: Operaciones CRUD con prioridades y fechas de vencimiento
- **Calendario**: Programación de eventos con integración de clases
- **Seguimiento de Hábitos**: Formación y registro de hábitos personales
- **Sincronización de Datos**: Sincronización multi-dispositivo con resolución de conflictos
- **Análisis**: Métricas de productividad y seguimiento de sesiones de estudio

## 🔧 Configuración e Instalación

### Prerrequisitos
- Python 3.8+
- Cuenta de Supabase
- Variables de entorno configuradas

### Desarrollo Local
```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd Api-Study

# Instalar dependencias
pip install -r requirements.txt

# Copiar plantilla de entorno
cp .env.example .env

# Configurar variables de entorno
# Editar .env con tus credenciales de Supabase

# Ejecutar la aplicación
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Variables de Entorno
```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu_clave_anonima
SUPABASE_SERVICE_ROLE_KEY=tu_clave_de_rol_de_servicio
SUPABASE_JWT_SECRET=tu_secreto_jwt
ENVIRONMENT=production
```

## 📡 Endpoints de la API

### URL Base
- **Desarrollo**: `http://localhost:8000`
- **Producción**: `https://tu-app.railway.app`

### Autenticación
```http
POST /auth/signup          # Registro de usuario
POST /auth/signin          # Inicio de sesión de usuario
POST /auth/signout         # Cierre de sesión de usuario
GET  /auth/profile         # Obtener perfil de usuario
PUT  /auth/profile         # Actualizar perfil de usuario
PATCH /auth/profile        # Actualización parcial del perfil
```

### Clases
```http
GET    /classes            # Listar todas las clases
POST   /classes            # Crear nueva clase
GET    /classes/{id}       # Obtener clase específica
PUT    /classes/{id}       # Actualizar clase
PATCH  /classes/{id}       # Actualización parcial de clase
DELETE /classes/{id}       # Eliminar clase
```

### Tareas
```http
GET    /tasks              # Listar tareas (con filtros)
POST   /tasks              # Crear nueva tarea
GET    /tasks/{id}         # Obtener tarea específica
PUT    /tasks/{id}         # Actualizar tarea
PATCH  /tasks/{id}         # Actualización parcial de tarea
DELETE /tasks/{id}         # Eliminar tarea
POST   /tasks/{id}/complete # Marcar tarea como completada
```

### Calendario
```http
GET    /calendar           # Listar eventos (con filtros)
POST   /calendar           # Crear nuevo evento
GET    /calendar/{id}      # Obtener evento específico
PUT    /calendar/{id}      # Actualizar evento
PATCH  /calendar/{id}      # Actualización parcial de evento
DELETE /calendar/{id}      # Eliminar evento
```

### Hábitos
```http
GET    /habits             # Listar hábitos
POST   /habits             # Crear nuevo hábito
GET    /habits/{id}        # Obtener hábito específico
PUT    /habits/{id}        # Actualizar hábito
DELETE /habits/{id}        # Eliminar hábito
GET    /habits/{id}/logs   # Obtener registros de hábitos
POST   /habits/{id}/logs   # Crear registro de hábito
```

### Sincronización
```http
POST   /sync/pull          # Extraer datos del servidor
POST   /sync/push          # Enviar datos al servidor
GET    /sync/status        # Obtener estado de sincronización
```

### Análisis
```http
GET    /analytics/productivity    # Obtener métricas de productividad
GET    /analytics/study-sessions  # Obtener sesiones de estudio
GET    /analytics/dashboard       # Obtener datos del dashboard
POST   /analytics/study-session   # Crear sesión de estudio
```

### Notificaciones
```http
GET    /notifications            # Listar notificaciones
POST   /notifications           # Crear notificación
GET    /notifications/{id}      # Obtener notificación específica
PUT    /notifications/{id}      # Actualizar notificación
PATCH  /notifications/{id}      # Actualización parcial de notificación
DELETE /notifications/{id}      # Eliminar notificación
POST   /notifications/{id}/mark-read # Marcar como leída
```

### Dispositivos de Usuario
```http
GET    /devices                 # Listar dispositivos
POST   /devices                 # Registrar dispositivo
GET    /devices/{id}            # Obtener dispositivo específico
PUT    /devices/{id}            # Actualizar dispositivo
PATCH  /devices/{id}            # Actualización parcial de dispositivo
DELETE /devices/{id}            # Desactivar dispositivo
POST   /devices/{id}/sync       # Actualizar timestamp de sincronización
```

### Perfil de Usuario
```http
GET    /profile/me              # Obtener perfil actual
POST   /profile                 # Crear perfil
PUT    /profile/me              # Actualizar perfil
PATCH  /profile/me              # Actualización parcial de perfil
DELETE /profile/me              # Eliminar perfil
```

## 🔐 Autenticación

La API utiliza tokens JWT para autenticación. Incluye el token en el header de Autorización:

```http
Authorization: Bearer <tu-jwt-token>
```

### Flujo de Autenticación
1. El usuario se registra o inicia sesión
2. La API devuelve un token JWT
3. Incluir el token en solicitudes posteriores
4. El token expira después de 30 minutos (configurable)

## 📱 Integración con React Native + Expo

### Instalación
```bash
# Instalar cliente HTTP
npm install axios
# o
npm install @react-native-async-storage/async-storage
```

### Configuración del Cliente API
```typescript
// api/client.ts
import axios, { AxiosInstance } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = __DEV__ 
      ? 'http://localhost:8000'  // Desarrollo
      : 'https://tu-app.railway.app'; // Producción

    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Agregar interceptor de solicitud para token de autenticación
    this.client.interceptors.request.use(async (config) => {
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Métodos de autenticación
  async signUp(email: string, password: string, name: string) {
    const response = await this.client.post('/auth/signup', {
      email,
      password,
      name,
    });
    return response.data;
  }

  async signIn(email: string, password: string) {
    const response = await this.client.post('/auth/signin', {
      email,
      password,
    });
    
    // Almacenar token
    if (response.data.session?.access_token) {
      await AsyncStorage.setItem('auth_token', response.data.session.access_token);
    }
    
    return response.data;
  }

  // Métodos de clases
  async getClasses() {
    const response = await this.client.get('/classes');
    return response.data;
  }

  async createClass(classData: {
    name: string;
    code?: string;
    instructor?: string;
    color?: string;
    credits?: number;
    semester?: string;
    description?: string;
  }) {
    const response = await this.client.post('/classes', classData);
    return response.data;
  }

  async updateClass(classId: string, updates: any) {
    const response = await this.client.put(`/classes/${classId}`, updates);
    return response.data;
  }

  async deleteClass(classId: string) {
    const response = await this.client.delete(`/classes/${classId}`);
    return response.data;
  }
}

export default new ApiClient();
```

### Ejemplo de Componente React Native: Crear Clase

```typescript
// components/CreateClassScreen.tsx
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
} from 'react-native';
import ApiClient from '../api/client';

interface ClassFormData {
  name: string;
  code: string;
  instructor: string;
  color: string;
  credits: string;
  semester: string;
  description: string;
}

export default function CreateClassScreen({ navigation }: any) {
  const [formData, setFormData] = useState<ClassFormData>({
    name: '',
    code: '',
    instructor: '',
    color: '#3B82F6',
    credits: '',
    semester: '',
    description: '',
  });
  const [loading, setLoading] = useState(false);

  const colors = [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B',
    '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'
  ];

  const handleInputChange = (field: keyof ClassFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    if (!formData.name.trim()) {
      Alert.alert('Error', 'El nombre de la clase es requerido');
      return;
    }

    setLoading(true);
    try {
      const classData = {
        name: formData.name.trim(),
        code: formData.code.trim() || undefined,
        instructor: formData.instructor.trim() || undefined,
        color: formData.color,
        credits: formData.credits ? parseInt(formData.credits) : undefined,
        semester: formData.semester.trim() || undefined,
        description: formData.description.trim() || undefined,
      };

      console.log('🚀 Creando clase:', classData);
      
      const result = await ApiClient.createClass(classData);
      
      console.log('✅ Clase creada:', result);
      
      Alert.alert(
        'Éxito',
        '¡Clase creada exitosamente!',
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    } catch (error: any) {
      console.error('❌ Error creando clase:', error);
      
      let errorMessage = 'Error al crear la clase';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      Alert.alert('Error', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.form}>
        <Text style={styles.title}>Crear Nueva Clase</Text>

        {/* Nombre de la Clase */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Nombre de la Clase *</Text>
          <TextInput
            style={styles.input}
            value={formData.name}
            onChangeText={(value) => handleInputChange('name', value)}
            placeholder="ej., Introducción a las Ciencias de la Computación"
            placeholderTextColor="#9CA3AF"
          />
        </View>

        {/* Código de la Clase */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Código de la Clase</Text>
          <TextInput
            style={styles.input}
            value={formData.code}
            onChangeText={(value) => handleInputChange('code', value)}
            placeholder="ej., CS101"
            placeholderTextColor="#9CA3AF"
            autoCapitalize="characters"
          />
        </View>

        {/* Instructor */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Instructor</Text>
          <TextInput
            style={styles.input}
            value={formData.instructor}
            onChangeText={(value) => handleInputChange('instructor', value)}
            placeholder="ej., Dr. Smith"
            placeholderTextColor="#9CA3AF"
          />
        </View>

        {/* Créditos */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Créditos</Text>
          <TextInput
            style={styles.input}
            value={formData.credits}
            onChangeText={(value) => handleInputChange('credits', value)}
            placeholder="ej., 3"
            placeholderTextColor="#9CA3AF"
            keyboardType="numeric"
          />
        </View>

        {/* Semestre */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Semestre</Text>
          <TextInput
            style={styles.input}
            value={formData.semester}
            onChangeText={(value) => handleInputChange('semester', value)}
            placeholder="ej., Otoño 2024"
            placeholderTextColor="#9CA3AF"
          />
        </View>

        {/* Selección de Color */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Color</Text>
          <View style={styles.colorContainer}>
            {colors.map((color) => (
              <TouchableOpacity
                key={color}
                style={[
                  styles.colorOption,
                  { backgroundColor: color },
                  formData.color === color && styles.selectedColor,
                ]}
                onPress={() => handleInputChange('color', color)}
              />
            ))}
          </View>
        </View>

        {/* Descripción */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Descripción</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={formData.description}
            onChangeText={(value) => handleInputChange('description', value)}
            placeholder="Descripción opcional..."
            placeholderTextColor="#9CA3AF"
            multiline
            numberOfLines={3}
          />
        </View>

        {/* Botón de Envío */}
        <TouchableOpacity
          style={[styles.submitButton, loading && styles.disabledButton]}
          onPress={handleSubmit}
          disabled={loading}
        >
          <Text style={styles.submitButtonText}>
            {loading ? 'Creando...' : 'Crear Clase'}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  form: {
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 20,
    textAlign: 'center',
  },
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#1F2937',
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  colorContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  colorOption: {
    width: 40,
    height: 40,
    borderRadius: 20,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedColor: {
    borderColor: '#1F2937',
    borderWidth: 3,
  },
  submitButton: {
    backgroundColor: '#3B82F6',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginTop: 20,
  },
  disabledButton: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});
```

### Manejo de Errores y Estados de Carga

```typescript
// hooks/useApi.ts
import { useState } from 'react';
import { Alert } from 'react-native';

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const executeRequest = async <T>(
    request: () => Promise<T>,
    options?: {
      showErrorAlert?: boolean;
      errorTitle?: string;
    }
  ): Promise<T | null> => {
    setLoading(true);
    setError(null);

    try {
      const result = await request();
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Ocurrió un error';
      setError(errorMessage);

      if (options?.showErrorAlert !== false) {
        Alert.alert(
          options?.errorTitle || 'Error',
          errorMessage
        );
      }

      return null;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, executeRequest };
}
```

## 🔄 Modelos de Datos

### Modelo de Clase
```typescript
interface Class {
  id: string;
  user_id: string;
  name: string;
  code?: string;
  instructor?: string;
  color: string;
  credits?: number;
  semester?: string;
  description?: string;
  syllabus_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

### Modelo de Tarea
```typescript
interface Task {
  id: string;
  user_id: string;
  class_id?: string;
  title: string;
  description?: string;
  due_date?: string;
  priority: 1 | 2 | 3; // 1=Alta, 2=Media, 3=Baja
  status: 'pending' | 'in_progress' | 'completed';
  estimated_duration?: number;
  completion_percentage: number;
  tags: string[];
  created_at: string;
  updated_at: string;
  completed_at?: string;
}
```

## 📊 Formato de Respuesta

### Respuesta Exitosa
```json
{
  "id": "uuid",
  "name": "Introducción a las Ciencias de la Computación",
  "code": "CS101",
  "instructor": "Dr. Smith",
  "color": "#3B82F6",
  "credits": 3,
  "semester": "Otoño 2024",
  "user_id": "user-uuid",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Respuesta de Error
```json
{
  "detail": "Mensaje de error aquí"
}
```

## 🧪 Pruebas

### Verificación de Salud
```bash
curl http://localhost:8000/health
```

### Probar Autenticación
```bash
# Registrarse
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Usuario de Prueba"}'

# Iniciar sesión
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

## 🚀 Despliegue

La API está desplegada en Railway. Ver [DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md) para instrucciones detalladas de despliegue.

### URL de Producción
- API: `https://tu-app.railway.app`
- Documentación: `https://tu-app.railway.app/docs`

## 📚 Recursos Adicionales

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de Supabase](https://supabase.com/docs)
- [Guía de Despliegue Railway](https://docs.railway.app/)
- [React Native Expo](https://expo.dev/)

## 🤝 Contribuir

1. Hacer fork del repositorio
2. Crear una rama de características
3. Realizar tus cambios
4. Probar exhaustivamente
5. Enviar una pull request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT.

## 🧑‍💻 Ejemplos de Uso de la API

### Crear una clase
```bash
curl -X POST http://localhost:8000/classes \
  -H "Authorization: Bearer <tu-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Matemáticas II",
    "code": "MAT2024",
    "instructor": "Prof. García",
    "color": "#3B82F6",
    "credits": 4,
    "semester": "2025A",
    "description": "Álgebra avanzada"
  }'
```

### Actualizar parcialmente una clase (PATCH)
```bash
curl -X PATCH http://localhost:8000/classes/<id-clase> \
  -H "Authorization: Bearer <tu-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "instructor": "Prof. Juan Pérez",
    "color": "#F59E0B"
  }'
```

### Eliminar una clase
```bash
curl -X DELETE http://localhost:8000/classes/<id-clase> \
  -H "Authorization: Bearer <tu-jwt-token>"
```

### Crear una tarea
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer <tu-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Resolver ejercicios de álgebra",
    "due_date": "2025-07-20T23:59:00Z",
    "priority": 1,
    "class_id": "<id-clase>"
  }'
```

### Actualizar parcialmente una tarea (PATCH)
```bash
curl -X PATCH http://localhost:8000/tasks/<id-tarea> \
  -H "Authorization: Bearer <tu-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "completion_percentage": 100
  }'
```

### Marcar tarea como completada
```bash
curl -X POST http://localhost:8000/tasks/<id-tarea>/complete \
  -H "Authorization: Bearer <tu-jwt-token>"
```

### Crear evento de calendario
```bash
curl -X POST http://localhost:8000/calendar \
  -H "Authorization: Bearer <tu-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Examen final",
    "start_datetime": "2025-07-25T09:00:00Z",
    "end_datetime": "2025-07-25T11:00:00Z",
    "class_id": "<id-clase>"
  }'
```

### Actualizar parcialmente un evento de calendario (PATCH)
```bash
curl -X PATCH http://localhost:8000/calendar/<id-evento> \
  -H "Authorization: Bearer <tu-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Aula 101"
  }'
```

### Crear notificación
```bash
curl -X POST http://localhost:8000/notifications \
  -H "Authorization: Bearer <tu-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Recordatorio de entrega",
    "message": "No olvides entregar la tarea de matemáticas hoy."
  }'
```

### Marcar notificación como leída
```bash
curl -X POST http://localhost:8000/notifications/<id-notificacion>/mark-read \
  -H "Authorization: Bearer <tu-jwt-token>"
```

### Actualizar parcialmente el perfil de usuario (PATCH)
```bash
curl -X PATCH http://localhost:8000/profile/me \
  -H "Authorization: Bearer <tu-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Juan Pérez",
    "timezone": "America/Mexico_City"
  }'
```