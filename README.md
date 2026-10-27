# Dompet Digital & Split Bill (Fintech CLI)
> **Tugas Besar Mata Kuliah Object-Oriented Programming (OOP) - Bagian UTS**

Proyek ini adalah aplikasi simulasi dompet digital dan pemecah tagihan grup (*split bill*) berbasis antarmuka baris perintah (CLI) yang dibangun dengan bahasa pemrograman **Python** dengan menerapkan prinsip-prinsip utama OOP.

---

## 📌 Apa yang Ada Saat Ini (Kondisi Awal)
- Repositori baru diinisialisasi.
- Dokumen acuan fondasi proyek (`README.md`) telah dibuat sebagai panduan pengerjaan bertahap.
- Ruang lingkup kerja saat ini difokuskan penuh pada **Fitur UTS (Nomor 1–10)**.

---

## 🎯 Fondasi Konsep OOP yang Wajib Diterapkan di UTS

1. **Inheritance & Abstract Base Classes (ABC)**
   - Menggunakan modul `abc` bawaan Python (`ABC`, `@abstractmethod`).
   - Contoh penerapan:
     - Kelas abstrak `PaymentMethod` yang diturunkan menjadi berbagai metode top-up nyata (misal: `BankTransfer`, `EWallet`, `CreditCard`).
     - Hirarki kelas rekening/wallet atau grup.

2. **Polymorphism**
   - Berbagai turunan `PaymentMethod` mengimplementasikan fungsi pembayaran/top-up dengan validasi dan perilakunya masing-masing, namun dipanggil melalui antarmuka yang seragam.

3. **Custom Exception Handling**
   - Menangani kasus-kasus galat bisnis dengan kelas eksepsi kustom:
     - `TransferLimitException`: Dilempar saat transfer melebihi limit harian yang ditentukan.
     - `InsufficientFundsException`: Dilempar saat saldo wallet tidak mencukupi untuk transfer atau pembayaran tagihan.

---

## 📋 Checklist & Roadmap Fitur UTS (Fitur 1–10)

Berikut daftar target fitur UTS beserta status pengerjaannya:

| No | Fitur UTS | Konsep OOP Terkait | Status |
|:--:|:---|:---|:---:|
| 1 | **Registrasi pengguna & inisialisasi Wallet** (saldo awal 0) | Encapsulation, Constructor (`__init__`) | ⏳ Belum Mulai |
| 2 | **Top-up saldo via metode pembayaran** | Inheritance / ABC, Polymorphism | ⏳ Belum Mulai |
| 3 | **Transfer ke pengguna lain + cek limit harian** | Encapsulation, State Tracking | ⏳ Belum Mulai |
| 4 | **Raise `TransferLimitException` & `InsufficientFundsException`** | Custom Exception Handling | ⏳ Belum Mulai |
| 5 | **Bayar tagihan** (listrik, air, internet) | Polymorphism / Enumeration | ⏳ Belum Mulai |
| 6 | **Catat setiap transaksi ke riwayat** | Composition, Association | ⏳ Belum Mulai |
| 7 | **Buat grup split bill & tambah anggota** | Aggregation, List Management | ⏳ Belum Mulai |
| 8 | **Input pengeluaran bersama ke grup** | Association, Object Interaction | ⏳ Belum Mulai |
| 9 | **Split tagihan rata antar anggota** | Algoritma Pembagian Rata (Equal Split) | ⏳ Belum Mulai |
| 10 | **Tampilkan siapa berutang ke siapa & berapa** (CLI) | CLI Output Formatting | ⏳ Belum Mulai |

---

## 🧱 Blueprint Fondasi Kelas (Class Architecture)

Rencana struktur kelas dasar yang akan dibangun bertahap:

```text
src/
├── exceptions/
│   └── wallet_exceptions.py     # InsufficientFundsException, TransferLimitException
├── models/
│   ├── user.py                  # Class User (id, nama, email, wallet)
│   ├── wallet.py                # Class Wallet (saldo, limit harian, riwayat transaksi)
│   ├── transaction.py           # Class Transaction (id, tipe, jumlah, timestamp, deskripsi)
│   ├── bill.py                  # Class Bill / Biller (listrik, air, internet)
│   └── group.py                 # Class Group (nama grup, anggota, daftar pengeluaran)
├── services/
│   ├── payment_methods.py       # ABC PaymentMethod (Bank, E-Wallet, Kartu)
│   └── split_bill_service.py    # Logika penghitungan utang & split rata
└── main.py                      # Menu CLI interaktif dan alur program
```

---

## 👣 Rencana Pengerjaan Bertahap (Step-by-Step)

Agar fondasi mudah dipahami langkah demi langkah, kita bagi pengerjaannya menjadi 4 langkah kecil:

1. **Langkah 1: Fondasi Exception & Model Inti (Fitur 1, 4, 6)**
   - Membuat `InsufficientFundsException` & `TransferLimitException`.
   - Membuat model `Wallet`, `User`, dan pencatatan `Transaction`.
2. **Langkah 2: Top-Up Polymorphic & Layanan Transfer/Tagihan (Fitur 2, 3, 5)**
   - Membuat ABC `PaymentMethod` dan implementasinya (Polymorphism).
   - Menambahkan logika transfer antar wallet dengan pengecekan limit harian.
   - Menambahkan fungsionalitas bayar tagihan (listrik, air, internet).
3. **Langkah 3: Grup Split Bill & Perhitungan Utang (Fitur 7, 8, 9, 10)**
   - Membuat model `Group` dan penambahan anggota.
   - Menghitung pembagian rata pengeluaran (*equal split*).
   - Menghitung dan menampilkan siapa berutang ke siapa.
4. **Langkah 4: Antarmuka Interaktif CLI (`main.py`)**
   - Menghubungkan semua fitur ke menu terminal yang interaktif dan mudah diuji coba.
