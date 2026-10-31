# Spending, Providers, and Failure Handling

## Cost and authentication

The limits (no paid services, credits, top-ups, fallback, or API-key billing
without the user's approval; no secrets in output) are in the global CLAUDE.md.
When checking an auth path, inspect only enough metadata/status to verify it.

## Failure handling

When a provider/tool/subagent fails:
1. identify the actual failure;
2. retry once only if the cause is transient and retry is safe;
3. do not mutate multiple configs randomly;
4. do not silently switch billing sources/models/providers;
5. return the failure and a specific next action to main Claude/user.

Protect reproducibility over "make it work somehow."
