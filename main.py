"""
Main Program - Antarmuka CLI Dompet Digital & Split Bill
Menjalankan dan menguji fitur fondasi awal (User, Wallet, Exception, Riwayat).
"""

from models import (
    User,
    InsufficientFundsException,
    TransferLimitException
)


def print_header(title: str) -> None:
    print("\n" + "=" * 45)
    print(f"  {title.upper()}")
    print("=" * 45)


def main():
    # Penyimpanan data sementara pengguna
    users = {}

    # Buat 2 akun contoh untuk mempermudah uji coba langsung
    user1 = User("USR-01", "Budi Santoso", "081211112222", "budi@email.com")
    user2 = User("USR-02", "Siti Rahma", "081233334444", "siti@email.com")
    users[user1.user_id] = user1
    users[user2.user_id] = user2

    # Akun pengguna yang sedang aktif saat ini
    active_user = user1

    while True:
        print_header("Aplikasi Dompet Digital (Fintech CLI)")
        print(f"Pengguna Aktif: {active_user.name} ({active_user.user_id})")
        print(f"Saldo Saat Ini : Rp {active_user.wallet.get_balance():,.2f}")
        print(f"Sisa Limit Harian: Rp {active_user.wallet.get_remaining_daily_limit():,.2f}")
        print("-" * 45)
        print("1. Registrasi Pengguna Baru") # fitur 1
        print("2. Ganti Pengguna Aktif")
        print("3. Top-Up Saldo Dasar (Kredit)")
        print("4. Tarik Tunai / Pengeluaran (Uji InsufficientFundsException)")
        print("5. Transfer ke Pengguna Lain (Uji Limit & Exception)")
        print("6. Lihat Riwayat Transaksi") # fitur 6
        print("0. Keluar")
        print("-" * 45)

        pilihan = input("Pilih menu (0-6): ").strip()

        if pilihan == "1":
            # Fitur 1: Registrasi Pengguna & Inisialisasi Wallet Saldo 0
            print_header("Registrasi Pengguna Baru")
            user_id = f"USR-{len(users) + 1:02d}"
            nama = input("Masukkan Nama Lengkap: ").strip()
            no_hp = input("Masukkan Nomor HP     : ").strip()
            email = input("Masukkan Email        : ").strip()

            if not nama or not no_hp:
                print(">> [Error]: Nama dan Nomor HP wajib diisi!")
                continue

            baru = User(user_id, nama, no_hp, email)
            users[user_id] = baru
            print(f">> Berhasil mendaftarkan {baru.name} dengan ID: {user_id}")
            print(f">> Saldo awal wallet otomatis diinisialisasi: Rp {baru.wallet.get_balance():,.2f}")

        elif pilihan == "2":
            # Beralih antar pengguna
            print_header("Daftar Pengguna")
            for uid, u in users.items():
                status = " (Aktif)" if u == active_user else ""
                print(f"[{uid}] {u.name} - Saldo: Rp {u.wallet.get_balance():,.2f}{status}")

            target_id = input("\nMasukkan User ID yang ingin dipilih: ").strip().upper()
            if target_id in users:
                active_user = users[target_id]
                print(f">> Pengguna aktif beralih ke: {active_user.name}")
            else:
                print(">> [Error]: User ID tidak ditemukan!")

        elif pilihan == "3":
            # Top up saldo dasar (Fitur 2)
            print_header("Top-Up Saldo")
            try:
                nominal = float(input("Masukkan nominal top-up: Rp "))
                active_user.wallet.credit(nominal, description="Top-up Saldo", tx_type="TOPUP")
                print(f">> Top-up berhasil! Saldo baru: Rp {active_user.wallet.get_balance():,.2f}")
            except ValueError as e:
                print(f">> [Error]: Input tidak valid! ({e})")

        elif pilihan == "4":
            # Tarik Tunai - menguji penangkapan InsufficientFundsException (Fitur 4)
            print_header("Tarik Tunai / Pengeluaran")
            try:
                nominal = float(input("Masukkan nominal penarikan: Rp "))
                active_user.wallet.debit(nominal, description="Tarik Tunai", tx_type="WITHDRAW")
                print(f">> Penarikan berhasil! Sisa saldo: Rp {active_user.wallet.get_balance():,.2f}")
            except InsufficientFundsException as e:
                # Tangkap custom exception jika saldo tidak cukup
                print(f">> [GAGAL - InsufficientFundsException]: {e}")
            except ValueError as e:
                print(f">> [Error]: Input tidak valid! ({e})")

        elif pilihan == "5":
            # Transfer antar pengguna - menguji TransferLimitException & InsufficientFundsException (Fitur 3 & 4)
            print_header("Transfer Saldo Antar Pengguna")
            tujuan_id = input("Masukkan User ID penerima: ").strip().upper()

            if tujuan_id == active_user.user_id:
                print(">> [Error]: Tidak bisa transfer ke akun sendiri!")
                continue

            if tujuan_id not in users:
                print(">> [Error]: Pengguna tujuan tidak ditemukan!")
                continue

            penerima = users[tujuan_id]

            try:
                nominal = float(input(f"Masukkan nominal transfer ke {penerima.name}: Rp "))

                # 1. Cek batas limit transfer harian terlebih dahulu (Fitur 3 & 4)
                active_user.wallet.check_and_track_transfer_limit(nominal)

                # 2. Kurangi saldo pengirim (akan lempar InsufficientFundsException jika kurang)
                active_user.wallet.debit(
                    nominal,
                    description=f"Transfer ke {penerima.name}",
                    reference_info=f"To: {penerima.user_id}",
                    tx_type="TRANSFER_OUT"
                )

                # 3. Tambahkan saldo ke penerima
                penerima.wallet.credit(
                    nominal,
                    description=f"Transfer dari {active_user.name}",
                    reference_info=f"From: {active_user.user_id}",
                    tx_type="TRANSFER_IN"
                )

                print(f">> Transfer Rp {nominal:,.2f} ke {penerima.name} BERHASIL!")
                print(f">> Sisa limit harian Anda: Rp {active_user.wallet.get_remaining_daily_limit():,.2f}")

            except TransferLimitException as e:
                # Tangkap custom exception saat limit harian terlampaui
                print(f">> [GAGAL - TransferLimitException]: {e}")
            except InsufficientFundsException as e:
                # Tangkap custom exception saat saldo tidak mencukupi
                print(f">> [GAGAL - InsufficientFundsException]: {e}")
            except ValueError as e:
                print(f">> [Error]: Input tidak valid! ({e})")

        elif pilihan == "6":
            # Fitur 6: Menampilkan riwayat transaksi
            print_header(f"Riwayat Transaksi: {active_user.name}")
            riwayat = active_user.wallet.get_transaction_history()

            if not riwayat:
                print("Belum ada transaksi pada akun ini.")
            else:
                for trx in riwayat:
                    print(trx)

        elif pilihan == "0":
            print("\nTerima kasih telah menggunakan aplikasi Dompet Digital!\n")
            break

        else:
            print(">> Pilihan tidak valid, silakan coba lagi.")


if __name__ == "__main__":
    main()
