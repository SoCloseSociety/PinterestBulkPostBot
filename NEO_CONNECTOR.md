# NEO_CONNECTOR -- PinterestBulkPostBot
- service: pinterestbulk
- base_url_prod: N/A (no HTTP API -- local CLI / Selenium browser-automation bot)
- auth: none (interactive Pinterest login in a real browser; no service auth, no API key)
- env_required: []
- generated_at:

## Endpoints
NONE. This project exposes **no HTTP/webhook/SSE/WebSocket/cron/queue endpoints**.

Proof from code (`main.py`, the only logic file, 480 LOC):
- No web framework imported. `requirements.txt` = `beautifulsoup4`, `selenium`,
  `webdriver-manager` only -- no flask/fastapi/aiohttp/uvicorn/express.
- `grep -rniE 'flask|fastapi|aiohttp|uvicorn|@app\.|app\.route|@router|websocket|http.server'`
  over `*.py` returns nothing.
- Entry point is a CLI: `main()` -> `argparse.ArgumentParser` (`main.py:347-375`),
  guarded by `if __name__ == "__main__": main()` (`main.py:479-480`).
- It drives Chrome via Selenium (`create_driver`, `main.py:155`) to log into
  `https://www.pinterest.com/login/` and post pins through the Pinterest web UI
  (`PINTEREST_PIN_BUILDER_URL`, `main.py:31-32`). These are Pinterest's own pages,
  not endpoints this repo serves.

### Invocation surface (CLI only -- NOT an HTTP API)
The program is invoked as `python main.py [flags]`. Flags (`main.py:355-374`):

| flag | type | required | default | description |
|------|------|----------|---------|-------------|
| --config | str (path) | no | config.json | JSON config file path |
| --csv | str (path) | no | None | per-image metadata CSV (filename,title,description,link,board) |
| --headless | flag | no | False | run Chrome headless |
| --board | str | no | None | Pinterest board name override |
| --images | str (path) | no | bulk_post_pinterest | images folder |

config.json keys (`load_config` defaults, `main.py:89-95`): `board_name`,
`login_wait_seconds`, `delay_between_pins`, `images_folder`, `headless`.

Runtime is interactive: it prompts on stdin for login confirmation and default
pin metadata (`main.py:209`, `404-410`) and waits up to `login_wait_seconds`
for a human to log in. This cannot run unattended/headless-API style.

## Flows
Single local flow (no network API):
1. `python main.py --csv pins.csv --board "X"` -> loads config + CSV metadata.
2. Opens Chrome, navigates to Pinterest login, **waits for human login** (`wait_for_login`).
3. For each image in the folder: navigate to pin-builder, upload, fill title/desc/link,
   select board, wait for publish (`post_single_pin`, `main.py:332`).
4. Prints a summary to stdout. No callbacks, no job ids, no polling.

## Gaps
- None affecting endpoint discovery: the repo is unambiguously a local CLI bot with
  zero served endpoints.

## Recap for NeoBot wiring
- Endpoints found: **0**. Already covered: 0. New: 0.
- **DO NOT wire this repo as Neo HTTP tools.** There is no API to call. Any future
  Neo integration would have to shell out to `python main.py ...` on a host that has
  Chrome + an interactive Pinterest session, which violates the unattended-tool model.
  Treat as a manual/operator-run utility, not a fleet service.
