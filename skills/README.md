# Skills

🇹🇷 Türkçe · 🇬🇧 [English ↓](#english) · Kurulum: [INSTALL.md](INSTALL.md)

Skill, Claude Code'a belirli bir iş türü için hazır talimatlar veren bir klasördür. Claude ilgili işi fark edince skill'i yükler ve oradaki iş akışını izler. Bir skill'i `/skill-adı` yazarak elle de çağırabilirsin.

| Skill | Tür | Ne yapar | Bağımlılık |
|---|---|---|---|
| [`game-dev-director`](game-dev-director/SKILL.md) | Skill | Oyun projeleri için teknik lider iş akışı (aşama, kapı, playtest) | Yok. Codex CLI isteğe bağlı |
| [`context-meter`](context-meter/) | Plugin (mod) | Prompt'un altında bağlam doluluğunu gösterir: `ctx █████░░░░░ 100k/200k · 50%` | Yok |

## game-dev-director

Yeni ya da devam eden bir oyun projesinde Claude'u **teknik lider** gibi çalıştırır (v5). Temeli bir oyun geliştirme kılavuzu: riskli varsayımı en ucuz yoldan test et, daha pahalı işe ancak kanıt geldikçe geç. Önce "eğlenceli mi?", sanat, meta ve cila en son.
- **Aşama ve kapı:** proje hangi aşamada (fikir, prototip, dikey dilim, üretim, cila, sınırlı yayın, bakım) bilinir. Bir aşamadan çıkış takvimle değil kanıtla olur: devam, tekrar dene ya da öldür.
- **İstek gelince:** Claude önce isteğin özellik sırasında nereye düştüğünü, hangi kapıyı atladığını ve daha ucuz bir öğrenme yolu olup olmadığını söyler. Karar kullanıcının.
- **Kapsam:** pahalı denemeye zaman kutusu ve öldürme ölçütü; her özellik bir ana ilkeye (pillar) hizmet eder; yeni fikirler önce kesme listesine; ikincil mekanikler tek tek.
- **"Bitti":** çalışıyor + iyi hissettiriyor + gerçek cihazda denendi + başkası oynadı. Playtest kapıları ve kontrol listesi dahil.
- **Proje kurtarma ve durum takibi:** `docs/ai/` dosyalarından kaldığı yeri bulur, her checkpoint'te günceller.

Klasör yapısı:
- `SKILL.md`: ana iş akışı.
- `references/`: phases-and-ladder (aşamalar, kapılar, 16 basamaklı özellik sırası, sanatın zamanı), playtest, project-workflow, state-and-handoff, quality, delegation, codex, assets, spending-and-failures. Claude bunları yalnızca gerektiğinde okur.
- `templates/`: `ONE_PAGE.md` (vizyon, ana ilkeler, kesme listesi, "1.0 bitti" tanımı), `HANDOFF.md`, `CURRENT_TASK.md` ve `CODEX_BRIEF.md`.

Genel kurallar (kaynak önceliği, devretme, git, maliyet) skill'de tekrarlanmaz, global `CLAUDE.md`'de durur ([`agents/CLAUDE.md.template`](../agents/CLAUDE.md.template)).

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
| [`game-dev-director`](game-dev-director/SKILL.md) | Skill | Technical-lead workflow for game projects (phases, gates, playtests) | None. Codex CLI optional |
| [`context-meter`](context-meter/) | Plugin (mod) | Shows context usage under the prompt: `ctx █████░░░░░ 100k/200k · 50%` | None |

### game-dev-director

Makes Claude act as **technical lead** on a new or continuing game project (v5). Its core is a game-development playbook: test the riskiest assumption as cheaply as possible and move to more expensive work only as evidence arrives. "Is it fun?" first; art, meta and polish last.
- **Phase and gate:** the project's phase is known (idea, prototype, vertical slice, production, polish, limited release, upkeep). A phase is left on evidence, not on the calendar: continue, retry or kill.
- **When a request arrives:** Claude first says where it sits in the build order, which gate it skips, and whether a cheaper way to learn exists. The user decides.
- **Scope:** a timebox and kill criterion for expensive experiments; every feature serves a pillar; new ideas go to the cut list first; secondary mechanics one at a time.
- **Done:** works + feels good + tried on a real device + played by someone else. Playtest gates and checklist included.
- **Project recovery and state tracking:** finds where you left off from `docs/ai/` and updates it at every checkpoint.

Folder layout:
- `SKILL.md`: the main workflow.
- `references/`: phases-and-ladder (phases, gates, 16-step build ladder, art timing), playtest, project-workflow, state-and-handoff, quality, delegation, codex, assets, spending-and-failures. Claude reads them only when needed.
- `templates/`: `ONE_PAGE.md` (vision, pillars, cut list, "1.0 is done" line), `HANDOFF.md`, `CURRENT_TASK.md` and `CODEX_BRIEF.md`.

General rules (source of truth, delegation, git, cost) are not repeated in the skill; they live in the global `CLAUDE.md` ([`agents/CLAUDE.md.template`](../agents/CLAUDE.md.template)).

It works best together with the agents in [`agents/`](../agents/), but it also works on its own.

### context-meter

A small TypeScript **mod** that shows, live under the prompt, how much context the active session is using. It reminds you to take a checkpoint or delegate to a subagent before the context fills up. It's a plugin, not a classic skill; see [INSTALL.md](INSTALL.md#english) for details.

### More coming

New skills will be added to this list as they are written.
