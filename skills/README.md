# Skills

🇹🇷 Türkçe · 🇬🇧 [English ↓](#english) · Kurulum: [INSTALL.md](INSTALL.md)

Skill, Claude Code'a belirli bir iş türü için hazır talimatlar veren bir klasördür. Claude ilgili işi fark edince skill'i yükler ve oradaki iş akışını izler. Bir skill'i `/skill-adı` yazarak elle de çağırabilirsin.

| Skill | Tür | Ne yapar | Bağımlılık |
|---|---|---|---|
| [`game-dev-director`](game-dev-director/SKILL.md) | Skill | Oyun projeleri için teknik direktör iş akışı | Yok. Codex CLI isteğe bağlı |
| [`context-meter`](context-meter/) | Plugin (mod) | Prompt'un altında bağlam doluluğunu gösterir: `ctx █████░░░░░ 100k/200k · 50%` | Yok |

## game-dev-director

Yeni ya da devam eden bir oyun projesinde Claude'u **teknik direktör** gibi çalıştırır. Şunları kapsar:
- **Proje kurtarma:** `docs/ai/HANDOFF.md`, `PROJECT_CONTEXT.md` ve `CURRENT_TASK.md` dosyalarından kaldığı yeri bulur.
- **Planlama:** gereksinimleri, araştırmayı, mimariyi ve milestone planını çıkarır.
- **Devretme:** sınırlı işleri Sonnet subagent'lara, büyük implementasyonu Codex CLI'a verir.
- **Kalite:** debug, inceleme, test ve sürüm öncesi kontrolleri yürütür.
- **Durum takibi:** her checkpoint'te handoff dosyalarını günceller.

Klasör yapısı:
- `SKILL.md`: ana iş akışı.
- `references/`: delegation, codex, state-and-handoff, project-workflow, quality, assets ve spending-and-failures belgeleri. Claude bunları yalnızca gerektiğinde okur.
- `templates/`: `HANDOFF.md`, `CURRENT_TASK.md` ve `CODEX_BRIEF.md` şablonları.

[`agents/`](../agents/) altındaki agent'larla birlikte kullanınca en iyi sonucu verir, ama tek başına da çalışır.

## context-meter

Aktif oturumun ne kadar bağlam kullandığını prompt'un altındaki satırda canlı gösteren küçük bir TypeScript **mod**'u. Bağlam dolmadan önce bir checkpoint almayı ya da işi bir subagent'a devretmeyi hatırlatır. Klasik bir skill değil, plugin olarak kurulur. Ayrıntılar [INSTALL.md](INSTALL.md) dosyasında.

## Daha fazlası yolda

Yeni skill'ler eklendikçe bu listeye girecek.

---

<a id="english"></a>

## English

🇬🇧 English · 🇹🇷 [Türkçe ↑](#skills) · Install: [INSTALL.md](INSTALL.md#english)

A skill is a folder that gives Claude Code ready-made instructions for a particular kind of task. When Claude recognizes that task, it loads the skill and follows its workflow. You can also call a skill by hand with `/skill-name`.

| Skill | Type | What it does | Dependencies |
|---|---|---|---|
| [`game-dev-director`](game-dev-director/SKILL.md) | Skill | Technical-director workflow for game projects | None. Codex CLI optional |
| [`context-meter`](context-meter/) | Plugin (mod) | Shows context usage under the prompt: `ctx █████░░░░░ 100k/200k · 50%` | None |

### game-dev-director

Makes Claude act as **technical director** on a new or continuing game project. It covers:
- **Project recovery:** finds where you left off from `docs/ai/HANDOFF.md`, `PROJECT_CONTEXT.md` and `CURRENT_TASK.md`.
- **Planning:** works out requirements, research, architecture and the milestone plan.
- **Delegation:** hands bounded work to Sonnet subagents and substantial implementation to Codex CLI.
- **Quality:** runs debugging, review, testing and release checks.
- **State tracking:** updates the handoff files at every checkpoint.

Folder layout:
- `SKILL.md`: the main workflow.
- `references/`: delegation, codex, state-and-handoff, project-workflow, quality, assets and spending-and-failures docs. Claude reads them only when needed.
- `templates/`: `HANDOFF.md`, `CURRENT_TASK.md` and `CODEX_BRIEF.md` templates.

It works best together with the agents in [`agents/`](../agents/), but it also works on its own.

### context-meter

A small TypeScript **mod** that shows, live under the prompt, how much context the active session is using. It reminds you to take a checkpoint or delegate to a subagent before the context fills up. It's a plugin, not a classic skill; see [INSTALL.md](INSTALL.md#english) for details.

### More coming

New skills will be added to this list as they are written.
