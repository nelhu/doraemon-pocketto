import assert from 'node:assert/strict'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'

const pluginRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const transport = new StdioClientTransport({
  command: 'node',
  args: [path.join(pluginRoot, 'mcp', 'server.mjs')],
  stderr: 'pipe',
})
const client = new Client({
  name: 'visualize-pro-smoke',
  version: '0.1.1',
})

try {
  await client.connect(transport)

  const tools = await client.listTools()
  const renderer = tools.tools.find((tool) => tool.name === 'render_widget_html')
  assert(renderer, 'render_widget_html tool was not registered')
  assert.equal(renderer._meta['ui/resourceUri'], 'ui://visualize-pro/widget-v1.html')

  const resources = await client.listResources()
  assert(
    resources.resources.some((resource) => resource.uri === 'ui://visualize-pro/widget-v1.html'),
    'widget resource was not registered',
  )

  const resource = await client.readResource({ uri: 'ui://visualize-pro/widget-v1.html' })
  const widget = resource.contents[0]
  assert.equal(widget.mimeType, 'text/html;profile=mcp-app')
  assert.match(widget.text, /id="visualize-pro-widget"/)
  assert.match(widget.text, /notifyIntrinsicHeight/)
  assert.match(widget.text, /ResizeObserver/)
  assert.match(widget.text, /data-auto-height/)
  assert.doesNotMatch(widget.text, /unpkg|https?:\/\//)

  const result = await client.callTool({
    name: 'render_widget_html',
    arguments: {
      title: 'Smoke test',
      html: '<section id="smoke-widget" aria-label="Smoke test"><strong>ready</strong></section>',
    },
  })
  assert.equal(result.isError, false)
  assert.equal(result.structuredContent.renderer, 'visualize-pro')
  assert.match(result.structuredContent.localPreviewUrl, /^http:\/\/127\.0\.0\.1:\d+\/render\//)

  const response = await fetch(result.structuredContent.localPreviewUrl)
  assert.equal(response.status, 200)
  const preview = await response.text()
  assert.match(preview, /id="smoke-widget"/)
  assert.doesNotMatch(preview, /unpkg|https?:\/\/(?!127\.0\.0\.1)/)

  const rejected = await client.callTool({
    name: 'render_widget_html',
    arguments: {
      title: 'Blocked network',
      html: '<div id="bad"><script src="https://unpkg.com/example.js"></script></div>',
    },
  })
  assert.equal(rejected.isError, true)

  console.log('PASS: MCP resource, intrinsic height, tool result, offline CSP, and loopback preview')
} finally {
  await client.close()
}
