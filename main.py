import cv2
import os
import threading
from ultralytics import YOLO

#os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"    #kamera bağlantısı için ip username ve passwordu doğru girmek gerekir
#RTSP_URL = "rtsp://admin:TkT321456@192.168.4.3:554/Streaming/Channels/102"
CAM_INDEX = 0  # laptopun web cami ile bağlanma
class VideoStream:              #Python normalde satır satır çalışır. Kameradan yeni kare gelene kadar tüm kod durur.
    def __init__(self, src):    #Yapay zeka düşünürken kameranın akışını arka planda kesintisiz devam ettirmek için yazılmış özel bir yapıdır.
        self.stream = cv2.VideoCapture(src) #, cv2.CAP_FFMPEG
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.ret = False
        self.frame = None
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            if not self.stream.isOpened():
                continue
            # Lagı önlemek için grab() kullanıyoruz. 
            # Kareyi arka planda numpy dizisine çevirmeden (decode etmeden) sadece yakalar.
            if self.stream.grab():
                self.ret, self.frame = self.stream.retrieve()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.stopped = True
        self.stream.release()

model = YOLO('yolo11n.pt') 

#  Pencerenin tam ekran veya istenilen boyuta getirilebilmesini sağlar
windowname = "Kamera"
cv2.namedWindow(windowname, cv2.WINDOW_NORMAL)

print("Optimize edilmiş sistem başlatılıyor...")
vs = VideoStream(CAM_INDEX).start() #RTSP_URL  harici bir kamera bağlanmak istenirse bunu yazın

while True:
    ret, frame = vs.read()
    
    if not ret or frame is None:
        continue
        
    # conf (güven) oranı 0.50
    # Model sadece %50 ve üzeri emin olduğu nesneleri çizecek.
    # Sadece insan (0) ve arabaları (2) algılamak istersen 'classes=[0, 2]' parametresini ekleyebilirsiniz.
    results = model(frame, stream=True, imgsz=320, conf=0.5)
    
    for r in results:
        annotated_frame = r.plot()
        
    cv2.imshow(windowname, annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):  #q ya bas çıkış yap
        break

vs.stop()
cv2.destroyAllWindows()