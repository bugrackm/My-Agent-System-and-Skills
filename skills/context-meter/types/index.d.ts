export type MeterLine = string | null

declare module 'claude-code' {
  interface PluginState {
    'context-meter': { line: MeterLine }
  }
}
