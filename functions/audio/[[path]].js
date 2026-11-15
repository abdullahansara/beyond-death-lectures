// Cloudflare Pages serves static files without HTTP Range support. Browsers need byte ranges to show an
// audio file's length, to seek, and (Safari) to play at all. This function answers range requests for /audio/*.
export async function onRequest({ request, env }) {
  const asset = await env.ASSETS.fetch(request);
  if (!asset.ok) return asset;

  const headers = new Headers(asset.headers);
  headers.set('Accept-Ranges', 'bytes');
  headers.set('Cache-Control', 'public, max-age=86400');

  const range = request.headers.get('Range');
  if (request.method === 'HEAD' || !range) {
    return new Response(request.method === 'HEAD' ? null : asset.body, { status: asset.status, headers });
  }

  const m = /^bytes=(\d*)-(\d*)$/.exec(range.trim());
  const buf = await asset.arrayBuffer();
  const size = buf.byteLength;
  if (!m || (m[1] === '' && m[2] === '')) {
    return new Response(buf, { status: 200, headers });
  }
  let start, end;
  if (m[1] === '') {                       // suffix range: last N bytes
    const n = parseInt(m[2], 10);
    start = Math.max(0, size - n);
    end = size - 1;
  } else {
    start = parseInt(m[1], 10);
    end = m[2] === '' ? size - 1 : Math.min(parseInt(m[2], 10), size - 1);
  }
  if (start >= size || start > end) {
    headers.set('Content-Range', `bytes */${size}`);
    return new Response(null, { status: 416, headers });
  }
  headers.set('Content-Range', `bytes ${start}-${end}/${size}`);
  headers.set('Content-Length', String(end - start + 1));
  return new Response(buf.slice(start, end + 1), { status: 206, headers });
}
