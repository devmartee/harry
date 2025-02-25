from cvzone.FaceDetectionModule import FaceDetector
import cv2

class FaceIdentification:
    def __init__(self):
        self._running = True

    def stop(self):
        self._running = False

    def face_search(self):
        try:
            video = cv2.VideoCapture(0)
            detector = FaceDetector()
            while self._running:
                _, img = video.read()
                img, bboxes = detector.findFaces(img, draw=True)

                cv2.imshow('identificador', img)
                if cv2.waitKey(1) == 27:
                    break
            video.release()
            cv2.destroyAllWindows()
        except:
            print("Erro ao abrir a câmera")