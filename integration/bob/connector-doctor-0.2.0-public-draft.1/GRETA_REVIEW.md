# Greta patterns reviewed — November 2, 2026

Public primary sources inspected: [connector catalogue](https://www.greta.sh/connectors), [GitHub workflow](https://www.greta.sh/connectors/github), [code-export acceptance guide](https://www.greta.sh/field-guides/a-code-export-acceptance-test-for-ai-app-builders). The Docs link redirected to a learning-hub page with no readable body in the web reader. This review does not establish dashboard internals, API schemas, authentication implementation or actual live connector health.

Greta's public catalogue describes setup through a host dashboard, scoped authentication and revocation. Its GitHub page illustrates event → AI processing → notification. Its export guide recommends testing the actual exported project in a fresh environment. These are vendor descriptions and a proposed test method, not independently measured service behavior. We copied no vendor code, branded UI or prose; no private WIT material was sent to Greta.

| Classification | Pattern and WIT disposition |
|---|---|
| REUSE | Bob RC1 already checks actual host capabilities, respects denial, preserves consent, verifies saves and offers ordinary-chat fallback. Existing catalogue and installation-doctor rules already cover discovery and evidence. |
| INTEGRATE | A compact connection-state distinction, exact callable-tool/action checks, a read-only host bridge and result consistency checks now support Bob's existing host step. |
| IMPROVE | Repair advisory ambiguity around provider-side drafts, stale/copied observations, complete request binding, connector-level versus tool-level scope, and uncertain outcomes. Independently rerun the original candidate and test reproducible installation. |
| DEFER | Event listeners, visual flow builder, universal OAuth broker, broad vendor-specific adapter catalogue, hosted dashboards and automatic notifications. No need for them to run RC1 trials. |
| REJECT | Proprietary source extraction, sharing private records/source with Greta, treating marketing as executable access, automatic sends, new subscriptions, copying credentials or bypassing denials. |

Review scope: documented public patterns only. Existing RC1 and catalogue discovery were reused; no vendor integration engine, subscriptions or background automation were introduced.
