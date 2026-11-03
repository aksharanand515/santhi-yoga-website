<?php
/* ==================================================================
   Santhi School of Yoga & Vedanta Studies: a read-only MCP server
   ------------------------------------------------------------------
   An AI agent (Claude, ChatGPT and the like) can connect to
   https://santhiyogaindia.com/mcp and ask about the school: its key
   facts, any page of the site, a search across the Journal, and a
   ready-written WhatsApp message to book a class. Nothing here
   changes anything or sends anything: it only reads llms.txt and the
   Markdown copy of each page that tools/build.js writes.

   Model Context Protocol over Streamable HTTP, stateless: one POST,
   one JSON reply, no sessions. It answers both the current revision
   (2026-07-28, server/discover) and the older ones that open with
   initialize. .htaccess routes /mcp here; the server card that
   describes it is .well-known/mcp/server-card.json.

   Everything it serves is public, so any web page may call it
   (Access-Control-Allow-Origin: *) and no sign-in is needed.
   ================================================================== */

const SITE = 'https://santhiyogaindia.com';
const SERVER_INFO = ['name' => 'santhiyogaindia', 'title' => 'Santhi School of Yoga & Vedanta Studies', 'version' => '1.0.0'];
const VERSIONS = ['2026-07-28', '2025-11-25', '2025-06-18', '2025-03-26', '2024-11-05'];
const LEGACY_DEFAULT = '2025-11-25';
const WHATSAPP = '917907714144';
const EMAIL = 'santhiyogacochin@gmail.com';
const INSTRUCTIONS = 'Read-only information about Santhi School of Yoga & Vedanta Studies, a traditional Hatha Yoga school in Fort Kochi, Kerala, India: '
  . 'daily walk-in classes, private sessions, retreats and a 28-day 200-hour yoga teacher training. Start with get_school_facts for times, prices and dates; '
  . 'they are kept current, so prefer them over older sources. Use search_site and get_page for anything else. '
  . 'Enquiries and bookings happen on WhatsApp: draft_booking_message writes the message, and the person sends it themselves.';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Accept, Authorization, MCP-Protocol-Version, Mcp-Session-Id, Mcp-Method, Mcp-Name, Last-Event-ID');
header('Cache-Control: no-store');
header('X-Robots-Tag: noindex');

$httpMethod = $_SERVER['REQUEST_METHOD'] ?? 'GET';
if ($httpMethod === 'OPTIONS') { http_response_code(204); exit; }
if ($httpMethod !== 'POST') {
  // No event stream to open: this server only answers POSTs
  header('Allow: POST, OPTIONS');
  reply(405, ['error' => 'This is a Model Context Protocol server (Streamable HTTP). Send JSON-RPC requests by POST.',
    'serverCard' => SITE . '/.well-known/mcp/server-card.json']);
}

$headerVersion = $_SERVER['HTTP_MCP_PROTOCOL_VERSION'] ?? '';
if ($headerVersion !== '' && !in_array($headerVersion, VERSIONS, true)) {
  reply(400, rpcError(null, -32022, 'Unsupported protocol version', ['supported' => VERSIONS, 'requested' => $headerVersion]));
}

$raw = file_get_contents('php://input', false, null, 0, 1000000);
$body = json_decode((string) $raw, true);
if (!is_array($body)) reply(400, rpcError(null, -32700, 'Parse error: the body must be a JSON-RPC message'));

// A batch (older revisions) gets a batch back; notifications get no answer at all
$isBatch = array_keys($body) === range(0, count($body) - 1);
$answers = [];
$status = 200;
foreach ($isBatch ? $body : [$body] as $msg) {
  $answer = handle(is_array($msg) ? $msg : [], $headerVersion, $status);
  if ($answer !== null) $answers[] = $answer;
}
if (!$answers) { http_response_code(202); exit; }
reply($isBatch ? 200 : $status, $isBatch ? $answers : $answers[0]);

/* ---------- JSON-RPC ---------- */

function reply(int $status, $data): void {
  http_response_code($status);
  header('Content-Type: application/json; charset=utf-8');
  echo json_encode($data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
  exit;
}

function rpcError($id, int $code, string $message, $data = null): array {
  $error = ['code' => $code, 'message' => $message];
  if ($data !== null) $error['data'] = $data;
  return ['jsonrpc' => '2.0', 'id' => $id, 'error' => $error];
}

function handle(array $msg, string $headerVersion, int &$status): ?array {
  if (!isset($msg['method']) || !is_string($msg['method'])) {
    // A reply from the client to something we never asked: nothing to say
    return array_key_exists('id', $msg) && !isset($msg['result']) && !isset($msg['error'])
      ? rpcError($msg['id'], -32600, 'Invalid request') : null;
  }
  if (!array_key_exists('id', $msg)) return null; // notifications/initialized and the like
  $id = $msg['id'];
  $params = isset($msg['params']) && is_array($msg['params']) ? $msg['params'] : [];
  $version = $headerVersion ?: (string) ($params['_meta']['io.modelcontextprotocol/protocolVersion'] ?? '');
  $modern = $version === '2026-07-28';

  try {
    switch ($msg['method']) {
      case 'initialize':
        $asked = (string) ($params['protocolVersion'] ?? '');
        $result = [
          'protocolVersion' => in_array($asked, VERSIONS, true) && $asked !== '2026-07-28' ? $asked : LEGACY_DEFAULT,
          'capabilities' => capabilities(),
          'serverInfo' => SERVER_INFO,
          'instructions' => INSTRUCTIONS,
        ];
        break;
      case 'server/discover':
        $modern = true;
        $result = [
          'supportedVersions' => VERSIONS,
          'capabilities' => capabilities(),
          '_meta' => ['io.modelcontextprotocol/serverInfo' => SERVER_INFO],
          'instructions' => INSTRUCTIONS,
          'ttlMs' => 3600000,
          'cacheScope' => 'public',
        ];
        break;
      case 'ping':
        $result = new stdClass();
        break;
      case 'tools/list':
        $result = ['tools' => tools()];
        break;
      case 'tools/call':
        $result = callTool((string) ($params['name'] ?? ''), isset($params['arguments']) && is_array($params['arguments']) ? $params['arguments'] : []);
        break;
      case 'resources/list':
        $result = ['resources' => resources()];
        break;
      case 'resources/templates/list':
        $result = ['resourceTemplates' => [[
          'uriTemplate' => SITE . '/{path}index.md', 'name' => 'page', 'title' => 'Any page of the site, as Markdown',
          'description' => 'The Markdown copy of a page, e.g. ' . SITE . '/teacher-training/index.md', 'mimeType' => 'text/markdown',
        ]]];
        break;
      case 'resources/read':
        $uri = (string) ($params['uri'] ?? '');
        $file = fileForUrl($uri);
        if ($file === null) return rpcError($id, -32602, 'Resource not found', ['uri' => $uri]);
        $result = ['contents' => [[
          'uri' => $uri, 'mimeType' => substr($file, -3) === '.md' ? 'text/markdown' : 'text/plain', 'text' => file_get_contents($file),
        ]]];
        break;
      default:
        if ($modern) $status = 404;
        return rpcError($id, -32601, 'Method not found: ' . $msg['method']);
    }
  } catch (Throwable $e) {
    return rpcError($id, -32603, 'Internal error');
  }
  if ($modern && is_array($result)) $result = ['resultType' => 'complete'] + $result;
  return ['jsonrpc' => '2.0', 'id' => $id, 'result' => $result];
}

function capabilities(): array {
  return ['tools' => ['listChanged' => false], 'resources' => ['listChanged' => false]];
}

/* ---------- The site's own files ---------- */

/* A page address (full URL, /about/, about, /about/index.md) to its Markdown
   file, or llms.txt. Anything outside the site's own pages is refused. */
function fileForUrl(string $url): ?string {
  $path = $url;
  if (stripos($path, SITE) === 0) $path = substr($path, strlen(SITE));
  elseif (preg_match('#^[a-z][a-z0-9+.-]*://#i', $path)) return null;
  $path = (string) parse_url($path, PHP_URL_PATH);
  $path = trim(preg_replace('#(^|/)index\.(html|md)$#', '$1', $path), '/');
  if ($path === 'llms.txt') return __DIR__ . '/llms.txt';
  if (!preg_match('#^[a-z0-9-]+(/[a-z0-9-]+)*$#', $path) && $path !== '') return null;
  $file = __DIR__ . '/' . ($path === '' ? '' : $path . '/') . 'index.md';
  return is_file($file) ? $file : null;
}

function llms(): string {
  return str_replace("\r\n", "\n", (string) file_get_contents(__DIR__ . '/llms.txt'));
}

/* Every page listed in llms.txt: [title, url, description] */
function pages(): array {
  preg_match_all('#^- \[([^\]]+)\]\((' . preg_quote(SITE, '#') . '/[^)]*)\): (.*)$#m', llms(), $m, PREG_SET_ORDER);
  $pages = [];
  foreach ($m as $row) {
    if (fileForUrl($row[2]) === null || substr($row[2], -3) === '.md') continue; // the "For AI agents" links
    $pages[$row[2]] = [$row[1], $row[2], $row[3]];
  }
  return array_values($pages);
}

function resources(): array {
  $list = [['uri' => SITE . '/llms.txt', 'name' => 'llms.txt', 'title' => 'The school and every page, in one file', 'mimeType' => 'text/plain']];
  foreach (pages() as [$title, $url, $desc]) {
    $list[] = ['uri' => $url . 'index.md', 'name' => trim((string) parse_url($url, PHP_URL_PATH), '/') ?: 'home', 'title' => $title, 'description' => $desc, 'mimeType' => 'text/markdown'];
  }
  return $list;
}

/* ---------- Tools ---------- */

function tools(): array {
  $readOnly = ['readOnlyHint' => true, 'destructiveHint' => false, 'idempotentHint' => true, 'openWorldHint' => false];
  return [
    [
      'name' => 'get_school_facts',
      'title' => 'Key facts about the school',
      'description' => 'The current key facts about Santhi School of Yoga & Vedanta Studies in Fort Kochi, Kerala: address, class times, prices, teacher training dates and fees, the teacher, and how to get in touch.',
      'inputSchema' => ['type' => 'object', 'properties' => new stdClass()],
      'annotations' => $readOnly,
    ],
    [
      'name' => 'search_site',
      'title' => 'Search the site',
      'description' => 'Search the school\'s pages and its Journal of yoga, Ayurveda and Kerala travel guides. Returns the best matching pages with their address and a summary; read one with get_page.',
      'inputSchema' => [
        'type' => 'object',
        'properties' => [
          'query' => ['type' => 'string', 'description' => 'What to look for, e.g. "pranayama for beginners" or "airport to Fort Kochi"'],
          'limit' => ['type' => 'integer', 'minimum' => 1, 'maximum' => 20, 'default' => 8, 'description' => 'How many pages to return'],
        ],
        'required' => ['query'],
      ],
      'annotations' => $readOnly,
    ],
    [
      'name' => 'get_page',
      'title' => 'Read a page',
      'description' => 'Read one page of santhiyogaindia.com as Markdown, e.g. "/teacher-training/", "/services/" or a Journal article address from search_site.',
      'inputSchema' => [
        'type' => 'object',
        'properties' => ['path' => ['type' => 'string', 'description' => 'The page address or path, e.g. "/teacher-training/" or "https://santhiyogaindia.com/about/"']],
        'required' => ['path'],
      ],
      'annotations' => $readOnly,
    ],
    [
      'name' => 'draft_booking_message',
      'title' => 'Draft a booking message',
      'description' => 'Write an enquiry or booking message to the school and return a WhatsApp link and an email link that open with it filled in. Nothing is sent: the person opens a link and presses send. Classes need no booking; this is for questions, private sessions, retreats and the teacher training.',
      'inputSchema' => [
        'type' => 'object',
        'properties' => [
          'name' => ['type' => 'string', 'description' => 'The name of the person enquiring'],
          'interest' => ['type' => 'string', 'enum' => ['a daily Hatha Yoga class', 'a private session', 'the 200-hour teacher training', 'a retreat', 'a workshop', 'online classes', 'something else'], 'description' => 'What they would like to join'],
          'dates' => ['type' => 'string', 'description' => 'When, e.g. "12 to 15 March" or "the January 2027 batch"'],
          'people' => ['type' => 'integer', 'minimum' => 1, 'maximum' => 20, 'default' => 1, 'description' => 'How many people'],
          'note' => ['type' => 'string', 'description' => 'Anything else the teacher should know: a question, an injury, where they are staying'],
        ],
        'required' => ['name', 'interest'],
      ],
      'annotations' => $readOnly,
    ],
  ];
}

function text(string $s, bool $isError = false): array {
  return ['content' => [['type' => 'text', 'text' => $s]], 'isError' => $isError];
}

function callTool(string $name, array $args): array {
  switch ($name) {
    case 'get_school_facts':
      $doc = llms();
      $cut = strpos($doc, "\n## Main pages");
      return text(trim($cut === false ? $doc : substr($doc, 0, $cut)) . "\n\nEvery page: " . SITE . '/llms.txt');

    case 'search_site':
      $query = trim((string) ($args['query'] ?? ''));
      if ($query === '') return text('Give a query to search for.', true);
      $limit = max(1, min(20, (int) ($args['limit'] ?? 8)));
      $terms = array_values(array_filter(preg_split('/[^\p{L}\p{N}]+/u', mb_strtolower($query)), function ($t) { return mb_strlen($t) > 1; }));
      $scored = [];
      foreach (pages() as [$title, $url, $desc]) {
        $t = mb_strtolower($title); $d = mb_strtolower($desc);
        $file = fileForUrl($url);
        $b = $file ? mb_strtolower((string) file_get_contents($file)) : '';
        $score = 0;
        foreach ($terms as $term) {
          $score += 6 * substr_count($t, $term) + 3 * substr_count($d, $term) + min(10, substr_count($b, $term)) * 0.3;
        }
        if ($score > 0) $scored[] = [$score, "- [$title]($url): $desc"];
      }
      usort($scored, function ($a, $b) { return $b[0] <=> $a[0]; });
      if (!$scored) return text("Nothing on the site matches \"$query\". The school's key facts are in get_school_facts; every page is listed at " . SITE . '/llms.txt');
      return text(implode("\n", array_column(array_slice($scored, 0, $limit), 1)));

    case 'get_page':
      $file = fileForUrl((string) ($args['path'] ?? ''));
      if ($file === null) return text('No page at that address. Use search_site to find one, or see ' . SITE . '/llms.txt for every page.', true);
      return text((string) file_get_contents($file));

    case 'draft_booking_message':
      $who = trim((string) ($args['name'] ?? ''));
      $what = trim((string) ($args['interest'] ?? ''));
      if ($who === '' || $what === '') return text('A name and what they would like to join are both needed.', true);
      $people = max(1, min(20, (int) ($args['people'] ?? 1)));
      $dates = trim((string) ($args['dates'] ?? ''));
      $note = trim((string) ($args['note'] ?? ''));
      $message = "Namaste Achu,\n\nMy name is $who, and I would love to join $what"
        . ($dates !== '' ? " ($dates)" : '')
        . ($people > 1 ? " for $people people" : '') . '.'
        . ($note !== '' ? "\n\n$note" : '')
        . "\n\nWith thanks,\n$who";
      $wa = 'https://wa.me/' . WHATSAPP . '?text=' . rawurlencode($message);
      $mail = 'mailto:' . EMAIL . '?subject=' . rawurlencode('Enquiry: ' . $what) . '&body=' . rawurlencode($message);
      return text("Message:\n\n$message\n\nSend it on WhatsApp (the school replies fastest there): $wa\n\nOr by email: $mail\n\nNothing has been sent. The person opens one of the links and presses send.");
  }
  return text('Unknown tool: ' . $name, true);
}
