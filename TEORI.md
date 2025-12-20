**Bagian Teori – Sistem Terdistribusi (Pub-Sub Log Aggregator)**

**T1. Karakteristik Sistem Terdistribusi dan Trade-off Desain Pub–Sub Aggregator**

Sistem terdistribusi terdiri dari sekumpulan komponen otonom yang berkomunikasi melalui jaringan dan berkoordinasi untuk mencapai tujuan bersama, tetapi bagi pengguna tampak sebagai satu sistem terpadu. Karakteristik utama sistem terdistribusi meliputi concurrency, tidak adanya global clock, serta kemungkinan terjadinya kegagalan parsial (Coulouris et al., 2012). Dalam konteks log aggregator berbasis publish–subscribe, karakteristik ini sangat relevan karena publisher dan consumer berjalan secara independen dan dapat mengalami keterlambatan, duplikasi, atau crash tanpa menghentikan keseluruhan sistem.

Arsitektur publish–subscribe dipilih karena mampu mendekopel pengirim dan penerima pesan. Publisher tidak perlu mengetahui siapa consumer-nya, sementara consumer dapat diskalakan secara horizontal. Trade-off utama dari desain ini adalah meningkatnya kompleksitas pengelolaan konsistensi dan ordering event. Tidak adanya jaminan pengiriman exactly-once menyebabkan kemungkinan event yang sama dikirim lebih dari satu kali. Oleh karena itu, sistem log aggregator harus dirancang untuk menerima duplikasi sebagai kondisi normal.

Dalam rancangan sistem ini, trade-off tersebut diatasi dengan menerapkan idempotent consumer dan deduplication store yang persisten. Pendekatan ini menukar kompleksitas implementasi dengan peningkatan reliabilitas sistem. Desain ini sejalan dengan prinsip sistem terdistribusi yang menekankan toleransi kegagalan dan ketersediaan dibandingkan konsistensi ketat, terutama ketika sistem harus tetap berjalan meskipun terjadi gangguan pada salah satu komponen (Tanenbaum & van Steen, 2023).

**T2. Kapan Memilih Arsitektur Publish–Subscribe Dibanding Client–Server**

Arsitektur client–server cocok digunakan ketika interaksi bersifat sinkron, terarah, dan jumlah klien relatif terbatas. Sebaliknya, publish–subscribe lebih tepat dipilih ketika sistem membutuhkan skalabilitas tinggi, loose coupling, dan dukungan komunikasi asinkron. Dalam sistem log aggregator terdistribusi, sumber log dapat berasal dari banyak service yang berjalan secara paralel dan tidak selalu aktif pada waktu yang sama.

Publish–subscribe memungkinkan setiap service bertindak sebagai publisher tanpa bergantung pada ketersediaan consumer. Event log dapat dikirim ke broker atau topic tertentu, lalu diproses oleh satu atau lebih consumer secara independen. Hal ini sulit dicapai dengan model client–server karena server akan menjadi bottleneck dan single point of failure. Selain itu, client–server menuntut server mengetahui konteks setiap klien, sedangkan publish–subscribe menghilangkan ketergantungan tersebut.

Secara teknis, publish–subscribe juga lebih tahan terhadap perubahan sistem. Penambahan consumer baru tidak memerlukan perubahan pada publisher. Dalam konteks UAS ini, pendekatan tersebut mendukung pengujian konkurensi dengan multi-worker consumer serta memudahkan simulasi crash dan restart container. Oleh karena itu, publish–subscribe dipilih karena lebih selaras dengan kebutuhan sistem terdistribusi yang dinamis, scalable, dan fault-tolerant, sebagaimana dibahas dalam literatur sistem terdistribusi modern (Coulouris et al., 2012; Tanenbaum & van Steen, 2023).

**T3. At-least-once vs Exactly-once Delivery dan Peran Idempotent Consumer**

Model at-least-once delivery menjamin bahwa setiap event akan dikirim minimal satu kali, tetapi memungkinkan terjadinya duplikasi. Sebaliknya, exactly-once delivery menjamin event diproses tepat satu kali, namun sangat sulit dicapai secara praktis dalam sistem terdistribusi karena kegagalan jaringan dan crash parsial (Tanenbaum & van Steen, 2023). Oleh karena itu, banyak sistem nyata memilih at-least-once delivery dan memindahkan kompleksitas penanganan duplikasi ke sisi consumer.

Dalam sistem log aggregator ini, pendekatan at-least-once digunakan karena lebih realistis dan selaras dengan karakteristik publish–subscribe. Untuk menjaga konsistensi, consumer dirancang bersifat idempotent, artinya pemrosesan event yang sama lebih dari sekali tidak akan mengubah state sistem setelah pemrosesan pertama. Setiap event memiliki event_id unik yang disimpan dalam deduplication store. Sebelum memproses event, consumer memeriksa apakah event_id tersebut sudah pernah diproses.

Pendekatan ini secara efektif mensimulasikan perilaku exactly-once di level aplikasi, meskipun secara jaringan hanya tersedia at-least-once delivery. Strategi ini umum digunakan karena lebih sederhana, tahan terhadap crash, dan dapat dipadukan dengan retry serta backoff. Dengan demikian, idempotent consumer menjadi komponen kunci dalam menjamin konsistensi data tanpa mengorbankan ketersediaan sistem (Coulouris et al., 2012).

**T4. Skema Penamaan topic dan event_id untuk Deduplication**

Penamaan dalam sistem terdistribusi berperan penting untuk identifikasi, routing, dan pengelolaan state. Topic digunakan sebagai kanal logis untuk mengelompokkan event berdasarkan sumber atau jenisnya, misalnya logs.auth, logs.payment, atau logs.system. Skema penamaan topic yang hierarkis memudahkan pengelolaan dan perluasan sistem tanpa mengganggu komponen lain (Coulouris et al., 2012).

Sementara itu, event_id digunakan sebagai identitas unik setiap event untuk mendukung deduplication. Agar collision-resistant, event_id dibentuk dari kombinasi beberapa atribut, seperti UUID v4, timestamp, dan identifier publisher. Pendekatan ini mengurangi probabilitas benturan ID hingga tingkat yang dapat diabaikan secara praktis. Dalam sistem ini, event_id menjadi primary key atau unique constraint pada tabel deduplication store.

Dengan skema ini, setiap event yang masuk dapat diverifikasi secara deterministik. Jika event_id sudah ada, event dianggap duplikat dan tidak diproses ulang. Penamaan yang konsisten dan unik ini sangat penting untuk menjaga konsistensi dalam kondisi retry, crash, atau reordering event. Strategi ini sejalan dengan prinsip penamaan global yang dianjurkan dalam sistem terdistribusi modern (Tanenbaum & van Steen, 2023).

**T5. Ordering Praktis dengan Timestamp dan Monotonic Counter**

Ordering event dalam sistem terdistribusi merupakan tantangan karena tidak adanya global clock. Perbedaan latensi jaringan dan clock drift antar node menyebabkan event dapat diterima tidak sesuai urutan waktu sebenarnya. Oleh karena itu, sistem ini menerapkan ordering praktis menggunakan kombinasi timestamp dan monotonic counter lokal.

Timestamp digunakan untuk memberikan perkiraan urutan waktu antar event, sementara monotonic counter memastikan urutan lokal pada satu publisher tetap terjaga. Pendekatan ini tidak menjamin total ordering global, tetapi cukup untuk kebutuhan log aggregator yang berfokus pada analisis dan audit, bukan transaksi real-time yang ketat. Menurut Tanenbaum dan van Steen (2023), pendekatan ini termasuk dalam logical ordering yang lebih ringan dibandingkan mekanisme consensus penuh.

Batasan utama dari pendekatan ini adalah kemungkinan terjadinya event out-of-order ketika event dari publisher berbeda tiba hampir bersamaan. Dampaknya, log mungkin tidak sepenuhnya kronologis. Namun, karena sistem dirancang eventual consistent dan idempotent, dampak ini dapat ditoleransi. Ordering digunakan terutama untuk keperluan observability dan debugging, bukan sebagai dasar pengambilan keputusan kritis.

**T6. Failure Modes dan Strategi Mitigasi**

Sistem terdistribusi rentan terhadap berbagai mode kegagalan, seperti crash service, timeout jaringan, duplikasi pesan, dan restart container. Dalam sistem pub-sub log aggregator, kegagalan paling umum adalah consumer crash setelah menerima event tetapi sebelum menyelesaikan pemrosesan. Kondisi ini dapat menyebabkan event dikirim ulang saat consumer pulih.

Untuk memitigasi hal tersebut, sistem menerapkan retry dengan exponential backoff dan deduplication store yang persisten. Retry memastikan event tidak hilang, sementara deduplication mencegah pemrosesan ganda. Deduplication store disimpan pada volume Docker sehingga tetap tersedia meskipun container dihentikan atau dibuat ulang.

Crash recovery dilakukan dengan cara consumer membaca ulang state deduplication saat startup. Dengan demikian, sistem dapat melanjutkan operasi tanpa inkonsistensi. Pendekatan ini sesuai dengan prinsip fault tolerance dalam sistem terdistribusi, yaitu menerima kegagalan sebagai kondisi normal dan merancang sistem agar dapat pulih secara otomatis (Coulouris et al., 2012).

**T7. Eventual Consistency pada Log Aggregator**

Eventual consistency berarti bahwa state sistem akan menjadi konsisten seiring waktu jika tidak ada update baru. Model ini umum digunakan pada sistem terdistribusi yang mengutamakan ketersediaan dan toleransi kegagalan dibandingkan konsistensi ketat (Tanenbaum & van Steen, 2023).

Dalam sistem log aggregator, eventual consistency diterapkan karena log dari berbagai service tidak harus tersedia secara serentak dan berurutan. Yang terpenting adalah tidak ada log yang hilang atau diproses ganda. Idempotency dan deduplication berperan penting dalam menjaga konsistensi akhir meskipun event diterima secara tidak berurutan atau berulang.

Dengan pendekatan ini, sistem dapat tetap beroperasi meskipun terjadi delay atau retry. Setelah semua event diproses, state agregat akan mencerminkan kondisi yang benar. Model ini sangat sesuai untuk sistem monitoring dan logging, di mana toleransi terhadap inkonsistensi sementara dapat diterima.

**T8. Desain Transaksi: ACID dan Pencegahan Lost Update**

Transaksi digunakan untuk memastikan bahwa operasi kritis dijalankan secara atomik dan konsisten. Prinsip ACID, khususnya atomicity dan isolation, sangat penting untuk mencegah lost update ketika beberapa consumer memproses event secara paralel (Coulouris et al., 2012).

Dalam sistem ini, penyimpanan log dan pencatatan event_id dilakukan dalam satu transaksi database. Jika transaksi gagal, tidak ada perubahan yang disimpan, sehingga sistem tetap konsisten. Isolation level yang digunakan memastikan bahwa dua consumer tidak dapat memproses event yang sama secara bersamaan.

Dengan pendekatan ini, lost update dapat dihindari karena hanya satu transaksi yang berhasil memasukkan event_id tertentu. Transaksi yang gagal akan di-retry, tetapi deduplication memastikan tidak terjadi duplikasi data. Strategi ini menunjukkan penerapan konsep Bab 8 secara langsung dalam implementasi sistem.

**T9. Kontrol Konkurensi dan Idempotent Write Pattern**

Kontrol konkurensi diperlukan ketika beberapa consumer berjalan secara paralel. Dalam sistem ini, kontrol dilakukan melalui unique constraint pada kolom event_id serta operasi upsert yang idempotent. Jika dua consumer mencoba memproses event yang sama, hanya satu yang berhasil melakukan insert.

Idempotent write pattern memastikan bahwa operasi tulis dapat dijalankan berulang kali tanpa mengubah hasil akhir. Jika event sudah ada, operasi ditolak atau diabaikan tanpa efek samping. Pendekatan ini lebih sederhana dibandingkan locking eksplisit dan lebih cocok untuk sistem terdistribusi yang skalabel (Tanenbaum & van Steen, 2023).

Dengan kombinasi constraint database dan transaksi, sistem terbukti bebas race condition saat diuji dengan multi-worker consumer. Hal ini menunjukkan penerapan Bab 9 secara praktis dan efektif.

**T10. Orkestrasi Docker Compose, Keamanan, dan Observability**

Docker Compose digunakan untuk mengorkestrasi seluruh service dalam satu jaringan lokal terisolasi. Setiap service berjalan pada container terpisah dengan network internal sehingga tidak bergantung pada layanan eksternal. Pendekatan ini meningkatkan keamanan dan reproduktibilitas sistem.

Persistensi data dijamin melalui volume Docker yang menyimpan database dan deduplication store. Dengan demikian, data tetap aman meskipun container dihapus atau direstart. Observability disediakan melalui logging terpusat dan endpoint seperti GET /stats untuk memantau jumlah event, duplikasi, dan status consumer.

Pendekatan ini mendukung koordinasi antar service dan memudahkan pengujian readiness serta liveness. Secara keseluruhan, orkestrasi ini mencerminkan prinsip sistem terdistribusi berbasis web dan koordinasi modern sebagaimana dibahas dalam Bab 10–13 (Coulouris et al., 2012; Tanenbaum & van Steen, 2023).

**Daftar Pustaka**

Coulouris, G., Dollimore, J., Kindberg, T., & Blair, G. (2012). Distributed systems: Concepts and design (5th ed.). Addison-Wesley.

Tanenbaum, A. S., & van Steen, M. (2023). Distributed systems (4th ed.). Maarten van Steen.
