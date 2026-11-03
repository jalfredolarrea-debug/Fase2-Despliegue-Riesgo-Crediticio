# Fase 2 | Despliegue de un modelo de riesgo crediticio

Proyecto académico de contenerización, integración y validación
de un modelo Random Forest mediante FastAPI, Streamlit y Docker.

## Objetivo

Demostrar el despliegue reproducible de un modelo previamente
entrenado y validado sobre South German Credit.

## Antecedentes

- Actividad 5: entrenamiento y evaluación inicial.
- Actividad 6: validación independiente y selección del modelo.
- Fase 2: serialización, API, interfaz, Docker y pruebas.

## Modelo

- Algoritmo: Random Forest.
- Registros: 1,000 (800 desarrollo; 200 prueba reservada).
- Variables predictoras: 20.
- Umbral de clasificación: 0.28.
- ROC-AUC de prueba: 0.7588.
- Dictamen: NO-GO para uso bancario real.

El sistema es exclusivamente académico y no puede utilizarse
para adoptar decisiones crediticias.

## Arquitectura

Usuario -> Streamlit -> FastAPI -> Modelo Random Forest

La comunicación entre contenedores se realiza mediante HTTP
dentro de una red privada de Docker Compose.

## Requisitos

- Docker Engine.
- Docker Compose.
- Recursos suficientes para ejecutar dos contenedores.
- Puertos 8765 y 8766 disponibles.

## Iniciar la aplicación

Ejecutar desde la raíz del repositorio:

    docker compose up -d --build

Verificar el estado:

    docker compose ps

API:
    http://127.0.0.1:8765/health

Interfaz:
    http://127.0.0.1:8766

En Codespaces se utiliza el reenvío privado de puertos.

## Pruebas

Con Python disponible en el entorno anfitrión:

    python tests/test_integracion.py

El script compara 200 predicciones históricas y prueba
la validación de entradas incorrectas.

## Reconstrucción del modelo

    docker build -f Dockerfile.train -t fase2-entrenamiento .

    docker run --rm \
      -v "$PWD/artifacts:/app/artifacts" \
      fase2-entrenamiento

El entrenamiento verifica las probabilidades y métricas
contra la evaluación histórica antes de guardar el modelo.

## Detener los servicios

    docker compose down

## Limitaciones

La ejecución validada se realizó en GitHub Codespaces.
Es un entorno remoto, no una instalación física local.

La validación técnica del despliegue no modifica el dictamen
estadístico NO-GO de la Actividad 6.

## Documentación adicional

- [Manual de despliegue - PDF](docs/Fase2_Manual_Despliegue.pdf)
- [Manual de despliegue - Word](docs/Fase2_Manual_Despliegue.docx)
- [Informe de validación - PDF](docs/Fase2_Informe_Validacion.pdf)
- [Informe de validación - Word](docs/Fase2_Informe_Validacion.docx)
- [Arquitectura técnica](docs/ARQUITECTURA.md)

## Origen de los datos

South German Credit, conjunto de datos público utilizado
en las Actividades 5 y 6. No se emplean datos bancarios
reales ni información confidencial de clientes.

## Fuente y licencia de datos

South German Credit [Dataset]. (2020).
UCI Machine Learning Repository.
https://doi.org/10.24432/C5QG88

Licencia del conjunto de datos: CC BY 4.0.

El archivo data/creditos.csv corresponde a una version
preprocesada para fines academicos. Se reconoce la
fuente original y sus condiciones de atribucion.
