# 🚀 Pub-Sub Idempotent Event Aggregator

Sistem **event aggregator terdistribusi** yang dirancang untuk menangani **throughput tinggi** dengan jaminan **Idempotency**, **Deduplication**, dan **konsistensi data**.  
Dibangun menggunakan arsitektur **multi-service** berbasis **Docker Compose**.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python)

---

## 👤 Identitas

**Nama**        : **Anitya C R Sinaga**  
**NIM**         : **11231011**  
**Mata Kuliah** : **Sistem Paralel dan Terdistribusi (Kelas A)**  

📺 **Video Demo (YouTube – Unlisted/Public)**  
👉 https://youtu.be/ZD58cn6yZmU

---

## 📌 Ringkasan Proyek

Proyek ini menyelesaikan permasalahan umum dalam sistem terdistribusi, yaitu **duplikasi event** akibat retry, kegagalan jaringan, atau request paralel.

Dengan memanfaatkan **event_id sebagai kunci idempotency** dan **constraint unik di database**, sistem menjamin bahwa **setiap event hanya diproses satu kali**, meskipun dikirim berkali-kali atau secara bersamaan.

Seluruh layanan berjalan **secara lokal** di dalam Docker tanpa ketergantungan layanan eksternal.

---

## ✨ Fitur Utama

- ✅ **Idempotency & Deduplication**  
  Event dengan `(topic, event_id)` yang sama tidak akan diproses ulang.

- ✅ **Atomic Transaction (ACID)**  
  Penyimpanan event dan update statistik dilakukan dalam satu transaksi database.

- ✅ **Concurrency Safe**  
  Aman terhadap request paralel dan race condition.

- ✅ **Persistensi Data**  
  Data tetap tersimpan meskipun container dihentikan atau dijalankan ulang.

- ✅ **Observability**  
  Endpoint `/health`, `/stats`, dan `/events` untuk monitoring sistem.

- ✅ **Automated & Load Testing**  
  Pengujian otomatis menggunakan **pytest** dan **k6**.

---

## 🏗️ Arsitektur Sistem



Publisher Service ---> Aggregator Service ---> PostgreSQL
|
v
Redis


**Penjelasan singkat:**
- **Publisher** berperan sebagai produsen event.
- **Aggregator** menerima, memvalidasi, melakukan deduplication, dan menyimpan event.
- **PostgreSQL** menyimpan event dan statistik secara persisten.
- **Redis** digunakan sebagai broker internal.

---

## 🚀 Cara Menjalankan Sistem

### 1️⃣ Prasyarat
- Docker
- Docker Compose

### 2️⃣ Build & Run

Jalankan perintah berikut di root project:

```bash
docker compose up --build


Tunggu hingga muncul log:

Uvicorn running on http://0.0.0.0:8080
Database initialized successfully

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

deduplication

konkurensi

persistence

validasi schema

statistik sistem

Menjalankan Test
pip install -r tests/requirements.txt
pytest tests/test_basic.py -v

🔥 Load Testing (k6)

Load testing dilakukan untuk menguji stabilitas sistem di bawah beban tinggi.

Menjalankan k6
& "path\to\k6.exe" run k6_publish_test.js


Indikator keberhasilan:

checks_succeeded: 100%

http_req_failed: 0%

💾 Persistensi Data

Sistem menggunakan named Docker volume untuk PostgreSQL.
Data tetap tersedia meskipun container dihentikan dan dijalankan ulang.

docker compose down
docker compose up

📦 Deliverables

Repository ini berisi:

Source code Aggregator & Publisher

Dockerfile & docker-compose.yml

Automated testing (pytest)

Load testing (k6)

README & laporan

Link video demo

🏁 Penutup

Sistem ini dibangun untuk memenuhi kebutuhan pemrosesan event dalam sistem terdistribusi yang andal, konsisten, dan tahan terhadap kegagalan, sesuai dengan materi mata kuliah Sistem Paralel dan Terdistribusi.
