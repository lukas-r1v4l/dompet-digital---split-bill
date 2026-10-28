from datetime import datetime
import uuid # import library uuid guna menghasilkan nomor transaksi unik
from typing import List

# Import tambahan khusus Langkah 2 (Polymorphism / ABC & Enumeration)
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict


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

class PaymentMethod(ABC):
    """
    Abstract Base Class untuk semua metode pembayaran yang dipakai saat top-up saldo.

    Setiap kelas turunan WAJIB meng-override method `process_payment()`
    sehingga perilaku tiap channel pembayaran bisa berbeda-beda (Polymorphism).
    """

    def __init__(self, method_id: str, name: str, admin_fee_percent: float = 0.0):
        self._method_id = method_id
        self._name = name
        # Disimpan sebagai rasio (0.7% -> 0.007) agar perhitungan lebih mudah
        self._admin_fee_percent = float(admin_fee_percent) / 100.0

    @property
    def method_id(self) -> str:
        return self._method_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def admin_fee_percent(self) -> float:
        """Biaya admin dalam persen (contoh: 0.7 berarti 0.7%)."""
        return self._admin_fee_percent * 100.0

    # Biaya admin juga bisa di-override (contoh: biaya flat untuk gerai retail)
    def calculate_admin_fee(self, amount: float) -> float:
        return float(amount) * self._admin_fee_percent

    # Validasi nominal bisa di-override sesuai aturan masing-masing metode
    def validate_amount(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Nominal top-up harus lebih besar dari 0.")

    @abstractmethod
    def process_payment(self, amount: float) -> dict:
        """
        Mensimulasikan proses pembayaran ke channel masing-masing.
        Mengembalikan dictionary berisi informasi channel (referensi/pesan).
        """

    def top_up(self, wallet: Wallet, amount: float) -> Transaction:
        """
        Alur top-up saldo (template method):
        1. Validasi nominal sesuai aturan metode pembayaran.
        2. Hitung biaya admin.
        3. Proses pembayaran ke channel (Polymorphism).
        4. Kreditkan saldo bersih ke wallet pengguna.
        """
        self.validate_amount(amount)

        admin_fee = self.calculate_admin_fee(amount)
        net_amount = float(amount) - admin_fee
        if net_amount <= 0:
            raise ValueError("Nominal top-up terlalu kecil untuk menutup biaya admin.")

        channel_info = self.process_payment(amount)

        return wallet.credit(
            net_amount,
            description=f"Top-Up via {self._name}",
            reference_info=f"{channel_info.get('reference', '-')} | Biaya admin: Rp {admin_fee:,.2f}",
            tx_type="TOPUP"
        )

    def __str__(self) -> str:
        return f"[{self._method_id}] {self._name} (Admin fee {self.admin_fee_percent:.2f}%)"


class BankTransfer(PaymentMethod):
    """Top-up melalui transfer bank / Virtual Account."""

    MIN_AMOUNT = 10000.0

    def __init__(
        self,
        method_id: str = "PM-BANK",
        name: str = "Transfer Bank (Virtual Account)",
        admin_fee_percent: float = 0.0
    ):
        super().__init__(method_id, name, admin_fee_percent)
        self.__virtual_account = f"8808{uuid.uuid4().hex[:8].upper()}"

    @property
    def virtual_account(self) -> str:
        return self.__virtual_account

    def validate_amount(self, amount: float) -> None:
        super().validate_amount(amount)
        if amount < self.MIN_AMOUNT:
            raise ValueError(f"Minimal top-up via Transfer Bank adalah Rp {self.MIN_AMOUNT:,.2f}.")

    def process_payment(self, amount: float) -> dict:
        return {
            "channel": "BANK_TRANSFER",
            "reference": f"VA {self.__virtual_account}",
            "message": f"Silakan transfer Rp {amount:,.2f} ke Virtual Account {self.__virtual_account}."
        }


class EWallet(PaymentMethod):
    """Top-up melalui e-wallet (GoPay / OVO / DANA)."""

    MAX_AMOUNT = 10000000.0

    def __init__(
        self,
        method_id: str = "PM-EWALLET",
        name: str = "E-Wallet (GoPay/OVO/DANA)",
        admin_fee_percent: float = 0.7
    ):
        super().__init__(method_id, name, admin_fee_percent)

    def validate_amount(self, amount: float) -> None:
        super().validate_amount(amount)
        if amount > self.MAX_AMOUNT:
            raise ValueError(f"Maksimal top-up via E-Wallet adalah Rp {self.MAX_AMOUNT:,.2f} per transaksi.")

    def process_payment(self, amount: float) -> dict:
        return {
            "channel": "E_WALLET",
            "reference": f"EW-{uuid.uuid4().hex[:8].upper()}",
            "message": f"Permintaan top-up Rp {amount:,.2f} dikirim ke aplikasi e-wallet Anda."
        }


class CreditCard(PaymentMethod):
    """Top-up melalui kartu kredit / debit."""

    MIN_AMOUNT = 50000.0
    MAX_AMOUNT = 25000000.0

    def __init__(
        self,
        method_id: str = "PM-CARD",
        name: str = "Kartu Kredit / Debit",
        admin_fee_percent: float = 2.5
    ):
        super().__init__(method_id, name, admin_fee_percent)

    def validate_amount(self, amount: float) -> None:
        super().validate_amount(amount)
        if amount < self.MIN_AMOUNT:
            raise ValueError(f"Minimal top-up via Kartu adalah Rp {self.MIN_AMOUNT:,.2f}.")
        if amount > self.MAX_AMOUNT:
            raise ValueError(f"Maksimal top-up via Kartu adalah Rp {self.MAX_AMOUNT:,.2f} per transaksi.")

    def process_payment(self, amount: float) -> dict:
        return {
            "channel": "CARD",
            "reference": f"CC-{uuid.uuid4().hex[:8].upper()}",
            "message": f"Otorisasi pembayaran Rp {amount:,.2f} pada kartu berhasil."
        }


class RetailOutlet(PaymentMethod):
    """Top-up melalui gerai retail (Alfamart / Indomaret)."""

    MAX_AMOUNT = 5000000.0
    ADMIN_FEE_FLAT = 2500.0

    def __init__(
        self,
        method_id: str = "PM-RETAIL",
        name: str = "Gerai Retail (Alfamart/Indomaret)",
        admin_fee_percent: float = 0.0
    ):
        super().__init__(method_id, name, admin_fee_percent)

    # Gerai retail memakai biaya flat, bukan persentase (Polymorphism)
    def calculate_admin_fee(self, amount: float) -> float:
        return self.ADMIN_FEE_FLAT

    def validate_amount(self, amount: float) -> None:
        super().validate_amount(amount)
        if amount > self.MAX_AMOUNT:
            raise ValueError(f"Maksimal top-up via Gerai Retail adalah Rp {self.MAX_AMOUNT:,.2f} per transaksi.")

    def process_payment(self, amount: float) -> dict:
        return {
            "channel": "RETAIL",
            "reference": f"RT-{uuid.uuid4().hex[:8].upper()}",
            "message": f"Tunjukkan kode pembayaran ke kasir untuk membayar Rp {amount:,.2f}."
        }


def get_payment_methods() -> List[PaymentMethod]:
    """Daftar metode pembayaran yang tersedia untuk top-up (Fitur 2)."""
    return [BankTransfer(), EWallet(), CreditCard(), RetailOutlet()]


def find_payment_method(method_id: str) -> PaymentMethod:
    """Mencari metode pembayaran berdasarkan ID-nya."""
    dicari = (method_id or "").strip().upper()
    for metode in get_payment_methods():
        if metode.method_id.upper() == dicari:
            return metode
    raise ValueError(f"Metode pembayaran '{method_id}' tidak tersedia.")


# --- FITUR 5: Enumeration Jenis Tagihan & ABC Bill --------------------

class BillType(Enum):
    """Enumerasi kategori tagihan yang dapat dibayarkan (Fitur 5)."""

    LISTRIK = "LISTRIK"
    AIR = "AIR"
    INTERNET = "INTERNET"

    @property
    def label(self) -> str:
        labels = {
            BillType.LISTRIK: "Tagihan Listrik (PLN)",
            BillType.AIR: "Tagihan Air (PDAM)",
            BillType.INTERNET: "Tagihan Internet / TV Kabel",
        }
        return labels[self]


class Bill(ABC):
    """
    Kelas abstrak untuk tagihan yang bisa dibayar menggunakan saldo wallet.

    Kelas konkrit (Listrik/Air/Internet) meng-override `get_admin_fee()`
    dan `get_description()` sehingga tiap tagihan punya aturan sendiri (Polymorphism).
    """

    def __init__(
        self,
        bill_type: BillType,
        customer_number: str,
        customer_name: str,
        amount: float,
        period: str = ""
    ):
        self.__bill_id = f"BILL-{uuid.uuid4().hex[:8].upper()}"
        self.__bill_type = bill_type
        self.__customer_number = customer_number.strip()
        self.__customer_name = customer_name.strip()
        self.__amount = float(amount)
        self.__period = period.strip()
        self.__is_paid = False

    @property
    def bill_id(self) -> str:
        return self.__bill_id

    @property
    def bill_type(self) -> BillType:
        return self.__bill_type

    @property
    def customer_number(self) -> str:
        return self.__customer_number

    @property
    def customer_name(self) -> str:
        return self.__customer_name

    @property
    def amount(self) -> float:
        return self.__amount

    @property
    def period(self) -> str:
        return self.__period

    @property
    def is_paid(self) -> bool:
        return self.__is_paid

    @abstractmethod
    def get_admin_fee(self) -> float:
        """Biaya admin pembayaran tagihan (berbeda untuk tiap jenis tagihan)."""

    @abstractmethod
    def get_description(self) -> str:
        """Keterangan tagihan yang akan tercatat di riwayat transaksi."""

    @property
    def total_amount(self) -> float:
        """Total yang harus dibayar = nominal tagihan + biaya admin."""
        return self.__amount + self.get_admin_fee()

    def mark_as_paid(self) -> None:
        self.__is_paid = True

    def to_dict(self) -> dict:
        return {
            "bill_id": self.__bill_id,
            "type": self.__bill_type.label,
            "customer_number": self.__customer_number,
            "customer_name": self.__customer_name,
            "amount": self.__amount,
            "admin_fee": self.get_admin_fee(),
            "total": self.total_amount,
            "period": self.__period,
            "is_paid": self.__is_paid
        }

    def __str__(self) -> str:
        status = "LUNAS" if self.__is_paid else "BELUM LUNAS"
        periode = f" | Periode: {self.__period}" if self.__period else ""
        return (
            f"{self.__bill_id} | {self.__bill_type.label} | No. {self.__customer_number} "
            f"({self.__customer_name}){periode} | Tagihan: Rp {self.__amount:,.2f} | "
            f"Admin: Rp {self.get_admin_fee():,.2f} | Total: Rp {self.total_amount:,.2f} | {status}"
        )


class ElectricityBill(Bill):
    """Tagihan listrik prabayar/pascabayar (PLN)."""

    ADMIN_FEE = 2500.0

    def __init__(self, customer_number: str, customer_name: str, amount: float, period: str = ""):
        super().__init__(BillType.LISTRIK, customer_number, customer_name, amount, period)

    def get_admin_fee(self) -> float:
        return self.ADMIN_FEE

    def get_description(self) -> str:
        periode = f" periode {self.period}" if self.period else ""
        return f"Bayar Tagihan Listrik {self.customer_number}{periode}"


class WaterBill(Bill):
    """Tagihan air bersih (PDAM)."""

    ADMIN_FEE = 1500.0

    def __init__(self, customer_number: str, customer_name: str, amount: float, period: str = ""):
        super().__init__(BillType.AIR, customer_number, customer_name, amount, period)

    def get_admin_fee(self) -> float:
        return self.ADMIN_FEE

    def get_description(self) -> str:
        periode = f" periode {self.period}" if self.period else ""
        return f"Bayar Tagihan Air {self.customer_number}{periode}"


class InternetBill(Bill):
    """Tagihan internet / TV kabel."""

    ADMIN_FEE_PERCENT = 1.0

    def __init__(self, customer_number: str, customer_name: str, amount: float, period: str = ""):
        super().__init__(BillType.INTERNET, customer_number, customer_name, amount, period)

    # Biaya admin internet dihitung persentase dari nominal tagihan (Polymorphism)
    def get_admin_fee(self) -> float:
        return self.amount * (self.ADMIN_FEE_PERCENT / 100.0)

    def get_description(self) -> str:
        periode = f" periode {self.period}" if self.period else ""
        return f"Bayar Tagihan Internet {self.customer_number}{periode}"


# --- LAYANAN: Transfer Antar User & Pembayaran Tagihan ----------------

class TransferService:
    """
    Layanan transfer antar user dengan validasi limit harian (Fitur 3).
    Menggabungkan validasi TransferLimitException & InsufficientFundsException.
    """

    def __init__(self, users: Dict[str, User]):
        self._users = dict(users)

    @property
    def users(self) -> Dict[str, User]:
        return dict(self._users)

    def find_user(self, user_id: str) -> User:
        dicari = (user_id or "").strip().upper()
        if dicari not in self._users:
            raise ValueError(f"Pengguna dengan ID '{user_id}' tidak ditemukan.")
        return self._users[dicari]

    def transfer(self, sender: User, receiver: User, amount: float) -> Transaction:
        if sender.user_id == receiver.user_id:
            raise ValueError("Tidak bisa transfer ke akun sendiri!")
        if amount <= 0:
            raise ValueError("Nominal transfer harus lebih besar dari 0.")

        # Cek saldo lebih dulu supaya limit harian tidak terpakai
        # ketika transfer akhirnya gagal karena saldo tidak cukup.
        if sender.wallet.get_balance() < amount:
            raise InsufficientFundsException(
                f"Saldo tidak cukup (Saldo: Rp {sender.wallet.get_balance():,.2f}, "
                f"Dibutuhkan: Rp {amount:,.2f})."
            )

        # Validasi limit transfer harian (melempar TransferLimitException)
        sender.wallet.check_and_track_transfer_limit(amount)

        trx_out = sender.wallet.debit(
            amount,
            description=f"Transfer ke {receiver.name}",
            reference_info=f"To: {receiver.user_id}",
            tx_type="TRANSFER_OUT"
        )
        receiver.wallet.credit(
            amount,
            description=f"Transfer dari {sender.name}",
            reference_info=f"From: {sender.user_id}",
            tx_type="TRANSFER_IN"
        )
        return trx_out


class BillPaymentService:
    """Layanan pembayaran tagihan listrik, air, dan internet (Fitur 5)."""

    # Mapping kategori tagihan ke kelas konkritnya (Polymorphism)
    BILL_CLASSES = {
        BillType.LISTRIK: ElectricityBill,
        BillType.AIR: WaterBill,
        BillType.INTERNET: InternetBill,
    }

    def get_bill_types(self) -> List[BillType]:
        return list(BillType)

    def create_bill(
        self,
        bill_type: BillType,
        customer_number: str,
        customer_name: str,
        amount: float,
        period: str = ""
    ) -> Bill:
        if bill_type not in self.BILL_CLASSES:
            raise ValueError(f"Jenis tagihan '{bill_type}' tidak dikenal.")
        if not customer_number.strip():
            raise ValueError("Nomor pelanggan wajib diisi.")
        if amount <= 0:
            raise ValueError("Nominal tagihan harus lebih besar dari 0.")

        bill_class = self.BILL_CLASSES[bill_type]
        return bill_class(customer_number, customer_name, amount, period)

    def pay_bill(self, user: User, bill: Bill) -> Transaction:
        if bill.is_paid:
            raise ValueError(f"Tagihan {bill.bill_id} sudah pernah dibayar.")

        # wallet.debit() akan melempar InsufficientFundsException jika saldo kurang
        trx = user.wallet.debit(
            bill.total_amount,
            description=bill.get_description(),
            reference_info=f"Bill: {bill.bill_id}",
            tx_type="BILL_PAYMENT"
        )
        bill.mark_as_paid()
        return trx

class GroupExpense:
    def __init__(
        self,
        title: str,
        amount: float,
        paid_by: User,
        participants: List[User],
        shares: Dict[str, float] = None,
        expense_id: str = None
    ):
        if not title or not title.strip():
            raise ValueError("Judul pengeluaran bersama tidak boleh kosong.")
        if float(amount) <= 0:
            raise ValueError("Nominal pengeluaran bersama harus lebih besar dari 0.")
        if not participants:
            raise ValueError("Peserta pengeluaran bersama tidak boleh kosong.")

        self.__expense_id = expense_id or f"EXP-{uuid.uuid4().hex[:6].upper()}"
        self.__title = title.strip()
        self.__amount = float(amount)
        self.__paid_by = paid_by
        self.__participants = list(participants)
        # Dictionary {user_id: nominal_bagian_masing_masing}
        self.__shares: Dict[str, float] = dict(shares) if shares else {}
        self.__timestamp = datetime.now()

    @property
    def expense_id(self) -> str:
        return self.__expense_id

    @property
    def title(self) -> str:
        return self.__title

    @property
    def amount(self) -> float:
        return self.__amount

    @property
    def paid_by(self) -> User:
        return self.__paid_by

    @property
    def participants(self) -> List[User]:
        return list(self.__participants)

    @property
    def shares(self) -> Dict[str, float]:
        return dict(self.__shares)

    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    def set_shares(self, shares: Dict[str, float]) -> None:
        self.__shares = dict(shares)

    def to_dict(self) -> dict:
        return {
            "expense_id": self.__expense_id,
            "title": self.__title,
            "amount": self.__amount,
            "paid_by": self.__paid_by.user_id,
            "paid_by_name": self.__paid_by.name,
            "participants": [u.user_id for u in self.__participants],
            "shares": dict(self.__shares),
            "timestamp": self.__timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

    def __str__(self) -> str:
        waktu = self.__timestamp.strftime("%d/%m/%Y %H:%M")
        per_orang = self.__amount / len(self.__participants) if self.__participants else 0.0
        return (
            f"[{waktu}] {self.__expense_id} | {self.__title} | "
            f"Total: Rp {self.__amount:,.2f} (Ditalangi oleh: {self.__paid_by.name}) | "
            f"Split Rata ({len(self.__participants)} anggota): Rp {per_orang:,.2f}/orang"
        )


class ExpenseIterator:
    def __init__(self, expenses: List[GroupExpense]):
        self._expenses = list(expenses)
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self) -> GroupExpense:
        if self._index >= len(self._expenses):
            raise StopIteration
        item = self._expenses[self._index]
        self._index += 1
        return item


class BaseGroup(ABC):
    def __init__(self, group_id: str, name: str, creator: User = None):
        if not name or not name.strip():
            raise ValueError("Nama grup tidak boleh kosong.")

        self._group_id = group_id.strip().upper()
        self._name = name.strip()
        # Menggunakan List untuk pengurutan anggota dan set untuk cek keunikan ID 
        self._members: List[User] = []
        self._member_ids: set = set()
        self._expenses: List[GroupExpense] = []
        # Dictionary bersarang {id_pengutang: {id_pemberi_pinjaman: nominal}}
        self._debt_matrix: Dict[str, Dict[str, float]] = {}

        if creator is not None:
            self.add_member(creator)

    @property
    def group_id(self) -> str:
        return self._group_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def members(self) -> List[User]:
        return list(self._members)

    @property
    def expenses(self) -> List[GroupExpense]:
        return list(self._expenses)

    # Memungkinkan objek grup diiterasi langsung dengan "for exp in group:"
    def __iter__(self):
        return ExpenseIterator(self._expenses)

    # Generator function dengan keyword "yield" untuk mengambil pengeluaran
    def iter_expenses(self):
        for exp in self._expenses:
            yield exp

    # Fitur 7 - Menambahkan anggota ke dalam grup
    def add_member(self, user: User) -> None:
        if not isinstance(user, User):
            raise TypeError("Anggota yang ditambahkan harus berupa objek User.")
        if user.user_id in self._member_ids:
            raise ValueError(f"{user.name} ({user.user_id}) sudah menjadi anggota grup '{self._name}'.")

        self._members.append(user)
        self._member_ids.add(user.user_id)
        self._debt_matrix[user.user_id] = {}

    def has_member(self, user_id: str) -> bool:
        return (user_id or "").strip().upper() in self._member_ids

    def get_member(self, user_id: str) -> User:
        dicari = (user_id or "").strip().upper()
        for member in self._members:
            if member.user_id.upper() == dicari:
                return member
        raise ValueError(f"Pengguna '{user_id}' bukan anggota grup '{self._name}'.")

    @abstractmethod
    def calculate_split(
        self,
        total_amount: float,
        participants: List[User] = None
    ) -> Dict[str, float]:
        pass

    def _record_debt(self, debtor_id: str, creditor_id: str, amount: float) -> None:
        if debtor_id == creditor_id or amount <= 0:
            return

        hutang_sebaliknya = self._debt_matrix.get(creditor_id, {}).get(debtor_id, 0.0)

        if hutang_sebaliknya > 0:
            if hutang_sebaliknya > amount:
                self._debt_matrix[creditor_id][debtor_id] = hutang_sebaliknya - amount
                return
            elif hutang_sebaliknya < amount:
                sisa = amount - hutang_sebaliknya
                self._debt_matrix[creditor_id][debtor_id] = 0.0
                self._debt_matrix.setdefault(debtor_id, {})
                self._debt_matrix[debtor_id][creditor_id] = (
                    self._debt_matrix[debtor_id].get(creditor_id, 0.0) + sisa
                )
                return
            else:
                self._debt_matrix[creditor_id][debtor_id] = 0.0
                return

        self._debt_matrix.setdefault(debtor_id, {})
        self._debt_matrix[debtor_id][creditor_id] = (
            self._debt_matrix[debtor_id].get(creditor_id, 0.0) + amount
        )

    # Fitur 8 dan 9 - Input pengeluaran bersama ke grup & otomatis hitung split rata
    def add_expense(
        self,
        payer: User,
        amount: float,
        title: str,
        participants: List[User] = None
    ) -> GroupExpense:
        if len(self._members) < 2:
            raise ValueError("Grup harus memiliki minimal 2 anggota sebelum mencatat pengeluaran.")
        if not self.has_member(payer.user_id):
            raise ValueError(f"Pembayar ({payer.name}) harus terdaftar sebagai anggota grup '{self._name}'.")
        if float(amount) <= 0:
            raise ValueError("Nominal pengeluaran harus lebih besar dari 0.")

        peserta = list(participants) if participants else list(self._members)
        for p in peserta:
            if not self.has_member(p.user_id):
                raise ValueError(f"Peserta ({p.name}) bukan anggota grup '{self._name}'.")

        # Mengitung pembagian tagihan secara polimorfik >> Fitur 9
        pembagian = self.calculate_split(float(amount), peserta)

        expense = GroupExpense(
            title=title,
            amount=float(amount),
            paid_by=payer,
            participants=peserta,
            shares=pembagian
        )
        self._expenses.append(expense)

        # Memperbarui posisi utang setiap anggota terhadap payer >> penalang dana
        for user_id, bagian in pembagian.items():
            if user_id != payer.user_id and bagian > 0:
                self._record_debt(debtor_id=user_id, creditor_id=payer.user_id, amount=bagian)

        return expense

    # Fitur 10 - Mengambil daftar siapa berutang ke siapa & berapa nominalnya
    def get_debt_relations(self) -> List[dict]:
        # Dictionary comprehension untuk memetakan user_id -> objek User
        peta_member = {m.user_id: m for m in self._members}
        daftar_utang = []

        for debtor_id, creditors in self._debt_matrix.items():
            for creditor_id, nominal in creditors.items():
                if nominal > 0.009:  # Mengabaikan selisih pembulatan di bawah 1 sen
                    daftar_utang.append({
                        "from_user": peta_member[debtor_id],
                        "to_user": peta_member[creditor_id],
                        "amount": round(nominal, 2)
                    })
        return daftar_utang

    # Fitur 10 - Menyusun teks ringkasan siapa berutang ke siapa & berapa nominalnya
    def format_debt_summary_cli(self) -> str:
        relasi_utang = self.get_debt_relations()
        if not relasi_utang:
            return "Tidak ada utang antar anggota di grup ini (Semua impas / lunas)."

        # Membuat list comprehension untuk menyusun baris teks CLI
        baris = [
            f"  {idx}. {item['from_user'].name} ({item['from_user'].user_id}) "
            f"berutang ke {item['to_user'].name} ({item['to_user'].user_id}) "
            f"sebesar Rp {item['amount']:,.2f}"
            for idx, item in enumerate(relasi_utang, start=1)
        ]
        return "\n".join(baris)

    # Fitur 10 - Menampilkan langsung siapa berutang ke siapa & berapa ke layar CLI
    def show_debt_summary(self) -> None:
        print(f"=== Ringkasan Utang Grup: {self._name} ({self._group_id}) ===")
        print(self.format_debt_summary_cli())

    def get_total_expenses(self) -> float:
        # Generator expression di dalam sum()
        return sum(exp.amount for exp in self._expenses)

    def __str__(self) -> str:
        nama_anggota = ", ".join([m.name for m in self._members]) or "Belum ada anggota"
        return (
            f"[{self._group_id}] {self._name} | "
            f"Anggota ({len(self._members)}): {nama_anggota} | "
            f"Total Pengeluaran: Rp {self.get_total_expenses():,.2f}"
        )


class Group(BaseGroup):
    def __init__(self, group_id: str, name: str, creator: User = None):
        # Memanggil constructor kelas induk (Materi P02 super().__init__)
        super().__init__(group_id, name, creator)

    # Override method abstrak calculate_split untuk pembagian rata (Fitur 9 - Polymorphism)
    def calculate_split(
        self,
        total_amount: float,
        participants: List[User] = None
    ) -> Dict[str, float]:
        peserta = list(participants) if participants else list(self._members)
        if not peserta:
            raise ValueError("Tidak ada anggota di dalam grup untuk membagi tagihan.")

        bagian_rata = round(float(total_amount) / len(peserta), 2)
        # Dictionary comprehension untuk membagi rata ke setiap peserta (Materi P06)
        return {u.user_id: bagian_rata for u in peserta}


# Berfungsi sebagai alias agar dapat kompatibel jika dipanggil sebagai EqualSplitGroup maupun Group
EqualSplitGroup = Group


class SplitBillService:
    def __init__(self, users: Dict[str, User]):
        self._users = users
        self._groups: Dict[str, Group] = {}

    @property
    def groups(self) -> List[Group]:
        return list(self._groups.values())

    def create_group(self, name: str, creator: User = None, initial_members: List[User] = None) -> Group:
        group_id = f"GRP-{len(self._groups) + 1:02d}"
        grup_baru = Group(group_id=group_id, name=name, creator=creator)

        if initial_members:
            for member in initial_members:
                if not grup_baru.has_member(member.user_id):
                    grup_baru.add_member(member)

        self._groups[group_id] = grup_baru
        return grup_baru

    def find_group(self, group_id: str) -> Group:
        dicari = (group_id or "").strip().upper()
        if dicari not in self._groups:
            raise ValueError(f"Grup dengan ID '{group_id}' tidak ditemukan.")
        return self._groups[dicari]

    def add_member_to_group(self, group_id: str, user_id: str) -> Group:
        grup = self.find_group(group_id)
        uid = (user_id or "").strip().upper()
        if uid not in self._users:
            raise ValueError(f"Pengguna dengan ID '{user_id}' tidak terdaftar di sistem.")

        grup.add_member(self._users[uid])
        return grup

    def add_group_expense(
        self,
        group_id: str,
        payer_id: str,
        amount: float,
        title: str
    ) -> GroupExpense:
        grup = self.find_group(group_id)
        pembayar = grup.get_member(payer_id)
        return grup.add_expense(payer=pembayar, amount=amount, title=title)

    def get_group_debt_summary(self, group_id: str) -> str:
        grup = self.find_group(group_id)
        return grup.format_debt_summary_cli()