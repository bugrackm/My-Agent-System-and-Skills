# Brain for Windows: kalıcı hafıza sistemi

🇹🇷 Türkçe · 🇬🇧 [English ↓](#english) · Kurulum: [INSTALL.md](INSTALL.md)

Bu klasör, [`brain/`](../brain/README.md) hafıza sisteminin **Windows'a özel, bağımsız** sürümü. Fikir aynı: Claude Code her oturuma sıfırdan başlar; beyin ne yaptığını, nerede kaldığını, açık işleri ve öğrendiklerini düz Markdown dosyalarında tutar ve her oturumun başında Claude'a hatırlatır. Oturum akışı, vault yapısı ve bilgi kaynağı öncelikleri için [`brain/README.md`](../brain/README.md) geçerli. Bu sayfa yalnızca Windows'ta neyin farklı olduğunu anlatıyor.

> **Hangisini kurmalıyım?**
> - Sadece Windows kullanıyorsan: **bu klasörü** kur.
> - Sadece Linux ve/veya macOS kullanıyorsan: [`brain/`](../brain/README.md) kur.
> - Aynı beyni Windows, Linux ve macOS'ta **birlikte** kullanmak istiyorsan: Windows'ta Claude Code'u **WSL** içinde çalıştır ve oraya da [`brain/`](../brain/README.md) kur. Bu durumda Windows makinen de bir Linux makinesi gibi davranır ve senkron sorunsuz olur.

`brain-windows/` ile `brain/` ayrı gelişir. Birine gelen bir değişiklik ötekine kendiliğinden geçmez.

## Windows'ta neler farklı

| Konu | `brain/` (Linux/macOS) | `brain-windows/` |
|---|---|---|
| Hook'u çalıştıran shell | `sh` | `powershell.exe -NoProfile -EncodedCommand …`: Claude Code komutu Git Bash'le de PowerShell'le de çalıştırsa aynı sonuç; yoldaki boşluk, `'` veya `$` tırnakları bozmaz, PowerShell profilin çıktıyı kirletemez |
| Python komutu | `python3` | Kurulumda kullandığın Python'un **tam yolu** `settings.json`'a yazılır; `python3`/`python`/`py` tahmini yok |
| Hook çıktısı | UTF-8 | Yalnızca ASCII JSON; Türkçe karakterler ve emoji `\uXXXX` olarak geçer. Windows kod sayfaları (cp1254, cp1252) çıktıyı bozamaz |
| Varsayılan vault yolu | `~/Documents/Brain` | `%USERPROFILE%\Brain`. `Documents` çoğu zaman OneDrive'a bağlıdır; OneDrive ile git aynı klasörü senkronlarken çakışır |
| Claude Code'a bağlama | symlink | kopya; güncellemede `update-runtime.py` kopyaları yeniler |
| Git | etkileşimsiz `pull` | aynısı + Git Credential Manager'ın hook sırasında pencere açması engellenir |
| `vault-doctor` | standart kontroller | + Windows'ta geçersiz dosya adları, yalnız harf büyüklüğü farklı dosyalar, uzun yollar, OneDrive içindeki vault, eksik `.gitattributes`, eski kalmış kurulum kopyaları |

## Neden Windows ile Linux/macOS beyinlerini ayrı tutmalısın

Önerim: **Windows'ta bir beyin, Linux/macOS'ta ayrı bir beyin.** Yani ayrı vault ve ayrı private repo. Aynı vault'u git üzerinden iki dünya arasında paylaşırsan şu sorunlar çıkabilir:

1. **Satır sonları.** Windows'ta git dosyaları CRLF'ye çevirebilir; her commit'te değişmemiş satırlar da diff'e girer. (Vault şablonundaki `.gitattributes` bunu tek bir beyin içinde önler.)
2. **Mutlak yollar.** Hafıza dosyaları proje yollarını tutar (`LAST_SESSION.md`, `300-Projects/PROJECT_INDEX.md`). `C:\Users\...\Projects\oyun` Linux'ta, `/home/...` Windows'ta anlamsızdır; hook projeyi tanıyamaz.
3. **Büyük/küçük harf.** Linux `Not.md` ile `not.md`'yi iki ayrı dosya sayar; Windows ve macOS aynı dosya sayar. Linux'ta oluşan böyle bir çift, Windows'ta checkout'u bozar.
4. **Yasak dosya adları.** Windows'ta `< > : " | ? *` karakterleri, sonda nokta/boşluk ve `CON`, `NUL`, `AUX`, `COM1` gibi ayrılmış adlar kullanılamaz. Linux'ta açılan `Soru: neden?.md` notu Windows'ta açılmaz.
5. **Uzun yollar.** Windows'ta 260 karakter sınırı derin klasörlerde sorun çıkarabilir.
6. **Kilitli dosyalar.** Windows, bir editörde açık olan dosyayı kilitleyebilir; hook'un oturum başındaki `git pull`'u başarısız olur.
7. **Eşzamanlı oturumlar.** İki makinede aynı anda çalışırsan iki taraf da `LAST_SESSION.md` ve `THREADS.md`'yi yazar; push sırasında merge çatışması çıkar.
8. **Symlink'ler.** Vault içindeki symlink'ler Windows'ta çoğu zaman düz metin dosyasına dönüşür.

Bunlar ayrı beyinlerde hiç oluşmaz. Üç platformu tek beyinle kullanmak zorundaysan WSL yolunu seç (yukarıdaki kutu).

## Teşekkür

Windows tarafındaki bazı çözümler (EncodedCommand ile hook çağırma, satır sonu farklarını yok sayma, dosya türüne göre LF sabitleme) [avenoxbeyin](https://github.com/avenoxai/avenoxbeyin)'in Windows desteğinden (MIT) esinlendi. Teşekkürler Avenox. 🙏

## Gizlilik

Vault zamanla kişisel bilgilerle dolar. **Private** tut; git remote'u açacaksan mutlaka `--private` kullan.

---

<a id="english"></a>

## English

🇬🇧 English · 🇹🇷 [Türkçe ↑](#brain-for-windows-kalıcı-hafıza-sistemi) · Install: [INSTALL.md](INSTALL.md#english)

This folder is a **standalone, Windows-only** version of the [`brain/`](../brain/README.md#english) memory system. The idea is the same: Claude Code starts every session from scratch; the brain keeps what you did, where you left off, open work and what you learned in plain Markdown files, and reminds Claude of them at the start of each session. For the session flow, vault layout and source-of-truth priorities, see [`brain/README.md`](../brain/README.md#english). This page only covers what is different on Windows.

> **Which one should I install?**
> - Windows only: install **this folder**.
> - Linux and/or macOS only: install [`brain/`](../brain/README.md#english).
> - One brain shared across Windows, Linux and macOS: run Claude Code inside **WSL** on Windows and install [`brain/`](../brain/README.md#english) there as well. Your Windows machine then behaves like a Linux machine and sync just works.

`brain-windows/` and `brain/` evolve separately. A change to one does not reach the other on its own.

### What is different on Windows

| Topic | `brain/` (Linux/macOS) | `brain-windows/` |
|---|---|---|
| Shell running the hook | `sh` | `powershell.exe -NoProfile -EncodedCommand …`: same result whether Claude Code runs the command through Git Bash or PowerShell; spaces, `'` or `$` in paths can't break quoting, and your PowerShell profile can't pollute the output |
| Python command | `python3` | The **full path** of the Python you install with is written into `settings.json`; no guessing `python3`/`python`/`py` |
| Hook output | UTF-8 | ASCII-only JSON; non-ASCII letters and emoji travel as `\uXXXX`. Windows code pages (cp1252, cp1254) can't break it |
| Default vault path | `~/Documents/Brain` | `%USERPROFILE%\Brain`. `Documents` is often redirected into OneDrive, and OneDrive plus git syncing the same folder conflict |
| Wiring into Claude Code | symlinks | copies; `update-runtime.py` refreshes them on update |
| Git | non-interactive `pull` | same, plus Git Credential Manager is prevented from opening a window during a hook |
| `vault-doctor` | standard checks | + names invalid on Windows, files differing only by case, long paths, a vault inside OneDrive, missing `.gitattributes`, stale installed copies |

### Why keep Windows and Linux/macOS brains separate

Recommendation: **one brain on Windows, a separate brain on Linux/macOS**, i.e. separate vaults and separate private repos. If you share one vault between the two worlds through git, you can hit these problems:

1. **Line endings.** Git on Windows may convert files to CRLF, so unchanged lines show up in every diff. (The vault template's `.gitattributes` prevents this within one brain.)
2. **Absolute paths.** Memory files store project paths (`LAST_SESSION.md`, `300-Projects/PROJECT_INDEX.md`). `C:\Users\...\Projects\game` means nothing on Linux, and `/home/...` means nothing on Windows; the hook can't recognise the project.
3. **Letter case.** Linux treats `Note.md` and `note.md` as two files; Windows and macOS treat them as one. Such a pair created on Linux breaks checkout on Windows.
4. **Forbidden names.** Windows rejects `< > : " | ? *`, a trailing dot or space, and reserved names such as `CON`, `NUL`, `AUX`, `COM1`. A note called `Question: why?.md` made on Linux won't open on Windows.
5. **Long paths.** Windows' 260-character limit can bite in deep folders.
6. **Locked files.** Windows may lock a file that is open in an editor, so the hook's `git pull` at session start fails.
7. **Concurrent sessions.** Working on two machines at once means both write `LAST_SESSION.md` and `THREADS.md`, which leads to merge conflicts on push.
8. **Symlinks.** Symlinks inside the vault often turn into plain text files on Windows.

None of this happens with separate brains. If you must use one brain across all three platforms, take the WSL route (see the box above).

### Credit

Some of the Windows solutions (invoking hooks via EncodedCommand, ignoring line-ending-only differences, pinning LF per file type) were inspired by the Windows support in [avenoxbeyin](https://github.com/avenoxai/avenoxbeyin) (MIT). Thank you, Avenox. 🙏

### Privacy

Over time the vault fills with personal information. Keep it **private**; if you create a git remote, always use `--private`.
