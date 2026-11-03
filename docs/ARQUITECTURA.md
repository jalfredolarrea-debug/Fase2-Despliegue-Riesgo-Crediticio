# Arquitectura técnica

## Componentes

1. Frontend: Streamlit, contenedor independiente.
2. Backend: FastAPI, API REST con tres endpoints.
3. Modelo: Random Forest serializado con joblib.
4. Infraestructura: Docker Compose con dos servicios.

## Endpoints

- GET /health: disponibilidad.
- GET /schema: variables y umbral.
- POST /predict: inferencia crediticia académica.

## Comunicación

Streamlit consume la API mediante solicitudes HTTP.
Docker Compose utiliza el nombre de servicio "api" como
destino interno: http://api:8000.

Los puertos de desarrollo se publican solamente sobre
la interfaz loopback del anfitrión.

## Validación

Se comparan 200 predicciones con los resultados históricos.
La API rechaza variables faltantes, adicionales, tipos
incorrectos, valores negativos y categorías fuera de dominio.

## Alcance

Prototipo académico, sin autorización de producción.
Dictamen del modelo: NO-GO para uso bancario real.
