from datetime import datetime
import uuid # import library uuid guna menghasilkan nomor transaksi unik
from typing import List


# Custom exception untuk menangani error jika saldo tidak cukup (Fitur 4)
class InsufficientFundsException(Exception):
    def __init__(self, message: str = "Saldo tidak mencukupi."):
        # Memanggil constructor milik class induk (Exception)
        super().__init__(message)


# Custom exception untuk menangani error jika transfer melebihi limit harian (Fitur 4)
class TransferLimitException(Exception):
    def __init__(self, message: str = "Melebihi limit transfer harian."):
        # Memanggil constructor milik class induk (Exception)
        super().__init__(message)


class Transaction:
    def __init__(
        self,
        transaction_type: str,
        amount: float,
        description: str = "",
        reference_info: str = "",
        transaction_id: str = None
    ):
        # Prefix '__' membuat atribut menjadi private agar datanya terlindungi (enkapsulasi)
        self.__transaction_id = transaction_id or f"TRX-{uuid.uuid4().hex[:8].upper()}"
        self.__transaction_type = transaction_type.upper()
        self.__amount = float(amount)
        self.__description = description
        self.__reference_info = reference_info
        self.__timestamp = datetime.now()

    # @property berfungsi sebagai 'getter' agar atribut private bisa dibaca dari luar
    @property
    def transaction_id(self) -> str:
        return self.__transaction_id

    @property
    def transaction_type(self) -> str:
        return self.__transaction_type

    @property
    def amount(self) -> float:
        return self.__amount

    @property
    def description(self) -> str:
        return self.__description

    @property
    def reference_info(self) -> str:
        return self.__reference_info

    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    # Mengubah objek transaksi menjadi dictionary agar mudah dikelola atau diekspor
    def to_dict(self) -> dict:
        return {
            "id": self.__transaction_id,
            "type": self.__transaction_type,
            "amount": self.__amount,
            "description": self.__description,
            "reference": self.__reference_info,
            "timestamp": self.__timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

    # Format tampilan saat objek transaksi dicetak (misal: di terminal)
    def __str__(self) -> str:
        waktu = self.__timestamp.strftime("%d/%m/%Y %H:%M")
        tanda = "+" if self.__transaction_type in ("CREDIT", "TOPUP", "TRANSFER_IN") else "-"
        ref = f" [{self.__reference_info}]" if self.__reference_info else ""
        return f"[{waktu}] {self.__transaction_id} | {self.__transaction_type} | {tanda}Rp {self.__amount:,.2f} | {self.__description}{ref}"


class Wallet:
    def __init__(self, initial_balance: float = 0.0, daily_limit: float = 5000000.0):
        # Saldo awal default 0 (Fitur 1)
        self.__balance = float(initial_balance)
        self.__daily_limit = float(daily_limit)
        # Menampung total nominal yang sudah ditransfer pada hari ini
        self.__daily_transferred = 0.0
        # List untuk menyimpan riwayat transaksi (Fitur 6)
        self.__transactions: List[Transaction] = []

    def get_balance(self) -> float:
        return self.__balance

    def get_daily_limit(self) -> float:
        return self.__daily_limit

    def get_remaining_daily_limit(self) -> float:
        # Menghitung sisa kuota transfer harian yang masih tersedia
        return max(0.0, self.__daily_limit - self.__daily_transferred)

    # Validasi limit transfer harian sebelum melakukan pengiriman dana (Fitur 3 & 4)
    def check_and_track_transfer_limit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Nominal transfer harus lebih besar dari 0.")

        # Jika akumulasi transfer hari ini + transfer baru melebihi batas limit
        if self.__daily_transferred + amount > self.__daily_limit:
            sisa = self.get_remaining_daily_limit()
            raise TransferLimitException(
                f"Transfer Rp {amount:,.2f} melebihi limit harian (Sisa: Rp {sisa:,.2f})."
            )

        # Catat penambahan transfer harian jika masih dalam batas limit
        self.__daily_transferred += amount

    # Menambahkan saldo ke wallet dan otomatis mencatat ke riwayat transaksi
    def credit(
        self,
        amount: float,
        description: str = "Pemasukan dana",
        reference_info: str = "",
        tx_type: str = "CREDIT"
    ) -> Transaction:
        if amount <= 0:
            raise ValueError("Nominal harus lebih besar dari 0.")

        self.__balance += amount
        trx = Transaction(tx_type, amount, description, reference_info)
        self.__transactions.append(trx)
        return trx

    # Mengurangi saldo wallet dan melempar error jika saldo tidak cukup (Fitur 4 & 5)
    def debit(
        self,
        amount: float,
        description: str = "Pengeluaran dana",
        reference_info: str = "",
        tx_type: str = "DEBIT"
    ) -> Transaction:
        if amount <= 0:
            raise ValueError("Nominal harus lebih besar dari 0.")

        # Cek apakah saldo mencukupi
        if self.__balance < amount:
            raise InsufficientFundsException(
                f"Saldo tidak cukup (Saldo: Rp {self.__balance:,.2f}, Dibutuhkan: Rp {amount:,.2f})."
            )

        self.__balance -= amount
        trx = Transaction(tx_type, amount, description, reference_info)
        self.__transactions.append(trx)
        return trx

    # Digunakan untuk reset batasan harian ketika berganti hari
    def reset_daily_limit(self) -> None:
        self.__daily_transferred = 0.0

    # Mengembalikan salinan list riwayat transaksi (Fitur 6)
    def get_transaction_history(self) -> List[Transaction]:
        return list(self.__transactions)


class User:
    def __init__(self, user_id: str, name: str, phone_number: str, email: str = ""):
        self.__user_id = user_id
        self.__name = name
        self.__phone_number = phone_number
        self.__email = email
        # Setiap user baru otomatis dibuatkan wallet pribadi bersaldo 0 (Fitur 1)
        self.__wallet = Wallet(initial_balance=0.0)

    @property
    def user_id(self) -> str:
        return self.__user_id

    @property
    def name(self) -> str:
        return self.__name

    # Setter untuk memvalidasi perubahan nama agar tidak kosong
    @name.setter
    def name(self, new_name: str) -> None:
        if not new_name.strip():
            raise ValueError("Nama tidak boleh kosong.")
        self.__name = new_name.strip()

    @property
    def phone_number(self) -> str:
        return self.__phone_number

    @property
    def email(self) -> str:
        return self.__email

    @property
    def wallet(self) -> Wallet:
        return self.__wallet

    def to_dict(self) -> dict:
        return {
            "user_id": self.__user_id,
            "name": self.__name,
            "phone_number": self.__phone_number,
            "email": self.__email,
            "balance": self.__wallet.get_balance()
        }

    def __str__(self) -> str:
        return f"User({self.__user_id} - {self.__name} | Saldo: Rp {self.__wallet.get_balance():,.2f})"
