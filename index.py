from listening import Identification, RecognizeSpeech
from identification import FaceIdentification
import threading
import time
import os

stop_camera = threading.Event()

def clean():
    if os.name == 'nt':
        os.system("cls")
    else:
        os.system("clear")

def start_speech():
    identificador = Identification()
    cumprimento = identificador.verificar_horario()
    identificador.falar("Olá, {} Robô ligado.".format(cumprimento))

def start_camera():
    identificador = Identification()
    identificador.falar("Abrindo câmera para identificação de rosto.")
    cam_identific = FaceIdentification()
    threading.current_thread().cam_identific = cam_identific
    cam_identific.face_search()

def start_ouvir():
    ouvir = RecognizeSpeech()
    while True:
        texto_reconhecido = ouvir.reconhece_fala()
        if texto_reconhecido and "harry" in texto_reconhecido:
            ouvir.responde_em_voz("Sim, estou ouvindo...")
            while True:
                comando = ouvir.reconhece_fala()
                if comando == "sair":
                    ouvir.responde_em_voz("Encerrando o assistente. Até logo!")
                    stop_camera.set()
                    camera_thread.cam_identific.stop()
                    clean()
                    break
                ouvir.responde(comando)
            break

if __name__ == "__main__":
    speech_thread = threading.Thread(target=start_speech)
    camera_thread = threading.Thread(target=start_camera)
    listen_thread = threading.Thread(target=start_ouvir)

    speech_thread.start()
    camera_thread.start()
    time.sleep(5)  
    clean()
    listen_thread.start()

    speech_thread.join()
    camera_thread.join()
    listen_thread.join()
