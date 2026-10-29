# Skills: kurulum

🇹🇷 Türkçe · 🇬🇧 [English ↓](#english) · Açıklama: [README.md](README.md)

## game-dev-director

Repo kök klasöründen:

```bash
mkdir -p ~/.claude/skills
if [ -e ~/.claude/skills/game-dev-director ]; then
  echo "zaten var; önce farkına bak"
else
  cp -r skills/game-dev-director ~/.claude/skills/
  # git pull ile güncel kalmak istersen kopya yerine:
  # ln -s "$PWD/skills/game-dev-director" ~/.claude/skills/game-dev-director
fi
```

Doğrulamak için yeni bir oturum aç ve `/game-dev-director` yaz. Ya da bir oyun projesinde *"bu projede kaldığımız yeri bul"* de; skill kendiliğinden devreye girmeli.

## context-meter (plugin)

`context-meter` bir mod olduğu için skill klasörüne kopyalanmaz, plugin olarak kurulur. Bu repo aynı zamanda bir plugin marketplace'i. Claude Code 2.1.275 ve sonrasında tek satır yeterli:

```text
/plugin install context-meter --marketplace bugrackm/My-Agent-System-and-Skills
```

Daha eski sürümlerde iki adımda:

```text
/plugin marketplace add bugrackm/My-Agent-System-and-Skills
/plugin install context-meter@my-agent-system
```

Kalıcı kurulum yapmadan tek bir oturumda denemek için:

```bash
claude --plugin-dir ./skills/context-meter
```

Kurulduktan sonra prompt'un altında `ctx █████░░░░░ 100k/200k · 50%` gibi bir satır görünür.

---

<a id="english"></a>

## English

🇬🇧 English · 🇹🇷 [Türkçe ↑](#skills-kurulum) · Overview: [README.md](README.md#english)

### game-dev-director

From the repo root:

```bash
mkdir -p ~/.claude/skills
if [ -e ~/.claude/skills/game-dev-director ]; then
  echo "already exists; diff it first"
else
  cp -r skills/game-dev-director ~/.claude/skills/
  # to stay current with git pull, symlink instead:
  # ln -s "$PWD/skills/game-dev-director" ~/.claude/skills/game-dev-director
fi
```

To verify, open a new session and type `/game-dev-director`. Or, in a game project, say *"find where we left off in this project"*; the skill should kick in on its own.

### context-meter (plugin)

`context-meter` is a mod, so it isn't copied into the skills folder; it's installed as a plugin. This repo is also a plugin marketplace. On Claude Code 2.1.275 or later, one line is enough:

```text
/plugin install context-meter --marketplace bugrackm/My-Agent-System-and-Skills
```

On older versions, use two steps:

```text
/plugin marketplace add bugrackm/My-Agent-System-and-Skills
/plugin install context-meter@my-agent-system
```

To try it for a single session without installing it:

```bash
claude --plugin-dir ./skills/context-meter
```

Once installed, a line like `ctx █████░░░░░ 100k/200k · 50%` appears under the prompt.
