# Multi-Region Hospital Status Sync Design

## Goal

Extend the existing `hospital-status-sync` worker so one process can sequentially synchronize multiple configured ERMCT regions while preserving the current single-region behavior.

## Configuration

`HOSPITAL_STATUS_SYNC_TARGETS` is optional. When non-empty, it contains ordered comma-separated `sido:sigungu` pairs. Whitespace around entries and pair values is ignored. Every entry must contain exactly one separator with non-empty `sido` and `sigungu` values; malformed input is reported as a configuration error before synchronization starts.

When the variable is unset or empty, the worker continues to use `--sido` / `--sigungu` and their existing `HOSPITAL_STATUS_SYNC_SIDO` / `HOSPITAL_STATUS_SYNC_SIGUNGU` fallbacks.

`HOSPITAL_STATUS_SYNC_TARGET_DELAY_SECONDS` is optional, defaults to `3`, and must be a non-negative integer. The delay applies only between targets.

## Worker Structure

The existing fetch, normalization, and Supabase upsert behavior remains in `run_sync_once()`. It will accept explicit region values for multi-target orchestration while retaining fallback resolution for single-region callers.

New focused helpers will:

- parse and validate target configuration;
- resolve either configured targets or the legacy single target;
- parse and validate the target delay;
- run one complete cycle over all targets in order.

`run_sync_cycle()` logs each target start and result, continues after returned failures or raised exceptions, sleeps only between targets, and returns `1` if any target failed. Its final summary reports total, succeeded, failed, and `success` or `partial-failed` status.

## Runtime Behavior

One-shot mode runs one complete target cycle and returns its status. Long-running mode runs a complete target cycle, logs its status, sleeps for `--interval-seconds`, and retries every target during the next cycle. A target failure does not terminate the worker loop.

## Deployment

`docker-compose.prod.yml` remains unchanged because the worker already receives `.env.production`. `.env.production.example` will document blank, opt-in multi-target configuration, a commented Seoul example, and the default target delay without exposing server credentials to frontend variables.

## Testing

Unit tests will cover:

- legacy single-region fallback;
- ordered multi-target parsing;
- malformed and empty pair rejection;
- sequential execution and between-target delays;
- configurable delay and the three-second default;
- continued processing and partial-failure cycle status;
- deployment environment-template entries and unchanged server-only secret handling.

Validation will use Poetry for the focused tests, full test suite, and `compileall`. No frontend or unrelated backend files will change.
