import json
import os
import uuid
from datetime import datetime, timezone

# Data awal kosong/default
data = {
    "selected_wallet": None,
    "wallets": {}
}

DATA_FILE = "data.json"

# Dictionary pemetaan penerjemahan kategori
CATEGORY_MAP = {
    "food": "Makanan & Minuman",
    "transportation": "Transportasi",
    "tool": "Alat & Perlengkapan",
    "income": "Pemasukan",
    "etc": "Lain-lain"
}

def translate_category(cat_key):
    return CATEGORY_MAP.get(cat_key.lower(), cat_key.capitalize())

def format_rupiah(nominal):
    return f"Rp {nominal:,.0f}".replace(",", ".")

def save_data(filename=DATA_FILE, silent=True):
    """Menyimpan seluruh state data ke file JSON."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        if not silent:
            print(f"✅ Data berhasil disimpan ke '{filename}'!")
    except Exception as e:
        print(f"❌ Gagal menyimpan data: {e}")

def load_data(filename=DATA_FILE, silent=False):
    """Memuat data dari file JSON."""
    global data
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                data = loaded_data
            if not silent:
                print(f"✅ Data berhasil dimuat dari '{filename}'!")
        except Exception as e:
            if not silent:
                print(f"❌ Gagal membaca file '{filename}': {e}")
    else:
        if not silent:
            print(f"⚠ File '{filename}' tidak ditemukan.")

def get_active_wallet():
    selected_id = data.get('selected_wallet')
    if selected_id and selected_id in data['wallets']:
        return data['wallets'][selected_id]
    return None

def buat_wallet_baru(nama_wallet=None):
    """Fungsi pembantu untuk membuat wallet baru dilengkapi saldo awal."""
    if not nama_wallet:
        print("\n--- Buat Pembukuan (Wallet) Baru ---")
        nama_wallet = input("Masukkan nama wallet baru (misal: Dompet Utama, Tabungan): ").strip()
    
    if not nama_wallet:
        print("❌ Nama wallet tidak boleh kosong!")
        return None

    new_id = str(uuid.uuid4())
    records = []

    # Opsi memasukkan saldo awal
    print("\n💡 Disarankan mengisi saldo awal untuk pembukuan baru.")
    saldo_input = input("Masukkan saldo awal (tekan Enter jika Rp 0): ").strip()
    
    if saldo_input:
        try:
            saldo_awal = float(saldo_input)
            if saldo_awal > 0:
                initial_record = {
                    "id": str(uuid.uuid4()),
                    "name": "Setoran Awal Wallet",
                    "type": "income",
                    "category": "income",
                    "amount": saldo_awal,
                    "datetime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                }
                records.append(initial_record)
                print(f"💵 Saldo awal sebesar {format_rupiah(saldo_awal)} telah dicatat.")
        except ValueError:
            print("⚠️ Input saldo awal tidak valid, saldo diawali dengan Rp 0.")

    data['wallets'][new_id] = {
        "name": nama_wallet,
        "records": records
    }
    
    # Otomatis pilih wallet ini jika belum ada wallet aktif
    if not data.get('selected_wallet') or data['selected_wallet'] not in data['wallets']:
        data['selected_wallet'] = new_id

    # Auto-save setelah buat wallet
    save_data()
    print(f"✅ Wallet '{nama_wallet}' berhasil dibuat dan disimpan!")
    return new_id

def cek_dan_buat_wallet_awal():
    """Memastikan minimal ada 1 wallet saat aplikasi berjalan."""
    if not data['wallets']:
        print("===========================================")
        print(" Selamat Datang di Aplikasi Duit.Gue!")
        print("===========================================")
        print("Belum ada pembukuan (wallet) yang terdaftar.")
        print("Silakan buat wallet pertama Anda untuk memulai.\n")
        
        while not data['wallets']:
            buat_wallet_baru()

def tambah_wallet():
    buat_wallet_baru()

def hapus_wallet():
    if not data['wallets']:
        print("\n❌ Tidak ada wallet untuk dihapus.")
        return

    print("\n--- Hapus Pembukuan (Wallet) ---")
    print("Daftar Wallet:")
    wallet_list = list(data['wallets'].items())
    for idx, (w_id, w_data) in enumerate(wallet_list, start=1):
        status = "(Aktif)" if w_id == data['selected_wallet'] else ""
        print(f"[{idx}] {w_data['name']} {status}")

    try:
        pilihan = int(input("\nPilih nomor wallet yang ingin dihapus (0 untuk batal): "))
        if pilihan == 0:
            return
        if 1 <= pilihan <= len(wallet_list):
            target_id, target_data = wallet_list[pilihan - 1]
            konfirmasi = input(f"⚠️ Yakin ingin menghapus wallet '{target_data['name']}'? (y/n): ").strip().lower()
            if konfirmasi == 'y':
                del data['wallets'][target_id]
                
                # Jika wallet yang dihapus sedang aktif, atur ke wallet lain atau buat baru
                if data['selected_wallet'] == target_id:
                    if data['wallets']:
                        data['selected_wallet'] = list(data['wallets'].keys())[0]
                        print(f"🔄 Wallet aktif diubah ke '{data['wallets'][data['selected_wallet']]['name']}'.")
                    else:
                        data['selected_wallet'] = None
                        
                # Auto-save setelah hapus wallet
                save_data()
                print(f"✅ Wallet '{target_data['name']}' berhasil dihapus.")
                
                if not data['wallets']:
                    cek_dan_buat_wallet_awal()
        else:
            print("❌ Pilihan nomor tidak valid.")
    except ValueError:
        print("❌ Input harus berupa angka.")

def ganti_wallet_aktif():
    if not data['wallets']:
        return

    print("\n--- Pilih / Ganti Wallet Aktif ---")
    wallet_list = list(data['wallets'].items())
    for idx, (w_id, w_data) in enumerate(wallet_list, start=1):
        status = "(Aktif)" if w_id == data['selected_wallet'] else ""
        print(f"[{idx}] {w_data['name']} {status}")

    try:
        pilihan = int(input("\nPilih nomor wallet: "))
        if 1 <= pilihan <= len(wallet_list):
            selected_id, selected_data = wallet_list[pilihan - 1]
            data['selected_wallet'] = selected_id
            # Auto-save pilihan wallet aktif
            save_data()
            print(f"✅ Wallet aktif diubah menjadi '{selected_data['name']}'!")
        else:
            print("❌ Pilihan tidak valid.")
    except ValueError:
        print("❌ Input harus berupa angka.")

def ekspor_wallet():
    active_wallet = get_active_wallet()
    if not active_wallet:
        print("\n❌ Wallet aktif tidak ditemukan!")
        return

    print("\n--- Ekspor Wallet ---")
    filename_default = f"wallet_{active_wallet['name'].lower().replace(' ', '_')}.json"
    filename = input(f"Masukkan nama file ekspor [{filename_default}]: ").strip()
    if not filename:
        filename = filename_default

    if not filename.endswith('.json'):
        filename += '.json'

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(active_wallet, f, indent=4, ensure_ascii=False)
        print(f"✅ Wallet '{active_wallet['name']}' berhasil diekspor ke '{filename}'!")
    except Exception as e:
        print(f"❌ Gagal mengekspor wallet: {e}")

def impor_wallet():
    print("\n--- Impor Wallet ---")
    filename = input("Masukkan nama file JSON wallet yang ingin diimpor: ").strip()

    if not os.path.exists(filename):
        print(f"❌ File '{filename}' tidak ditemukan!")
        return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            wallet_data = json.load(f)

        if "name" not in wallet_data or "records" not in wallet_data:
            print("❌ Format file JSON wallet tidak valid! Harus memiliki key 'name' dan 'records'.")
            return

        new_wallet_id = str(uuid.uuid4())
        data['wallets'][new_wallet_id] = wallet_data

        print(f"✅ Wallet '{wallet_data['name']}' berhasil diimpor!")
        
        pilih = input("Jadikan wallet ini sebagai wallet aktif? (y/n): ").strip().lower()
        if pilih == 'y':
            data['selected_wallet'] = new_wallet_id
            print(f"✅ Wallet aktif diubah ke '{wallet_data['name']}'.")

        # Auto-save setelah impor
        save_data()

    except Exception as e:
        print(f"❌ Gagal mengimpor wallet: {e}")

def tambah_transaksi(record_type):
    active_wallet = get_active_wallet()
    if not active_wallet:
        print("\n❌ Wallet aktif tidak ditemukan!")
        return

    label = "Pemasukan" if record_type == "income" else "Pengeluaran"
    print(f"\n--- Tambah {label} ---")
    name = input("Masukkan nama transaksi : ").strip()
    
    if not name:
        print("❌ Nama transaksi tidak boleh kosong!")
        return

    try:
        amount = float(input("Masukkan jumlah nominal : "))
        if amount <= 0:
            print("❌ Nominal harus lebih besar dari 0!")
            return
    except ValueError:
        print("❌ Input nominal harus berupa angka!")
        return

    if record_type == "income":
        category = "income"
    else:
        print("\nPilih Kategori Pengeluaran:")
        print("[1] Makanan & Minuman (food)")
        print("[2] Transportasi (transportation)")
        print("[3] Alat & Perlengkapan (tool)")
        print("[4] Lain-lain (etc)")
        pilihan = input("Pilihan kategori (1-4): ").strip()
        
        kat_map = {"1": "food", "2": "transportation", "3": "tool", "4": "etc"}
        category = kat_map.get(pilihan, "etc")

    new_record = {
        "id": str(uuid.uuid4()),
        "name": name,
        "type": record_type,
        "category": category,
        "amount": amount,
        "datetime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    active_wallet['records'].append(new_record)
    # Auto-save transaksi baru
    save_data()
    print(f"✅ {label} '{name}' sebesar {format_rupiah(amount)} berhasil ditambahkan!")

def hapus_transaksi():
    active_wallet = get_active_wallet()
    if not active_wallet:
        print("\n❌ Wallet aktif tidak ditemukan!")
        return

    records = active_wallet.get('records', [])
    if not records:
        print("\n❌ Belum ada transaksi untuk dihapus di wallet ini.")
        return

    print(f"\n--- Hapus Transaksi ({active_wallet['name']}) ---")
    for idx, rec in enumerate(records, start=1):
        simbol = "(+)" if rec['type'] == 'income' else "(-)"
        tanggal = rec['datetime'][:10]
        kategori_indo = translate_category(rec['category'])
        print(f"[{idx}] [{tanggal}] {simbol} {rec['name']} - {format_rupiah(rec['amount'])} ({kategori_indo})")

    try:
        pilihan = int(input("\nPilih nomor transaksi yang ingin dihapus (0 untuk batal): "))
        if pilihan == 0:
            return
        if 1 <= pilihan <= len(records):
            target_record = records[pilihan - 1]
            konfirmasi = input(f"⚠️ Yakin ingin menghapus transaksi '{target_record['name']}' ({format_rupiah(target_record['amount'])})? (y/n): ").strip().lower()
            if konfirmasi == 'y':
                deleted_item = records.pop(pilihan - 1)
                # Auto-save setelah hapus transaksi
                save_data()
                print(f"✅ Transaksi '{deleted_item['name']}' berhasil dihapus!")
        else:
            print("❌ Pilihan nomor tidak valid.")
    except ValueError:
        print("❌ Input harus berupa angka.")

def ganti_nama_wallet():
    active_wallet = get_active_wallet()
    if not active_wallet:
        print("\n❌ Wallet aktif tidak ditemukan!")
        return

    print(f"\n--- Ganti Nama Wallet ---")
    print(f"Nama wallet saat ini: {active_wallet['name']}")
    nama_baru = input("Masukkan nama wallet baru: ").strip()

    if nama_baru:
        active_wallet['name'] = nama_baru
        # Auto-save setelah ubah nama
        save_data()
        print(f"✅ Nama wallet berhasil diubah menjadi '{nama_baru}'!")
    else:
        print("❌ Nama wallet tidak boleh kosong!")

def tampilkanMenu():
    print("===========================================")
    print(" Duit.Gue - Manajemen dan Analisis Keuangan")
    print("===========================================\n")
    print("Pilih menu tindakan di bawah ini:")
    print("[a] Tambah pembukuan (wallet)")
    print("[b] Hapus pembukuan (wallet)")
    print("[s] Pilih / Switch wallet aktif")
    print("[c] Ganti nama wallet aktif")
    print("[d] Tambah Pemasukan (+)")
    print("[e] Tambah Pengeluaran (-)")
    print("[r] Hapus Transaksi (Record)")
    print("[f] Simpan Manual (Save data.json)")
    print("[g] Muat Ulang Data (Load data.json)")
    print("[h] Ekspor Wallet Aktif ke File JSON")
    print("[i] Impor Wallet dari File JSON")
    print("[q] Keluar Aplikasi\n")
    
    active_wallet = get_active_wallet()
    if not active_wallet:
        print("Wallet aktif tidak ditemukan!")
        return

    print(f"=== {active_wallet['name']} ===")
    
    total_income = 0
    total_outcome = 0
    outcome_categories = {}

    records = active_wallet.get('records', [])
    
    if not records:
        print("Belum ada transaksi di wallet ini.")
    else:
        for record in records:
            if record['type'] == 'income':
                total_income += record['amount']
            elif record['type'] == 'outcome':
                total_outcome += record['amount']
                category = record['category']
                outcome_categories[category] = outcome_categories.get(category, 0) + record['amount']
                
            simbol = "(+)" if record['type'] == 'income' else "(-)"
            tanggal = record['datetime'][:10]
            kategori_indo = translate_category(record['category'])
            
            print(f"[{tanggal}] {simbol} {record['name']} - {format_rupiah(record['amount'])} ({kategori_indo})")

    balance = total_income - total_outcome

    print("\n------------------------------")
    print(f"Pemasukan  : {format_rupiah(total_income)}")
    print(f"Pengeluaran: {format_rupiah(total_outcome)}")
    print(f"Sisa Saldo : {format_rupiah(balance)}")

    # --- ANALISIS KATEGORI PENGELUARAN ---
    print("\n--- Analisis Pengeluaran ---")
    if total_outcome > 0:
        sorted_categories = sorted(outcome_categories.items(), key=lambda x: x[1], reverse=True)
        top_category_key, top_amount = sorted_categories[0]
        
        for category_key, amount in sorted_categories:
            percentage = (amount / total_outcome) * 100
            kategori_indo = translate_category(category_key)
            print(f"- {kategori_indo:<20}: {format_rupiah(amount)} ({percentage:.2f}%)")
        
        top_percentage = (top_amount / total_outcome) * 100
        top_kategori_indo = translate_category(top_category_key)
        print(f"\n📌 Pengeluaran terbesar pada kategori '{top_kategori_indo}' sebesar {format_rupiah(top_amount)} ({top_percentage:.1f}% dari total pengeluaran).")
    else:
        print("Belum ada pengeluaran untuk dianalisis.")

def main_loop():
    # Otomatis muat data saat aplikasi dinyalakan
    load_data(silent=True)
    
    # Cek apakah data kosong / belum ada wallet
    cek_dan_buat_wallet_awal()
    
    while True:
        tampilkanMenu()
        pilihan = input("\nPilih menu [a-i/s/r/q]: ").strip().lower()
        
        if pilihan == 'a':
            tambah_wallet()
        elif pilihan == 'b':
            hapus_wallet()
        elif pilihan == 's':
            ganti_wallet_aktif()
        elif pilihan == 'c':
            ganti_nama_wallet()
        elif pilihan == 'd':
            tambah_transaksi("income")
        elif pilihan == 'e':
            tambah_transaksi("outcome")
        elif pilihan == 'r':
            hapus_transaksi()
        elif pilihan == 'f':
            save_data(silent=False)
        elif pilihan == 'g':
            load_data()
            cek_dan_buat_wallet_awal()
        elif pilihan == 'h':
            ekspor_wallet()
        elif pilihan == 'i':
            impor_wallet()
        elif pilihan == 'q':
            save_data(silent=False)
            print("\nTerima kasih telah menggunakan Duit.Gue!")
            break
        else:
            print("\n⚠️ Menu belum tersedia atau pilihan tidak valid.")
            
        input("\nTekan Enter untuk melanjutkan...")

if __name__ == "__main__":
    main_loop()