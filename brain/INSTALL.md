# Brain: kurulum

🇹🇷 Türkçe · 🇬🇧 [English ↓](#english) · Açıklama: [README.md](README.md)

**Gereksinimler:** Claude Code, Python 3.9+ ve git. Komutlar Linux ve macOS içindir. Hepsi repo kök klasöründen çalıştırılır:

```bash
git clone https://github.com/bugrackm/My-Agent-System-and-Skills.git
cd My-Agent-System-and-Skills
```

## 1. Vault'un yerini seç

```bash
export BRAIN_HOME="$HOME/Documents/Brain"     # istersen başka bir yol seç
[ -e "$BRAIN_HOME" ] && echo "DUR: $BRAIN_HOME zaten var, başka bir yol seç"
```

## 2. Vault'u ve çalışma zamanını kopyala

```bash
mkdir -p "$(dirname "$BRAIN_HOME")"
cp -r brain/vault-template "$BRAIN_HOME"
cp -r brain/runtime "$BRAIN_HOME/runtime"
```

## 3. Hook'u ve agent'ı Claude Code'a bağla

```bash
mkdir -p ~/.claude/hooks ~/.claude/agents
ln -s "$BRAIN_HOME/runtime/hooks/brain-memory.py"  ~/.claude/hooks/brain-memory.py
ln -s "$BRAIN_HOME/runtime/agents/memory-keeper.md" ~/.claude/agents/memory-keeper.md
```

Symlink yerine kopya da kullanabilirsin. Symlink'in avantajı, vault'taki `runtime/` güncellendiğinde Claude Code'un otomatik olarak yeni sürümü kullanması.

## 4. Hook'ları `settings.json`'a ekle

```bash
python3 brain/merge-settings.py --brain-home "$BRAIN_HOME" --dry-run   # önce ne değişeceğini gör
python3 brain/merge-settings.py --brain-home "$BRAIN_HOME"
```

Betik önce `settings.json` dosyanı yedekler. Ardından yalnızca eksik olan 4 hook'u (SessionStart, UserPromptSubmit, Stop, SessionEnd) ve `env.BRAIN_HOME` değerini ekler. Diğer ayarlarına dokunmaz. Tekrar çalıştırmak güvenlidir.

## 5. `CLAUDE.md`'ye hafıza kurallarını ekle

Ana modelin checkpoint'lerde `memory-keeper`'ı çalıştırmayı bilmesi için [`agents/CLAUDE.md.template`](../agents/CLAUDE.md.template) içindeki **"Brain (optional)"** ve **"Memory protocol"** bölümlerini `~/.claude/CLAUDE.md` dosyana ekle. Dosya yoksa şablonun tamamını kopyalayabilirsin.

## 6. Kendini tanıt

`$BRAIN_HOME/850-Memory/CORE.md` dosyasını aç ve kısaca doldur: kim olduğun, neyle uğraştığın, nasıl çalışmayı sevdiğin. Diğer hafıza dosyalarını `memory-keeper` dolduracak.

## 7. Senkronizasyon (isteğe bağlı ama önerilir)

```bash
cd "$BRAIN_HOME"
git init && git add -A && git commit -m "brain: initial vault"
gh repo create my-brain --private --source . --push     # MUTLAKA --private
```

Vault bir git reposu olduğunda hook oturum başında `pull` yapar, `memory-keeper` de yazdıktan sonra commit ve push eder. Böylece birden fazla bilgisayarda aynı beyni kullanabilirsin. Diğer makinede repoyu aynı yola klonlayıp 3. ve 4. adımları tekrarlaman yeterli.

## 8. Doğrula

```bash
python3 "$BRAIN_HOME/runtime/tools/vault-doctor.py"            # beklenen: vault-doctor: OK
python3 -m unittest discover -s "$BRAIN_HOME/runtime/tests"   # beklenen: OK
```

Yeni bir Claude Code oturumu aç ve *"bağlamında hangi [Brain …] blokları var?"* diye sor. `[Brain — Last Session]`, `[Brain — Active Threads]` ve `[Brain memory policy]` görünmeli.

## Kaldırma

`~/.claude/settings.json` içinden `brain-memory.py` hook'larını sil (ya da `merge-settings.py`'nin aldığı yedeği geri yükle). Ardından iki symlink'i ve `~/.claude/brain-state` klasörünü sil. Vault'un kendisi sende kalır.

---

<a id="english"></a>

## English

🇬🇧 English · 🇹🇷 [Türkçe ↑](#brain-kurulum) · Overview: [README.md](README.md#english)

**Requirements:** Claude Code, Python 3.9+ and git. The commands are for Linux and macOS. Run them all from the repo root:

```bash
git clone https://github.com/bugrackm/My-Agent-System-and-Skills.git
cd My-Agent-System-and-Skills
```

### 1. Choose where the vault lives

```bash
export BRAIN_HOME="$HOME/Documents/Brain"     # pick another path if you like
[ -e "$BRAIN_HOME" ] && echo "STOP: $BRAIN_HOME already exists, choose another path"
```

### 2. Copy the vault and the runtime

```bash
mkdir -p "$(dirname "$BRAIN_HOME")"
cp -r brain/vault-template "$BRAIN_HOME"
cp -r brain/runtime "$BRAIN_HOME/runtime"
```

### 3. Connect the hook and the agent to Claude Code

```bash
mkdir -p ~/.claude/hooks ~/.claude/agents
ln -s "$BRAIN_HOME/runtime/hooks/brain-memory.py"  ~/.claude/hooks/brain-memory.py
ln -s "$BRAIN_HOME/runtime/agents/memory-keeper.md" ~/.claude/agents/memory-keeper.md
```

Copies work too. The advantage of symlinks is that when `runtime/` in the vault is updated, Claude Code picks up the new version automatically.

### 4. Add the hooks to `settings.json`

```bash
python3 brain/merge-settings.py --brain-home "$BRAIN_HOME" --dry-run   # see what would change first
python3 brain/merge-settings.py --brain-home "$BRAIN_HOME"
```

The script backs up your `settings.json` first. Then it adds only the missing 4 hooks (SessionStart, UserPromptSubmit, Stop, SessionEnd) and `env.BRAIN_HOME`. It leaves your other settings alone. Running it again is safe.

### 5. Add the memory rules to `CLAUDE.md`

So the main model knows to run `memory-keeper` at checkpoints, add the **"Brain (optional)"** and **"Memory protocol"** sections from [`agents/CLAUDE.md.template`](../agents/CLAUDE.md.template) to your `~/.claude/CLAUDE.md`. If you don't have that file, you can copy the whole template.

### 6. Introduce yourself

Open `$BRAIN_HOME/850-Memory/CORE.md` and fill it in briefly: who you are, what you work on, how you like to work. `memory-keeper` will fill in the other memory files.

### 7. Sync (optional, recommended)

```bash
cd "$BRAIN_HOME"
git init && git add -A && git commit -m "brain: initial vault"
gh repo create my-brain --private --source . --push     # ALWAYS --private
```

When the vault is a git repo, the hook pulls at session start and `memory-keeper` commits and pushes after writing. That way you can use the same brain on several computers. On another machine, clone the repo to the same path and repeat steps 3 and 4.

### 8. Verify

```bash
python3 "$BRAIN_HOME/runtime/tools/vault-doctor.py"            # expected: vault-doctor: OK
python3 -m unittest discover -s "$BRAIN_HOME/runtime/tests"   # expected: OK
```

Open a new Claude Code session and ask *"which [Brain …] blocks are in your context?"* You should see `[Brain — Last Session]`, `[Brain — Active Threads]` and `[Brain memory policy]`.

### Uninstall

Delete the `brain-memory.py` hooks from `~/.claude/settings.json` (or restore the backup `merge-settings.py` made). Then delete the two symlinks and the `~/.claude/brain-state` folder. Your vault stays with you.
