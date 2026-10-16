# Provenance and Licensing Boundary

This skill is an original synthesis created for the `doraemon-pocketto` repository on 2026-07-22.

## Phoenix influence

The design was informed at a concept level by an internal Phoenix Generative UI implementation, including relationship-first form selection, content-first visual hierarchy, deterministic SVG geometry, semantic color, and progressive visual complexity. The inspected implementation snapshot included `packages/sdk/src/agent/widget-guidelines.ts` at revision `17fe7277d53d776a4d1cdbda31c37d78e2e529dc` in Phoenix PC.

No Phoenix source code, fixed prompt text, token names, assets, or runtime-specific `widget` fence was copied into this skill. Phoenix's renderer and prompt injection are not dependencies.

## Codex renderer investigation

The output contract was checked against OpenAI's bundled Visualize plugin
version 1.0.14 and the installed Codex Desktop host to identify the renderer
boundary. The `::codex-inline-vis` directive is consumed by app-level code, and
its wrapper assets cannot be replaced by a personal skill or plugin manifest.

The bundled plugin is proprietary. This skill does not copy or redistribute its
`SKILL.md`, scripts, assets, package content, or implementation.

## Runtime boundary

`visualize-pro` replaces the bundled skill's authoring workflow and avoids its
directive renderer. The companion plugin registers an independent MCP App
resource and `render_widget_html` tool. Its HTML, CSS, SVG, JavaScript, CSP, and
loopback fallback are original implementations under
`plugins/visualize-pro`.

The in-conversation surface still depends on Codex's generic MCP Apps sandbox.
The loopback fallback exists because a skill or plugin cannot replace that
host-level sandbox.

## Dependencies and redistribution

- Required runtime: Node.js and Codex MCP Apps support
- Required local tool: Python 3 for optional validation
- Included runtime bundle dependencies: `@modelcontextprotocol/sdk` 1.29.0
  (MIT) and `zod` 4.4.3 (MIT)
- Included third-party assets: none
- Default output dependencies: none

Any future library, map boundary file, font, icon, or copied example must record
its exact source, version, license, and redistribution terms here before it is
committed. CDN and remote runtime dependencies are forbidden by the renderer
contract.
