# 🚀 UAS Sistem Terdistribusi: Pub-Sub Log Aggregator

**Nama**: [Anitya C R Sinaga]  
**NIM**: [11231011]  
**Mata Kuliah**: Sistem Paralel dan Terdistribusi

---

## 📋 Deskripsi Sistem

Sistem Pub-Sub log aggregator terdistribusi dengan fitur:
- ✅ **Idempotency**: Event yang sama hanya diproses sekali
- ✅ **Deduplication**: Menggunakan UNIQUE constraint (topic, event_id)
- ✅ **Transaksi ACID**: Semua operasi dalam transaksi database
- ✅ **Concurrency Control**: Handle multiple requests tanpa race condition
- ✅ **Persistensi**: Data aman dengan Docker volumes
- ✅ **Observability**: Metrics dan audit logging

---

## 🏗️ Arsitektur Sistem
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  Publisher  │────────>│ Aggregator  │<───────>│  PostgreSQL │
│  Service    │  HTTP   │   Service   │   SQL   │  Database   │
└─────────────┘         └─────────────┘         └─────────────┘
│
│ Redis
▼
┌─────────────┐
│    Broker   │
└─────────────┘

### Komponen:
1. **Aggregator**: Service utama (FastAPI) yang menerima dan memproses event
2. **Publisher**: Service generator event (simulasi produsen)
3. **PostgreSQL**: Database persisten untuk event dan stats
4. **Redis**: Message broker (opsional untuk queueing)

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (Windows/Mac) atau Docker Engine (Linux)
- Docker Compose
- Git

### 1. Clone Repository
```bash
git clone <repository-url>
cd uas-sistem-terdistribusi
