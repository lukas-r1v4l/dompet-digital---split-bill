"""
Program Utama Antarmuka CLI Dompet Digital & Split Bill
Gateway peran (Admin & Pengguna), sistem autentikasi PIN, serta audit pengguna dan ulasan.
"""

from typing import Dict
from models import (
    User,
    Admin,
    FeedbackService,
    InsufficientFundsException,
    TransferLimitException,
    BillType,
    BillPaymentService,
    TransferService,
    find_payment_method,
    get_payment_methods
)


def print_header(title: str) -> None:
    print("\n" + "=" * 48)
    print(f"  {title.upper()}")
    print("=" * 48)


def validate_name(nama):
    teks = nama.strip() if nama else ""
    if len(teks) < 3:
        raise ValueError("Nama lengkap minimal terdiri dari 3 karakter.")
    if not teks.replace(" ", "").isalpha():
        raise ValueError("Nama lengkap hanya boleh berisi huruf dan spasi.")
    return teks


def validate_phone(no_hp):
    teks = no_hp.strip() if no_hp else ""
    if not teks.isdigit():
        raise ValueError("Nomor HP harus berupa angka.")
    if len(teks) < 10 or len(teks) > 13:
        raise ValueError("Nomor HP harus terdiri dari 10 sampai 13 digit.")
    if not (teks.startswith("08") or teks.startswith("628")):
        raise ValueError("Nomor HP harus diawali dengan '08' atau '628'.")
    return teks


def validate_email(email):
    teks = email.strip() if email else ""
    if not teks:
        raise ValueError("Email tidak boleh kosong.")
    if " " in teks or "@" not in teks or "." not in teks:
        raise ValueError("Format email tidak valid (contoh yang benar: nama@domain.com).")

    bagian = teks.split("@")
    if len(bagian) != 2 or not bagian[0] or not bagian[1]:
        raise ValueError("Format email tidak valid (contoh yang benar: nama@domain.com).")

    domain = bagian[1]
    if "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise ValueError("Format email tidak valid (contoh yang benar: nama@domain.com).")

    return teks


def find_user_by_id_or_phone(users, identifier):
    target = identifier.strip() if identifier else ""
    for u in users.values():
        if u.name == target or u.user_id == target or u.phone_number == target:
            return u
    return None


def find_admin_by_id_or_phone(admins, identifier):
    target = identifier.strip() if identifier else ""
    for a in admins.values():
        if a.name == target or a.admin_id == target or a.phone_number == target:
            return a
    return None


# --- MENU TRANSAKSI PENGGUNA AKTIF ---

def menu_pengguna_aktif(
    active_user: User,
    users: Dict[str, User],
    transfer_service: TransferService,
    bill_service: BillPaymentService,
    feedback_service: FeedbackService
) -> None:
    while True:
        print_header("Dashboard Pengguna Dompet Digital")
        print(f"Pengguna Aktif   : {active_user.name}")
        print(f"Saldo Saat Ini   : Rp {active_user.wallet.get_balance():,.2f}")
        print(f"Sisa Limit Harian: Rp {active_user.wallet.get_remaining_daily_limit():,.2f}")
        print("-" * 48)
        print("1. Top-Up via Metode Pembayaran")
        print("2. Transfer Antar User")
        print("3. Bayar Tagihan (Listrik / Air / Internet)")
        print("4. Tarik Tunai / Pengeluaran")
        print("5. Lihat Riwayat Transaksi")
        print("6. Berikan Ulasan & Saran Aplikasi")
        print("7. Ganti PIN")
        print("0. Log Out")
        print("-" * 48)

        pilihan = input("Pilih menu (0-7): ").strip()

        if pilihan == "1":
            # Fitur 2: Top-up saldo via polimorfisme
            print_header("Top-Up Saldo via Metode Pembayaran")
            daftar_metode = get_payment_methods()
            print("Metode pembayaran yang tersedia:")
            for nomor, metode in enumerate(daftar_metode, start=1):
                print(f"  {nomor}. {metode}")
            print("  0. Kembali")
            print("-" * 48)

            pilihan_metode = input("Pilih menu (0-4): ").strip()
            if pilihan_metode == "0":
                continue

            try:
                if pilihan_metode.isdigit():
                    indeks = int(pilihan_metode) - 1
                    if indeks < 0 or indeks >= len(daftar_metode):
                        raise ValueError(f"Pilihan '{pilihan_metode}' tidak ada dalam daftar.")
                    metode_dipilih = daftar_metode[indeks]
                else:
                    metode_dipilih = find_payment_method(pilihan_metode)

                nominal = float(input(f"Nominal top-up ({metode_dipilih.name}): Rp "))
                trx = metode_dipilih.top_up(active_user.wallet, nominal)

                print(f"\nTop-up BERHASIL via {metode_dipilih.name}!")
                print(f"Biaya admin : Rp {metode_dipilih.calculate_admin_fee(nominal):,.2f}")
                print(f"Saldo masuk : Rp {trx.amount:,.2f}")
                print(f"Saldo akhir : Rp {active_user.wallet.get_balance():,.2f}")
            except ValueError as e:
                print(f"[Error]: {e}")

        elif pilihan == "2":
            # Fitur 3: Transfer antar pengguna
            print_header("Transfer Antar Pengguna")
            tujuan_id = input("Masukkan Nama / User ID / No HP penerima: ").strip()
            if not tujuan_id:
                continue

            try:
                penerima = find_user_by_id_or_phone(users, tujuan_id)
                if not penerima:
                    raise ValueError(f"Penerima '{tujuan_id}' tidak ditemukan.")
                if penerima.user_id == active_user.user_id:
                    raise ValueError("Tidak bisa transfer ke akun sendiri!")

                nominal = float(input(f"Nominal transfer ke {penerima.name}: Rp "))
                trx = transfer_service.transfer(active_user, penerima, nominal)

                print(f"\nTransfer Rp {nominal:,.2f} ke {penerima.name} BERHASIL!")
                print(f"ID Transaksi: {trx.transaction_id}")
                print(f"Sisa limit harian: Rp {active_user.wallet.get_remaining_daily_limit():,.2f}")
            except (ValueError, TransferLimitException, InsufficientFundsException) as e:
                print(f"[Gagal Transfer]: {e}")

        elif pilihan == "3":
            # Fitur 5: Bayar tagihan
            print_header("Bayar Tagihan")
            print("Jenis tagihan:")
            for nomor, tipe in enumerate(bill_service.get_bill_types(), start=1):
                print(f"  {nomor}. {tipe.label}")
            print("  0. Kembali")
            print("-" * 48)

            pilih_tipe = input("Pilih menu (0-3): ").strip()
            if pilih_tipe == "0":
                continue

            try:
                if pilih_tipe.isdigit():
                    indeks = int(pilih_tipe) - 1
                    if indeks < 0 or indeks >= len(bill_service.get_bill_types()):
                        raise ValueError(f"Pilihan '{pilih_tipe}' tidak valid.")
                    tipe = bill_service.get_bill_types()[indeks]
                else:
                    tipe = BillType[pilih_tipe.upper()]

                no_pelanggan = input("Nomor pelanggan: ").strip()
                nama_pelanggan = input("Nama pelanggan : ").strip()
                nominal = float(input("Nominal tagihan: Rp "))
                periode = input("Periode (opsional): ").strip()

                tagihan = bill_service.create_bill(tipe, no_pelanggan, nama_pelanggan, nominal, periode)
                print(f"\n{tagihan}")

                if input("Bayar sekarang? (y/n): ").strip().lower() != "y":
                    print("Pembayaran dibatalkan.")
                    continue

                trx = bill_service.pay_bill(active_user, tagihan)
                print(f"Pembayaran BERHASIL! (ID: {trx.transaction_id})")
                print(f"Sisa saldo: Rp {active_user.wallet.get_balance():,.2f}")
            except (ValueError, KeyError, IndexError, InsufficientFundsException) as e:
                print(f"[Gagal Pembayaran]: {e}")

        elif pilihan == "4":
            # Fitur 4: Tarik tunai & cek saldo
            print_header("Tarik Tunai / Pengeluaran")
            try:
                nominal = float(input("Nominal penarikan: Rp "))
                active_user.wallet.debit(nominal, description="Tarik Tunai", tx_type="WITHDRAW")
                print(f"Penarikan berhasil! Sisa saldo: Rp {active_user.wallet.get_balance():,.2f}")
            except InsufficientFundsException as e:
                print(f"[Gagal - Saldo Kurang]: {e}")
            except ValueError as e:
                print(f"[Error]: {e}")

        elif pilihan == "5":
            # Fitur 6: Riwayat transaksi
            print_header(f"Riwayat Transaksi: {active_user.name}")
            riwayat = active_user.wallet.get_transaction_history()
            if not riwayat:
                print("Belum ada riwayat transaksi.")
            else:
                for trx in riwayat:
                    print(trx)

        elif pilihan == "6":
            # Ulasan & feedback pengguna
            print_header("Beri Ulasan & Komentar")
            try:
                rating = int(input("Masukkan rating (1-5 bintang): "))
                komentar = input("Tuliskan ulasan / komentar: ").strip()
                fb = feedback_service.add_feedback(active_user, rating, komentar)
                print(f"Terima kasih atas ulasan Anda! (ID: {fb.feedback_id})")
            except ValueError as e:
                print(f"[Error]: {e}")

        elif pilihan == "7":
            # Ganti PIN aktif
            print_header("Ganti PIN Akun")
            pin_lama = input("Masukkan PIN lama: ").strip()
            if not active_user.verify_pin(pin_lama):
                print("[Gagal]: PIN lama tidak sesuai.")
                continue

            pin_baru = input("Masukkan PIN baru (6 digit angka): ").strip()
            pin_confirm = input("Konfirmasi PIN baru: ").strip()
            if pin_baru != pin_confirm:
                print("[Error]: Konfirmasi PIN baru tidak cocok!")
                continue

            try:
                active_user.reset_pin_with_phone(active_user.phone_number, pin_baru)
                print("PIN berhasil diubah!")
            except ValueError as e:
                print(f"[Error]: {e}")

        elif pilihan == "0":
            print(f"User {active_user.name} berhasil log out.\n")
            break

        else:
            print("Pilihan menu tidak valid.")


# --- PORTAL PENGGUNA (LOGIN / SIGN UP / LUPA PIN) ---

def portal_pengguna(
    users: Dict[str, User],
    transfer_service: TransferService,
    bill_service: BillPaymentService,
    feedback_service: FeedbackService
) -> None:
    while True:
        print_header("Portal Pengguna Dompet Digital")
        print("1. Log In")
        print("2. Sign Up")
        print("3. Lupa PIN")
        print("0. Kembali ke Menu Utama")
        print("-" * 48)

        pilihan = input("Pilih menu (0-3): ").strip()

        if pilihan == "1":
            print_header("Log In Pengguna")
            identitas = input("Masukkan Nama, User ID, atau Nomor HP: ").strip()
            user = find_user_by_id_or_phone(users, identitas)

            if not user:
                print("[Error]: Pengguna tidak ditemukan. Silakan Sign Up terlebih dahulu.")
                continue

            pin = input("Masukkan PIN (6 digit): ").strip()
            if user.verify_pin(pin):
                print(f"\nSelamat datang kembali, {user.name}!")
                menu_pengguna_aktif(user, users, transfer_service, bill_service, feedback_service)
            else:
                print("[Error]: PIN yang Anda masukkan salah!")

        elif pilihan == "2":
            # Fitur 1: Registrasi Pengguna & Inisialisasi Wallet Saldo 0
            print_header("Sign Up Pengguna Baru")
            try:
                nama_input = input("Nama Lengkap : ")
                nama = validate_name(nama_input)

                # Cek apakah nama sudah pernah digunakan
                if any(u.name.lower() == nama.lower() for u in users.values()):
                    print(f"[Error]: Nama '{nama}' sudah terdaftar. Silakan gunakan variasi nama lain.")
                    continue

                no_hp_input = input("Nomor HP     : ")
                no_hp = validate_phone(no_hp_input)

                # Cek duplikasi nomor HP
                if find_user_by_id_or_phone(users, no_hp):
                    print("[Error]: Nomor HP sudah terdaftar pada akun lain.")
                    continue

                email_input = input("Email        : ")
                email = validate_email(email_input)

                pin = input("Buat PIN (6 digit angka)     : ").strip()
                pin_confirm = input("Konfirmasi PIN (masukkan lagi): ").strip()
                if pin != pin_confirm:
                    print("[Error]: Konfirmasi PIN tidak cocok!")
                    continue

                user_id = f"USR-{len(users) + 1:02d}"
                baru = User(user_id=user_id, name=nama, phone_number=no_hp, email=email, pin=pin)
                users[user_id] = baru

                print("\nPendaftaran Berhasil!")
                print(f"Nama Akun  : {baru.name}")
                print(f"Nomor HP   : {baru.phone_number}")
                print(f"Saldo Awal : Rp {baru.wallet.get_balance():,.2f}")
                print("Catatan: Anda sekarang dapat langsung login menggunakan Nama atau Nomor HP.")
            except ValueError as e:
                print(f"[Pendaftaran Gagal]: {e}")

        elif pilihan == "3":
            print_header("Lupa PIN Pengguna")
            identitas = input("Masukkan Nama, User ID, atau Nomor HP terdaftar: ").strip()
            user = find_user_by_id_or_phone(users, identitas)

            if not user:
                print("[Error]: Akun tidak ditemukan.")
                continue

            verifikasi_hp = input("Masukkan Nomor HP untuk verifikasi: ").strip()
            pin_baru = input("Masukkan PIN baru (6 digit angka): ").strip()
            pin_confirm = input("Konfirmasi PIN baru: ").strip()
            if pin_baru != pin_confirm:
                print("[Error]: Konfirmasi PIN baru tidak cocok!")
                continue

            try:
                user.reset_pin_with_phone(verifikasi_hp, pin_baru)
                print(f"\nPIN untuk {user.name} berhasil direset! Silakan Log In.")
            except ValueError as e:
                print(f"[Gagal Reset PIN]: {e}")

        elif pilihan == "0":
            break

        else:
            print("Pilihan tidak valid.")


# --- MENU ADMIN AKTIF & PORTAL ADMIN ---

def menu_admin_aktif(
    active_admin: Admin,
    users: Dict[str, User],
    feedback_service: FeedbackService
) -> None:
    while True:
        print_header("Dashboard Administrator")
        print(f"Admin Aktif: {active_admin.name}")
        print("-" * 48)
        print("1. Lihat Seluruh Data Pengguna")
        print("2. Lihat Komentar & Ulasan Pengguna")
        print("3. Ringkasan Statistik Dompet Digital")
        print("0. Log Out")
        print("-" * 48)

        pilihan = input("Pilih menu (0-3): ").strip()

        if pilihan == "1":
            print_header("Data Seluruh Pengguna Dompet Digital")
            if not users:
                print("Belum ada pengguna terdaftar di sistem.")
            else:
                print(f"{'User ID':<8} | {'Nama Lengkap':<18} | {'Nomor HP':<14} | {'Saldo Wallet':>15}")
                print("-" * 62)
                for u in users.values():
                    print(f"{u.user_id:<8} | {u.name:<18} | {u.phone_number:<14} | Rp {u.wallet.get_balance():>12,.2f}")
                print("-" * 62)
                print(f"Total: {len(users)} pengguna terdaftar.")

        elif pilihan == "2":
            print_header("Daftar Komentar & Ulasan Pengguna")
            semua_fb = feedback_service.get_all_feedback()
            if not semua_fb:
                print("Belum ada ulasan dari pengguna.")
            else:
                rata = feedback_service.get_average_rating()
                print(f"Rata-rata Penilaian: {rata:.1f} / 5.0 (Total: {len(semua_fb)} ulasan)\n")
                for fb in semua_fb:
                    print(f"- {fb}")

        elif pilihan == "3":
            print_header("Ringkasan Statistik Sistem")
            total_saldo = sum(u.wallet.get_balance() for u in users.values())
            print(f"Jumlah Pengguna Terdaftar : {len(users)} orang")
            print(f"Total Saldo Beredar       : Rp {total_saldo:,.2f}")
            print(f"Rata-rata Rating Ulasan   : {feedback_service.get_average_rating():.2f} / 5.0")

        elif pilihan == "0":
            print(f"Admin {active_admin.name} berhasil log out.\n")
            break

        else:
            print("Pilihan menu tidak valid.")


def portal_admin(
    admins: Dict[str, Admin],
    users: Dict[str, User],
    feedback_service: FeedbackService
) -> None:
    while True:
        print_header("Portal Administrator")
        print("1. Log In Admin")
        print("2. Lupa PIN Admin")
        print("0. Kembali ke Menu Utama")
        print("-" * 48)

        pilihan = input("Pilih menu (0-2): ").strip()

        if pilihan == "1":
            print_header("Log In Administrator")
            identitas = input("Masukkan Nama, Admin ID, atau Nomor HP: ").strip()
            admin = find_admin_by_id_or_phone(admins, identitas)

            if not admin:
                print("[Error]: Admin tidak ditemukan.")
                continue

            pin = input("Masukkan PIN Admin (6 digit): ").strip()
            if admin.verify_pin(pin):
                print(f"\nAkses diterima. Selamat datang, {admin.name}!")
                menu_admin_aktif(admin, users, feedback_service)
            else:
                print("[Error]: PIN Admin salah!")

        elif pilihan == "2":
            print_header("Lupa PIN Admin")
            identitas = input("Masukkan Nama, Admin ID, atau Nomor HP: ").strip()
            admin = find_admin_by_id_or_phone(admins, identitas)

            if not admin:
                print("[Error]: Akun admin tidak ditemukan.")
                continue

            verifikasi_hp = input("Masukkan Nomor HP terdaftar: ").strip()
            pin_baru = input("Masukkan PIN baru (6 digit angka): ").strip()
            pin_confirm = input("Konfirmasi PIN baru: ").strip()
            if pin_baru != pin_confirm:
                print("[Error]: Konfirmasi PIN baru tidak cocok!")
                continue

            try:
                admin.reset_pin_with_phone(verifikasi_hp, pin_baru)
                print(f"\nPIN untuk {admin.name} berhasil diperbarui!")
            except ValueError as e:
                print(f"[Gagal Reset PIN]: {e}")

        elif pilihan == "0":
            break

        else:
            print("Pilihan tidak valid.")


# --- MAIN PROGRAM (PINTU UTAMA / GATEWAY) ---

def main():
    # Penyimpanan in-memory tanpa hardcoded user dummy
    users: Dict[str, User] = {}
    admins: Dict[str, Admin] = {
        "ADM-01": Admin("ADM-01", "Administrator Dompet", "080000000000", "123456")
    }

    # Inisialisasi service layer
    transfer_service = TransferService(users)
    bill_service = BillPaymentService()
    feedback_service = FeedbackService()

    while True:
        print_header("Aplikasi Dompet Digital & Split Bill")
        print("Selamat datang di Layanan Fintech.")
        print("-" * 48)
        print("1. Masuk sebagai Pengguna Dompet Digital")
        print("2. Masuk sebagai Administrator")
        print("0. Keluar dari Aplikasi")
        print("-" * 48)

        pilihan = input("Pilih menu (0-2): ").strip()

        if pilihan == "1":
            portal_pengguna(users, transfer_service, bill_service, feedback_service)
        elif pilihan == "2":
            portal_admin(admins, users, feedback_service)
        elif pilihan == "0":
            print("\nTerima kasih telah menggunakan aplikasi Dompet Digital!\n")
            break
        else:
            print("Pilihan tidak valid, silakan coba lagi.")


if __name__ == "__main__":
    main()
