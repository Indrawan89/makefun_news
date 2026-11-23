# news-image-20261122-dense — PROGRESS (rewrite from scratch)

## Status: REWRITE SELESAI + TERUJI (23 Nov 2026, ~21:20 WIB)

Poster padat "THE WORLD TODAY — Sunday 22 November 2026" ditulis ulang
TOTAL dari nol. Alasan: bundle v2 dari build sebelumnya GAGAL check
`thinking_reproduces` (4,7%, butuh >=30%) karena main.py lama dibaca
lalu diketik ulang — baris hasil ketik-ulang dihitung "copied", bukan
"authored". Rewrite ini tidak membaca file .py apa pun: tidak membuka
main.py lama (edisi 22 Nov maupun 23 Nov), tidak memakai cp/mv/import.
Daftar 33 berita diambil dari PROGRESS.md lama + poster PNG lama (fakta
berita, bukan kode), lalu generator ditulis baru dari pengetahuan sendiri.

## Yang ditulis baru
- `main.py` — Python stdlib murni, ditulis dari nol:
  - Font bitmap 5x7 rancangan sendiri (A-Z, 0-9, spasi, - . , : ; ' % / $ ( ) ! ? & +).
  - Canvas bytearray sendiri (dot/box/disc/glyph/text/text_w/text_right/text_center).
  - Encoder PNG sendiri (signature, IHDR, IDAT zlib level 9, IEND, CRC32).
  - Layout engine sendiri: masthead navy + rule emas, panel lead COP31
    (headline scale 4, deck 3 baris, 3 chip fakta, panel termometer 1.5C),
    dua kolom region, panel "Also today", footer sumber.
- `README.md` — ditulis baru (3 live badge make.fun, repo makefun_news).
- `PROGRESS.md` — file ini, ditulis baru.

## Isi poster (sama seperti sebelumnya — 33 berita, 7 region)
- Lead: COP31 gagal di Antalya + panel termometer 1.5C + chip 2 DAYS
  OVERTIME / $120BN DROPPED / 200 NATIONS.
- Europe 5, Middle East 4, Asia 4, Americas 4, Africa 4, Oceania 3,
  Sport/Tech 4, Also today 4. Tiap berita: 1 baris judul + 1 baris deck.
- Footer: "SOURCES: REUTERS - BBC - AP - AFP - THE HINDU - YONHAP -
  22 NOV 2026" + "THE WORLD TODAY - 33 STORIES".

## Hasil uji
- `output/entry.png` — 1024x1024, 28.259 byte, sha256
  5d31c9b55117adebba150522798fbe561f85b9f36a502e2555b687f54980aed8
  (2x run byte-identical — deterministik). TIDAK sama dengan PNG lama
  (sha 5d7c90c5…), sesuai harapan: implementasi baru, poster sama.
- Visual check 1x via render: masthead tidak tumpang tindih, semua 33
  berita 1 baris judul + 1 baris deck, tidak ada teks terpotong / keluar
  panel / tumpang tindih. Kolom kiri berakhir ~y=965, kanan ~y=890,
  footer y=992-1009.

## Yang belum (tugas parent)
- Bundle transcripts (v1 baru) + check dengan --transcripts
  (target thinking_reproduces >=30%).
- Push ke repo makefun_news (repo ini berisi entry Agile Zenith;
  parent yang putuskan: ganti isi repo dengan folder dense ini).
- Loop EVAL ke user + submit sebelum 24 Nov 07:00 WIB.
