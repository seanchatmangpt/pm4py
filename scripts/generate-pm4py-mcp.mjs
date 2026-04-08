/**
 * Generate pm4py FastMCP server from ontology via O* projector engine.
 *
 * Usage: node scripts/generate-pm4py-mcp.mjs
 *
 * Pipeline: ontology/pm4py_mcp.nt → SPARQL → templates/fastmcp-server.njk → pm4py_mcp/server.py
 */

import { readFileSync, mkdirSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ROOT = join(__dirname, '..')

// Paths
const ONTOLOGY_PATH = join(ROOT, 'ontology', 'pm4py_mcp.nt')
const TEMPLATE_PATH = join(ROOT, 'templates', 'fastmcp-server.njk')
const OUTPUT_PATH = join(ROOT, 'pm4py_mcp', 'server.py')

const SPARQL_QUERY = `
PREFIX pm4py: <urn:pm4py-mcp:>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

SELECT
  ?toolName
  ?toolDescription
  ?pythonModule
  ?pythonFunction
  ?argName
  ?argType
  ?argDescription
  ?required
  ?defaultValue
WHERE {
  ?tool a pm4py:McpTool ;
        pm4py:toolName ?toolName ;
        pm4py:toolDescription ?toolDescription ;
        pm4py:pythonModule ?pythonModule ;
        pm4py:pythonFunction ?pythonFunction .

  OPTIONAL {
    ?tool pm4py:hasArg ?arg .
    ?arg pm4py:argName ?argName ;
         pm4py:argType ?argType .
    OPTIONAL { ?arg pm4py:argDescription ?argDescription }
    OPTIONAL { ?arg pm4py:required ?required }
    OPTIONAL { ?arg pm4py:defaultValue ?defaultValue }
  }
}
ORDER BY ?toolName ?argName
`

async function main() {
  // 1. Load ontology into a KGCStore
  const { KGCStore } = await import('@unrdf/kgc-4d')
  const store = new KGCStore()

  const ontologyContent = readFileSync(ONTOLOGY_PATH, 'utf-8')
  await store.load(ontologyContent, { format: 'application/n-triples' })

  const stats = store.stats()
  console.log(`Loaded ontology: ${stats.triples} triples`)

  // 2. Execute SPARQL query
  const raw = store.query(SPARQL_QUERY)
  const arr = Array.isArray(raw) ? raw : raw === true ? [] : [raw]

  // Unwrap RDF term objects to plain values
  const bindings = arr.map((row) => {
    const unwrapped = {}
    for (const [key, val] of Object.entries(row)) {
      unwrapped[key] = val && typeof val === 'object' && 'value' in val ? val.value : val
    }
    return unwrapped
  })

  console.log(`SPARQL returned ${bindings.length} binding rows`)

  // 3. Render Nunjucks template
  const nunjucksMod = await import('nunjucks')
  const { Environment: Nunjucks, FileSystemLoader } = nunjucksMod
  const loader = new FileSystemLoader([join(ROOT, 'templates')])
  const env = new Nunjucks(loader, {
    autoescape: false,
    trimBlocks: true,
    lstripBlocks: true,
  })

  const templateName = 'fastmcp-server.njk'
  const rendered = env.render(templateName, {
    results: bindings,
    family: 'pm4py-mcp',
    now: new Date(),
    project: { name: 'pm4py-mcp', version: '2.7.22.1' },
  })

  // 4. Write output
  mkdirSync(dirname(OUTPUT_PATH), { recursive: true })
  writeFileSync(OUTPUT_PATH, rendered, 'utf-8')

  console.log(`Generated: ${OUTPUT_PATH}`)
  console.log(`Size: ${rendered.length} bytes`)
}

main().catch((err) => {
  console.error('Generation failed:', err)
  process.exit(1)
})
