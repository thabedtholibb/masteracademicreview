# FAQ (Bahasa Indonesia)

## Cakupan

**Apakah alat ini menulis seluruh paper saya?**
Tidak. Alat ini membantu menulis **naskah review** (13 genre) beserta artefak
yang bisa diaudit. Alat ini tidak merancang eksperimen dan tidak menghasilkan
temuan baru.

**Apakah menjamin diterima di jurnal Q1?**
Tidak. `journal-match` memberi peringkat jurnal berdasarkan bukti yang **Anda**
verifikasi; skornya ukuran kecocokan, bukan peluang diterima.

**Apakah bisa dipakai dalam Bahasa Indonesia?**
Ya. Skill merespons dalam bahasa yang Anda pakai. Surat pengantar dan balasan
reviewer bisa dibuat dalam Bahasa Indonesia dengan `--lang id`. Nama standar
pelaporan, DOI, dan nama database tetap seperti aslinya.

**Apakah harus clone repositori?**
Untuk alat-alatnya tidak: pasang dengan pip (lihat [README](../../README.id.md))
lalu pakai perintah `mar`. Untuk skill (`SKILL.md`) di Claude Code dan sejenisnya,
ya: ikuti [docs/INSTALL.md](../INSTALL.md).

## Referensi dan bukti

**Bisakah AI mengarang referensi?**
Bisa. Karena itu ada `verify_refs.py`. Secara offline ia menangkap DOI ganda,
sitasi tanpa daftar pustaka, dan referensi yatim. Dengan `--online` ia mencocokkan
DOI, judul, dan tahun ke Crossref. Referensi yang tidak bisa dilacak harus
diperbaiki atau dihapus.

**`verify_refs.py` memberi AMBIGUOUS atau NO_MATCH untuk sumber yang nyata?**
Buku, laporan, dan pedoman berakronim (PRISMA, GRADE) sering tidak terdaftar di
Crossref dengan judul yang Anda kutip. Cek manual ke penerbit atau situs pedoman,
lalu perbaiki entrinya.

**Boleh scraping Scopus untuk tabel jurnal?**
Tidak, karena melanggar ketentuan layanan. Cari manual dan catat sumber serta
tanggalnya di `journal-match/evidence_worksheet.md`.

**Apakah SINTA sama dengan kuartil Scopus?**
Tidak. SINTA adalah peringkat nasional, sedangkan kuartil Scopus/SJR adalah
metrik internasional. Keduanya mengukur hal berbeda dan tidak boleh disamakan.

## Metode

**Berapa studi yang dibutuhkan untuk meta-analisis?**
Penggabungan bisa dari dua studi, tetapi estimasi heterogenitas tidak stabil bila
studinya sangat sedikit. Engine memberi peringatan untuk k < 10 pada uji Egger,
analisis subgrup, dan meta-regresi. *Prediction interval* butuh k ≥ 3.

**Estimator random-effects mana yang dipakai?**
Rekomendasi #1: REML dengan penyesuaian Hartung-Knapp-Sidik-Jonkman
(`random_effects(..., method="reml", hksj=True)`). DerSimonian-Laird dipakai
sebagai analisis sensitivitas bila bidang Anda mengharapkannya.

**Kenapa deduplikasi tidak menghapus semua yang mirip?**
Prinsip JEV: yang pasti dihapus otomatis, yang meragukan hanya direkomendasikan.
Menghapus dua studi berbeda yang judulnya mirip adalah kesalahan yang lebih
berbahaya daripada menyisakan satu duplikat untuk dicek manusia.

**Kenapa gate gagal padahal teks terlihat lengkap?**
`check_review.py` sengaja ketat. Ia menolak bila ada field header yang hilang,
section wajib genre yang tidak ada, sitasi tanpa referensi, artefak yang dirujuk
tetapi tidak ada, `TODO` atau `[citation needed]` yang tertinggal, atau gate
"passed" dengan skor checklist tidak lengkap. Laporannya mengurutkan perbaikan
dari yang paling menentukan.

**Apakah protokol harus diregistrasi?**
Untuk systematic review, meta-analisis, umbrella, rapid, realist, dan
meta-synthesis: ya, bila jurnal mengharapkannya (PROSPERO atau OSF). Scoping dan
mapping review diregistrasi di OSF. `protocol.py` membuat dokumennya.

## File dan keluaran

**Di mana file keluaran?**
Di samping `review.md`: `prisma_flow.svg`, `screening_log.csv`, `agreement.md`,
`ref_check.md`, `review_check.md`, dan lainnya. Daftar lengkap ada di
[`shared/output_spec.md`](../../shared/output_spec.md).

**Diagram PRISMA mana yang dipakai?**
Default untuk systematic review baru, `--variant scoping` untuk scoping review,
dan `--variant update` untuk review pembaruan (studi baru + studi versi
sebelumnya).
