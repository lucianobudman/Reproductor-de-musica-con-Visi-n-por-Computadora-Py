import cv2
import mediapipe as mp
import pygame
import os
import time
import numpy as np

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
class Config:
    FPS = 30
    CARPETA_CANCIONES = "C:/Users/luciano/Desktop/Python/music"
    IMAGEN_NO_DISPONIBLE = "C:/Users/luciano/Desktop/Python/caratulas/no-disponible.jpg"
    TIEMPO_ESPERA_GESTO_ACTIVACION = 3.0
    TIEMPO_PAUSA_ENTRE_ACTIVACIONES = 3.0
    TIEMPO_PAUSA_DESPUES_DE_MOSTRAR = 3.0
    TIEMPO_PAUSA_NAVEGACION = 3.0
    TIEMPO_PAUSA_REPRODUCCION = 20.0
    NUM_CANCIONES_POR_PAGINA = 5
    RETRASO_GESTO = 1.0  
    VOLUMEN_INICIAL = 0.5
    ANCHO_VENTANA = 1280
    ALTO_VENTANA = 720

# -----------------------------
# DETECCIÓN DE MANOS
# -----------------------------
class HandDetector:
    def __init__(self, max_hands=1, detection_confidence=0.7, track_confidence=0.7):
        self.hands_module = mp.solutions.hands
        self.hands = self.hands_module.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=track_confidence,
        )
        self.drawing_utils = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        finger_count = 0

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                finger_tips = [4, 8, 12, 16, 20]
                
                # Cuento el pulgar
                if hand_landmarks.landmark[finger_tips[0]].x < hand_landmarks.landmark[finger_tips[0] - 1].x:
                    finger_count += 1
                
                # Cuento los otros cuatro dedos
                for id in range(1, 5):
                    if hand_landmarks.landmark[finger_tips[id]].y < hand_landmarks.landmark[finger_tips[id] - 2].y:
                        finger_count += 1

                if draw:
                    self.drawing_utils.draw_landmarks(
                        img, hand_landmarks, self.hands_module.HAND_CONNECTIONS
                    )
        return img, finger_count

# -----------------------------
# REPRODUCTOR DE MÚSICA
# -----------------------------
class MusicPlayer:
    def __init__(self, carpeta_canciones):
        pygame.mixer.init()
        self.carpeta_canciones = carpeta_canciones
        self.lista_canciones = self.cargar_canciones()
        self.indice_actual = 0
        self.is_playing = False
        self.volumen = Config.VOLUMEN_INICIAL
        if self.lista_canciones:
            self.cargar_cancion(self.indice_actual)

    def cargar_canciones(self):
        canciones = []
        if os.path.exists(self.carpeta_canciones):
            for file in os.listdir(self.carpeta_canciones):
                if file.endswith(".mp3"):
                    canciones.append(file)
        else:
            os.makedirs(self.carpeta_canciones)
        return canciones

    def cargar_cancion(self, indice):
        pygame.mixer.music.load(os.path.join(self.carpeta_canciones, self.lista_canciones[indice]))
        pygame.mixer.music.set_volume(self.volumen)

    def play(self):
        pygame.mixer.music.play()
        self.is_playing = True

    def pause(self):
        pygame.mixer.music.pause()
        self.is_playing = False

    def unpause(self):
        pygame.mixer.music.unpause()
        self.is_playing = True

    def toggle_play(self):
        if self.is_playing:
            self.pause()
        else:
            self.unpause()

    def next_song(self):
        self.indice_actual = (self.indice_actual + 1) % len(self.lista_canciones)
        self.cargar_cancion(self.indice_actual)
        self.play()

    def previous_song(self):
        self.indice_actual = (self.indice_actual - 1) % len(self.lista_canciones)
        self.cargar_cancion(self.indice_actual)
        self.play()

    def get_current_song(self):
        if self.lista_canciones:
            return self.lista_canciones[self.indice_actual]
        return None

# -----------------------------
# INTERFAZ DE USUARIO
# -----------------------------
class UIManager:
    def __init__(self, imagen_por_defecto):
        self.imagen_por_defecto = imagen_por_defecto
        self.current_page = 0

    def draw_ui(self, frame, music_player, img_height, img_width):
        if not music_player.lista_canciones:
            cv2.putText(frame, "No hay canciones disponibles", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return frame

        # Dibujar lista de canciones (paginada)
        start_index = self.current_page * Config.NUM_CANCIONES_POR_PAGINA
        end_index = min(start_index + Config.NUM_CANCIONES_POR_PAGINA, len(music_player.lista_canciones))
        y_offset = 50
        for i, song in enumerate(music_player.lista_canciones[start_index:end_index]):
            color = (0, 255, 0) if (start_index + i) == music_player.indice_actual else (255, 255, 255)
            cv2.putText(frame, song, (50, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 40

        current_song = music_player.get_current_song()
        if current_song:
            cover_path = os.path.join(music_player.carpeta_canciones, os.path.splitext(current_song)[0] + ".jpg")
            if os.path.exists(cover_path):
                cover_img = cv2.imread(cover_path)
            elif os.path.exists(self.imagen_por_defecto):
                cover_img = cv2.imread(self.imagen_por_defecto)
            else:
                cover_img = np.zeros((200, 200, 3), dtype=np.uint8)

            cover_img = cv2.resize(cover_img, (200, 200))
            frame[img_height - 220:img_height - 20, img_width - 220:img_width - 20] = cover_img

        return frame

    def next_page(self, music_player):
        total_pages = (len(music_player.lista_canciones) // Config.NUM_CANCIONES_POR_PAGINA) + (1 if len(music_player.lista_canciones) % Config.NUM_CANCIONES_POR_PAGINA != 0 else 0)
        self.current_page = (self.current_page + 1) % total_pages

    def previous_page(self, music_player):
        total_pages = (len(music_player.lista_canciones) // Config.NUM_CANCIONES_POR_PAGINA) + (1 if len(music_player.lista_canciones) % Config.NUM_CANCIONES_POR_PAGINA != 0 else 0)
        self.current_page = (self.current_page - 1 + total_pages) % total_pages

# -----------------------------
# CONTROL DE GESTOS
# -----------------------------
class GestureController:
    def __init__(self, hand_detector, music_player, ui_manager):
        self.hand_detector = hand_detector
        self.music_player = music_player
        self.ui_manager = ui_manager
        self.last_gesture_time = 0
        self.last_processed_gesture = -1

    def update(self, frame, img_height, img_width):
        frame, finger_count = self.hand_detector.find_hands(frame)

        current_time = time.time()
        
        if (
            current_time - self.last_gesture_time > Config.RETRASO_GESTO
            and finger_count != self.last_processed_gesture
        ):
            if finger_count == 0:  # ✊ Pausar/Reanudar
                self.music_player.toggle_play()
                self.last_gesture_time = current_time
                self.last_processed_gesture = 0
                print("DEBUG: Gesto 'Toggle Play' detectado.")

            elif finger_count == 1:  # 1 Siguiente canción
                self.music_player.next_song()
                self.last_gesture_time = current_time
                self.last_processed_gesture = 1
                print("DEBUG: Gesto 'Siguiente Canción' detectado.")

            elif finger_count == 2:  # 2 Canción anterior
                self.music_player.previous_song()
                self.last_gesture_time = current_time
                self.last_processed_gesture = 2
                print("DEBUG: Gesto 'Canción Anterior' detectado.")

            elif finger_count == 3:  # 3 Página siguiente
                self.ui_manager.next_page(self.music_player)
                self.last_gesture_time = current_time
                self.last_processed_gesture = 3
                print("DEBUG: Gesto 'Página Siguiente' detectado.")

            elif finger_count == 4:  # 4 Página anterior
                self.ui_manager.previous_page(self.music_player)
                self.last_gesture_time = current_time
                self.last_processed_gesture = 4
                print("DEBUG: Gesto 'Página Anterior' detectado.")
        
        frame = self.ui_manager.draw_ui(frame, self.music_player, img_height, img_width)
        return frame

# -----------------------------
# PROGRAMA PRINCIPAL
# -----------------------------
def main():
    hand_detector = HandDetector()
    music_player = MusicPlayer(Config.CARPETA_CANCIONES)
    ui_manager = UIManager(Config.IMAGEN_NO_DISPONIBLE)
    gesture_controller = GestureController(hand_detector, music_player, ui_manager)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: No se pudo abrir la cámara.")
        return

    print("INFO: Iniciando bucle principal. Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("ERROR: No se pudo leer el frame de la cámara.")
            break

        img_height, img_width, _ = frame.shape

        final_frame = gesture_controller.update(frame, img_height, img_width)

        cv2.imshow("Reproductor Musical por Gestos", final_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.mixer.quit()

if __name__ == "__main__":
    main()