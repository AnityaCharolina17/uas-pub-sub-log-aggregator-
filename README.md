#**Pub-Sub Idempotent Event Aggregator**

**##Nama : Anitya C R Sinaga
##NIM : 11231011
##Mata Kuliah : Sistem Paralel dan Terdistribusi (Kelas A)

##Video Demo (YouTube)**
https://youtu.be/ZD58cn6yZmU

**Deskripsi Sistem**

Sistem Pub-Sub Idempotent Event Aggregator adalah sistem terdistribusi berbasis multi-service yang dirancang untuk menangani pengiriman event dengan throughput tinggi, aman terhadap duplikasi, serta tahan terhadap konkurensi dan restart container.

Sistem ini memastikan bahwa setiap event hanya diproses satu kali (idempotent), meskipun terjadi:

pengiriman ulang event,

request paralel,

kegagalan jaringan,

atau restart service.

Seluruh komponen dijalankan secara lokal menggunakan Docker Compose, tanpa ketergantungan layanan eksternal.

**Fitur Utama**

1. Idempotency & Deduplication
Event dengan kombinasi (topic, event_id) yang sama hanya diproses sekali menggunakan constraint unik di database.

2. Atomic Transaction (ACID)
Penyimpanan event dan pembaruan statistik dilakukan dalam satu transaksi PostgreSQL.

3. Concurrency Safe
Aman terhadap request paralel dan race condition.

4. Persistensi Data
Data tetap tersimpan meskipun container dihentikan atau dijalankan ulang, menggunakan Docker volume.

5. Observability
Menyediakan endpoint /health, /stats, dan /events untuk monitoring sistem.

6. Automated Testing & Load Testing
Diuji menggunakan pytest dan k6 untuk validasi fungsional dan performa.

**Arsitektur Sistem**
Publisher Service  --->  Aggregator Service  --->  PostgreSQL
                            |
                            v
                          Redis


Penjelasan singkat:

Publisher mengirim event ke Aggregator melalui HTTP.

Aggregator memvalidasi, melakukan deduplication, dan menyimpan event.

PostgreSQL menyimpan event dan statistik secara persisten.

Redis digunakan sebagai message broker internal.

**Cara Menjalankan Sistem**
1. Prasyarat

Docker & Docker Compose

Git

2. Build & Run

Jalankan perintah berikut di root project:

docker compose up --build


Tunggu hingga muncul log:

Uvicorn running on http://0.0.0.0:8080
Database initialized successfully

Endpoint API
Endpoint	Method	Fungsi
/health	GET	Status layanan dan uptime
/publish	POST	Mengirim event
/events	GET	Melihat event tersimpan
/stats	GET	Statistik pemrosesan event

**Pengujian**
Automated Testing (pytest)

Sistem diuji menggunakan 12 test case, mencakup:

deduplication,

konkurensi,

persistence,

validasi schema,

statistik sistem.

Menjalankan test:

pip install -r tests/requirements.txt
pytest tests/test_basic.py -v

Load Testing (k6)

Load testing digunakan untuk menguji performa sistem pada beban tinggi.

Menjalankan k6:

& "path\to\k6.exe" run k6_publish_test.js


**Indikator keberhasilan:**

checks_succeeded: 100%

http_req_failed: 0%

**Persistensi Data**

Sistem menggunakan named Docker volume untuk PostgreSQL.
Data tetap tersedia meskipun container dihentikan dan dijalankan ulang:

docker compose down
docker compose up
