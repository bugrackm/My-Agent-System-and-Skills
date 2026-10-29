# Spending, Providers, and Failure Handling

## Cost boundary

Default is zero surprise overage.

Do not:
- enable automatic paid fallback;
- enable automatic balance top-up;
- switch to an API-key billed provider;
- add paid third-party services;
- consume paid image/API credits

without explicit user approval.

## Authentication

Do not display or copy secret/token content.
Inspect only enough metadata/status to verify the intended auth path.

Codex should use the user's existing ChatGPT subscription authentication unless
explicitly changed by the user.

## Failure handling

When a provider/tool/subagent fails:
1. identify the actual failure;
2. retry once only if the cause is transient and retry is safe;
3. do not mutate multiple configs randomly;
4. do not silently switch billing sources/models/providers;
5. return the failure and a specific next action to main Claude/user.

Protect reproducibility over "make it work somehow."
