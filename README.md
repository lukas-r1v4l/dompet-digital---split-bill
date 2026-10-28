# Dompet Digital & Split Bill (Fintech CLI)

> **Tugas Besar Mata Kuliah Object-Oriented Programming (OOP) - Bagian UTS**

Proyek ini adalah aplikasi simulasi dompet digital dan pemecah tagihan grup (_split bill_) berbasis antarmuka baris perintah (CLI) yang dibangun dengan bahasa pemrograman **Python** dengan menerapkan prinsip-prinsip utama OOP.

---

## 📌 Struktur File Proyek (Sederhana & Mudah Dibaca)

Seluruh kelas OOP disatukan secara terstruktur di dalam satu file model utama, sehingga alur dan hirarki kelas dapat dibaca langsung dari atas ke bawah:

```text
dompet-digital---split-bill/
├── README.md           # Dokumentasi dan checklist fitur
├── models.py           # Seluruh Class OOP (Exception, Transaction, Wallet, User, dll.)
└── main.py             # Program utama CLI (interaktif)
```

---

## 🎯 Fondasi Konsep OOP yang Diterapkan di UTS

1. **Inheritance & Abstract Base Classes (ABC)**
   - Menggunakan modul `abc` (`ABC`, `@abstractmethod`).
   - Menerapkan pewarisan `super().__init__(...)` sesuai materi Pertemuan 02 & 03.

2. **Polymorphism**
   - Menggunakan method overriding untuk berbagai metode pembayaran dan tagihan.

3. **Custom Exception Handling**
   - Menangani kasus-kasus galat bisnis dengan kelas eksepsi kustom turunan `Exception` (Pertemuan 04):
     - `TransferLimitException`: Dilempar saat transfer melebihi limit harian yang ditentukan.
     - `InsufficientFundsException`: Dilempar saat saldo wallet tidak mencukupi untuk transfer atau pembayaran tagihan.

---

## 📋 Checklist & Roadmap Fitur UTS (Fitur 1–10)

Berikut daftar target fitur UTS beserta status pengerjaannya:

| No  | Fitur UTS                                                         | Konsep OOP Terkait                      |         Status         |
| :-: | :---------------------------------------------------------------- | :-------------------------------------- | :--------------------: |
|  1  | **Registrasi pengguna & inisialisasi Wallet** (saldo awal 0)      | Encapsulation, Constructor (`__init__`) | ✅ Selesai (Langkah 1) |
|  2  | **Top-up saldo via metode pembayaran**                            | Inheritance / ABC, Polymorphism         | ✅ Selesai (Langkah 2) |
|  3  | **Transfer ke pengguna lain + cek limit harian**                  | Encapsulation, State Tracking           | ✅ Selesai (Langkah 2) |
|  4  | **Raise `TransferLimitException` & `InsufficientFundsException`** | Custom Exception Handling               | ✅ Selesai (Langkah 1) |
|  5  | **Bayar tagihan** (listrik, air, internet)                        | Polymorphism / Enumeration              | ✅ Selesai (Langkah 2) |
|  6  | **Catat setiap transaksi ke riwayat**                             | Composition, Association                | ✅ Selesai (Langkah 1) |
|  7  | **Buat grup split bill & tambah anggota**                         | Aggregation, List Management            | ✅ Selesai (Langkah 3) |
|  8  | **Input pengeluaran bersama ke grup**                             | Association, Object Interaction         | ✅ Selesai (Langkah 3) |
|  9  | **Split tagihan rata antar anggota**                              | Algoritma Pembagian Rata (Equal Split)  | ✅ Selesai (Langkah 3) |
| 10  | **Tampilkan siapa berutang ke siapa & berapa** (CLI)              | CLI Output Formatting                   | ✅ Selesai (Langkah 3) |

---

## 👣 Rencana Pengerjaan Bertahap (Step-by-Step)

1. **Langkah 1: Fondasi Exception & Model Inti (Fitur 1, 4, 6)** ✅ _Selesai_
   - Membuat custom exception `InsufficientFundsException` & `TransferLimitException`.
   - Membuat model dasar `Wallet` (saldo awal 0), `User`, dan pencatatan `Transaction`.
2. **Langkah 2: Top-Up Polymorphic & Layanan Transfer/Tagihan (Fitur 2, 3, 5)** ⏳ _Berikutnya_
   - Membuat ABC `PaymentMethod` dan implementasinya (Polymorphism).
   - Menambahkan fungsionalitas transfer antar user dengan validasi limit harian.
   - Menambahkan fungsionalitas bayar tagihan (listrik, air, internet).
3. **Langkah 3: Grup Split Bill & Perhitungan Utang (Fitur 7, 8, 9, 10)** ✅ _Selesai_
   - Membuat model `Group` dan penambahan anggota.
   - Menghitung pembagian rata pengeluaran bersama (_equal split_).
   - Menghitung dan menampilkan siapa berutang ke siapa dan berapa nominalnya.
4. **Langkah 4: Antarmuka Interaktif CLI Final (`main.py`)** ⏳ _Belum Mulai_
   - Menghubungkan seluruh fitur lengkap (Fitur 1 s.d. 10) ke menu terminal interaktif yang komprehensif.
