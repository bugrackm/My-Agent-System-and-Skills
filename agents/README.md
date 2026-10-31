# Agents: orkestrasyon sistemi

🇹🇷 Türkçe · 🇬🇧 [English ↓](#english) · Kurulum: [INSTALL.md](INSTALL.md)

Bu klasör, Claude Code'da **ana oturumu teknik lider** gibi çalıştıran düzeni içerir. Ana model planlar, karar verir ve sonucu kabul eder. Ara işleri ise daha ucuz ve dar kapsamlı çalışanlara devreder.

## Neden?

Ana oturumun bağlamı değerli ve sınırlı. Bir test log'u, büyük bir `git diff` ya da on sayfalık web araması bu bağlamı hızla doldurur. Bu sistemde o çıktılar subagent'ın kendi bağlamında kalır, ana oturuma yalnızca kısa bir özet döner. Sonuç olarak oturumlar daha uzun sürer, daha az sıkıştırılır ve daha ucuza gelir.

## Kim ne yapar

| Rol | Ne zaman | Model |
|---|---|---|
| **Ana Claude** | Mimari, plan, kullanıcıyla konuşma, büyük kararlar, sonucu kabul etme | Senin seçtiğin model (ör. Opus) |
| [`repo-explorer`](repo-explorer.md) | Repo keşfi, dosya arama, git/diff inceleme. Salt okunur | Sonnet · medium |
| [`researcher`](researcher.md) | Dış araştırma, resmi dokümantasyon, güncel API/araç doğrulama. Salt okunur | Sonnet · medium |
| [`reviewer`](reviewer.md) | Biten bir değişikliğin bağımsız incelemesi: doğruluk, güvenlik, regresyon. Salt okunur | Sonnet · high |
| [`sonnet-worker`](sonnet-worker.md) | Küçük, düşük riskli işler: ufak düzenleme, config, rutin doğrulama | Sonnet · medium |
| **Codex CLI** | Büyük, çok dosyalı implementasyon, refactor, zor debug | Codex (ChatGPT aboneliği) |
| [`codex-runner`](codex-runner.md) | Biten bir Codex çalışmasının log'unu okur, çalışma ağacını doğrular, kısa rapor verir. Salt okunur | Sonnet · medium |

`memory-keeper` agent'ı beyin sistemine ait olduğu için [`brain/`](../brain/) altında duruyor.

**Ne zaman devredilir?** Birkaç komutla bitecek işi ana oturum kendisi yapar. Her subagent sıfırdan başlar ve kendi kullanım hakkını harcar. Bu yüzden yalnızca sınırlı, kendi içinde tamamlanan ve çıktısı büyük işler devredilir. Paralel agent sadece gerçekten bağımsız işler için çalıştırılır.

**Salt okunur agent'lar `CLAUDE.md` yüklemez.** `researcher`, `repo-explorer` ve `reviewer` dosyalarında `omitClaudeMd: true` var (Claude Code 2.1.271+). Ana oturuma yazılmış "teknik lider ol, devret" kuralları onların işi değil. İhtiyaç duydukları her kural (gizli bilgi, kapsam sınırı) ya kendi dosyalarında ya da ana oturumun verdiği görev metninde yazar.

## Codex akışı

1. Ana oturum bir `CODEX_BRIEF` yazar: hedef, kapsam, kısıtlar, kabul kriterleri ve kapsam dışı işler.
2. **`codex exec` komutunu ana oturum çalıştırır** ve bitmesini bekler. Bu görev bir subagent'a verilmez, çünkü subagent kendi turu bittiğinde kapanır ve uzun bir Codex çalışmasını sonuna kadar bekleyemez.
3. Çalışma bitince `codex-runner` log'u ve değişiklikleri inceler, testleri çalıştırır ve kısa bir rapor döner.
4. Ana oturum sonucu kabul eder ya da düzeltme ister. Gerekirse işi `reviewer`'a da inceletir.

Codex isteğe bağlıdır. Kurulu değilse büyük işleri ana oturum ya da `sonnet-worker` yapar.

## `CLAUDE.md.template`

Global `~/.claude/CLAUDE.md` için bir başlangıç şablonu. Bu dosya ana modele rolünü, devretme kurallarını, doğru bilgi kaynaklarının öncelik sırasını, `docs/ai/` üzerinden proje kurtarmayı ve güvenlik/maliyet kurallarını anlatır. "Brain (optional)" bölümü beyni kurmadıysan silinebilir.

Temel kurallar:
- Otomatik ücretli API'ye geçiş yok. Codex, ChatGPT aboneliğiyle çalışır, API anahtarına geçmez.
- Açık onay olmadan yıkıcı git işlemi ya da force push yapılmaz.
- Commit ve push yalnızca istendiğinde ve doğrulamadan sonra yapılır.
- Test edilmemiş iş bitmiş sayılmaz.
- Her kural tek yerde yaşar ve bir cümlelik gerekçesiyle yazılır.

---

<a id="english"></a>

## English

🇬🇧 English · 🇹🇷 [Türkçe ↑](#agents-orkestrasyon-sistemi) · Install: [INSTALL.md](INSTALL.md#english)

This folder holds a setup that makes the **main Claude Code session act as technical lead**. The main model plans, decides and accepts the result. It hands the intermediate work to cheaper, narrowly scoped workers.

### Why?

The main session's context is valuable and limited. A test log, a large `git diff` or ten pages of web search fill it up quickly. In this setup that output stays in the subagent's own context, and only a short summary comes back to the main session. As a result, sessions last longer, get compacted less often and cost less.

### Who does what

| Role | When | Model |
|---|---|---|
| **Main Claude** | Architecture, planning, talking to the user, high-impact decisions, accepting results | Your choice (e.g. Opus) |
| [`repo-explorer`](repo-explorer.md) | Repository exploration, file discovery, git/diff inspection. Read-only | Sonnet · medium |
| [`researcher`](researcher.md) | External research, official documentation, current API/tool verification. Read-only | Sonnet · medium |
| [`reviewer`](reviewer.md) | Independent review of a finished change: correctness, security, regressions. Read-only | Sonnet · high |
| [`sonnet-worker`](sonnet-worker.md) | Small, low-risk work: minor edits, config, routine verification | Sonnet · medium |
| **Codex CLI** | Substantial multi-file implementation, refactors, hard debugging | Codex (ChatGPT subscription) |
| [`codex-runner`](codex-runner.md) | Reads a finished Codex run's log, verifies the working tree, returns a short report. Read-only | Sonnet · medium |

The `memory-keeper` agent belongs to the brain system, so it lives under [`brain/`](../brain/).

**When to delegate?** The main session does work itself when a few tool calls finish it. Every subagent starts cold and spends its own usage, so only bounded, self-contained work with large output is delegated. Parallel agents are only for genuinely independent work.

**Read-only agents don't load `CLAUDE.md`.** `researcher`, `repo-explorer` and `reviewer` set `omitClaudeMd: true` (Claude Code 2.1.271+). The "act as technical lead, delegate" rules written for the main session aren't their job. Any rule they need (secrets, scope limits) is in their own file or in the brief the main session gives them.

### The Codex flow

1. The main session writes a `CODEX_BRIEF`: objective, scope, constraints, acceptance criteria and non-goals.
2. **The main session runs `codex exec`** and waits for it to finish. This is never handed to a subagent, because a subagent closes when its turn ends and can't wait out a long Codex run.
3. When the run finishes, `codex-runner` reviews the log and the changes, runs the tests and returns a short report.
4. The main session accepts the result or asks for fixes. If needed, it also has `reviewer` check the work.

Codex is optional. Without it, the main session or `sonnet-worker` handles large tasks.

### `CLAUDE.md.template`

A starting template for your global `~/.claude/CLAUDE.md`. It tells the main model its role, the delegation rules, the priority order of sources of truth, project recovery through `docs/ai/`, and the safety/cost rules. You can delete the "Brain (optional)" section if you didn't install the brain.

Key rules:
- No automatic switch to a paid API. Codex runs on your ChatGPT subscription and never switches to an API key.
- No destructive git operations or force pushes without explicit approval.
- Commit and push only when asked, and only after verification.
- Untested work is not finished.
- Each rule lives in one place, with a one-line reason.
