import pandas as pd
import mysql.connector

# Fungsi untuk membaca file Excel dan memasukkan data ke MySQL
def import_excel_to_mysql(excel_file, mysql_config, table_name):
    # Membaca data dari file Excel menggunakan pandas
    df = pd.read_excel(excel_file, dtype={'nis': str})

    # Menghubungkan ke database MySQL
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()

    # Memasukkan data ke tabel MySQL
    for _, row in df.iterrows():
        insert_query = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES {tuple(row.values)}"
        cursor.execute(insert_query)
        conn.commit()

    # Menutup koneksi
    cursor.close()
    conn.close()

# Configurasi MySQL
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'face_reg'
}

# Nama tabel di MySQL
table_name = 'siswa'

# Nama file Excel yang akan diimpor
excel_file = 'import.xlsx'

# Memanggil fungsi untuk mengimpor data
import_excel_to_mysql(excel_file, mysql_config, table_name)
