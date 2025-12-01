# main.py
import sys
from PySide6.QtWidgets import QApplication

from database.veritabani import VeritabaniYoneticisi
from ui.ana_pencere import AnaPencere

def main():
    """
    Uygulamanın ana giriş noktası.
    """
    # 1. QApplication örneği oluştur
    uygulama = QApplication(sys.argv)

    # 2. Veritabanı yöneticisini başlat
    veritabani_yoneticisi = None
    try:
        veritabani_yoneticisi = VeritabaniYoneticisi()

        # 3. Ana pencereyi oluştur ve veritabanı yöneticisini ona ver
        ana_pencere = AnaPencere(veritabani_yoneticisi)

        # 4. Ana pencereyi göster
        ana_pencere.show()

        # 5. Uygulamanın olay döngüsünü başlat
        sys.exit(uygulama.exec())

    finally:
        # 6. Uygulama kapandığında veritabanı bağlantısını kapat
        if veritabani_yoneticisi:
            veritabani_yoneticisi.baglantiyi_kapat()
            print("Veritabanı bağlantısı kapatıldı.")

if __name__ == '__main__':
    main()
