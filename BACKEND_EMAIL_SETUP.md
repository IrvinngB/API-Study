# Configuración del Backend para Email y Reset de Contraseña

## 📦 Instalación de dependencias

Si quieres usar el enfoque con requests (recomendado), instala:

```bash
cd Api-Study
pip install requests
```

## 🔐 Variables de entorno

Crea un archivo `.env` en el directorio `Api-Study`:

```env
# Supabase Configuration
SUPABASE_URL=https://llnmvrxgiykxeiinycbt.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxsbm12cnhnaXlreGVpaW55Y2J0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAzMDA0NjIsImV4cCI6MjA2NTg3NjQ2Mn0.TCuyoJagBgoOhVnsCQabuXmeFy1o0QeEMR6e1gL40MI
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key_aqui

# Database
DATABASE_URL=tu_database_url
```

## 🔑 Obtener el Service Role Key

1. Ve a tu dashboard de Supabase: https://supabase.com/dashboard/project/llnmvrxgiykxeiinycbt
2. Ve a **Settings > API**
3. Copia la **service_role** key (no la anon key)
4. Pégala en el archivo `.env` como `SUPABASE_SERVICE_ROLE_KEY`

⚠️ **IMPORTANTE**: Nunca expongas la service role key en el frontend. Solo úsala en el backend.

## 🧪 Testing

### 1. Registrar usuario
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "name": "Test User"}'
```

### 2. Reset de contraseña
```bash
curl -X POST http://localhost:8000/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## 🚀 Flujo completo

1. **Usuario se registra** → Recibe email con link `studyvault://confirm-email`
2. **Hace clic en enlace** → Abre la app en pantalla de confirmación
3. **Usuario olvida contraseña** → Solicita reset
4. **Recibe email** → Link `studyvault://reset-password`
5. **Hace clic** → Abre app en pantalla de nueva contraseña
6. **Establece nueva contraseña** → Regresa al login

## 🔍 Logs útiles

Revisa los logs de tu backend para ver:
- Errores de Supabase
- URLs de deep link generadas
- Respuestas de la API

```python
# En auth.py ya tienes logs como:
print(f"Supabase error: {response.status_code} - {response.text}")
print(f"Reset password error: {e}")
```
