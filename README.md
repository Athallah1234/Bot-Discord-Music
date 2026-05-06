# 🎵 Ultimate Modern Discord Music Bot — Grandmaster Edition

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Discord.py-v2.0%2B-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord.py">
  <img src="https://img.shields.io/badge/yt--dlp-Latest-red?style=for-the-badge&logo=youtube&logoColor=white" alt="yt-dlp">
  <img src="https://img.shields.io/badge/FFmpeg-Optimized-0078D4?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg">
  <img src="https://img.shields.io/badge/Status-Production--Ready-success?style=for-the-badge" alt="Status">
</p>

---

## 🌟 Overview
Mahakarya bot musik Discord yang dibangun menggunakan **Python murni**, menggabungkan kecepatan ekstraksi metadata `yt-dlp` dengan kejernihan audio `FFmpeg`. Bot ini menghadirkan kontrol interaktif dan sistem antrean cerdas yang belum pernah ada sebelumnya di kelas bot Python.

---

## 📌 Navigasi Cepat (Hyper-Interactive TOC)
<details open>
<summary><b>Klik untuk Membuka Daftar Isi</b></summary>

1. [✨ Fitur Unggulan](#-fitur-unggulan)
2. [🎮 Daftar Perintah Lengkap](#-daftar-perintah-slash-commands)
3. [🚀 Panduan Setup & Instalasi](#-panduan-setup-cepat)
4. [📂 Arsitektur & Struktur Folder](#-struktur--arsitektur)
5. [💡 Pro-Tips for DJs](#-pro-tips-for-djs)
6. [🛠️ Deep Dive: Teknis & Optimasi](#%EF%B8%8F-deep-dive-teknis--optimasi)
   - [Optimasi FFmpeg & Stream](#optimasi-ffmpeg--stream)
   - [Skalabilitas Multi-Server](#skalabilitas-multi-server)
   - [Penanganan Rate Limit](#penanganan-rate-limit)
7. [🌐 Hosting & Produksi](#-hosting--pemeliharaan)
8. [📈 Roadmap & Riwayat Versi](#-roadmap--changelog)
9. [⚖️ Hukum & Lisensi](#-penafian--lisensi)
</details>

---

## ✨ Fitur Unggulan

### 🎧 Audio Engine
- **Direct Stream (No Buffer)**: Teknologi streaming langsung yang meminimalisir delay.
- **Opus Optimized**: Kualitas suara setara CD (48kHz) dengan enkripsi penuh.
- **Smart Reconnection**: Otomatis menyambung kembali jika terjadi gangguan sinyal internet.

### 🤖 Automation
- **Auto-Join & Auto-Deafen**: Bot langsung bekerja efisien sejak detik pertama masuk Voice Channel.
- **Auto-Cleanup**: Pembersihan resource secara otomatis setelah pemutaran selesai untuk menjaga kesehatan memori RAM.
- **Idle Timeout**: Bot akan otomatis keluar dari VC jika tidak ada lagu yang diputar selama 5 menit.

---

## 🎮 Daftar Perintah (Slash Commands)

| Kategori | Perintah | Parameter | Deskripsi |
| :--- | :--- | :--- | :--- |
| **Dasar** | `/play` | `query` | Putar lagu dari YouTube (URL/Judul) |
| | `/help` | - | Menu bantuan interaktif ini |
| **Playback** | `/pause` | - | Jeda pemutaran musik |
| | `/resume` | - | Lanjutkan musik yang dijeda |
| | `/skip` | - | Lompat ke lagu berikutnya di antrean |
| | `/stop` | - | Hentikan total & hapus semua lagu |
| **Antrean** | `/queue` | - | Lihat 10 daftar lagu mendatang |
| | `/shuffle` | - | Acak urutan lagu di antrean |
| | `/remove` | `index` | Hapus lagu di posisi tertentu |
| **Sistem** | `/volume` | `1-100` | Sesuaikan kekerasan suara |
| | `/nowplaying`| - | Info lengkap lagu saat ini |
| | `/join` | - | Panggil bot ke Voice Channel |
| | `/leave` | - | Paksa bot keluar dari VC |

---

## 🚀 Panduan Setup Cepat

### 1. Prasyarat Sistem
- **Python 3.10+** (Gunakan 3.11+ untuk performa tercepat).
- **FFmpeg** terinstal dan terdaftar di `PATH` sistem.

### 2. Instalasi Library
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi .env
```env
DISCORD_TOKEN=Token_Anda
GUILD_ID=ID_Server_Anda (Untuk Sinkronisasi Instan)
DEBUG_MODE=False
```

---

## 💡 Pro-Tips for DJs
- **Pencarian Akurat**: Gunakan format `Artis - Judul Lagu` untuk mendapatkan hasil yang 100% tepat.
- **Volume Emas**: Untuk kualitas suara terbaik di Discord, gunakan volume di kisaran **50-70%**.
- **Interactive UI**: Gunakan tombol di bawah pesan "Now Playing" untuk kontrol yang lebih responsif daripada mengetik perintah.

---

## 📂 Struktur & Arsitektur

<details>
<summary><b>📁 Klik untuk Detail Struktur Folder</b></summary>

```text
MusicBot/
├── cogs/
│   └── music.py        # Kumpulan Perintah Slash
├── modules/
│   ├── player.py       # Mesin Utama (Player Engine)
│   └── ui.py           # Komponen UI Tombol
├── utils/
│   ├── logger.py       # Log Profesional
│   └── helpers.py      # Fungsi Pendukung
├── logs/               # Folder Log File
├── .env                # Kredensial Rahasia
├── LICENSE             # Lisensi MIT
└── bot.py              # Entry Point
```
</details>

---

## 🛠️ Deep Dive: Teknis & Optimasi

### Optimasi FFmpeg & Stream
Kami menggunakan parameter `-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5` yang memungkinkan FFmpeg untuk terus mencoba mengambil data stream jika terjadi gangguan koneksi sesaat tanpa memutus lagu.

### Skalabilitas Multi-Server
Bot ini menggunakan sistem **Guild-Based Player Mapping**. Artinya, setiap server (Guild) memiliki instance `MusicPlayer` yang terisolasi sepenuhnya. Hal ini menjamin:
- Antrean tidak tertukar antar server.
- Pengaturan volume tiap server berbeda.
- Task asinkron berjalan secara paralel tanpa membebani satu sama lain.

### Penanganan Rate Limit
Dengan memisahkan ekstraksi metadata (`yt-dlp`) dari proses streaming, bot meminimalisir resiko terkena blokir IP oleh YouTube (429 Too Many Requests). Penggunaan `run_in_executor` memastikan proses ekstraksi tidak membuat bot hang.

---

## 🌐 Hosting & Pemeliharaan

### Hosting VPS (Ubuntu/Linux)
Rekomendasi penggunaan dengan **PM2**:
```bash
pm2 start bot.py --name "discord-music" --interpreter python3
```

### Penanganan Video Umur (Age-Restricted)
Jika Anda menemui error video yang dibatasi usia, gunakan `cookies.txt` dan masukkan ke dalam parameter `ytdl_format_options` di `modules/player.py`.

---

## 📈 Roadmap & Changelog
- **v1.5.0**: Grandmaster Documentation Release & Optimized Handlers.
- **v1.4.0**: Shuffle, Remove, and Help commands implementation.
- **v1.2.0**: Interactive Buttons & Slash Migration.
- **v1.0.0**: Stable Core Release.

---

## ⚖️ Penafian & Lisensi
Proyek ini dilisensikan di bawah **MIT License**. Gunakan dengan bijak dan patuhi **ToS YouTube**.

---

> [!IMPORTANT]
> Jaga keamanan file `.env` Anda. Jangan pernah mempublikasikan Token Bot di repositori publik.

**© 2026 Antigravity - Dokumentasi Grandmaster Final.**
