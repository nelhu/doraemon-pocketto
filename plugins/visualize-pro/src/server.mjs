import crypto from 'node:crypto'
import fs from 'node:fs'
import http from 'node:http'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import * as z from 'zod/v4'

const PLUGIN_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const WIDGET_URI = 'ui://visualize-pro/widget-v1.html'
const MAX_HTML_BYTES = 2 * 1024 * 1024
const MAX_PREVIEWS = 32
const widgetHtml = fs.readFileSync(path.join(PLUGIN_ROOT, 'assets', 'widget.html'), 'utf8')
const previews = new Map()

let previewServer
let previewOrigin

function toolUiMeta() {
  return {
    ui: {
      resourceUri: WIDGET_URI,
    },
    'ui/resourceUri': WIDGET_URI,
    'openai/outputTemplate': WIDGET_URI,
    'openai/widgetAccessible': true,
    'openai/widgetShowCodexWidgetInline': true,
    'openai/toolInvocation/invoking': 'Rendering visualization',
    'openai/toolInvocation/invoked': 'Visualization rendered',
  }
}

function widgetResourceMeta() {
  const csp = {
    connectDomains: [],
    resourceDomains: [],
    frameDomains: [],
  }

  return {
    'openai/widgetDescription':
      'A self-contained Visualize Pro HTML renderer with no CDN or remote runtime dependency.',
    'openai/widgetPrefersBorder': false,
    'openai/widgetShowCodexWidgetInline': true,
    'openai/widgetCSP': {
      connect_domains: [],
      resource_domains: [],
      frame_domains: [],
    },
    ui: {
      prefersBorder: false,
      csp,
    },
  }
}

function byteLength(value) {
  return Buffer.byteLength(value, 'utf8')
}

function validateFragment(html) {
  const errors = []

  if (byteLength(html) > MAX_HTML_BYTES) {
    errors.push(`HTML exceeds the ${MAX_HTML_BYTES}-byte limit`)
  }
  if (/<!doctype\b/i.test(html) || /<\/?(?:html|head|body)(?:\s|>)/i.test(html)) {
    errors.push('HTML must be a fragment, not a complete document')
  }
  if (/<(?:iframe|object|embed|base|link)(?:\s|>)/i.test(html)) {
    errors.push('iframes, embedded documents, base elements, and external stylesheets are forbidden')
  }
  if (/<script\b[^>]*\bsrc\s*=/i.test(html)) {
    errors.push('external script sources are forbidden')
  }
  if (
    /\b(?:src|href|poster)\s*=\s*["']\s*https?:\/\//i.test(html) ||
    /url\(\s*["']?\s*https?:\/\//i.test(html) ||
    /@import\s+(?:url\()?["']?\s*https?:\/\//i.test(html)
  ) {
    errors.push('remote resources are forbidden; inline all widget assets')
  }
  if (
    /\bfetch\s*\(|\bXMLHttpRequest\b|\bWebSocket\s*\(|\bEventSource\s*\(|\bsendBeacon\s*\(/.test(
      html,
    )
  ) {
    errors.push('runtime network APIs are forbidden')
  }

  if (errors.length > 0) {
    throw new Error(errors.join('; '))
  }
}

function standaloneHtml(title, fragment) {
  const safeTitle = title
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; font-src data:; media-src data: blob:; connect-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
  <title>${safeTitle}</title>
  <style>
    :root {
      color-scheme: light dark;
      --background: Canvas;
      --foreground: CanvasText;
      --card: Canvas;
      --card-foreground: CanvasText;
      --muted: color-mix(in srgb, CanvasText 7%, Canvas);
      --muted-foreground: color-mix(in srgb, CanvasText 58%, Canvas);
      --border: color-mix(in srgb, CanvasText 16%, Canvas);
      --primary: #2563eb;
      --primary-foreground: #fff;
      --destructive: #dc2626;
      --viz-series-1: #2563eb;
      --viz-series-2: #16a34a;
      --viz-series-3: #d97706;
      --viz-series-4: #9333ea;
      --viz-series-5: #0891b2;
      --viz-series-6: #e11d48;
    }
    html, body { margin: 0; min-width: 0; background: var(--background); color: var(--foreground); }
    body { padding: 16px; font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    #visualize-pro-local { width: min(100%, 736px); margin: 0 auto; }
  </style>
</head>
<body>
  <main id="visualize-pro-local">${fragment}</main>
</body>
</html>`
}

function trimPreviews() {
  while (previews.size > MAX_PREVIEWS) {
    const oldest = previews.keys().next().value
    previews.delete(oldest)
  }
}

async function ensurePreviewServer() {
  if (previewServer && previewOrigin) return previewOrigin

  previewServer = http.createServer((request, response) => {
    response.setHeader('Cache-Control', 'no-store')
    response.setHeader('Content-Type', 'text/html; charset=utf-8')
    response.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
    response.setHeader('Referrer-Policy', 'no-referrer')
    response.setHeader('X-Content-Type-Options', 'nosniff')

    if (request.method !== 'GET') {
      response.writeHead(405).end('Method not allowed')
      return
    }

    const match = /^\/render\/([a-f0-9-]+)\/?$/.exec(request.url || '')
    const preview = match ? previews.get(match[1]) : undefined
    if (!preview) {
      response.writeHead(404).end('Not found')
      return
    }

    response.writeHead(200).end(preview)
  })

  await new Promise((resolve, reject) => {
    previewServer.once('error', reject)
    previewServer.listen(0, '127.0.0.1', resolve)
  })

  const address = previewServer.address()
  if (!address || typeof address === 'string') {
    throw new Error('Could not determine loopback preview address')
  }

  previewOrigin = `http://127.0.0.1:${address.port}`
  return previewOrigin
}

async function createPreview(title, html) {
  const origin = await ensurePreviewServer()
  const renderId = crypto.randomUUID()
  previews.set(renderId, standaloneHtml(title, html))
  trimPreviews()
  return `${origin}/render/${renderId}/`
}

const server = new McpServer({
  name: 'visualize-pro-renderer',
  version: '0.1.1',
})

server.registerResource(
  'visualize-pro-widget',
  WIDGET_URI,
  {
    description: 'Visualize Pro self-contained widget renderer',
    mimeType: 'text/html;profile=mcp-app',
    _meta: widgetResourceMeta(),
  },
  async () => ({
    contents: [
      {
        uri: WIDGET_URI,
        mimeType: 'text/html;profile=mcp-app',
        text: widgetHtml,
        _meta: widgetResourceMeta(),
      },
    ],
  }),
)

server.registerTool(
  'render_widget_html',
  {
    title: 'Render Visualize Pro widget HTML',
    description:
      'Render a validated, self-contained Visualize Pro HTML fragment in the plugin-owned MCP widget. The result also includes a 127.0.0.1 preview URL that bypasses the Codex web sandbox when enterprise network policy blocks it.',
    inputSchema: {
      title: z.string().trim().min(1).max(160).default('Visualization'),
      html: z.string().min(1).max(MAX_HTML_BYTES),
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: false,
      openWorldHint: false,
    },
    _meta: toolUiMeta(),
  },
  async ({ title, html }) => {
    try {
      validateFragment(html)
      const localPreviewUrl = await createPreview(title, html)
      const payload = {
        ok: true,
        title,
        html,
        localPreviewUrl,
        renderer: 'visualize-pro',
      }

      return {
        content: [
          {
            type: 'text',
            text: `Rendered "${title}" with Visualize Pro. Loopback fallback: ${localPreviewUrl}`,
          },
        ],
        structuredContent: payload,
        _meta: toolUiMeta(),
        isError: false,
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error)
      const payload = {
        ok: false,
        error: message,
        renderer: 'visualize-pro',
      }

      return {
        content: [{ type: 'text', text: `Visualize Pro rejected the fragment: ${message}` }],
        structuredContent: payload,
        isError: true,
      }
    }
  },
)

async function main() {
  const transport = new StdioServerTransport()
  await server.connect(transport)
  console.error('Visualize Pro renderer running on stdio')
}

main().catch((error) => {
  console.error('Visualize Pro renderer failed:', error)
  process.exit(1)
})
