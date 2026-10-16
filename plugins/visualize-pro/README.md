# Visualize Pro Renderer

`visualize-pro` is the rendering companion for the repository's
`skills/visualize-pro` authoring skill. It registers a local MCP tool named
`render_widget_html` and a self-contained MCP App resource at
`ui://visualize-pro/widget-v1.html`.

## Why it exists

The bundled Visualize renderer injects its own wrapper and remote scripts. A
skill cannot replace that host-level directive renderer. This plugin uses a
separate supported surface: its own MCP App HTML resource. The resource has no
CDN, font, icon, analytics, or runtime network dependency.

Every successful render also receives a random `127.0.0.1` preview URL. That
URL is a fallback for environments where enterprise network policy prevents the
Codex MCP web sandbox from initializing.

The MCP App shell observes the mounted fragment with `ResizeObserver` and calls
`window.openai.notifyIntrinsicHeight(height)` after the initial render and every
dynamic size change. Supported hosts can therefore fit the iframe to its
content instead of adding an inner scrollbar. If the host does not expose that
API, ordinary document overflow remains available as the safe fallback.

## Runtime architecture

```text
visualize-pro skill
  -> self-contained HTML fragment
  -> render_widget_html MCP tool
       -> structuredContent.html
       -> plugin-owned MCP App resource
       -> ResizeObserver -> notifyIntrinsicHeight
       -> inline HTML/CSS/SVG/JS
       -> 127.0.0.1 preview fallback
```

The MCP server is bundled into `mcp/server.mjs`, so installed runtime does not
need `node_modules` or network access. Node.js is the only runtime dependency.

## Development

```bash
bun install
bun run build
bun test
```

Validate the plugin manifest:

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

Install the repository marketplace and plugin:

```bash
codex plugin marketplace add /Users/xuezi/dir/doraemon-pocketto
codex plugin add visualize-pro@doraemon-pocketto
```

Open a new Codex task after installation so tool discovery includes
`visualizeProRenderer`.

## Security and limitations

- Widget fragments are limited to 2 MB and must be self-contained.
- Remote scripts, styles, media URLs, frames, embedded documents, and runtime
  network APIs are rejected.
- Inline JavaScript is intentionally supported and runs inside the MCP App
  sandbox or the local preview document.
- The host can cap inline expansion at `window.openai.maxHeight`; very tall
  visuals should use a compact inline composition or offer fullscreen instead
  of introducing nested scrolling.
- MCP App rendering still relies on Codex's generic MCP Apps sandbox. The
  loopback URL is the non-sandbox fallback; it is not embedded in the answer.
- The loopback server binds only to `127.0.0.1`, keeps at most 32 previews in
  memory, and stops with the MCP server process.

## Provenance

This implementation is original to `doraemon-pocketto`. Its protocol shape
follows the public Model Context Protocol SDK and OpenAI Apps SDK conventions.
It includes no code, assets, or dependencies from the bundled Visualize plugin.

Dependency versions and licenses:

- `@modelcontextprotocol/sdk` 1.29.0, MIT
- `zod` 4.4.3, MIT
