// The hosted half of the async workshop, deployed by `python3 brain/workshop.py host`.
//
//   GET  /api/form            a health check: is the store connected, is the key set
//   GET  /api/form?t=TOKEN    the form and the answers saved so far
//   PUT  /api/form?t=TOKEN    save the answers (the page sends them as they are typed)
//   POST /api/form            create a form; only with the workspace's WORKSHOP_ADMIN_KEY
//
// The token in the link is the only identity: one link, one person, no login. Answers live in
// the project's Upstash Redis, one key per form, and the previous save is kept beside it.
// No dependencies: Upstash answers plain HTTP.

const STORE = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const STORE_KEY = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
const ADMIN = process.env.WORKSHOP_ADMIN_KEY || "";
const TOKEN = /^[A-Za-z0-9_-]{16,64}$/;
const MAX = 400_000;

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });

async function kv(...cmd) {
  if (!STORE || !STORE_KEY) throw new Error("no store");
  const r = await fetch(STORE, {
    method: "POST",
    headers: { authorization: `Bearer ${STORE_KEY}` },
    body: JSON.stringify(cmd),
  });
  const j = await r.json();
  if (j.error) throw new Error(j.error);
  return j.result;
}

const tokenOf = (req) => new URL(req.url).searchParams.get("t") || "";

function same(a, b) {
  if (a.length !== b.length) return false;
  let x = 0;
  for (let i = 0; i < a.length; i++) x |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return x === 0;
}

export async function GET(req) {
  const t = tokenOf(req);
  if (!t) return json({ ok: true, store: Boolean(STORE && STORE_KEY), admin: Boolean(ADMIN) });
  if (!TOKEN.test(t)) return json({ error: "not found" }, 404);
  try {
    const [spec, answers] = await kv("MGET", `form:${t}:spec`, `form:${t}:answers`);
    if (!spec) return json({ error: "not found" }, 404);
    return json({ spec: JSON.parse(spec), answers: answers ? JSON.parse(answers) : null });
  } catch {
    return json({ error: "store unavailable" }, 503);
  }
}

export async function PUT(req) {
  const t = tokenOf(req);
  if (!TOKEN.test(t)) return json({ error: "not found" }, 404);
  const text = await req.text();
  if (text.length > MAX) return json({ error: "too large" }, 413);
  let b;
  try {
    b = JSON.parse(text);
  } catch {
    return json({ error: "not json" }, 400);
  }
  if (!b || typeof b.answers !== "object" || Array.isArray(b.answers)) return json({ error: "no answers" }, 400);
  try {
    if (!(await kv("EXISTS", `form:${t}:spec`))) return json({ error: "not found" }, 404);
    const saved = new Date().toISOString();
    const body = JSON.stringify({ answers: b.answers, at: Number(b.at) || Date.now(), done: Boolean(b.done), saved });
    const prev = await kv("SET", `form:${t}:answers`, body, "GET");
    if (prev) await kv("SET", `form:${t}:prev`, prev);
    return json({ ok: true, saved });
  } catch {
    return json({ error: "store unavailable" }, 503);
  }
}

export async function POST(req) {
  const key = req.headers.get("x-workshop-key") || "";
  if (!ADMIN || !same(key, ADMIN)) return json({ error: "forbidden" }, 403);
  let b;
  try {
    b = await req.json();
  } catch {
    return json({ error: "not json" }, 400);
  }
  if (!TOKEN.test(b?.token || "") || !Array.isArray(b?.spec?.sections)) return json({ error: "not a form" }, 400);
  try {
    await kv("SET", `form:${b.token}:spec`, JSON.stringify(b.spec));
    return json({ ok: true }, 201);
  } catch {
    return json({ error: "store unavailable" }, 503);
  }
}
