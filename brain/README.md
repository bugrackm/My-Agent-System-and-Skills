# Brain: kalıcı hafıza sistemi

🇹🇷 Türkçe · 🇬🇧 [English ↓](#english) · Kurulum: [INSTALL.md](INSTALL.md)

Claude Code her oturuma sıfırdan başlar. Beyin, oturumlar arasındaki sürekliliği sağlar: ne yaptığını, nerede kaldığını, hangi işlerin açık olduğunu ve neler öğrendiğini düz Markdown dosyalarında tutar, her yeni oturumun başında da bunları Claude'a hatırlatır.

> **İlham:** Bu sistem Avenox'un [**avenoxbeyin**](https://github.com/avenoxai/avenoxbeyin) projesinden esinlenerek yapıldı. avenoxbeyin çok daha kapsamlı: Obsidian ile ikinci beyin, birden fazla AI istemcisi, Windows/macOS/Linux desteği, link ve video yakalama, arama ve tek komutla kurulum sunuyor. Buradaki sürüm **bilerek basit**: yalnızca Claude Code, tek bir Python hook dosyası, tek bir hafıza agent'ı ve düz klasörler. Büyük bir sistemle uğraşmak istemiyorsan bu sürüm birkaç dakikada kurulur. Daha fazlasını istiyorsan avenoxbeyin'e bak.

## Parçalar

| Parça | Dosya | Görevi |
|---|---|---|
| **Vault** | `vault-template/` → `~/Documents/Brain` | Hafızanın kendisi: Markdown klasörleri, tercihen private bir git reposu |
| **Hook** | `runtime/hooks/brain-memory.py` | Claude Code olaylarında çalışır, bağlamı ekler, hatırlatma yapar |
| **memory-keeper** | `runtime/agents/memory-keeper.md` | Hafızayı yazan Sonnet agent'ı: vault'a yazar, commit'ler ve push'lar |
| **vault-doctor** | `runtime/tools/vault-doctor.py` | Salt okunur sağlık kontrolü: kırık linkler, eski işler, dosya boyutları, sızan anahtarlar, eksik kurulum |
| **transcript-digest** | `runtime/tools/transcript-digest.py` | Yarım kalmış bir oturumun kaydını kısa ve anahtarlardan temizlenmiş bir özete çevirir |
| **merge-settings** | `merge-settings.py` | Hook'ları mevcut `settings.json` dosyana güvenle ekler |

## Bir oturum nasıl akar

1. **SessionStart:** Vault bir git reposuysa hook önce `git pull --ff-only` yapar (en fazla 5 sn). Ardından bağlama şu blokları ekler:
   - `[Brain — Last Session]`: son oturumun kısa özeti. Repoda daha yeni commit'ler varsa *STALE* olarak işaretlenir.
   - `[Brain — Active Threads]`: açık işlerin listesi.
   - Proje bilgisi: çalışma klasöründe `docs/ai/HANDOFF.md` varsa ondan bir alıntı ve kurtarma sırası.
   - Uyarılar, sadece gerektiğinde: `[Brain sync warning]`, `[Brain recovery required]`, `[Brain runtime drift]`, `[Brain health warning]`, `[Brain continuity warning]` (önceki anlamlı oturum kalıcı durumu güncellemeden bitmiş).
2. **UserPromptSubmit:** 12. ve 24. mesajda bir checkpoint hatırlatması gösterir.
3. **Stop:** Son hafıza yazımından bu yana 4 veya daha fazla mesaj geçtiyse, Claude'dan bir kereliğine `memory-keeper`'ı arka planda çalıştırmasını ister.
4. **SessionEnd:** Uzun bir oturum hafızaya hiç yazmadan kapandıysa, kayıt yolunu bir işarete yazar. Bir sonraki oturum `[Brain recovery required]` uyarısını görür ve `memory-keeper`'ı kurtarma modunda çalıştırır. İşaretler 7 gün sonra silinir.

Bağlam sıkıştırıldıktan (compaction) sonra hook `[Brain compaction checkpoint]` bloğunu ekler ve hafızanın güncellenmesini ister.

Hook her zaman **fail-open** çalışır: bir şey bozulursa uyarı verir ama Claude Code'u asla durdurmaz.

## Vault yapısı

```text
~/Documents/Brain/
├── VAULT.md               protokol: ne, ne zaman, nereye yazılır
├── 000-Inbox/             ham notlar, sonra ayıklanır
├── 100-Command-Center/    DASHBOARD, giriş noktası
├── 200-Goals/             uzun vadeli hedefler
├── 300-Projects/          PROJECT_INDEX: proje yolları ve durumları (kaynak kod değil)
├── 500-Knowledge/         uzun ömürlü teknik notlar
├── 600-Arsenal/           tekrar kullanılabilir iş akışları ve komutlar
├── 800-Mind/              çalışma tarzın ve tercihlerin
├── 850-Memory/            süreklilik çekirdeği
│   ├── CORE.md            kim olduğun, kalıcı bağlam (nadiren değişir)
│   ├── LAST_SESSION.md    son oturumlar (kısa, en fazla 3000 karakter)
│   ├── THREADS.md         açık işler ve durumları
│   ├── JOURNAL.md         yalnızca önemli gelişmeler (250 satırdan sonra arşivlenir)
│   └── MEMORY_PROTOCOL.md hafıza kuralları
├── 900-Archive/           kapanmış işler
├── Templates/
└── runtime/               hook, agent ve araçlar (bu repodan kopyalanır)
```

## Doğru bilgi kaynağının öncelik sırası

1. Projenin gerçek, güncel durumu: çalışma ağacı ve repo.
2. Projenin kendi dokümanları: `docs/ai/HANDOFF.md`, `PROJECT_CONTEXT.md`, `CURRENT_TASK.md`.
3. Beyin vault'u.
4. Claude Code'un kendi otomatik hafızası.
5. Eski sohbet geçmişi.

Beyin projenin kaynak kodunu ya da tüm dokümantasyonunu kopyalamaz. Sadece projenin nerede olduğunu, ne durumda olduğunu ve sıradaki adımı tutar.

## Gizlilik

Vault zamanla kişisel bilgilerle dolar. **Private** tut. Birden fazla bilgisayar kullanıyorsan private bir git reposu üzerinden senkronize et. `vault-doctor` her çalıştığında vault'ta `sk-`, `ghp_`, `AKIA` gibi anahtar kalıplarını da arar.

---

<a id="english"></a>

## English

🇬🇧 English · 🇹🇷 [Türkçe ↑](#brain-kalıcı-hafıza-sistemi) · Install: [INSTALL.md](INSTALL.md#english)

Claude Code starts every session from scratch. The brain provides continuity between sessions: it keeps what you did, where you left off, which work is still open and what you learned in plain Markdown files, and reminds Claude of them at the start of every new session.

> **Inspiration:** This system was inspired by [**avenoxbeyin**](https://github.com/avenoxai/avenoxbeyin) by Avenox. avenoxbeyin is much larger: an Obsidian-based second brain with several AI clients, Windows/macOS/Linux support, link and video capture, search and one-command installation. The version here is **deliberately simple**: Claude Code only, a single Python hook file, one memory agent and plain folders. If you don't want to deal with a big system, this one installs in a few minutes. If you need more, look at avenoxbeyin.

### Components

| Component | File | Job |
|---|---|---|
| **Vault** | `vault-template/` → `~/Documents/Brain` | The memory itself: Markdown folders, ideally a private git repo |
| **Hook** | `runtime/hooks/brain-memory.py` | Runs on Claude Code events, adds context, shows reminders |
| **memory-keeper** | `runtime/agents/memory-keeper.md` | The Sonnet agent that writes memory: writes to the vault, commits and pushes |
| **vault-doctor** | `runtime/tools/vault-doctor.py` | Read-only health check: broken links, stale threads, file sizes, leaked keys, incomplete install |
| **transcript-digest** | `runtime/tools/transcript-digest.py` | Turns the transcript of an unfinished session into a short summary with keys removed |
| **merge-settings** | `merge-settings.py` | Safely adds the hooks to your existing `settings.json` |

### How a session flows

1. **SessionStart:** if the vault is a git repo, the hook first runs `git pull --ff-only` (capped at 5 s). Then it adds these blocks to the context:
   - `[Brain — Last Session]`: a short summary of the last session. It's marked *STALE* if the repo has newer commits.
   - `[Brain — Active Threads]`: the list of open work.
   - Project info: if the working directory has `docs/ai/HANDOFF.md`, an excerpt from it plus the recovery order.
   - Warnings, only when needed: `[Brain sync warning]`, `[Brain recovery required]`, `[Brain runtime drift]`, `[Brain health warning]`, `[Brain continuity warning]` (a previous meaningful session ended without updating durable state).
2. **UserPromptSubmit:** shows a checkpoint reminder at the 12th and 24th prompt.
3. **Stop:** if 4 or more prompts have passed since the last memory write, it asks Claude once to run `memory-keeper` in the background.
4. **SessionEnd:** if a long session closed without ever writing memory, it writes the transcript path to a marker. The next session sees a `[Brain recovery required]` warning and runs `memory-keeper` in recovery mode. Markers are deleted after 7 days.

After the context is compacted, the hook adds a `[Brain compaction checkpoint]` block and asks for memory to be updated.

The hook is always **fail-open**: if something breaks, it warns but never blocks Claude Code.

### Vault layout

```text
~/Documents/Brain/
├── VAULT.md               protocol: what to write, when and where
├── 000-Inbox/             raw notes, sorted later
├── 100-Command-Center/    DASHBOARD, the entry point
├── 200-Goals/             long-term goals
├── 300-Projects/          PROJECT_INDEX: project paths and status (not source code)
├── 500-Knowledge/         long-lived technical notes
├── 600-Arsenal/           reusable workflows and commands
├── 800-Mind/              your working style and preferences
├── 850-Memory/            the continuity core
│   ├── CORE.md            who you are, lasting context (rarely changes)
│   ├── LAST_SESSION.md    recent sessions (short, at most 3000 characters)
│   ├── THREADS.md         open work and its status
│   ├── JOURNAL.md         meaningful developments only (archived after 250 lines)
│   └── MEMORY_PROTOCOL.md the memory rules
├── 900-Archive/           closed work
├── Templates/
└── runtime/               hook, agent and tools (copied from this repo)
```

### Priority order of sources of truth

1. The project's actual current state: the working tree and repo.
2. The project's own docs: `docs/ai/HANDOFF.md`, `PROJECT_CONTEXT.md`, `CURRENT_TASK.md`.
3. The brain vault.
4. Claude Code's native auto-memory.
5. Old chat history.

The brain never copies a project's source code or full documentation. It only records where the project is, what state it's in and the next step.

### Privacy

Over time the vault fills with personal information. Keep it **private**. If you use more than one computer, sync it through a private git repo. Every time `vault-doctor` runs, it also scans the vault for key patterns such as `sk-`, `ghp_` and `AKIA`.
