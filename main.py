"""
Main Program - Antarmuka CLI Dompet Digital & Split Bill
Menjalankan dan menguji fitur fondasi awal (User, Wallet, Exception, Riwayat).
"""

from models import (
    User,
    InsufficientFundsException,
    TransferLimitException,
    BillType,
    BillPaymentService,
    TransferService,
    find_payment_method,
    get_payment_methods
)


def print_header(title: str) -> None:
    print("\n" + "=" * 45)
    print(f"  {title.upper()}")
    print("=" * 45)


def main():
    # Penyimpanan data sementara pengguna
    users = {}

    # Buat 4 akun contoh untuk mempermudah uji coba langsung
    user1 = User("USR-01", "Budi Santoso", "081211112222", "budi@email.com")
    user2 = User("USR-02", "Siti Rahma", "081233334444", "siti@email.com")
    user3 = User("USR-03", "Andi Wijaya", "081255556666", "andi@email.com")
    user4 = User("USR-04", "Dewi Lestari", "081277778888", "dewi@email.com")
    users[user1.user_id] = user1
    users[user2.user_id] = user2
    users[user3.user_id] = user3
    users[user4.user_id] = user4

    # Akun pengguna yang sedang aktif saat ini
    active_user = user1

    # Layanan Langkah 2: transfer antar user & pembayaran tagihan
    transfer_service = TransferService(users)
    bill_service = BillPaymentService()

    while True:
        print_header("Aplikasi Dompet Digital (Fintech CLI)")
        print(f"Pengguna Aktif: {active_user.name} ({active_user.user_id})")
        print(f"Saldo Saat Ini : Rp {active_user.wallet.get_balance():,.2f}")
        print(f"Sisa Limit Harian: Rp {active_user.wallet.get_remaining_daily_limit():,.2f}")
        print("-" * 45)
        print("1. Registrasi Pengguna Baru") # fitur 1
        print("2. Ganti Pengguna Aktif")
        print("3. Top-Up via Metode Pembayaran (Polymorphism)")
        print("4. Transfer Antar User (Limit Harian)")
        print("5. Bayar Tagihan Listrik/Air/Internet")
        print("6. Tarik Tunai / Pengeluaran")
        print("7. Lihat Riwayat Transaksi") # fitur 6
        print("0. Keluar")
        print("-" * 45)

        pilihan = input("Pilih menu (0-7): ").strip()

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

        elif pilihan == "6":
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

        elif pilihan == "7":
            # Fitur 6: Menampilkan riwayat transaksi
            print_header(f"Riwayat Transaksi: {active_user.name}")
            riwayat = active_user.wallet.get_transaction_history()

            if not riwayat:
                print("Belum ada transaksi pada akun ini.")
            else:
                for trx in riwayat:
                    print(trx)

        elif pilihan == "3":
            # Fitur 2: Top-up saldo lewat berbagai metode pembayaran (Polymorphism)
            print_header("Top-Up Saldo via Metode Pembayaran")
            daftar_metode = get_payment_methods()
            print("Metode pembayaran yang tersedia:")
            for nomor, metode in enumerate(daftar_metode, start=1):
                print(f"  {nomor}. {metode}")
            print("-" * 45)
            print("Pilih dengan ANGKA (1-4) atau ketik ID metode (contoh: PM-BANK)")

            try:
                pilihan_metode = input("Pilih metode pembayaran: ").strip()

                # Terima input berupa angka urutan maupun ID metode
                if pilihan_metode.isdigit():
                    indeks = int(pilihan_metode) - 1
                    if indeks < 0 or indeks >= len(daftar_metode):
                        raise ValueError(f"Pilihan '{pilihan_metode}' tidak ada dalam daftar metode.")
                    metode_dipilih = daftar_metode[indeks]
                else:
                    metode_dipilih = find_payment_method(pilihan_metode)

                nominal = float(input(f"Masukkan nominal top-up ({metode_dipilih.name}): Rp "))
                trx = metode_dipilih.top_up(active_user.wallet, nominal)

                print(f">> Top-up BERHASIL via {metode_dipilih.name}!")
                print(f">> Biaya admin : Rp {metode_dipilih.calculate_admin_fee(nominal):,.2f}")
                print(f">> Saldo masuk : Rp {trx.amount:,.2f}")
                print(f">> Saldo wallet sekarang: Rp {active_user.wallet.get_balance():,.2f}")
            except ValueError as e:
                print(f">> [Error]: {e}")

        elif pilihan == "4":
            # Fitur 3: Transfer antar pengguna memakai TransferService
            print_header("Transfer Antar Pengguna (Layanan Transfer)")
            tujuan_id = input("Masukkan User ID penerima: ").strip().upper()

            try:
                penerima = transfer_service.find_user(tujuan_id)

                if penerima.user_id == active_user.user_id:
                    raise ValueError("Tidak bisa transfer ke akun sendiri!")

                nominal = float(input(f"Masukkan nominal transfer ke {penerima.name}: Rp "))
                trx = transfer_service.transfer(active_user, penerima, nominal)

                print(f">> Transfer Rp {nominal:,.2f} ke {penerima.name} BERHASIL!")
                print(f">> ID Transaksi: {trx.transaction_id}")
                print(f">> Sisa limit harian Anda: Rp {active_user.wallet.get_remaining_daily_limit():,.2f}")
            except ValueError as e:
                print(f">> [Error]: {e}")
            except TransferLimitException as e:
                print(f">> [GAGAL - TransferLimitException]: {e}")
            except InsufficientFundsException as e:
                print(f">> [GAGAL - InsufficientFundsException]: {e}")

        elif pilihan == "5":
            # Fitur 5: Bayar tagihan listrik, air, dan internet
            print_header("Bayar Tagihan (Listrik / Air / Internet)")
            print("Jenis tagihan yang tersedia:")
            for nomor, tipe in enumerate(bill_service.get_bill_types(), start=1):
                print(f"  {nomor}. {tipe.label}  [{tipe.name}]")
            print("-" * 45)

            try:
                pilih_tipe = input("Pilih jenis tagihan (angka/nama): ").strip()

                if pilih_tipe.isdigit():
                    tipe = bill_service.get_bill_types()[int(pilih_tipe) - 1]
                else:
                    tipe = BillType[pilih_tipe.upper()]

                no_pelanggan = input("Masukkan nomor pelanggan : ").strip()
                nama_pelanggan = input("Masukkan nama pelanggan  : ").strip()
                nominal = float(input("Masukkan nominal tagihan : Rp "))
                periode = input("Masukkan periode (opsional): ").strip()

                tagihan = bill_service.create_bill(tipe, no_pelanggan, nama_pelanggan, nominal, periode)
                print("\n" + str(tagihan))

                konfirmasi = input("Lanjutkan pembayaran? (y/n): ").strip().lower()
                if konfirmasi != "y":
                    print(">> Pembayaran dibatalkan.")
                    continue

                trx = bill_service.pay_bill(active_user, tagihan)
                print(f">> Pembayaran {tipe.label} BERHASIL! (ID: {trx.transaction_id})")
                print(f">> Sisa saldo: Rp {active_user.wallet.get_balance():,.2f}")
            except (ValueError, KeyError, IndexError) as e:
                print(f">> [Error]: Input tidak valid atau jenis tagihan tidak dikenal! ({e})")
            except InsufficientFundsException as e:
                print(f">> [GAGAL - InsufficientFundsException]: {e}")

        elif pilihan == "0":
            print("\nTerima kasih telah menggunakan aplikasi Dompet Digital!\n")
            break

        else:
            print(">> Pilihan tidak valid, silakan coba lagi.")


if __name__ == "__main__":
    main()
