# ui/not_listesi_bileseni.py
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QLineEdit, QHeaderView
)
from PySide6.QtCore import Signal, Qt
from datetime import datetime

class NotListesiBileseni(QFrame):
    """
    Notları bir tablo içinde listeleyen ve seçimleri bildiren arayüz bileşeni.
    """
    notAcmaIstegi = Signal(int)  # Not ID'si ile sinyal yayar
    filtreDegisti = Signal()     # Arama kutusu değiştiğinde sinyal yayar

    def __init__(self, veritabani_yoneticisi, parent=None):
        super().__init__(parent)
        self.db = veritabani_yoneticisi

        self.ana_layout = QVBoxLayout(self)
        self.ana_layout.setContentsMargins(0, 0, 0, 0) # Kenar boşluklarını sıfırla

        # Arama Kutusu
        self.arama_kutusu = QLineEdit()
        self.arama_kutusu.setPlaceholderText("Notlarda ara...")
        self.arama_kutusu.textChanged.connect(self.filtreDegisti.emit)

        # Notlar Tablosu
        self.tablo_notlar = QTableWidget()
        self.tablo_notlar.setColumnCount(2)
        self.tablo_notlar.setHorizontalHeaderLabels(["Başlık", "Son Değiştirme"])
        self.tablo_notlar.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tablo_notlar.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tablo_notlar.verticalHeader().setVisible(False)
        self.tablo_notlar.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tablo_notlar.itemDoubleClicked.connect(self._not_secildi)

        self.ana_layout.addWidget(self.arama_kutusu)
        self.ana_layout.addWidget(self.tablo_notlar)

    def notlari_guncelle(self, kategori_id, etiket_idler):
        """Verilen filtrelere göre not listesini yeniden doldurur."""
        arama_metni = self.arama_kutusu.text()
        notlar = self.db.get_notlari(
            kategori_id=kategori_id,
            etiket_idler=etiket_idler,
            arama_metni=arama_metni
        )

        self.tablo_notlar.setRowCount(0) # Tabloyu temizle
        self.tablo_notlar.setRowCount(len(notlar))

        for satir_index, not_kaydi in enumerate(notlar):
            not_id = not_kaydi['ID']
            baslik = not_kaydi['Baslik']
            tarih_str = not_kaydi['GuncellemeTarihi']

            # Tarihi formatla
            try:
                # Örnek format: 2024-05-20 15:45:00
                tarih_obj = datetime.strptime(tarih_str, '%Y-%m-%d %H:%M:%S')
                gosterim_tarihi = tarih_obj.strftime('%d.%m.%Y %H:%M')
            except (ValueError, TypeError):
                gosterim_tarihi = "N/A"

            # ID'yi ilk sütunun verisi olarak sakla
            id_item = QTableWidgetItem(baslik)
            id_item.setData(Qt.ItemDataRole.UserRole, not_id)

            tarih_item = QTableWidgetItem(gosterim_tarihi)

            self.tablo_notlar.setItem(satir_index, 0, id_item)
            self.tablo_notlar.setItem(satir_index, 1, tarih_item)

    def _not_secildi(self, item):
        """Bir not satırına çift tıklandığında sinyali yayar."""
        # ID'yi ilk sütundan al
        id_item = self.tablo_notlar.item(item.row(), 0)
        not_id = id_item.data(Qt.ItemDataRole.UserRole)
        self.notAcmaIstegi.emit(not_id)

    def get_secili_not_id(self):
        """Seçili satırdaki notun ID'sini döndürür."""
        secili_items = self.tablo_notlar.selectedItems()
        if secili_items:
            id_item = self.tablo_notlar.item(secili_items[0].row(), 0)
            return id_item.data(Qt.ItemDataRole.UserRole)
        return -1
