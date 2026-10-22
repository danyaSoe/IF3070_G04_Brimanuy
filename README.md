# IF3070_G04_Brimanuy

Simulator konfigurasi penempatan kendaraan pada geladak kapal menggunakan
local search: Hill-Climbing, Simulated Annealing, dan Genetic Algorithm.

## Setup

Project menggunakan Python 3.12 dan virtual environment pada folder `venv`.

```powershell
.\venv\Scripts\Activate.ps1
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Jika virtual environment belum ada:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Menjalankan melalui entry point utama

Local-search experiments (output ke `output/output_local/`):

```powershell
.\venv\Scripts\python.exe src\main.py local
```

Genetic Algorithm experiment matrix (output ke `output/output_GA/`):

```powershell
.\venv\Scripts\python.exe src\main.py ga --no-plots
```

Menjalankan web interface:

```powershell
.\venv\Scripts\python.exe src\main.py web
```

Buka <http://127.0.0.1:8000>. API tersedia di:

```text
GET  /api/algorithms
POST /api/simulate
```

Contoh request:

```json
{
  "case": "src/data/case1.json",
  "algorithm": "ga",
  "mode": "fee",
  "seed": 0,
  "parameters": {
    "pop_size": 50,
    "generations": 200,
    "crossover_rate": 0.9,
    "mutation_rate": 0.2,
    "elitism": 2
  }
}
```

## Input dan multi-kapal

Case JSON memiliki `vehicles` dan `ships`. Satu placement disimpan sebagai
`(ship_index, x, y, orientation)`. `ship_index = -1` berarti kendaraan berada
di luar kapal. Semua kapal pada array `ships` digunakan oleh generator state,
neighbor, objective, kapasitas, serialisasi, visualisasi, GA, dan API.

Objective utama memaksimalkan total shipping fee dengan penalty untuk overlap,
kendaraan keluar batas, dan kapasitas kapal yang terlampaui. Mode `urgency` dan
`area` juga tersedia.

## Testing

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Test mencakup objective dan constraint multi-kapal, GA, service runner, dan
endpoint FastAPI.

## Struktur project

```text
src/          Source code aplikasi dan data input
  algorithms/ Algoritma local search
  core/       Model, objective, neighbor, I/O, visualisasi
  data/       Case JSON
  experiments/ Runner dan export eksperimen
  service/    Runner bersama CLI dan web
  web/        FastAPI app dan halaman simulasi
  main.py     Entry point utama
src/tests/    Automated tests
output/       Hasil eksperimen (output_GA/ dan output_local/)
```
