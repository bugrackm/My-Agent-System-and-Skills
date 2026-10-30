"""Isolated subprocess coverage; never use the real Claude state or vault."""

from __future__ import annotations

import base64
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

RUNTIME = Path(__file__).resolve().parents[1]
PACKAGE = RUNTIME.parent
GIT_ATTRIBUTES = """* text=auto eol=lf
*.md   text eol=lf
*.py   text eol=lf
*.json text eol=lf
*.ps1  text eol=lf
*.sh   text eol=lf
"""


def encoded_hook_command(argument: str) -> str:
    script = f"& 'C:/Python/python.exe' 'C:/Users/<you>/.claude/hooks/brain-memory.py' {argument}; exit $LASTEXITCODE"
    encoded = base64.b64encode(script.encode('utf-16le')).decode('ascii')
    return ("C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile "
            "-NonInteractive -ExecutionPolicy Bypass -EncodedCommand " + encoded)


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.home = self.base / 'home'
        self.vault = self.base / 'vault'
        self.project = self.base / 'project'
        self.project.mkdir()
        self.mem = self.vault / '850-Memory'
        self.mem.mkdir(parents=True)
        for name in ('CORE', 'LAST_SESSION', 'THREADS', 'JOURNAL'):
            (self.mem / f'{name}.md').write_text('# Memory\n', encoding='utf-8')
        (self.vault / '.gitattributes').write_text(GIT_ATTRIBUTES, encoding='utf-8')
        runtime = self.vault / 'runtime'
        runtime.mkdir()
        template = (RUNTIME / 'settings.template.json').read_text(encoding='utf-8')
        (runtime / 'settings.template.json').write_text(template, encoding='utf-8')
        claude = self.home / '.claude'
        claude.mkdir(parents=True)
        live_settings = {'hooks': {
            event: [{'hooks': [{'type': 'command', 'command': encoded_hook_command(argument)}]}]
            for event, argument in (
                ('SessionStart', 'session-start'), ('UserPromptSubmit', 'prompt'),
                ('Stop', 'stop'), ('SessionEnd', 'session-end'),
            )
        }}
        (claude / 'settings.json').write_text(json.dumps(live_settings), encoding='utf-8')
        for name in ('hooks/brain-memory.py', 'agents/memory-keeper.md'):
            target = runtime / name
            target.parent.mkdir(exist_ok=True)
            target.write_text('', encoding='utf-8')
            (claude / name).parent.mkdir(exist_ok=True)
            shutil.copy2(target, claude / name)
        self.env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home), BRAIN_HOME=str(self.vault),
                        PYTHONDONTWRITEBYTECODE='1', GIT_CONFIG_NOSYSTEM='1')
        self.refs = claude / 'brain-state/needs-reflection'

    def run_script(self, script: str, *args: str, payload: dict | None = None) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(RUNTIME / script), *args],
                              input=json.dumps(payload) if payload is not None else '',
                              text=True, capture_output=True, env=self.env,
                              cwd=self.base, timeout=30)

    def hook(self, event: str, **extra: object) -> str:
        payload = dict(session_id='test', cwd=str(self.project), **extra)
        result = self.run_script('hooks/brain-memory.py', event, payload=payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        return result.stdout

    def prompts(self, count: int = 4) -> None:
        for _ in range(count):
            self.hook('prompt')

    def write_memory(self) -> None:
        path = self.mem / 'LAST_SESSION.md'
        stamp = path.stat().st_mtime + 10
        path.write_text('# Updated\n', encoding='utf-8')
        os.utime(path, (stamp, stamp))

    def markers(self) -> list[dict]:
        return [json.loads(p.read_text(encoding='utf-8')) for p in self.refs.glob('*.json')]

    def test_stop_stretches(self) -> None:
        self.hook('session-start')
        self.prompts(3)
        self.assertEqual(self.hook('stop'), '')
        self.prompts(1)
        self.assertEqual(self.hook('stop', stop_hook_active=True), '')
        output = json.loads(self.hook('stop', transcript_path='/tmp/transcript'))
        self.assertEqual(output['decision'], 'block')
        self.assertIn('memory-keeper', output['reason'])
        self.assertEqual(self.hook('stop'), '')
        self.write_memory()
        self.assertEqual(self.hook('stop'), '')
        self.prompts()
        self.assertEqual(json.loads(self.hook('stop'))['decision'], 'block')

    def test_prompt_observes_write_and_end_retains_evidence(self) -> None:
        self.hook('session-start')
        self.prompts()
        self.hook('stop')
        self.write_memory()
        self.prompts(1)
        self.assertEqual(self.hook('stop'), '')
        self.hook('session-end')
        self.assertEqual(self.markers(), [])

    def test_marker_rules(self) -> None:
        for docs, written, expected in ((False, False, 'global'), (False, True, None),
                                        (True, False, 'global'), (True, True, 'project')):
            with self.subTest(docs=docs, written=written):
                for p in self.refs.glob('*.json'):
                    p.unlink()
                if docs:
                    directory = self.project / 'docs/ai'
                    directory.mkdir(parents=True, exist_ok=True)
                    (directory / 'HANDOFF.md').write_text('handoff', encoding='utf-8')
                self.hook('session-start')
                self.prompts()
                self.hook('stop', transcript_path='/tmp/recovery.jsonl')
                if written:
                    self.write_memory()
                self.hook('session-end')
                markers = self.markers()
                self.assertEqual(len(markers), int(expected is not None))
                if expected:
                    self.assertEqual(markers[0]['kind'], expected)
                    self.assertEqual(markers[0]['session_id'], 'test')
                    self.assertEqual(markers[0]['transcript_path'], '/tmp/recovery.jsonl')

    def test_short_and_both_written(self) -> None:
        self.hook('session-start')
        self.prompts(3)
        self.hook('session-end')
        self.assertEqual(self.markers(), [])
        doc = self.project / 'HANDOFF.md'
        doc.write_text('old', encoding='utf-8')
        self.hook('session-start')
        self.prompts()
        self.write_memory()
        stamp = doc.stat().st_mtime + 10
        os.utime(doc, (stamp, stamp))
        self.hook('session-end')
        self.assertEqual(self.markers(), [])

    def add_marker(self, kind: str | None, root: str, transcript: Path) -> Path:
        self.refs.mkdir(parents=True, exist_ok=True)
        marker = self.refs / 'previous.json'
        data = dict(project_root=root, transcript_path=str(transcript), session_id='previous-session',
                    ended_at='2026-10-26', global_updated=False, project_updated=False)
        if kind:
            data['kind'] = kind
        marker.write_text(json.dumps(data), encoding='utf-8')
        return marker

    def test_recovery_compaction_and_drift(self) -> None:
        transcript = self.base / 'transcript.jsonl'
        transcript.write_text('', encoding='utf-8')
        marker = self.add_marker('global', '/another/root', transcript)
        self.hook('session-start', source='compact')
        self.assertTrue(marker.exists())
        self.prompts()
        self.hook('stop')
        compact = self.hook('session-start', source='compact')
        self.assertIn('[Brain compaction checkpoint]', compact)
        self.assertNotIn('[Brain recovery required]', compact)
        self.assertTrue(marker.exists())
        self.assertTrue(self.hook('stop'))
        live = self.home / '.claude/settings.json'
        data = json.loads(live.read_text(encoding='utf-8'))
        del data['hooks']['Stop']
        live.write_text(json.dumps(data), encoding='utf-8')
        output = self.hook('session-start')
        context = json.loads(output)['hookSpecificOutput']['additionalContext']
        self.assertIn('[Brain recovery required]', output)
        self.assertIn(str(transcript), context)
        self.assertIn('[Brain runtime drift]', output)
        self.assertIn('Stop', output)
        self.assertFalse(marker.exists())
        self.assertIn('[Brain — Last Session]', json.loads(output)['hookSpecificOutput']['additionalContext'])

    def test_no_upstream_vault_has_no_sync_warning(self) -> None:
        git = ['git', '-C', str(self.vault), '-c', 'user.name=t', '-c', 'user.email=t@example.com']
        for args in (['init', '-q'], ['add', '-A'], ['commit', '-q', '-m', 'init']):
            subprocess.run(git + args, check=True, capture_output=True, env=self.env, timeout=30)
        output = self.hook('session-start')
        self.assertNotIn('[Brain sync warning]', output)

    def test_marker_matching_and_missing_transcript(self) -> None:
        for kind in ('project', None):
            marker = self.add_marker(kind, '/elsewhere', self.base / 'gone')
            self.assertNotIn('continuity warning', self.hook('session-start'))
            self.assertTrue(marker.exists())
            marker.unlink()
        marker = self.add_marker('global', '/elsewhere', self.base / 'gone')
        self.assertIn('continuity warning', self.hook('session-start'))
        self.assertFalse(marker.exists())

    def test_fail_open(self) -> None:
        result = self.run_script('hooks/brain-memory.py', 'stop', payload=[])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        state = self.home / '.claude/brain-state'
        state.rmdir()
        state.write_text('cannot mkdir', encoding='utf-8')
        result = self.run_script('hooks/brain-memory.py', 'session-start', payload={})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')

    def test_claude_event_name_aliases(self) -> None:
        output = self.hook('SessionStart')
        self.assertIn('[Brain — Last Session]', json.loads(output)['hookSpecificOutput']['additionalContext'])
        self.assertEqual(self.hook('UserPromptSubmit'), '')
        self.assertEqual(self.hook('Stop'), '')
        self.assertEqual(self.hook('SessionEnd'), '')

    def test_digest(self) -> None:
        path = self.base / 'session.jsonl'
        records = [
            dict(type='user', timestamp='first', message={'content': 'hello <system-reminder>hidden</system-reminder> world'}),
            dict(type='user', message={'content': '<command-name>noise</command-name>'}),
            dict(type='user', message={'content': [{'type': 'tool_result', 'content': 'hidden result'}]}),
            dict(type='assistant', timestamp='last', message={'content': [
                {'type': 'thinking', 'thinking': 'hidden thought'},
                {'type': 'text', 'text': 'answer ' + 'sk-' + 'a' * 25},
                {'type': 'tool_use', 'name': 'Read', 'input': {'file_path': '/some/file'}},
                {'type': 'tool_use', 'name': 'Bash', 'input': {'command': 'echo ok'}}]})]
        path.write_text('broken\n' + '\n'.join(json.dumps(r) for r in records), encoding='utf-8')
        result = self.run_script('tools/transcript-digest.py', str(path))
        self.assertEqual(result.returncode, 0)
        for text in ('Session: session.jsonl', 'first', 'last', 'USER: hello', 'world',
                     'ASSISTANT: answer [REDACTED]', 'TOOL: Read /some/file', 'TOOL: Bash echo ok'):
            self.assertIn(text, result.stdout)
        for text in ('hidden', 'noise', 'sk-' + 'a' * 25):
            self.assertNotIn(text, result.stdout)
        records = [dict(type='assistant', message={'content': str(i) + 'x' * 2000}) for i in range(4)]
        path.write_text('\n'.join(json.dumps(r) for r in records), encoding='utf-8')
        result = self.run_script('tools/transcript-digest.py', str(path))
        self.assertLess(len(result.stdout), 6100)
        result = self.run_script('tools/transcript-digest.py', str(path), '--max-chars', '200')
        self.assertIn('chars omitted', result.stdout)
        self.assertTrue(result.stdout.rstrip().endswith('x' * 100))

    def doctor(self) -> subprocess.CompletedProcess:
        return self.run_script('tools/vault-doctor.py', '--today', '2026-10-27')

    def test_doctor_clean_and_checks(self) -> None:
        self.assertEqual(self.doctor().stdout.strip(), 'vault-doctor: OK')
        (self.vault / 'bad.md').write_text('[[missing]]\n`[[inline]]`\n```\n[[fenced]]\n```\n', encoding='utf-8')
        (self.mem / 'THREADS.md').write_text('## old\n- Status: 🟢\n- Last touched: 2026-01-01\n[[memory-missing]]', encoding='utf-8')
        (self.mem / 'LAST_SESSION.md').write_text('x' * 3001, encoding='utf-8')
        (self.mem / 'JOURNAL.md').write_text('line\n' * 251, encoding='utf-8')
        secret = 'ghp_' + 'a' * 25
        (self.vault / 'credential.toml').write_text(secret, encoding='utf-8')
        (self.home / '.claude/hooks/brain-memory.py').unlink()
        live = self.home / '.claude/settings.json'
        live.write_text('{}', encoding='utf-8')
        subprocess.run(['git', 'init', '-q', str(self.vault)], check=True,
                       capture_output=True, timeout=30)
        result = self.doctor()
        self.assertEqual(result.returncode, 1)
        for area in ('frontmatter', 'wikilinks', 'threads', 'last_session size', 'journal size', 'git', 'secrets', 'runtime drift'):
            self.assertIn(f'{area}:', result.stdout)
        self.assertIn('credential.toml:1', result.stdout)
        self.assertIn('memory-missing', result.stdout)
        self.assertNotIn('[[inline]]', result.stdout)
        self.assertNotIn('[[fenced]]', result.stdout)
        self.assertNotIn(secret, result.stdout)
        self.assertIn('hooks/brain-memory.py is missing', result.stdout)

    def test_all_secret_patterns(self) -> None:
        secrets = ['sk-' + 'a' * 25, 'ghp_' + 'b' * 25,
                   'AKIA' + 'A' * 16, '-----BEGIN RSA ' + 'PRIVATE KEY-----']
        transcript = self.base / 'secrets.jsonl'
        transcript.write_text(json.dumps({'type': 'user', 'message': {'content': ' '.join(secrets)}}), encoding='utf-8')
        result = self.run_script('tools/transcript-digest.py', str(transcript))
        self.assertEqual(result.stdout.count('[REDACTED]'), 4)
        (self.vault / 'keys.json').write_text('\n'.join(secrets), encoding='utf-8')
        result = self.doctor()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.count('ERROR secrets:'), 4)
        for secret in secrets:
            self.assertNotIn(secret, result.stdout)

    def test_doctor_ahead(self) -> None:
        def git(*args: str) -> None:
            subprocess.run(['git', '-C', str(self.vault), *args], env=self.env,
                           check=True, capture_output=True, timeout=30)
        git('init', '-q')
        git('config', 'user.email', 'test@example.invalid')
        git('config', 'user.name', 'Test')
        git('add', '.')
        git('commit', '-qm', 'initial')
        git('branch', 'upstream-test')
        git('branch', '--set-upstream-to=upstream-test')
        git('commit', '--allow-empty', '-qm', 'ahead')
        result = self.doctor()
        self.assertEqual(result.returncode, 0)
        self.assertIn('1 commit(s) ahead of upstream', result.stdout)


    def test_doctor_links_and_exclusions(self) -> None:
        folder = self.vault / 'notes'
        folder.mkdir()
        (folder / 'Target.md').write_text('---\ntitle: Target\n---\n', encoding='utf-8')
        (folder / 'Source.md').write_text('---\ntitle: Source\n---\n[[target|alias]] [[notes/Target.md#heading]] [[#local]]', encoding='utf-8')
        (folder / 'README.md').write_text('[[ignored]]', encoding='utf-8')
        (self.vault / 'runtime/ignored.md').write_text('[[ignored]]', encoding='utf-8')
        self.assertEqual(self.doctor().stdout.strip(), 'vault-doctor: OK')

    def test_encoding_regression_and_bom_input(self) -> None:
        sample = 'ş ğ ı İ 😀'
        (self.mem / 'LAST_SESSION.md').write_text('# Last Session\n' + sample, encoding='utf-8')
        (self.mem / 'THREADS.md').write_text('# Active Threads\n' + sample, encoding='utf-8')
        payload = json.dumps({'session_id': 'encoding', 'cwd': str(self.project)}).encode('utf-8')
        for codepage in ('cp1252', 'cp1254'):
            with self.subTest(codepage=codepage):
                env = dict(self.env, PYTHONIOENCODING=codepage)
                result = subprocess.run(
                    [sys.executable, str(RUNTIME / 'hooks/brain-memory.py'), 'session-start'],
                    input=payload, capture_output=True, env=env, cwd=self.base, timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout)
                result.stdout.decode('ascii')
                context = json.loads(result.stdout)['hookSpecificOutput']['additionalContext']
                self.assertIn(sample, context)

        bom_payload = json.dumps({
            'session_id': 'bom-turkish', 'cwd': str(self.project),
            'prompt': 'Türkçe istem: ş ğ ı İ',
        }, ensure_ascii=False).encode('utf-8-sig')
        result = subprocess.run(
            [sys.executable, str(RUNTIME / 'hooks/brain-memory.py'), 'prompt'],
            input=bom_payload, capture_output=True, env=self.env, cwd=self.base, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        state = self.home / '.claude/brain-state/sessions/bom-turkish.json'
        self.assertEqual(json.loads(state.read_text(encoding='utf-8'))['prompt_count'], 1)

    def run_merge(self, settings: Path, *args: str) -> subprocess.CompletedProcess:
        script = PACKAGE / 'merge-settings.py'
        if not script.is_file():
            self.skipTest('source-tree merge-settings.py is absent in the installed runtime layout')
        return subprocess.run(
            [sys.executable, str(script), '--settings', str(settings), *args],
            text=True, capture_output=True, env=self.env, cwd=self.base, timeout=30,
        )

    def test_merge_settings_render_update_backup_dry_run_and_idempotence(self) -> None:
        settings = self.base / 'config/settings.json'
        settings.parent.mkdir()
        original = {'theme': 'dark', 'hooks': {'Custom': [{'hooks': [{'type': 'command', 'command': 'keep-me'}]}]}}
        settings.write_text(json.dumps(original), encoding='utf-8-sig')
        python = self.base / "Python's $ Folder/python exe"
        hook = self.base / "Claude Hooks/O'Brien O’Brien $/brain-memory.py"
        brain = self.base / 'Brain Folder'
        common = ('--python', str(python), '--hook', str(hook), '--brain-home', str(brain))

        first = self.run_merge(settings, *common)
        self.assertEqual(first.returncode, 0, first.stderr)
        data = json.loads(settings.read_text(encoding='utf-8'))
        self.assertEqual(data['theme'], 'dark')
        self.assertEqual(data['hooks']['Custom'], original['hooks']['Custom'])
        self.assertEqual(data['env']['BRAIN_HOME'], brain.resolve().as_posix())
        self.assertEqual(data['env']['BRAIN_PYTHON'], python.resolve().as_posix())
        commands = {}
        for event in ('SessionStart', 'UserPromptSubmit', 'Stop', 'SessionEnd'):
            item = data['hooks'][event][0]['hooks'][0]
            self.assertNotIn('shell', item)
            commands[event] = item['command']
        command = commands['SessionStart']
        self.assertTrue(command.startswith(
            'C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe '
            '-NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand '
        ))
        encoded = command.rsplit(' ', 1)[1]
        decoded = base64.b64decode(encoded).decode('utf-16le')
        quoted_python = python.resolve().as_posix().replace("'", "''")
        quoted_hook = hook.resolve().as_posix().replace("'", "''").replace('’', '’’')
        expected = f"& '{quoted_python}' '{quoted_hook}' session-start; exit $LASTEXITCODE"
        self.assertEqual(decoded, expected)
        self.assertFalse(settings.read_bytes().startswith(b'\xef\xbb\xbf'))
        self.assertEqual(data['hooks']['SessionStart'][0]['hooks'][0]['timeout'], 30)
        self.assertEqual(data['hooks']['Stop'][0]['hooks'][0]['timeout'], 15)
        self.assertEqual(len(list(settings.parent.glob('settings.json.backup-*'))), 1)

        second = self.run_merge(settings, *common)
        self.assertIn('already up to date', second.stdout)
        self.assertEqual(len(list(settings.parent.glob('settings.json.backup-*'))), 1)

        data['env']['BRAIN_HOME'] = 'C:/keep/existing/brain'
        data['env']['BRAIN_PYTHON'] = 'C:/keep/existing/python.exe'
        settings.write_text(json.dumps(data), encoding='utf-8')
        kept = self.run_merge(settings, *common)
        self.assertIn('already up to date', kept.stdout)
        kept_data = json.loads(settings.read_text(encoding='utf-8'))
        self.assertEqual(kept_data['env']['BRAIN_HOME'], 'C:/keep/existing/brain')
        self.assertEqual(kept_data['env']['BRAIN_PYTHON'], 'C:/keep/existing/python.exe')

        data = kept_data
        stale = data['hooks']['SessionStart'][0]['hooks'][0]
        stale['command'] = "& 'C:/Old/python.exe' 'C:/Old/brain-memory.py' session-start"
        settings.write_text(json.dumps(data), encoding='utf-8')
        updated = self.run_merge(settings, *common, '--update')
        self.assertIn('updated brain-memory.py command', updated.stdout)
        self.assertIn('env.BRAIN_HOME = ', updated.stdout)
        self.assertIn('env.BRAIN_PYTHON = ', updated.stdout)
        refreshed = json.loads(settings.read_text(encoding='utf-8'))
        self.assertEqual(refreshed['hooks']['SessionStart'][0]['hooks'][0]['command'], commands['SessionStart'])
        self.assertEqual(refreshed['env']['BRAIN_HOME'], brain.resolve().as_posix())
        self.assertEqual(refreshed['env']['BRAIN_PYTHON'], python.resolve().as_posix())

        dry_settings = self.base / 'dry/settings.json'
        dry = self.run_merge(dry_settings, *common, '--dry-run')
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertIn('dry run', dry.stdout)
        self.assertFalse(dry_settings.exists())

    def test_merge_settings_rejects_unsafe_command_paths_without_writing(self) -> None:
        script = PACKAGE / 'merge-settings.py'
        if not script.is_file():
            self.skipTest('source-tree merge-settings.py is absent in the installed runtime layout')
        settings = self.base / 'unsafe-settings.json'
        settings.write_text('{"theme": "unchanged"}\n', encoding='utf-8')
        original = settings.read_bytes()
        module = runpy.run_path(str(script))
        for option in ('--python', '--hook'):
            for bad in ('bad\npath', 'bad\rpath', 'bad\0path'):
                with self.subTest(option=option, path=repr(bad)):
                    argv = ['merge-settings.py', '--settings', str(settings), option, bad]
                    error = io.StringIO()
                    with mock.patch.object(sys, 'argv', argv), redirect_stderr(error):
                        self.assertEqual(module['main'](), 2)
                    self.assertIn('nothing written', error.getvalue())
                    self.assertEqual(settings.read_bytes(), original)

    def test_merge_settings_validation_atomic_write_and_windowsapps_warning(self) -> None:
        script = PACKAGE / 'merge-settings.py'
        if not script.is_file():
            self.skipTest('source-tree merge-settings.py is absent in the installed runtime layout')
        settings = self.base / 'shape/settings.json'
        settings.parent.mkdir()
        for bad, message in (
            ({'hooks': {'Stop': ['not-an-object']}}, 'invalid hook group'),
            ({'hooks': {'Stop': [{'hooks': ['not-an-object']}]}}, 'non-object hook entry'),
        ):
            with self.subTest(message=message):
                settings.write_text(json.dumps(bad), encoding='utf-8')
                original = settings.read_bytes()
                result = self.run_merge(settings)
                self.assertEqual(result.returncode, 2)
                self.assertIn(message, result.stderr)
                self.assertIn('nothing written', result.stderr)
                self.assertEqual(settings.read_bytes(), original)

        warning = self.run_merge(
            settings, '--python', r'C:\Users\test\AppData\Local\Microsoft\WindowsApps\python.exe',
            '--dry-run',
        )
        self.assertIn('Microsoft Store alias', warning.stderr)
        self.assertIn('python.org', warning.stderr)

        settings.write_text('{"theme": "unchanged"}\n', encoding='utf-8')
        original = settings.read_bytes()
        module = runpy.run_path(str(script))
        argv = ['merge-settings.py', '--settings', str(settings)]
        output = io.StringIO()
        with mock.patch.object(sys, 'argv', argv), mock.patch.object(
                module['os'], 'replace', side_effect=OSError('simulated replace failure')), \
                redirect_stdout(output):
            with self.assertRaises(OSError):
                module['main']()
        self.assertEqual(settings.read_bytes(), original)
        self.assertEqual(list(settings.parent.glob(f'.{settings.name}.*.tmp')), [])

    def test_hook_identity_requires_event_argument_at_end(self) -> None:
        merge_script = PACKAGE / 'merge-settings.py'
        if not merge_script.is_file():
            self.skipTest('source-tree merge-settings.py is absent in the installed runtime layout')
        modules = (
            runpy.run_path(str(merge_script)),
            runpy.run_path(str(RUNTIME / 'hooks/brain-memory.py')),
            runpy.run_path(str(RUNTIME / 'tools/vault-doctor.py')),
        )
        script = "& 'C:/Python/python.exe' 'C:/stop/brain-memory.py' prompt; exit $LASTEXITCODE"
        encoded = base64.b64encode(script.encode('utf-16le')).decode('ascii')
        encoded_command = 'powershell.exe -EncodedCommand ' + encoded
        groups = [{'hooks': [{'command': encoded_command}]}]
        self.assertFalse(modules[0]['hook_identity'](encoded_command, 'stop'))
        self.assertTrue(modules[0]['hook_identity'](encoded_command, 'prompt'))
        for module in modules[1:]:
            self.assertFalse(module['hook_installed'](groups, 'stop'))
            self.assertTrue(module['hook_installed'](groups, 'prompt'))
            self.assertFalse(module['hook_installed'](
                [{'hooks': [{'command': 'python C:/stop/brain-memory.py prompt'}]}], 'stop'))

    def test_rendered_hook_drift_identity(self) -> None:
        settings = self.home / '.claude/settings.json'
        settings.write_text('{}', encoding='utf-8')
        result = self.run_merge(
            settings, '--python', sys.executable,
            '--hook', str(self.home / '.claude/hooks/brain-memory.py'),
            '--brain-home', str(self.vault),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        output = self.hook('session-start')
        self.assertNotIn('[Brain runtime drift]', output)
        data = json.loads(settings.read_text(encoding='utf-8'))
        data['hooks']['Stop'][0]['hooks'][0]['command'] = 'python brain-memory.py stop'
        del data['hooks']['SessionEnd']
        settings.write_text(json.dumps(data), encoding='utf-8')
        output = self.hook('session-start')
        self.assertIn('[Brain runtime drift]', output)
        self.assertIn('SessionEnd', output)
        self.assertNotIn('Stop,', output)

        settings.write_text('\ufeff' + json.dumps(data), encoding='utf-8')
        output = self.hook('session-start')
        self.assertIn('[Brain runtime drift]', output)

        doctor = self.doctor()
        self.assertIn('missing hook event SessionEnd', doctor.stdout)

    def test_update_runtime_copy_backup_dry_run_and_up_to_date(self) -> None:
        update_script = PACKAGE / 'update-runtime.py'
        if not update_script.is_file():
            self.skipTest('source-tree update-runtime.py is absent in the installed runtime layout')
        source_runtime = self.base / 'copy-brain/runtime'
        copy_home = self.base / 'copy-home'
        claude = copy_home / '.claude'
        for name, content in (('hooks/brain-memory.py', 'new hook'),
                              ('agents/memory-keeper.md', 'new agent')):
            path = source_runtime / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            target = claude / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('old', encoding='utf-8')
        command = [
            sys.executable, str(update_script),
            '--brain-home', str(self.base / 'copy-brain'),
        ]
        copy_env = dict(self.env, HOME=str(copy_home), USERPROFILE=str(copy_home))
        dry = subprocess.run(command + ['--dry-run'], text=True, capture_output=True,
                             env=copy_env, cwd=self.base, timeout=30)
        self.assertIn('dry run', dry.stdout)
        self.assertEqual((claude / 'hooks/brain-memory.py').read_text(encoding='utf-8'), 'old')
        copied = subprocess.run(command, text=True, capture_output=True,
                                env=copy_env, cwd=self.base, timeout=30)
        self.assertEqual(copied.returncode, 0, copied.stderr)
        self.assertEqual((claude / 'hooks/brain-memory.py').read_text(encoding='utf-8'), 'new hook')
        self.assertEqual(len(list((claude / 'hooks').glob('brain-memory.py.backup-*'))), 1)
        again = subprocess.run(command, text=True, capture_output=True,
                               env=copy_env, cwd=self.base, timeout=30)
        self.assertIn('runtime already up to date', again.stdout)

        source = source_runtime / 'hooks/brain-memory.py'
        target = claude / 'hooks/brain-memory.py'
        source.write_bytes(b'line one\nline two\n')
        target.write_bytes(b'line one\r\nline two\r\n')
        backups_before = list((claude / 'hooks').glob('brain-memory.py.backup-*'))
        crlf = subprocess.run(command, text=True, capture_output=True,
                              env=copy_env, cwd=self.base, timeout=30)
        self.assertEqual(crlf.returncode, 0, crlf.stderr)
        self.assertIn(f'up to date: {target}', crlf.stdout)
        self.assertEqual(target.read_bytes(), b'line one\r\nline two\r\n')
        self.assertEqual(list((claude / 'hooks').glob('brain-memory.py.backup-*')), backups_before)

    @unittest.skipIf(os.name == 'nt', 'Windows cannot create the invalid filename fixtures')
    def test_doctor_invalid_windows_filename_fixtures(self) -> None:
        bad_names = ('bad:name.md', 'control\x01.md', 'trailing. ', 'CON.txt')
        for name in bad_names:
            (self.vault / name).write_text('x', encoding='utf-8')
        (self.vault / 'Case.md').write_text('x', encoding='utf-8')
        (self.vault / 'case.md').write_text('x', encoding='utf-8')
        long_dir = self.vault / ('a' * 80) / ('b' * 80) / ('c' * 50)
        long_dir.mkdir(parents=True)
        result = self.doctor()
        for text in ('Windows-invalid character', 'ends with a dot or space',
                     'reserved Windows device name', 'case collision', 'exceeds 200 characters'):
            self.assertIn(text, result.stdout)

    def test_doctor_line_ending_onedrive_and_copy_checks(self) -> None:
        (self.vault / '.gitattributes').unlink()
        self.assertIn('eol=lf rule', self.doctor().stdout)
        (self.vault / '.gitattributes').write_text(GIT_ATTRIBUTES, encoding='utf-8')
        (self.home / '.claude/hooks/brain-memory.py').write_text('drift', encoding='utf-8')
        self.assertIn('differs from the runtime copy', self.doctor().stdout)

        source = self.vault / 'runtime/hooks/brain-memory.py'
        installed = self.home / '.claude/hooks/brain-memory.py'
        source.write_bytes(b'line one\nline two\n')
        installed.write_bytes(b'line one\r\nline two\r\n')
        self.assertNotIn('hooks/brain-memory.py differs', self.doctor().stdout)

        onedrive = self.base / 'OneDrive' / 'vault'
        (onedrive / '850-Memory').mkdir(parents=True)
        (onedrive / '.gitattributes').write_text(GIT_ATTRIBUTES, encoding='utf-8')
        result = self.run_script('tools/vault-doctor.py', '--vault', str(onedrive), '--today', '2026-10-27')
        self.assertIn('vault is inside OneDrive', result.stdout)

    def test_installed_runtime_test_discovery(self) -> None:
        if os.environ.get('BRAIN_WINDOWS_NESTED_DISCOVERY') == '1':
            self.skipTest('outer installed-layout test owns nested discovery')
        installed = self.base / 'installed-vault/runtime'
        shutil.copytree(RUNTIME, installed)
        env = dict(self.env, BRAIN_WINDOWS_NESTED_DISCOVERY='1')
        result = subprocess.run(
            [sys.executable, '-m', 'unittest', 'discover', '-s', str(installed / 'tests'), '-v'],
            text=True, capture_output=True, env=env, cwd=self.base, timeout=30,
        )
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertIn('OK (skipped=', output)
        self.assertIn('source-tree merge-settings.py is absent', output)
        self.assertIn('source-tree update-runtime.py is absent', output)

    def test_windows_filename_validation_categories(self) -> None:
        validate = runpy.run_path(str(RUNTIME / 'tools/vault-doctor.py'))['windows_name_problem']
        self.assertIn('invalid character', validate('bad:name.md'))
        self.assertIn('invalid character', validate('control\x01.md'))
        self.assertIn('dot or space', validate('trailing.'))
        for name in ('CON', 'prn.txt', 'AuX.md', 'NUL.json', 'COM1.log', 'lpt9.any'):
            with self.subTest(name=name):
                self.assertIn('reserved', validate(name))
        self.assertIsNone(validate('COM10.md'))
        self.assertIsNone(validate('normal-note.md'))

    @unittest.skipUnless(os.name == 'nt', 'Windows PowerShell integration')
    def test_windows_powershell_end_to_end(self) -> None:
        sample = 'ş ğ ı İ 😀'
        (self.mem / 'LAST_SESSION.md').write_text('# Last Session\n' + sample, encoding='utf-8')
        settings = self.base / 'powershell-settings.json'
        result = self.run_merge(
            settings, '--python', sys.executable,
            '--hook', str(RUNTIME / 'hooks/brain-memory.py'), '--brain-home', str(self.vault),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(settings.read_text(encoding='utf-8'))
        command = data['hooks']['SessionStart'][0]['hooks'][0]['command']
        payload = json.dumps({'session_id': 'powershell', 'cwd': str(self.project)}).encode('utf-8')
        invocations: list[tuple[str, str | list[str]]] = [
            ('shell=True', command),
            ('PowerShell -Command', ['powershell', '-NoProfile', '-NonInteractive', '-Command', command]),
        ]
        git_bash = Path('C:/Program Files/Git/bin/bash.exe')
        if git_bash.is_file():
            invocations.append(('Git Bash', [str(git_bash), '-c', command]))
        for label, invocation in invocations:
            with self.subTest(invocation=label):
                state = self.home / '.claude/brain-state/sessions/powershell.json'
                if state.exists():
                    state.unlink()
                invoked = subprocess.run(
                    invocation, shell=isinstance(invocation, str), input=payload,
                    capture_output=True, env=self.env, cwd=self.base, timeout=30,
                )
                self.assertEqual(invoked.returncode, 0, invoked.stderr)
                invoked.stdout.decode('ascii')
                output = json.loads(invoked.stdout)
                self.assertIn(sample, output['hookSpecificOutput']['additionalContext'])
                self.assertTrue(state.is_file(), f'{label} did not deliver JSON stdin to Python')

        failing = self.base / 'exit 3.py'
        failing.write_text('raise SystemExit(3)\n', encoding='utf-8')
        failing_settings = self.base / 'failing-settings.json'
        result = self.run_merge(
            failing_settings, '--python', sys.executable, '--hook', str(failing),
            '--brain-home', str(self.vault),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        failing_command = json.loads(failing_settings.read_text(encoding='utf-8'))[
            'hooks']['SessionStart'][0]['hooks'][0]['command']
        invoked = subprocess.run(
            failing_command, shell=True, input=b'', capture_output=True,
            env=self.env, cwd=self.base, timeout=30,
        )
        self.assertEqual(invoked.returncode, 3, invoked.stderr)


if __name__ == '__main__':
    unittest.main()

