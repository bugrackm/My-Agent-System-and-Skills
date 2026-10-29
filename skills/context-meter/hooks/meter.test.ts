import { expect, test } from 'claude-code/testing'

import { meter } from './register'

test('formats tokens, window and percent', () => {
  expect(meter({ tokens: 100_000, window: 200_000, percent: 50 })).toBe(
    'ctx █████░░░░░ 100k/200k · 50%',
  )
})

test('warns past 85% and shortens millions', () => {
  expect(meter({ tokens: 900_000, window: 1_000_000, percent: 90 })).toBe(
    'ctx █████████░ 900k/1M · 90% ⚠',
  )
})

test('shows unknown fill before the first response', () => {
  expect(meter({ window: 200_000 })).toBe('ctx ?/200k')
})

test('session.measure appends the meter to the prompt hint line', async ($, on) => {
  const tails: (string | undefined)[] = []
  on('session.measure', ($, e) => ({ changed: e.changed }))
  on('ui.render', ($, e) => {
    if (e.component === 'PromptHint') tails.push(e.props.tail)

    return { type: 'Text', props: {}, children: [] }
  })

  await $.session.measure({
    context: { tokens: 42_000, window: 200_000, percent: 21 },
    rateLimits: [],
    changed: ['context'],
  })

  for (const surface of ['terminal', 'desktop'] as const) {
    await $.ui.render({
      surface,
      component: 'PromptHint',
      requestId: 'hint',
      props: { isDraft: false, isWorking: false, hint: '? for shortcuts' },
    })
  }

  expect(tails).toEqual([' · ctx ██░░░░░░░░ 42k/200k · 21%', ' · ctx ██░░░░░░░░ 42k/200k · 21%'])
})
