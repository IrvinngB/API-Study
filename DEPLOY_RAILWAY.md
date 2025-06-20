# 🚀 Despliegue StudyVault API en Railway

## Pasos para Desplegar

### 1. Preparación
- ✅ Archivos preparados (Procfile, railway.json, requirements.txt)
- ✅ Variables de entorno configuradas
- ✅ CORS actualizado

### 2. Despliegue en Railway

1. **Crear cuenta en Railway**: https://railway.app
2. **Conectar repositorio**:
   - New Project → Deploy from GitHub repo
   - Seleccionar tu repositorio
   - Especificar la carpeta `Api-Study`

3. **Configurar variables de entorno** en Railway Dashboard:
   ```
   SUPABASE_URL=tu_supabase_url
   SUPABASE_KEY=tu_supabase_anon_key
   SUPABASE_SERVICE_KEY=tu_supabase_service_key
   ENVIRONMENT=production
   ```

4. **Desplegar**:
   - Railway detectará automáticamente Python
   - Usará el Procfile para ejecutar la aplicación
   - Asignará una URL pública

### 3. Configurar la App Móvil

Una vez desplegado, Railway te dará una URL como:
`https://tu-proyecto.railway.app`

Actualiza `StudyVault/database/api/client.ts`:

```typescript
this.baseURL = __DEV__
  ? "http://192.168.1.175:8000" // Development
  : "https://tu-proyecto.railway.app" // Production
```

### 4. Verificar Despliegue

- Endpoint de health: `https://tu-proyecto.railway.app/health`
- Documentación API: `https://tu-proyecto.railway.app/docs`

## Variables de Entorno Necesarias

```env
SUPABASE_URL=https://tuproyecto.supabase.co
SUPABASE_KEY=tu_anon_key
SUPABASE_SERVICE_KEY=tu_service_key
ENVIRONMENT=production
```

## Comandos Útiles

```bash
# Probar localmente antes del despliegue
cd Api-Study
pip install -r requirements.txt
uvicorn main:app --reload

# Verificar que funciona
curl http://localhost:8000/health
```

## Troubleshooting

- **502 Bad Gateway**: Verificar Procfile y que la app esté corriendo
- **CORS errors**: Actualizar allow_origins en main.py
- **Database errors**: Verificar variables de entorno de Supabase
