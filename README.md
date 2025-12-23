🚀 Pub-Sub Idempotent Event Aggregator

Nama : Anitya C R Sinaga
NIM : 11231011
Mata Kuliah : Sistem Paralel dan Terdistribusi (Kelas A)

📺 Video Demo (YouTube)
👉 https://youtu.be/ZD58cn6yZmU

📌 Deskripsi Sistem

Pub-Sub Idempotent Event Aggregator adalah sistem terdistribusi berbasis multi-service yang dirancang untuk menangani pengiriman event dengan throughput tinggi, aman terhadap duplikasi, dan tahan terhadap konkurensi.

Sistem ini memastikan setiap event hanya diproses satu kali (idempotent), meskipun terjadi:

pengiriman ulang event,

request paralel,

kegagalan jaringan,

atau restart container.

Seluruh sistem berjalan sepenuhnya di lingkungan lokal menggunakan Docker Compose, tanpa ketergantungan layanan eksternal.

✨ Fitur Utama

✅ Idempotency & Deduplication
Event dengan kombinasi (topic, event_id) yang sama hanya diproses sekali menggunakan unique constraint di database.

✅ Atomic Transaction (ACID)
Penyimpanan event dan pembaruan statistik dilakukan dalam satu transaksi PostgreSQL.

✅ Concurrency Safe
Aman terhadap request paralel dan race condition.

✅ Persistensi Data
Data tetap tersimpan meskipun container dihentikan atau dijalankan ulang melalui Docker volume.

✅ Observability
Menyediakan endpoint /health, /stats, dan /events untuk monitoring sistem.

✅ Automated & Load Testing
Sistem diuji menggunakan pytest dan k6 untuk validasi fungsional dan performa.

🏗️ Arsitektur Sistem
Publisher Service  --->  Aggregator Service  --->  PostgreSQL
                            |
                            v
                          Redis


Penjelasan singkat:

Publisher mengirim event ke Aggregator melalui HTTP.

Aggregator memvalidasi, melakukan deduplication, dan menyimpan event.

PostgreSQL menyimpan event dan statistik secara persisten.

Redis digunakan sebagai message broker internal.

🚀 Cara Menjalankan Sistem
1️⃣ Prasyarat

Docker

Docker Compose

Git

2️⃣ Build & Run Sistem

Jalankan perintah berikut di root project:

docker compose up --build


Tunggu hingga muncul log:

Uvicorn running on http://0.0.0.0:8080
Database initialized successfully


Artinya seluruh service sudah berjalan dengan normal.

🌐 Endpoint API
Endpoint	Method	Deskripsi
/health	GET	Status layanan dan uptime
/publish	POST	Mengirim event
/events	GET	Melihat event tersimpan
/stats	GET	Statistik pemrosesan event

Base URL:

http://localhost:8080

🧪 Automated Testing (pytest)

Sistem diuji menggunakan 12 test case, mencakup:

deduplication,

konkurensi,

persistence,

validasi schema,

statistik sistem.

Menjalankan Test
pip install -r tests/requirements.txt
pytest tests/test_basic.py -v


Semua test harus PASS sebelum demo.

🔥 Load Testing (k6)

Load testing digunakan untuk menguji performa sistem di bawah beban tinggi.

Menjalankan k6
& "path\to\k6.exe" run k6_publish_test.js

Indikator Keberhasilan

checks_succeeded: 100%

http_req_failed: 0%

Sistem tetap responsif selama pengujian

💾 Persistensi Data

Sistem menggunakan named Docker volume untuk PostgreSQL.

Untuk membuktikan persistensi data:

docker compose down
docker compose up


Data event tetap tersedia setelah container dijalankan ulang.
