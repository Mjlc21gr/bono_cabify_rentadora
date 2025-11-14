from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import requests
import json
import logging
import os
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Cabify - Seguros Bolívar",
    description="API para gestión de bonos y cobertura Cabify",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs de configuración
TOKEN_URL = "http://18.224.149.147:5032/cabify/token"
API_URL = "http://18.224.149.147:5032/cabify"


# Modelos Pydantic
class ValidarCoberturaRequest(BaseModel):
    placa: str = Field(..., description="Placa del vehículo")
    correo: str = Field(..., description="Correo electrónico")
    perdio_movilidad: str = Field(..., description="Si perdió movilidad: 'Sí' o 'No'")
    gestor: str = Field(..., description="Gestor asignado")


class GenerarBonoRequest(BaseModel):
    id: str = Field(..., description="ID de la consulta")
    numero_siniestro: str = Field(..., description="Número del siniestro")
    correo: str = Field(..., description="Correo del gestor")


class ProgramarTallerRequest(BaseModel):
    id: str = Field(..., description="ID de la consulta")
    numero_siniestro: str = Field(..., description="Número del siniestro")
    correo: str = Field(..., description="Correo del gestor")
    fecha_programado: str = Field(..., description="Fecha programada (YYYY-MM-DD)")


class GenerarBonoProgramadoRequest(BaseModel):
    id: str = Field(..., description="ID de gestión")
    numero_siniestro: str = Field(..., description="Número del siniestro")
    placa: str = Field(..., description="Placa del vehículo")
    gestor: str = Field(..., description="Gestor asignado")


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


# Función para obtener token
async def obtener_token():
    """Obtiene el token de autenticación de Cabify"""
    payload = {
        "usuario": "laura.mendez.giraldo",
        "password": "Seguro2025"
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(TOKEN_URL, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            datos = response.json()
            if datos.get("token"):
                logger.info("Token obtenido exitosamente")
                return datos["token"]
            else:
                logger.error("Token no encontrado en la respuesta")
                return None
        else:
            logger.error(f"Error al obtener token: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        logger.error(f"Error en la solicitud de token: {str(e)}")
        return None


# Dependencia para validar token
async def get_token():
    token = await obtener_token()
    if not token:
        raise HTTPException(status_code=401, detail="No se pudo obtener el token de autorización")
    return token


@app.get("/", response_model=dict)
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": "API Cabify - Seguros Bolívar",
        "version": "1.0.0",
        "endpoints": [
            "/validar-cobertura",
            "/generar-bono",
            "/programar-taller",
            "/generar-bono-programado",
            "/health"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check para el servicio"""
    try:
        # Verificar que podemos obtener token
        token = await obtener_token()
        if token:
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        else:
            return {"status": "unhealthy", "error": "Cannot obtain token"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.post("/validar-cobertura", response_model=ApiResponse)
async def validar_cobertura(request: ValidarCoberturaRequest, token: str = Depends(get_token)):
    """Valida la cobertura de Cabify para una placa específica"""

    payload = {
        "endpoint": "validacion_Cobertura",
        "tipoConsulta": "validar",
        "placa": request.placa,
        "correo": request.correo,
        "perdio_movilidad": request.perdio_movilidad,
        "gestor": request.gestor
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)

        logger.info(f"Respuesta validación cobertura: {response.text}")

        if response.status_code == 200:
            try:
                data = response.json()
                return ApiResponse(
                    success=True,
                    message="Cobertura validada exitosamente",
                    data=data
                )
            except json.JSONDecodeError:
                return ApiResponse(
                    success=True,
                    message="Cobertura validada exitosamente",
                    data={"response": response.text}
                )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error en la validación: {response.text}"
            )

    except requests.RequestException as e:
        logger.error(f"Error en validación cobertura: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en la solicitud: {str(e)}")


@app.post("/generar-bono", response_model=ApiResponse)
async def generar_y_enviar_bono(request: GenerarBonoRequest, token: str = Depends(get_token)):
    """Genera y envía un bono de Cabify por correo"""

    payload = {
        "endpoint": "gestionarBono",
        "operacion": "generarYEnviarCorreo",
        "datos": {
            "id_consulta": request.id,
            "numero_siniestro": request.numero_siniestro,
            "gestor": request.correo
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)

        logger.info(f"Respuesta generar bono: {response.text}")

        if response.status_code == 200:
            try:
                data = response.json()
                return ApiResponse(
                    success=True,
                    message="Bono generado y enviado exitosamente",
                    data=data
                )
            except json.JSONDecodeError:
                return ApiResponse(
                    success=True,
                    message="Bono generado y enviado exitosamente",
                    data={"response": response.text}
                )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al generar bono: {response.text}"
            )

    except requests.RequestException as e:
        logger.error(f"Error al generar bono: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en la solicitud: {str(e)}")


@app.post("/programar-taller", response_model=ApiResponse)
async def programar_taller(request: ProgramarTallerRequest, token: str = Depends(get_token)):
    """Programa un taller para el bono de Cabify"""

    payload = {
        "endpoint": "gestionarBono",
        "operacion": "programarTaller",
        "datos": {
            "id_consulta": request.id,
            "numero_siniestro": request.numero_siniestro,
            "gestor": request.correo,
            "fecha_probable_ingreso": request.fecha_programado
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)

        logger.info(f"Respuesta programar taller: {response.text}")

        if response.status_code == 200:
            try:
                data = response.json()
                return ApiResponse(
                    success=True,
                    message="Taller programado exitosamente",
                    data=data
                )
            except json.JSONDecodeError:
                return ApiResponse(
                    success=True,
                    message="Taller programado exitosamente",
                    data={"response": response.text}
                )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al programar taller: {response.text}"
            )

    except requests.RequestException as e:
        logger.error(f"Error al programar taller: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en la solicitud: {str(e)}")


@app.post("/generar-bono-programado", response_model=ApiResponse)
async def generar_bono_programado(request: GenerarBonoProgramadoRequest, token: str = Depends(get_token)):
    """Genera un bono programado de Cabify"""

    payload = {
        "endpoint": "gestionarBono",
        "operacion": "generarProgramado",
        "datos": {
            "id_gestion": request.id,
            "numero_siniestro": request.numero_siniestro,
            "placa": request.placa,
            "gestor": request.gestor
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)

        logger.info(f"Respuesta generar bono programado: {response.text}")

        if response.status_code == 200:
            try:
                data = response.json()
                return ApiResponse(
                    success=True,
                    message="Bono programado generado exitosamente",
                    data=data
                )
            except json.JSONDecodeError:
                return ApiResponse(
                    success=True,
                    message="Bono programado generado exitosamente",
                    data={"response": response.text}
                )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al generar bono programado: {response.text}"
            )

    except requests.RequestException as e:
        logger.error(f"Error al generar bono programado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en la solicitud: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)