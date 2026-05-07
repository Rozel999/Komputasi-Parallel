# %% [markdown]
# # Laporan Modul 1: Eksplorasi Paralelisme Dasar
# ## Speedup Analysis dengan Thread/Multiprocessing Sederhana
#
# **Nama:** Rozel Tasri Orama  
# **NIM:** 24343023  
# **Kelas:** Sesi 202523430063  
# **Mata Kuliah:** Komputasi Paralel dan Terdistribusi  
#
# Notebook ini berisi implementasi program serial dan paralel untuk menghitung nilai π menggunakan metode Monte Carlo, kemudian hasilnya dianalisis menggunakan `pandas` dan divisualisasikan dengan `matplotlib`.
#
# ## Spesifikasi Perangkat
# - **Nama perangkat:** ASUS TUF Gaming F15 FX506HF_FX506HF
# - **Processor:** 11th Gen Intel(R) Core(TM) i7-11800H @ 2.30GHz
# - **RAM:** 16.0 GB, 3200 MT/s
# - **GPU:** 4 GB, multiple GPUs installed
# - **Storage:** 954 GB, 766 GB used


# %% [markdown]
# ## 1. Import Library
# Library yang digunakan adalah `random`, `time`, `multiprocessing`, `pandas`, dan `matplotlib`.

# %%
import random
import time
import multiprocessing as mp
import pandas as pd
import matplotlib.pyplot as plt

TOTAL_POINTS = 5_000_000
PROCESS_COUNTS = [1, 2, 4, 8, 16, 32]
SEED = 24343023

random.seed(SEED)
print(f"CPU terdeteksi: {mp.cpu_count()} core/logical processor")

# %% [markdown]
# ## 2. Fungsi Perhitungan Monte Carlo
# Metode Monte Carlo menghitung pendekatan nilai π dengan cara membuat titik acak di dalam persegi, kemudian menghitung berapa banyak titik yang berada di dalam lingkaran.

# %%
def count_inside_circle(num_points: int) -> int:
    """Menghitung jumlah titik acak yang berada di dalam lingkaran satuan."""
    inside = 0
    for _ in range(num_points):
        x = random.random()
        y = random.random()
        if x * x + y * y <= 1:
            inside += 1
    return inside


def calculate_pi_serial(total_points: int) -> tuple[float, float]:
    """Menghitung nilai pi secara serial."""
    start = time.perf_counter()
    inside = count_inside_circle(total_points)
    pi_value = 4 * inside / total_points
    elapsed = time.perf_counter() - start
    return pi_value, elapsed


def calculate_pi_parallel(total_points: int, num_processes: int) -> tuple[float, float]:
    """Menghitung nilai pi secara paralel menggunakan multiprocessing."""
    points_per_process = total_points // num_processes
    remainder = total_points % num_processes
    work_distribution = [points_per_process] * num_processes
    work_distribution[0] += remainder

    start = time.perf_counter()
    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(count_inside_circle, work_distribution)
    inside = sum(results)
    pi_value = 4 * inside / total_points
    elapsed = time.perf_counter() - start
    return pi_value, elapsed

# %% [markdown]
# ## 3. Program Serial
# Bagian ini menjalankan perhitungan π secara serial sebagai pembanding utama.

# %%
serial_pi, serial_time = calculate_pi_serial(TOTAL_POINTS)

serial_result = pd.DataFrame({
    "Metode": ["Serial"],
    "Jumlah Titik": [TOTAL_POINTS],
    "Waktu Eksekusi (detik)": [round(serial_time, 4)],
    "Hasil pi": [round(serial_pi, 7)]
})

serial_result

# %% [markdown]
# ## 4. Program Paralel Multiproses
# Bagian ini menjalankan program paralel dengan variasi jumlah proses 1, 2, 4, 8, 16, dan 32.

# %%
parallel_rows = []

for processes in PROCESS_COUNTS:
    pi_value, elapsed = calculate_pi_parallel(TOTAL_POINTS, processes)
    speedup = serial_time / elapsed
    efficiency = speedup / processes
    parallel_rows.append({
        "Jumlah Proses": processes,
        "Waktu (detik)": round(elapsed, 4),
        "Speedup": round(speedup, 3),
        "Efficiency": round(efficiency, 3),
        "Hasil pi": round(pi_value, 7)
    })

df_results = pd.DataFrame(parallel_rows)
df_results

# %% [markdown]
# ## 5. Grafik Analisis
# Grafik berikut dibuat dari data `pandas DataFrame`.

# %%
plt.figure(figsize=(8, 5))
plt.plot(df_results["Jumlah Proses"], df_results["Waktu (detik)"], marker="o")
plt.title("Waktu Eksekusi vs Jumlah Proses")
plt.xlabel("Jumlah Proses")
plt.ylabel("Waktu Eksekusi (detik)")
plt.grid(True)
plt.show()

# %%
plt.figure(figsize=(8, 5))
plt.plot(df_results["Jumlah Proses"], df_results["Speedup"], marker="o", label="Speedup Aktual")
plt.plot(df_results["Jumlah Proses"], df_results["Jumlah Proses"], linestyle="--", label="Speedup Ideal")
plt.title("Speedup vs Jumlah Proses")
plt.xlabel("Jumlah Proses")
plt.ylabel("Speedup")
plt.legend()
plt.grid(True)
plt.show()

# %%
plt.figure(figsize=(8, 5))
plt.plot(df_results["Jumlah Proses"], df_results["Efficiency"], marker="o")
plt.title("Efficiency vs Jumlah Proses")
plt.xlabel("Jumlah Proses")
plt.ylabel("Efficiency")
plt.grid(True)
plt.show()

# %% [markdown]
# ## 6. Analisis Hasil
#
# ### 6.1 Faktor Overhead
# Speedup yang diperoleh tidak selalu mencapai kondisi ideal karena terdapat beberapa faktor overhead, yaitu:
#
# 1. Pembuatan dan pengelolaan proses membutuhkan waktu tambahan.
# 2. Data pekerjaan harus dibagi ke beberapa proses.
# 3. Hasil dari setiap proses perlu dikumpulkan kembali.
# 4. Jumlah proses yang terlalu banyak dapat menyebabkan context switching.
# 5. Tidak semua bagian program dapat diparalelkan.
#
# Karena faktor tersebut, penambahan jumlah proses tidak selalu menghasilkan peningkatan performa yang sebanding.

# %% [markdown]
# ### 6.2 Perbandingan dengan Amdahl's Law
# Amdahl's Law digunakan untuk menghitung batas maksimum speedup program paralel.
#
# Rumus:
#
# $$S(n) = \frac{1}{f + \frac{1-f}{n}}$$
#
# Keterangan:
# - $S(n)$ = speedup teoritis
# - $f$ = fraksi program yang berjalan serial
# - $n$ = jumlah proses
#
# Jika diasumsikan 5% program tidak dapat diparalelkan dan digunakan 8 proses, maka perhitungannya adalah:

# %%
f = 0.05
n = 8
amdahl_speedup = 1 / (f + ((1 - f) / n))
actual_speedup_8 = df_results.loc[df_results["Jumlah Proses"] == 8, "Speedup"].iloc[0]

pd.DataFrame({
    "Keterangan": ["Speedup Teoritis Amdahl", "Speedup Aktual 8 Proses"],
    "Nilai": [round(amdahl_speedup, 3), actual_speedup_8]
})

# %% [markdown]
# ## 7. Kesimpulan
# Berdasarkan percobaan, multiprocessing dapat mempercepat proses perhitungan nilai π dibandingkan program serial. Namun, speedup yang diperoleh tidak mencapai nilai ideal karena adanya overhead, pembagian tugas, penggabungan hasil, context switching, dan keterbatasan perangkat keras.
#
# Efisiensi program cenderung menurun ketika jumlah proses semakin banyak. Oleh karena itu, jumlah proses perlu disesuaikan dengan kemampuan perangkat keras dan karakteristik program agar performa paralel dapat berjalan lebih optimal.

# %% [markdown]
# ## 8. Link Repository GitHub
# Isi bagian ini setelah file notebook diunggah ke repository GitHub.
#
# Contoh:
# `https://github.com/USERNAME_KAMU/Komputasi-Parallel/blob/main/Modul1_Rozel_Tasri_Orama_24343023.ipynb`