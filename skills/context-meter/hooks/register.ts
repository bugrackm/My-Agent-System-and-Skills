import { atom, read, update } from 'claude-code'
import type { Register, SessionContextUsage } from 'claude-code'

import type { MeterLine } from '../types'

const WIDTH = 10

const line = atom({ plugin: 'context-meter', key: 'line' } as const, null as MeterLine)

const short = (n: number) =>
  n >= 1_000_000 ? `${+(n / 1_000_000).toFixed(1)}M` : n >= 1000 ? `${Math.round(n / 1000)}k` : `${n}`

export const meter = ({ tokens, window, percent }: SessionContextUsage) => {
  if (tokens === undefined) return `ctx ?/${short(window)}`

  const pct = percent ?? Math.round((tokens / window) * 100)
  const filled = Math.min(WIDTH, Math.round((pct / 100) * WIDTH))
  const warn = pct >= 85 ? ' ⚠' : ''

  return `ctx ${'█'.repeat(filled)}${'░'.repeat(WIDTH - filled)} ${short(tokens)}/${short(window)} · ${pct}%${warn}`
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    // 0.1.0 pinned the meter with $.ui.status; the host keeps that line across reloads.
    $.ui.status(undefined)
    const { context } = await $.session.usage()
    await update($, line, () => meter(context))

    return result
  })

  on('session.measure', async ($, e, next) => {
    await update($, line, () => meter(e.context))

    return next(e)
  })

  on('ui.render', { component: 'PromptHint' }, async ($, e, next) => {
    const text = await read($, line)

    return text === null ? next(e) : next({ ...e, props: { ...e.props, tail: ` · ${text}` } })
  })
}
