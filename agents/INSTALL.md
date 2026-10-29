# Agents: kurulum

🇹🇷 Türkçe · 🇬🇧 [English ↓](#english) · Açıklama: [README.md](README.md)

Komutlar repo kök klasöründen çalıştırılır:

```bash
git clone https://github.com/bugrackm/My-Agent-System-and-Skills.git
cd My-Agent-System-and-Skills
```

## 1. Yedek al

```bash
mkdir -p ~/.claude/agents
cp -a ~/.claude/agents ~/.claude/agents.backup-$(date +%F)
[ -f ~/.claude/CLAUDE.md ] && cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup-$(date +%F)
```

## 2. Agent'ları kopyala

```bash
for a in repo-explorer researcher reviewer sonnet-worker codex-runner; do
  if [ -e ~/.claude/agents/$a.md ]; then
    echo "zaten var, atlandı: $a.md (önce farkına bak)"
  else
    cp agents/$a.md ~/.claude/agents/
  fi
done
```

- İstediğin agent'ları seçebilirsin. Codex kullanmayacaksan `codex-runner` gerekmez.
- `git pull` ile güncel kalmak istersen kopyalamak yerine symlink kullan: `ln -s "$PWD/agents/reviewer.md" ~/.claude/agents/reviewer.md`
- `README.md` ve `INSTALL.md` agent değil, onları kopyalama.

## 3. Global `CLAUDE.md`

- **`~/.claude/CLAUDE.md` yoksa:** `cp agents/CLAUDE.md.template ~/.claude/CLAUDE.md`
- **Varsa:** üzerine yazma. Şablondaki bölümleri ("Delegation and context preservation", "Safety / cost" vb.) kendi dosyana ekle. Bunu agent'ına yaptırıyorsan değişiklikleri önce sana göstermesini iste.
- Beyni kurmayacaksan "Brain (optional)" bölümünü sil. "Memory protocol" bölümünde yalnızca vault/memory-keeper'a özgü kısımları ("Keep Brain global memory compact…" ve "Vault writes are delegated…" paragrafları) çıkar; repo-yerel kalıcı doküman kurallarını koru.

## 4. Codex CLI (isteğe bağlı)

```bash
npm install -g @openai/codex
codex login          # "Sign in with ChatGPT" seç; API anahtarı kullanma
codex --version
```

Kurallar `CLAUDE.md` içinde tanımlı: `codex exec` komutunu ana oturum çalıştırır, `codex-runner` sonucu doğrular ve sistem asla kendiliğinden ücretli API'ye geçmez.

## 5. Doğrula

Yeni bir Claude Code oturumu aç ve `/agents` yaz. Kurduğun agent'lar listede görünmeli. Ardından şunu dene: *"repo-explorer ile bu repodaki dosya yapısını özetle."*

---

<a id="english"></a>

## English

🇬🇧 English · 🇹🇷 [Türkçe ↑](#agents-kurulum) · Overview: [README.md](README.md#english)

Run the commands from the repo root:

```bash
git clone https://github.com/bugrackm/My-Agent-System-and-Skills.git
cd My-Agent-System-and-Skills
```

### 1. Back up

```bash
mkdir -p ~/.claude/agents
cp -a ~/.claude/agents ~/.claude/agents.backup-$(date +%F)
[ -f ~/.claude/CLAUDE.md ] && cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup-$(date +%F)
```

### 2. Copy the agents

```bash
for a in repo-explorer researcher reviewer sonnet-worker codex-runner; do
  if [ -e ~/.claude/agents/$a.md ]; then
    echo "already exists, skipped: $a.md (diff it first)"
  else
    cp agents/$a.md ~/.claude/agents/
  fi
done
```

- Pick only the agents you want. If you won't use Codex, you don't need `codex-runner`.
- To stay current with `git pull`, symlink instead of copying: `ln -s "$PWD/agents/reviewer.md" ~/.claude/agents/reviewer.md`
- `README.md` and `INSTALL.md` are not agents; don't copy them.

### 3. Global `CLAUDE.md`

- **If `~/.claude/CLAUDE.md` doesn't exist:** `cp agents/CLAUDE.md.template ~/.claude/CLAUDE.md`
- **If it exists:** don't overwrite it. Add the template's sections ("Delegation and context preservation", "Safety / cost", etc.) to your own file. If an agent does this for you, ask it to show you the changes first.
- If you won't install the brain, delete the "Brain (optional)" section. In "Memory protocol", remove only the vault/memory-keeper parts (the "Keep Brain global memory compact…" and "Vault writes are delegated…" paragraphs) and keep the repo-local durable-docs rules.

### 4. Codex CLI (optional)

```bash
npm install -g @openai/codex
codex login          # choose "Sign in with ChatGPT"; don't use an API key
codex --version
```

The rules are defined in `CLAUDE.md`: the main session runs `codex exec`, `codex-runner` verifies the result, and the system never switches to a paid API on its own.

### 5. Verify

Open a new Claude Code session and type `/agents`. The agents you installed should be listed. Then try: *"Use repo-explorer to summarize this repo's file structure."*
