# -*- coding: utf-8 -*-
"""
Not Defteri - Şifreleme Modülü
Notlar için şifreleme ve parola koruması.
"""

import os
import base64
import hashlib
import json
from typing import Optional, Tuple
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialogButtonBox, QMessageBox, QCheckBox,
    QFrame, QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class SifreYoneticisi:
    """
    Notlar için şifreleme işlemlerini yöneten sınıf.
    AES-256 şifreleme kullanır.
    """

    def __init__(self):
        self.iterations = 100000  # PBKDF2 iterasyon sayısı

    def _anahtar_turet(self, parola: str, tuz: bytes) -> bytes:
        """Paroladan şifreleme anahtarı türetir."""
        if not CRYPTO_AVAILABLE:
            # Basit hash tabanlı anahtar (güvenli değil, sadece fallback)
            return base64.urlsafe_b64encode(
                hashlib.pbkdf2_hmac('sha256', parola.encode(), tuz, self.iterations)[:32]
            )

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=tuz,
            iterations=self.iterations,
        )
        return base64.urlsafe_b64encode(kdf.derive(parola.encode()))

    def sifrele(self, metin: str, parola: str) -> str:
        """
        Metni şifreler.

        Args:
            metin: Şifrelenecek metin
            parola: Şifreleme parolası

        Returns:
            Base64 kodlanmış şifreli veri (tuz + şifreli içerik)
        """
        tuz = os.urandom(16)
        anahtar = self._anahtar_turet(parola, tuz)

        if CRYPTO_AVAILABLE:
            f = Fernet(anahtar)
            sifreli = f.encrypt(metin.encode())
        else:
            # Basit XOR şifreleme (güvenli değil, sadece fallback)
            sifreli = self._basit_sifrele(metin.encode(), anahtar)

        # Tuz + şifreli veriyi birleştir
        sonuc = base64.urlsafe_b64encode(tuz + sifreli)
        return sonuc.decode()

    def sifre_coz(self, sifreli_veri: str, parola: str) -> Optional[str]:
        """
        Şifreli veriyi çözer.

        Args:
            sifreli_veri: Base64 kodlanmış şifreli veri
            parola: Şifre çözme parolası

        Returns:
            Çözülmüş metin veya None (hatalı parola)
        """
        try:
            ham_veri = base64.urlsafe_b64decode(sifreli_veri.encode())
            tuz = ham_veri[:16]
            sifreli = ham_veri[16:]

            anahtar = self._anahtar_turet(parola, tuz)

            if CRYPTO_AVAILABLE:
                f = Fernet(anahtar)
                cozulmus = f.decrypt(sifreli)
            else:
                cozulmus = self._basit_sifre_coz(sifreli, anahtar)

            return cozulmus.decode()
        except Exception:
            return None

    def _basit_sifrele(self, veri: bytes, anahtar: bytes) -> bytes:
        """Basit XOR şifreleme (fallback)."""
        anahtar_bytes = base64.urlsafe_b64decode(anahtar)
        sonuc = bytearray()
        for i, byte in enumerate(veri):
            sonuc.append(byte ^ anahtar_bytes[i % len(anahtar_bytes)])
        return bytes(sonuc)

    def _basit_sifre_coz(self, veri: bytes, anahtar: bytes) -> bytes:
        """Basit XOR şifre çözme (fallback)."""
        return self._basit_sifrele(veri, anahtar)  # XOR kendi tersidir

    def parola_hash_olustur(self, parola: str) -> str:
        """Parola doğrulama için hash oluşturur."""
        tuz = os.urandom(16)
        hash_bytes = hashlib.pbkdf2_hmac('sha256', parola.encode(), tuz, self.iterations)
        return base64.urlsafe_b64encode(tuz + hash_bytes).decode()

    def parola_dogrula(self, parola: str, hash_str: str) -> bool:
        """Parolanın doğruluğunu kontrol eder."""
        try:
            ham_veri = base64.urlsafe_b64decode(hash_str.encode())
            tuz = ham_veri[:16]
            beklenen_hash = ham_veri[16:]

            gercek_hash = hashlib.pbkdf2_hmac('sha256', parola.encode(), tuz, self.iterations)
            return gercek_hash == beklenen_hash
        except Exception:
            return False

    def parola_guclu_mu(self, parola: str) -> Tuple[bool, str]:
        """
        Parola gücünü kontrol eder.

        Returns:
            (güçlü_mü, mesaj)
        """
        if len(parola) < 8:
            return False, "Parola en az 8 karakter olmalı"

        if not any(c.isupper() for c in parola):
            return False, "Parola en az bir büyük harf içermeli"

        if not any(c.islower() for c in parola):
            return False, "Parola en az bir küçük harf içermeli"

        if not any(c.isdigit() for c in parola):
            return False, "Parola en az bir rakam içermeli"

        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in parola):
            return False, "Parola en az bir özel karakter içermeli"

        return True, "Parola güçlü"


class SifreliNotDialog(QDialog):
    """Şifreli not için parola girişi dialogu."""

    parolaGirildi = pyqtSignal(str)

    def __init__(self, parent=None, mod: str = 'coz', not_baslik: str = ''):
        """
        Args:
            parent: Üst widget
            mod: 'sifrele' veya 'coz'
            not_baslik: Not başlığı
        """
        super().__init__(parent)
        self.mod = mod
        self.not_baslik = not_baslik
        self.sifre_yoneticisi = SifreYoneticisi()
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        """Dialog arayüzünü oluşturur."""
        if self.mod == 'sifrele':
            self.setWindowTitle('Notu Şifrele')
        else:
            self.setWindowTitle('Şifreli Not')

        self.setMinimumWidth(400)
        self.setModal(True)

        yerlesim = QVBoxLayout(self)

        # Başlık
        if self.not_baslik:
            baslik = QLabel(f'📝 {self.not_baslik}')
            baslik.setFont(QFont('Segoe UI', 12, QFont.Bold))
            yerlesim.addWidget(baslik)

        # Bilgi
        if self.mod == 'sifrele':
            bilgi = QLabel('Bu not şifrelenecek. Lütfen bir parola belirleyin.')
        else:
            bilgi = QLabel('Bu not şifrelidir. Görüntülemek için parolayı girin.')
        bilgi.setStyleSheet('color: gray;')
        yerlesim.addWidget(bilgi)

        # Uyarı - cryptography yoksa
        if not CRYPTO_AVAILABLE:
            uyari_frame = QFrame()
            uyari_frame.setStyleSheet('''
                QFrame {
                    background-color: #fff3cd;
                    border: 1px solid #ffc107;
                    border-radius: 6px;
                    padding: 10px;
                }
            ''')
            uyari_layout = QVBoxLayout(uyari_frame)
            uyari_label = QLabel('⚠️ cryptography kütüphanesi yüklü değil.\n'
                                'Basit şifreleme kullanılacak (daha az güvenli).')
            uyari_label.setStyleSheet('color: #856404;')
            uyari_layout.addWidget(uyari_label)
            yerlesim.addWidget(uyari_frame)

        yerlesim.addSpacing(10)

        # Form
        form = QFormLayout()

        # Parola girişi
        self.parola_input = QLineEdit()
        self.parola_input.setEchoMode(QLineEdit.Password)
        self.parola_input.setPlaceholderText('Parolayı girin...')
        form.addRow('Parola:', self.parola_input)

        # Şifreleme modunda parola tekrarı
        if self.mod == 'sifrele':
            self.parola_tekrar = QLineEdit()
            self.parola_tekrar.setEchoMode(QLineEdit.Password)
            self.parola_tekrar.setPlaceholderText('Parolayı tekrar girin...')
            form.addRow('Tekrar:', self.parola_tekrar)

            # Parola gücü göstergesi
            self.guc_label = QLabel('')
            form.addRow('', self.guc_label)

            self.parola_input.textChanged.connect(self._parola_gucunu_goster)

        yerlesim.addLayout(form)

        # Parolayı göster checkbox
        self.goster_check = QCheckBox('Parolayı göster')
        self.goster_check.stateChanged.connect(self._parola_goster_degisti)
        yerlesim.addWidget(self.goster_check)

        yerlesim.addSpacing(10)

        # Butonlar
        butonlar = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        butonlar.accepted.connect(self._onayla)
        butonlar.rejected.connect(self.reject)

        if self.mod == 'sifrele':
            butonlar.button(QDialogButtonBox.Ok).setText('Şifrele')
        else:
            butonlar.button(QDialogButtonBox.Ok).setText('Aç')
        butonlar.button(QDialogButtonBox.Cancel).setText('İptal')

        yerlesim.addWidget(butonlar)

        # Enter tuşu ile onaylama
        self.parola_input.returnPressed.connect(self._onayla)

    def _parola_goster_degisti(self, durum: int):
        """Parola göster/gizle değişikliği."""
        if durum == Qt.Checked:
            self.parola_input.setEchoMode(QLineEdit.Normal)
            if hasattr(self, 'parola_tekrar'):
                self.parola_tekrar.setEchoMode(QLineEdit.Normal)
        else:
            self.parola_input.setEchoMode(QLineEdit.Password)
            if hasattr(self, 'parola_tekrar'):
                self.parola_tekrar.setEchoMode(QLineEdit.Password)

    def _parola_gucunu_goster(self, parola: str):
        """Parola gücünü gösterir."""
        if not parola:
            self.guc_label.setText('')
            return

        guclu, mesaj = self.sifre_yoneticisi.parola_guclu_mu(parola)

        if guclu:
            self.guc_label.setText('✅ ' + mesaj)
            self.guc_label.setStyleSheet('color: green;')
        else:
            self.guc_label.setText('⚠️ ' + mesaj)
            self.guc_label.setStyleSheet('color: orange;')

    def _onayla(self):
        """Parola onaylama."""
        parola = self.parola_input.text()

        if not parola:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen bir parola girin.')
            return

        if self.mod == 'sifrele':
            parola_tekrar = self.parola_tekrar.text()

            if parola != parola_tekrar:
                QMessageBox.warning(self, 'Uyarı', 'Parolalar eşleşmiyor.')
                return

            # Parola gücü uyarısı (zorunlu değil)
            guclu, _ = self.sifre_yoneticisi.parola_guclu_mu(parola)
            if not guclu:
                cevap = QMessageBox.question(
                    self, 'Zayıf Parola',
                    'Parola yeterince güçlü değil. Yine de devam etmek istiyor musunuz?',
                    QMessageBox.Yes | QMessageBox.No
                )
                if cevap == QMessageBox.No:
                    return

        self.parolaGirildi.emit(parola)
        self.accept()

    def parola_getir(self) -> str:
        """Girilen parolayı döndürür."""
        return self.parola_input.text()


class SifreliNotYoneticisi:
    """Şifreli notları yönetir."""

    def __init__(self, veritabani):
        self.vt = veritabani
        self.sifre_yoneticisi = SifreYoneticisi()

    def not_sifrele(self, not_id: int, icerik: str, zengin_icerik: str, parola: str) -> bool:
        """
        Notu şifreler ve veritabanına kaydeder.

        Returns:
            Başarılı ise True
        """
        try:
            sifreli_icerik = self.sifre_yoneticisi.sifrele(icerik, parola)
            sifreli_zengin = self.sifre_yoneticisi.sifrele(zengin_icerik, parola)
            parola_hash = self.sifre_yoneticisi.parola_hash_olustur(parola)

            # Veritabanına kaydet
            self.vt.not_sifrele(not_id, sifreli_icerik, sifreli_zengin, parola_hash)
            return True
        except Exception as e:
            print(f"Şifreleme hatası: {e}")
            return False

    def sifre_coz(self, not_id: int, parola: str) -> Optional[Tuple[str, str]]:
        """
        Şifreli notu çözer.

        Returns:
            (düz_içerik, zengin_içerik) veya None
        """
        try:
            not_verisi = self.vt.sifreli_not_getir(not_id)
            if not not_verisi:
                return None

            # Parola doğrula
            if not self.sifre_yoneticisi.parola_dogrula(parola, not_verisi['parola_hash']):
                return None

            icerik = self.sifre_yoneticisi.sifre_coz(not_verisi['sifreli_icerik'], parola)
            zengin_icerik = self.sifre_yoneticisi.sifre_coz(not_verisi['sifreli_zengin_icerik'], parola)

            if icerik is None or zengin_icerik is None:
                return None

            return icerik, zengin_icerik
        except Exception as e:
            print(f"Şifre çözme hatası: {e}")
            return None

    def sifre_kaldir(self, not_id: int, parola: str) -> bool:
        """
        Notun şifresini kaldırır.

        Returns:
            Başarılı ise True
        """
        sonuc = self.sifre_coz(not_id, parola)
        if sonuc is None:
            return False

        icerik, zengin_icerik = sonuc
        self.vt.not_sifresini_kaldir(not_id, icerik, zengin_icerik)
        return True
