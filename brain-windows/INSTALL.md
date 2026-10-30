# Brain for Windows: kurulum

🇹🇷 Türkçe · 🇬🇧 [English ↓](#english) · Açıklama: [README.md](README.md)

**Gereksinimler:**
- Claude Code (Windows'ta, WSL dışında çalışan sürüm)
- [Python 3.10+](https://www.python.org/downloads/windows/) (python.org kurulumu önerilir)
- [Git for Windows](https://git-scm.com/download/win). Vault senkronu için ve Claude Code'un Bash aracı için gerekir.

Komutlar **PowerShell** içindir. Hepsi repo kök klasöründen çalıştırılır:

```powershell
git clone https://github.com/bugrackm/My-Agent-System-and-Skills.git
cd My-Agent-System-and-Skills
python --version      # 3.10 veya üstü yazmalı
```

`python --version` Microsoft Store'u açıyor ya da hata veriyorsa Python'u python.org'dan kur ("Add python.exe to PATH" kutusunu işaretle). Hook'lar, aşağıdaki 4. adımda `merge-settings.py`'yi hangi Python ile çalıştırırsan **o Python'un tam yolunu** kullanır.

## 1. Vault'un yerini seç

```powershell
$env:BRAIN_HOME = "$HOME\Brain"     # istersen başka bir yol seç (OneDrive dışında olsun)
if (Test-Path $env:BRAIN_HOME) { throw "DUR: $env:BRAIN_HOME zaten var, başka bir yol seç" }
```

## 2. Vault'u ve çalışma zamanını kopyala

```powershell
Copy-Item -Recurse brain-windows\vault-template $env:BRAIN_HOME
Copy-Item -Recurse brain-windows\runtime "$env:BRAIN_HOME\runtime"
```

## 3. Hook'u ve agent'ı Claude Code'a kopyala

```powershell
python brain-windows\update-runtime.py --brain-home $env:BRAIN_HOME --dry-run   # önce ne olacağını gör
python brain-windows\update-runtime.py --brain-home $env:BRAIN_HOME
```

Betik `runtime\hooks\brain-memory.py` dosyasını `~\.claude\hooks\` içine, `runtime\agents\memory-keeper.md` dosyasını `~\.claude\agents\` içine kopyalar. Orada farklı bir dosya varsa önce yedekler. Windows'ta symlink yerine kopya kullanılır.

## 4. Hook'ları `settings.json`'a ekle

```powershell
python brain-windows\merge-settings.py --brain-home $env:BRAIN_HOME --dry-run   # önce ne değişeceğini gör
python brain-windows\merge-settings.py --brain-home $env:BRAIN_HOME
```

Betik önce `settings.json` dosyanı yedekler. Ardından yalnızca eksik olan 4 hook'u (SessionStart, UserPromptSubmit, Stop, SessionEnd) PowerShell üzerinden çalışacak şekilde ve `env.BRAIN_HOME` ile `env.BRAIN_PYTHON` değerlerini ekler. Diğer ayarlarına dokunmaz. Tekrar çalıştırmak güvenlidir. Vault ya da Python OneDrive içindeyse veya `git` bulunamazsa uyarır.

## 5. `CLAUDE.md`'ye hafıza kurallarını ekle

Ana modelin checkpoint'lerde `memory-keeper`'ı çalıştırmayı bilmesi için [`agents/CLAUDE.md.template`](../agents/CLAUDE.md.template) içindeki **"Brain (optional)"** ve **"Memory protocol"** bölümlerini `~\.claude\CLAUDE.md` dosyana ekle. Dosya yoksa şablonun tamamını kopyalayabilirsin. Şablonda varsayılan vault yolu `~/Documents/Brain` yazıyor; Windows'ta bunu kendi yolunla (varsayılan `%USERPROFILE%\Brain`) değiştir.

## 6. Kendini tanıt

`$env:BRAIN_HOME\850-Memory\CORE.md` dosyasını aç ve kısaca doldur: kim olduğun, neyle uğraştığın, nasıl çalışmayı sevdiğin. Diğer hafıza dosyalarını `memory-keeper` dolduracak.

## 7. Senkronizasyon (isteğe bağlı)

```powershell
cd $env:BRAIN_HOME
git init; git add -A; git commit -m "brain: initial vault"
gh repo create my-brain --private --source . --push     # MUTLAKA --private
```

Vault bir git reposu olduğunda hook oturum başında `pull` yapar, `memory-keeper` de yazdıktan sonra commit ve push eder. Bu beyni **yalnızca Windows makineleri arasında** paylaş. Linux veya macOS ile aynı vault'u paylaşma; nedenleri [README.md](README.md#neden-windows-ile-linuxmacos-beyinlerini-ayrı-tutmalısın)'de. Üç platformda tek beyin istiyorsan WSL içinde [`brain/`](../brain/INSTALL.md) kur.

## 8. Doğrula

```powershell
python "$env:BRAIN_HOME\runtime\tools\vault-doctor.py"            # beklenen: vault-doctor: OK
python -m unittest discover -s "$env:BRAIN_HOME\runtime\tests"   # beklenen: OK
```

Vault'taki kopyada kurulum betikleri olmadığı için bazı testler `skipped` olarak atlanır; bu normal.

Yeni bir Claude Code oturumu aç ve *"bağlamında hangi [Brain …] blokları var?"* diye sor. `[Brain — Last Session]`, `[Brain — Active Threads]` ve `[Brain memory policy]` görünmeli. Görünmüyorsa Claude Code'u `claude --debug` ile başlatıp hook hatalarına bak.

## Güncelleme

Repoyu güncelledikten sonra yeni çalışma zamanını vault'a kopyala ve kurulu kopyaları yenile:

```powershell
cd <repo-klasörü>                    # My-Agent-System-and-Skills
$env:BRAIN_HOME = "$HOME\Brain"     # vault'un yolu
git pull
Copy-Item -Recurse -Force brain-windows\runtime\* "$env:BRAIN_HOME\runtime"
python brain-windows\update-runtime.py --brain-home $env:BRAIN_HOME
```

Python'u başka bir sürüme veya yola taşıdıysan hook komutlarını yeniden yaz:

```powershell
python brain-windows\merge-settings.py --brain-home $env:BRAIN_HOME --update
```

## Kaldırma

`~\.claude\settings.json` içinden `brain-memory.py` hook'larını sil (ya da `merge-settings.py`'nin aldığı yedeği geri yükle). Ardından `~\.claude\hooks\brain-memory.py`, `~\.claude\agents\memory-keeper.md` dosyalarını ve `~\.claude\brain-state` klasörünü sil. Vault'un kendisi sende kalır.

---

<a id="english"></a>

## English

🇬🇧 English · 🇹🇷 [Türkçe ↑](#brain-for-windows-kurulum) · Overview: [README.md](README.md#english)

**Requirements:**
- Claude Code (the native Windows build, not inside WSL)
- [Python 3.10+](https://www.python.org/downloads/windows/) (the python.org installer is recommended)
- [Git for Windows](https://git-scm.com/download/win), for vault sync and for Claude Code's Bash tool

The commands are for **PowerShell**. Run them all from the repo root:

```powershell
git clone https://github.com/bugrackm/My-Agent-System-and-Skills.git
cd My-Agent-System-and-Skills
python --version      # should print 3.10 or later
```

If `python --version` opens the Microsoft Store or fails, install Python from python.org (tick "Add python.exe to PATH"). The hooks use **the full path of whichever Python** you run `merge-settings.py` with in step 4.

### 1. Choose where the vault lives

```powershell
$env:BRAIN_HOME = "$HOME\Brain"     # pick another path if you like (keep it outside OneDrive)
if (Test-Path $env:BRAIN_HOME) { throw "STOP: $env:BRAIN_HOME already exists, choose another path" }
```

### 2. Copy the vault and the runtime

```powershell
Copy-Item -Recurse brain-windows\vault-template $env:BRAIN_HOME
Copy-Item -Recurse brain-windows\runtime "$env:BRAIN_HOME\runtime"
```

### 3. Copy the hook and the agent into Claude Code

```powershell
python brain-windows\update-runtime.py --brain-home $env:BRAIN_HOME --dry-run   # see what would happen first
python brain-windows\update-runtime.py --brain-home $env:BRAIN_HOME
```

The script copies `runtime\hooks\brain-memory.py` into `~\.claude\hooks\` and `runtime\agents\memory-keeper.md` into `~\.claude\agents\`. If a different file is already there, it backs it up first. Windows uses copies instead of symlinks.

### 4. Add the hooks to `settings.json`

```powershell
python brain-windows\merge-settings.py --brain-home $env:BRAIN_HOME --dry-run   # see what would change first
python brain-windows\merge-settings.py --brain-home $env:BRAIN_HOME
```

The script backs up your `settings.json` first. Then it adds only the missing 4 hooks (SessionStart, UserPromptSubmit, Stop, SessionEnd), set to run in PowerShell, plus `env.BRAIN_HOME` and `env.BRAIN_PYTHON`. It leaves your other settings alone. Running it again is safe. It warns if the vault or Python lives inside OneDrive, or if `git` can't be found.

### 5. Add the memory rules to `CLAUDE.md`

So the main model knows to run `memory-keeper` at checkpoints, add the **"Brain (optional)"** and **"Memory protocol"** sections from [`agents/CLAUDE.md.template`](../agents/CLAUDE.md.template) to your `~\.claude\CLAUDE.md`. If you don't have that file, you can copy the whole template. The template names `~/Documents/Brain` as the default vault path; on Windows, replace it with your path (default `%USERPROFILE%\Brain`).

### 6. Introduce yourself

Open `$env:BRAIN_HOME\850-Memory\CORE.md` and fill it in briefly: who you are, what you work on, how you like to work. `memory-keeper` will fill in the other memory files.

### 7. Sync (optional)

```powershell
cd $env:BRAIN_HOME
git init; git add -A; git commit -m "brain: initial vault"
gh repo create my-brain --private --source . --push     # ALWAYS --private
```

When the vault is a git repo, the hook pulls at session start and `memory-keeper` commits and pushes after writing. Share this brain **between Windows machines only**. Don't share the same vault with Linux or macOS; [README.md](README.md#why-keep-windows-and-linuxmacos-brains-separate) explains why. For one brain across all three platforms, install [`brain/`](../brain/INSTALL.md#english) inside WSL.

### 8. Verify

```powershell
python "$env:BRAIN_HOME\runtime\tools\vault-doctor.py"            # expected: vault-doctor: OK
python -m unittest discover -s "$env:BRAIN_HOME\runtime\tests"   # expected: OK
```

The vault copy doesn't include the install scripts, so a few tests are `skipped`; that's expected.

Open a new Claude Code session and ask *"which [Brain …] blocks are in your context?"* You should see `[Brain — Last Session]`, `[Brain — Active Threads]` and `[Brain memory policy]`. If they're missing, start Claude Code with `claude --debug` and look for hook errors.

### Updating

After updating the repo, copy the new runtime into the vault and refresh the installed copies:

```powershell
cd <repo-folder>                     # My-Agent-System-and-Skills
$env:BRAIN_HOME = "$HOME\Brain"     # your vault path
git pull
Copy-Item -Recurse -Force brain-windows\runtime\* "$env:BRAIN_HOME\runtime"
python brain-windows\update-runtime.py --brain-home $env:BRAIN_HOME
```

If you moved Python to another version or path, rewrite the hook commands:

```powershell
python brain-windows\merge-settings.py --brain-home $env:BRAIN_HOME --update
```

### Uninstall

Delete the `brain-memory.py` hooks from `~\.claude\settings.json` (or restore the backup `merge-settings.py` made). Then delete `~\.claude\hooks\brain-memory.py`, `~\.claude\agents\memory-keeper.md` and the `~\.claude\brain-state` folder. Your vault stays with you.
