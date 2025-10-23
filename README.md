# ✋ Reproductor de Música Controlado por Gestos (Python + Visión por Computadora)

Este proyecto es un **Reproductor de Música Interactivo** que permite al usuario controlar la reproducción, el volumen y la navegación de la biblioteca musical usando únicamente **gestos de la mano** capturados por la cámara web.

Utiliza el poder de **MediaPipe** para el rastreo de manos en tiempo real y **OpenCV** para el procesamiento de video y la interfaz.

## ✨ Características Principales

* **Control sin Contacto (Contactless):** Gestiona todas las funciones básicas del reproductor (Play/Pause, Siguiente/Anterior, Navegación) mediante gestos simples de la mano.
* **Detección de Dedos:** Identifica la cantidad de dedos levantados (de 0 a 4) para mapearlos a comandos específicos.
* **Interfaz Superpuesta:** Muestra la lista de canciones paginada, la canción actual resaltada y la carátula de la canción directamente en la ventana de video.
* **Arquitectura Modular:** El código está organizado en clases (`HandDetector`, `MusicPlayer`, `UIManager`, `GestureController`) para facilitar el mantenimiento y la expansión.

##Controles/Gestos

Gesto,Dedos Levantados,Acción
Puño Cerrado (✊), 0 ,Pausar / Reanudar la reproducción.
Dedo Índice (👆),1,Siguiente Canción.
Dos Dedos (✌️),2,Canción Anterior.
Tres Dedos,3,Página Siguiente (en la lista de canciones).
Cuatro Dedos,4,Página Anterior (en la lista de canciones).

## ⚙️ Requisitos y Configuración

### 1. Requisitos de Python

Necesitas tener **Python 3.x** instalado. Luego, instala las librerías necesarias usando `pip`:

```bash
pip install opencv-python mediapipe pygame numpy


