# ui/gezgin_bileseni.py
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QGroupBox, QTreeWidget, QTreeWidgetItem, QListWidget,
    QListWidgetItem, QSplitter
)
from PySide6.QtCore import Qt, Signal

class GezginBileseni(QFrame):
    """
    Kategorileri (QTreeWidget) ve etiketleri (QListWidget) gösteren
    ve filtre değişikliklerini bildiren arayüz bileşeni.
    """
    # Sinyal: Filtreleme kriterleri değiştiğinde yayılır.
    filtreDegisti = Signal()

    def __init__(self, veritabani_yoneticisi, parent=None):
        super().__init__(parent)
        self.db = veritabani_yoneticisi

        self.ana_layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.ana_layout.addWidget(self.splitter)

        # Kategoriler Grubu
        kategoriler_grup = QGroupBox("Kategoriler")
        kategoriler_layout = QVBoxLayout()

        self.agac_kategoriler = QTreeWidget()
        self.agac_kategoriler.setHeaderHidden(True)
        self.agac_kategoriler.itemSelectionChanged.connect(self.filtreDegisti.emit)
        kategoriler_layout.addWidget(self.agac_kategoriler)
        kategoriler_grup.setLayout(kategoriler_layout)

        # Etiketler Grubu
        etiketler_grup = QGroupBox("Etiketler")
        etiketler_layout = QVBoxLayout()

        self.liste_etiketler = QListWidget()
        self.liste_etiketler.itemChanged.connect(self._etiket_degisti)
        etiketler_layout.addWidget(self.liste_etiketler)
        etiketler_grup.setLayout(etiketler_layout)

        self.splitter.addWidget(kategoriler_grup)
        self.splitter.addWidget(etiketler_grup)

        self._bilesen_sinyali_bloklandi = False

    def verileri_yukle(self):
        """Kategorileri ve etiketleri veritabanından yükler."""
        self._kategorileri_yukle()
        self._etiketleri_yukle()

    def _kategorileri_yukle(self):
        """Kategori ağacını doldurur."""
        self.agac_kategoriler.clear()

        # Tüm Notlar kök düğümü
        tum_notlar_item = QTreeWidgetItem(self.agac_kategoriler, ["Tüm Notlar"])
        tum_notlar_item.setData(0, Qt.ItemDataRole.UserRole, -1) # ID olarak -1

        kategoriler = self.db.get_kategoriler()
        for kategori in kategoriler:
            item = QTreeWidgetItem(self.agac_kategoriler, [kategori['KategoriAdi']])
            item.setData(0, Qt.ItemDataRole.UserRole, kategori['ID'])

        self.agac_kategoriler.expandAll()
        if self.agac_kategoriler.topLevelItemCount() > 0:
            self.agac_kategoriler.setCurrentItem(tum_notlar_item)

    def _etiketleri_yukle(self):
        """Etiket listesini doldurur."""
        self._bilesen_sinyali_bloklandi = True
        self.liste_etiketler.clear()
        etiketler = self.db.get_etiketler()
        for etiket in etiketler:
            item = QListWidgetItem(etiket['EtiketAdi'], self.liste_etiketler)
            item.setData(Qt.ItemDataRole.UserRole, etiket['ID'])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
        self._bilesen_sinyali_bloklandi = False

    def _etiket_degisti(self, item):
        """Bir etiket işaretlendiğinde/kaldırıldığında sinyali yayar."""
        if not self._bilesen_sinyali_bloklandi:
            self.filtreDegisti.emit()

    def get_secili_kategori_id(self):
        """Seçili kategorinin ID'sini döndürür."""
        secili_item = self.agac_kategoriler.currentItem()
        if secili_item:
            return secili_item.data(0, Qt.ItemDataRole.UserRole)
        return -1

    def get_secili_etiket_idler(self):
        """İşaretlenmiş etiketlerin ID listesini döndürür."""
        idler = []
        for i in range(self.liste_etiketler.count()):
            item = self.liste_etiketler.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                idler.append(item.data(Qt.ItemDataRole.UserRole))
        return idler
