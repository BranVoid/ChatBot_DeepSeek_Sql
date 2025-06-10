# Generador de Query SQL con IA

Este proyecto es una aplicación web que permite generar consultas SQL a partir de descripciones en lenguaje natural utilizando inteligencia artificial. El sistema cuenta con un frontend desarrollado en React y un backend en Flask, el cual se conecta a la API de OpenRouter (DeepSeek) para procesar las solicitudes.

## Características

- Generación automática de consultas SQL desde texto en lenguaje natural.
- Interfaz de usuario intuitiva construida con React.
- Backend robusto en Flask para gestionar la lógica y la comunicación con la API de IA.
- Fácil de desplegar y personalizar.

## Estructura del Proyecto

```
chatbot_sql/
├── backend/         # Código fuente del backend (Flask)
├── frontend/        # Código fuente del frontend (React)
├── README.md        # Documentación del proyecto
└── requirements.txt # Dependencias del backend
```

## Requisitos

- Python 3.8+
- Node.js y npm
- Cuenta y clave de API en OpenRouter

## Instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/tu_usuario/chatbot_sql.git
    cd chatbot_sql
    ```

2. Instala las dependencias del backend:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

3. Instala las dependencias del frontend:
    ```bash
    cd ../frontend
    npm install
    ```

## Uso

1. Inicia el backend:
    ```bash
    cd backend
     . .\venv\Scripts\Activate.ps1
    ´python -m pip install -r requirements.txt
    ```

2. Inicia el frontend:
    ```bash
    cd ../frontend
    npm start
    ```

3. Accede a la aplicación desde tu navegador en `http://localhost:3000`.

## Configuración

- Asegúrate de configurar tu clave de API de OpenRouter en el archivo de variables de entorno del backend.

## Contribución

¡Las contribuciones son bienvenidas! Por favor, abre un issue o un pull request para sugerencias o mejoras.

## Licencia

Este proyecto está bajo la licencia MIT.
