from supabase import create_client, Client
import os
from typing import Optional

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")

print(f"🔧 Configurando Supabase:")
print(f"   URL: {SUPABASE_URL}")
print(f"   Anon Key: {SUPABASE_ANON_KEY[:20]}...")
print(f"   Service Key: {'✅ Configurado' if SUPABASE_SERVICE_ROLE_KEY else '❌ No configurado'}")

def get_supabase_service() -> Client:
    """
    Obtiene cliente de Supabase con service role key para operaciones administrativas
    """
    service_key = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY
    return create_client(SUPABASE_URL, service_key)

def get_supabase_anon() -> Client:
    """
    Obtiene cliente de Supabase con anon key para operaciones públicas
    """
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_user_supabase(access_token: str) -> Client:
    """
    Obtiene cliente de Supabase configurado con el token del usuario
    """
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    # Configurar el token de acceso para el cliente
    try:
        # Método actualizado para establecer el token
        client.auth.set_session(access_token, None)
        print(f"✅ Cliente Supabase configurado con token de usuario")
    except Exception as e:
        print(f"⚠️  Warning: No se pudo configurar token en cliente: {e}")
        # Continuar sin el token - algunas operaciones pueden fallar
    
    return client

# Instancia global del cliente de servicio
supabase_service = get_supabase_service()
supabase_anon = get_supabase_anon()

print("✅ Clientes de Supabase inicializados correctamente")
