"""Isolated subprocess coverage; never use the real Claude state or vault."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RUNTIME = Path(__file__).resolve().parents[1]


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.home = self.base / 'home'
        self.vault = self.base / 'vault'
        self.project = self.base / 'project'
        self.project.mkdir()
        self.mem = self.vault / '850-Memory'
        self.mem.mkdir(parents=True)
        for name in ('CORE', 'LAST_SESSION', 'THREADS', 'JOURNAL'):
            (self.mem / f'{name}.md').write_text('# Memory\n')
        runtime = self.vault / 'runtime'
        runtime.mkdir()
        template = (RUNTIME / 'settings.template.json').read_text()
        (runtime / 'settings.template.json').write_text(template)
        claude = self.home / '.claude'
        claude.mkdir(parents=True)
        (claude / 'settings.json').write_text(template)
        for name in ('hooks/brain-memory.py', 'agents/memory-keeper.md'):
            target = runtime / name
            target.parent.mkdir(exist_ok=True)
            target.write_text('')
            (claude / name).parent.mkdir(exist_ok=True)
            (claude / name).symlink_to(target)
        self.env = dict(os.environ, HOME=str(self.home), BRAIN_HOME=str(self.vault),
                        PYTHONDONTWRITEBYTECODE='1', GIT_CONFIG_NOSYSTEM='1')
        self.refs = claude / 'brain-state/needs-reflection'

    def run_script(self, script: str, *args: str, payload: dict | None = None) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(RUNTIME / script), *args],
                              input=json.dumps(payload) if payload is not None else '',
                              text=True, capture_output=True, env=self.env,
                              cwd=self.base, timeout=10)

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
        path.write_text('# Updated\n')
        os.utime(path, (stamp, stamp))

    def markers(self) -> list[dict]:
        return [json.loads(p.read_text()) for p in self.refs.glob('*.json')]

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
                    (directory / 'HANDOFF.md').write_text('handoff')
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
        doc.write_text('old')
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
        marker.write_text(json.dumps(data))
        return marker

    def test_recovery_compaction_and_drift(self) -> None:
        transcript = self.base / 'transcript.jsonl'
        transcript.write_text('')
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
        data = json.loads(live.read_text())
        del data['hooks']['Stop']
        live.write_text(json.dumps(data))
        output = self.hook('session-start')
        self.assertIn('[Brain recovery required]', output)
        self.assertIn(str(transcript), output)
        self.assertIn('[Brain runtime drift]', output)
        self.assertIn('Stop', output)
        self.assertFalse(marker.exists())
        self.assertIn('[Brain — Last Session]', output)

    def test_no_upstream_vault_has_no_sync_warning(self) -> None:
        git = ['git', '-C', str(self.vault), '-c', 'user.name=t', '-c', 'user.email=t@example.com']
        for args in (['init', '-q'], ['add', '-A'], ['commit', '-q', '-m', 'init']):
            subprocess.run(git + args, check=True, capture_output=True, env=self.env)
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
        state.write_text('cannot mkdir')
        result = self.run_script('hooks/brain-memory.py', 'session-start', payload={})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')

    def test_claude_event_name_aliases(self) -> None:
        output = self.hook('SessionStart')
        self.assertIn('[Brain — Last Session]', output)
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
        path.write_text('broken\n' + '\n'.join(json.dumps(r) for r in records))
        result = self.run_script('tools/transcript-digest.py', str(path))
        self.assertEqual(result.returncode, 0)
        for text in ('Session: session.jsonl', 'first', 'last', 'USER: hello', 'world',
                     'ASSISTANT: answer [REDACTED]', 'TOOL: Read /some/file', 'TOOL: Bash echo ok'):
            self.assertIn(text, result.stdout)
        for text in ('hidden', 'noise', 'sk-' + 'a' * 25):
            self.assertNotIn(text, result.stdout)
        records = [dict(type='assistant', message={'content': str(i) + 'x' * 2000}) for i in range(4)]
        path.write_text('\n'.join(json.dumps(r) for r in records))
        result = self.run_script('tools/transcript-digest.py', str(path))
        self.assertLess(len(result.stdout), 6100)
        result = self.run_script('tools/transcript-digest.py', str(path), '--max-chars', '200')
        self.assertIn('chars omitted', result.stdout)
        self.assertTrue(result.stdout.rstrip().endswith('x' * 100))

    def doctor(self) -> subprocess.CompletedProcess:
        return self.run_script('tools/vault-doctor.py', '--today', '2026-10-27')

    def test_doctor_clean_and_checks(self) -> None:
        self.assertEqual(self.doctor().stdout.strip(), 'vault-doctor: OK')
        (self.vault / 'bad.md').write_text('[[missing]]\n`[[inline]]`\n```\n[[fenced]]\n```\n')
        (self.mem / 'THREADS.md').write_text('## old\n- Status: 🟢\n- Last touched: 2026-01-01\n[[memory-missing]]')
        (self.mem / 'LAST_SESSION.md').write_text('x' * 3001)
        (self.mem / 'JOURNAL.md').write_text('line\n' * 251)
        secret = 'ghp_' + 'a' * 25
        (self.vault / 'credential.toml').write_text(secret)
        (self.home / '.claude/hooks/brain-memory.py').unlink()
        live = self.home / '.claude/settings.json'
        live.write_text('{}')
        subprocess.run(['git', 'init', '-q', str(self.vault)], check=True, capture_output=True)
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
        transcript.write_text(json.dumps({'type': 'user', 'message': {'content': ' '.join(secrets)}}))
        result = self.run_script('tools/transcript-digest.py', str(transcript))
        self.assertEqual(result.stdout.count('[REDACTED]'), 4)
        (self.vault / 'keys.json').write_text('\n'.join(secrets))
        result = self.doctor()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.count('ERROR secrets:'), 4)
        for secret in secrets:
            self.assertNotIn(secret, result.stdout)

    def test_doctor_ahead(self) -> None:
        def git(*args: str) -> None:
            subprocess.run(['git', '-C', str(self.vault), *args], env=self.env,
                           check=True, capture_output=True)
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
        (folder / 'Target.md').write_text('---\ntitle: Target\n---\n')
        (folder / 'Source.md').write_text('---\ntitle: Source\n---\n[[target|alias]] [[notes/Target.md#heading]] [[#local]]')
        (folder / 'README.md').write_text('[[ignored]]')
        (self.vault / 'runtime/ignored.md').write_text('[[ignored]]')
        self.assertEqual(self.doctor().stdout.strip(), 'vault-doctor: OK')


if __name__ == '__main__':
    unittest.main()

