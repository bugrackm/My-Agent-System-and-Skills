# Skills

🇹🇷 Türkçe · 🇬🇧 [English ↓](#english) · Kurulum: [INSTALL.md](INSTALL.md)

Skill, Claude Code'a belirli bir iş türü için hazır talimatlar veren bir klasördür. Claude ilgili işi fark edince skill'i yükler ve oradaki iş akışını izler. Bir skill'i `/skill-adı` yazarak elle de çağırabilirsin.

| Skill | Tür | Ne yapar | Bağımlılık |
|---|---|---|---|
| [`game-dev-director`](game-dev-director/SKILL.md) | Skill | Oyun projeleri için teknik lider iş akışı (aşama, kapı, playtest) | Yok. Codex CLI isteğe bağlı |
| [`context-meter`](context-meter/) | Plugin (mod) | Prompt'un altında bağlam doluluğunu gösterir: `ctx █████░░░░░ 100k/200k · 50%` | Yok |

## game-dev-director

Yeni ya da devam eden bir oyun projesinde Claude'u **teknik lider** gibi çalıştırır (v6.1). Kontrol listesi değil, karar vermeye yardım eden kısa notlardan oluşur.
- **Harita:** önce en ucuz risk: "eğlenceli mi?" → "hepsi böyle hissettirecek mi?" → "hepsini yapabilir miyim?" → "yayınlanabilir mi?". Sanat, meta ve ağır cila, temel kanıtlandıktan sonra en çok işe yarar. Bir istek bu sırayı atlıyorsa Claude bunu bir cümleyle söyler ve kararı sana bırakır. Sıradan isteklere tören eklemez.
- **İşi yapma:** kök nedeni düzelt; girdi, mantık, görsel ve sesi birlikte ele alan, oynanıp değerlendirilebilen dilimler. Atılabilir prototip kodu serbest, oyunun ihtiyacından önce genel sistem yazılmaz.
- **"Bitti":** çalışıyor, ilgili otomatik kontrollerden geçti, diff incelendi. His, girdi, ses, zamanlama ve görsellik söz konusuysa sen de oynadın; agent hissi değerlendiremez.
- **Playtest:** prototipten sonra, dikey dilimden sonra ve yayından önce 3-5 dış oyuncu. Anlatma, izle.
- **Godot web tuzakları (Gotchas):** Godot 4.7 belgeleri ve kaynak koduyla kontrol edilmiş, makul bir varsayıma ters düşen gerçekler. Örnek: web'de ivmeölçer sıfır döner; varsayılan "Sample" ses modu anlık ses üretimini desteklemez; havuzunda tek ses olan `AudioStreamRandomizer` hep aynı sesi çalar.

Klasör yapısı:
- `SKILL.md`: ana iş akışı.
- `references/`: phases-and-ladder (aşamalar, kapılar, özellik sırası, sanatın zamanı), playtest, assets, codex. Claude bunları yalnızca gerektiğinde okur.
- `templates/`: `ONE_PAGE.md` (vizyon, ana ilkeler, kesme listesi, "1.0 bitti" tanımı), `HANDOFF.md`, `CURRENT_TASK.md` ve `CODEX_BRIEF.md`.

Genel kurallar (rol, kaynak önceliği, proje kurtarma, durum dosyaları, devretme, git, maliyet, doğrulama raporu) skill'de tekrarlanmaz, global `CLAUDE.md`'de durur ([`agents/CLAUDE.md.template`](../agents/CLAUDE.md.template)). v5'teki `project-workflow`, `state-and-handoff`, `quality`, `delegation` ve `spending-and-failures` referansları bu yüzden kaldırıldı. Kendi `CLAUDE.md`'n varsa template'teki "Projects and source of truth", "Durable state" ve "Delegation" bölümlerinin karşılığı olduğundan emin ol.

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

Makes Claude act as **technical lead** on a new or continuing game project (v6.1). It is a set of short judgment aids, not a checklist.
- **Map:** cheapest risk first: "is it fun?" → "will all of it feel like this?" → "can I build all of it?" → "can it ship?". Art, meta and heavy polish pay off most once the core is proven. When a request skips that order, Claude says so in a sentence and leaves the call to you. Ordinary requests get no extra ceremony.
- **Doing the work:** fix root causes; build slices that touch input, logic, visuals and sound together so they can be played and judged. Throwaway prototype code is fine; general systems before the game needs them are not.
- **Done:** works, passes the relevant automated checks, diff reviewed, and for anything about feel, input, audio, timing or visuals, you have played it. An agent cannot judge feel.
- **Playtests:** 3-5 outside players after the prototype, after the vertical slice and before release. Watch, don't explain.
- **Godot web gotchas:** facts checked against the Godot 4.7 docs and source that break a reasonable assumption. For example: the accelerometer returns zero on web; the default "Sample" audio mode cannot generate audio at runtime; an `AudioStreamRandomizer` with one stream always plays that stream.

Folder layout:
- `SKILL.md`: the main workflow.
- `references/`: phases-and-ladder (phases, gates, build ladder, art timing), playtest, assets, codex. Claude reads them only when needed.
- `templates/`: `ONE_PAGE.md` (vision, pillars, cut list, "1.0 is done" line), `HANDOFF.md`, `CURRENT_TASK.md` and `CODEX_BRIEF.md`.

General rules (role, source of truth, project recovery, state files, delegation, git, cost, verification reporting) are not repeated in the skill; they live in the global `CLAUDE.md` ([`agents/CLAUDE.md.template`](../agents/CLAUDE.md.template)). That is why v5's `project-workflow`, `state-and-handoff`, `quality`, `delegation` and `spending-and-failures` references were removed. If you keep your own `CLAUDE.md`, make sure it covers the template's "Projects and source of truth", "Durable state" and "Delegation" sections.

It works best together with the agents in [`agents/`](../agents/), but it also works on its own.

### context-meter

A small TypeScript **mod** that shows, live under the prompt, how much context the active session is using. It reminds you to take a checkpoint or delegate to a subagent before the context fills up. It's a plugin, not a classic skill; see [INSTALL.md](INSTALL.md#english) for details.

### More coming

New skills will be added to this list as they are written.
