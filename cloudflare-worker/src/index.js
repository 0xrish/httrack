/**
 * Mikolabs Website Extractor Middleware - Cloudflare Worker
 * 
 * Proxies scraping requests to Apify Actor (mikolabs~web-extractor)
 * and generates clean CDN download URLs (cdn.mikolabs.xyz) for RapidAPI users.
 * Shields the Apify API token from end users.
 * 
 * Features SHA-256 URL hashing and intelligent Edge Caching to prevent
 * redundant Apify scraping runs and save compute costs.
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-RapidAPI-Key, X-RapidAPI-Host, X-RapidAPI-Proxy-Secret',
};

function jsonResponse(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      ...CORS_HEADERS,
      ...extraHeaders,
    },
  });
}

/**
 * Extract store ID from an Apify key-value store URL
 */
function extractStoreId(url) {
  if (!url) return null;
  const match = url.match(/key-value-stores\/([a-zA-Z0-9_-]+)/i);
  return match ? match[1] : null;
}

/**
 * Normalize URL string (removes trailing slashes, lowercases protocol/hostname)
 */
function normalizeUrl(targetUrl) {
  try {
    const parsed = new URL(targetUrl.trim());
    const path = parsed.pathname.replace(/\/+$/, '') || '/';
    return `${parsed.protocol.toLowerCase()}//${parsed.hostname.toLowerCase()}${path}${parsed.search}`;
  } catch (e) {
    return targetUrl.trim().toLowerCase().replace(/\/+$/, '');
  }
}

/**
 * Compute SHA-256 hash of a normalized URL string
 */
async function computeUrlHash(targetUrl) {
  const normalized = normalizeUrl(targetUrl);
  const encoder = new TextEncoder();
  const data = encoder.encode(normalized);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Pre-seeded default URLs with ready ZIP archives to save 100% compute costs
 */
const PRESEEDED_CACHE = {
  'https://bigbearslides.netlify.app': {
    url: 'https://bigbearslides.netlify.app',
    storeId: 'shFJd878gPppzwZdJ',
    outputName: 'bigbearslides.netlify.app',
    zipFile: 'bigbearslides.netlify.app_20261022_171711.zip',
    fileCount: 27,
    totalSize: 698242,
    totalSizeFormatted: '681.88 KB',
    zipSize: 661619,
    zipSizeFormatted: '646.11 KB',
    compressionRatio: 5.25,
    timestamp: '2026-10-22T17:17:39.476958',
    status: 'success'
  }
};

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const method = request.method.toUpperCase();

    // Handle CORS preflight
    if (method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    // Auth is ONLY required when initiating scrapes (POST /scrape, POST /scrape-async)
    // Download links (GET /download/:storeId/:key) and health checks do NOT require user auth.
    // The worker internally uses its own APIFY_TOKEN to extract and stream the zip to the user.
    const isScrapeAction = url.pathname === '/scrape' || url.pathname === '/scrape-async' || (url.pathname === '/' && method === 'POST');
    if (env.AUTH_BEARER_TOKEN && isScrapeAction) {
      const authHeader = request.headers.get('Authorization') || '';
      const queryToken = url.searchParams.get('token');
      const expectedBearer = `Bearer ${env.AUTH_BEARER_TOKEN}`;

      const isAuthorized = authHeader === expectedBearer ||
                           authHeader === env.AUTH_BEARER_TOKEN ||
                           queryToken === env.AUTH_BEARER_TOKEN;

      if (!isAuthorized) {
        return jsonResponse({
          error: 'Unauthorized: Missing or invalid Authorization header. Expected format: Authorization: Bearer <token>'
        }, 401);
      }
    }

    // Verify RapidAPI Secret if configured
    if (env.RAPIDAPI_PROXY_SECRET) {
      const proxySecret = request.headers.get('X-RapidAPI-Proxy-Secret');
      if (proxySecret !== env.RAPIDAPI_PROXY_SECRET) {
        return jsonResponse({ error: 'Unauthorized request: Invalid RapidAPI proxy secret' }, 401);
      }
    }

    const apifyToken = env.APIFY_TOKEN;
    if (!apifyToken) {
      return jsonResponse({ error: 'Server misconfiguration: APIFY_TOKEN environment variable is not configured' }, 500);
    }
    const actorId = env.ACTOR_ID || 'mikolabs~web-extractor';
    const cdnBase = (env.CDN_URL || 'https://cdn.mikolabs.xyz').replace(/\/+$/, '');

    // ROUTE: Health & Documentation
    if (url.pathname === '/' || url.pathname === '/health') {
      if (method === 'GET') {
        return jsonResponse({
          service: 'Mikolabs Web Extractor API',
          version: '1.2.0',
          status: 'online',
          cdn: cdnBase,
          caching: 'enabled (SHA-256 URL hashing + Edge Cache)',
          endpoints: {
            'POST /scrape': 'Start website scraping or retrieve cached ZIP directly by URL (Synchronous)',
            'POST /scrape-async': 'Start website scraping and receive runId (Asynchronous)',
            'GET /status/:runId': 'Check status of an asynchronous crawl',
            'GET /download/:storeId/:key': 'Public direct ZIP download stream (no user auth needed)'
          }
        });
      }
    }

    // ROUTE: Direct CDN ZIP Download proxy
    // Path: /download/:storeId/:key (or /download/:storeId/OUTPUT.zip)
    const downloadMatch = url.pathname.match(/^\/download\/([a-zA-Z0-9_-]+)\/(.+)$/);
    if (downloadMatch && method === 'GET') {
      const storeId = downloadMatch[1].trim();
      const recordKey = decodeURIComponent(downloadMatch[2]).trim().replace(/[\r\n\t]/g, '');

      const apifyRecordUrl = `https://api.apify.com/v2/key-value-stores/${storeId}/records/${encodeURIComponent(recordKey)}?token=${apifyToken}`;

      try {
        const apifyResp = await fetch(apifyRecordUrl, {
          cf: {
            cacheTtl: 604800, // 7 days edge cache
            cacheEverything: true,
          },
        });

        if (!apifyResp.ok) {
          return jsonResponse({
            error: `File not found or expired in storage (Status ${apifyResp.status})`,
            storeId,
            key: recordKey
          }, apifyResp.status);
        }

        const headers = new Headers(CORS_HEADERS);
        headers.set('Content-Type', apifyResp.headers.get('Content-Type') || 'application/zip');
        headers.set('Content-Disposition', `attachment; filename="${recordKey}"`);
        headers.set('Cache-Control', 'public, max-age=604800, s-maxage=604800');
        
        const contentLength = apifyResp.headers.get('Content-Length');
        if (contentLength) {
          headers.set('Content-Length', contentLength);
        }

        return new Response(apifyResp.body, {
          status: 200,
          headers,
        });
      } catch (err) {
        return jsonResponse({ error: `Failed to stream download: ${err.message}` }, 500);
      }
    }

    // ROUTE: Check Asynchronous Run Status
    // Path: /status/:runId
    const statusMatch = url.pathname.match(/^\/status\/([a-zA-Z0-9_-]+)$/);
    if (statusMatch && method === 'GET') {
      const runId = statusMatch[1];
      try {
        const runResp = await fetch(`https://api.apify.com/v2/actor-runs/${runId}?token=${apifyToken}`);
        if (!runResp.ok) {
          return jsonResponse({ error: `Run not found (${runResp.status})` }, runResp.status);
        }

        const runData = await runResp.json();
        const runStatus = runData?.data?.status;

        if (runStatus === 'SUCCEEDED') {
          const defaultDatasetId = runData.data.defaultDatasetId;
          const storeId = (runData.data.defaultKeyValueStoreId || '').trim();
          const datasetResp = await fetch(`https://api.apify.com/v2/datasets/${defaultDatasetId}/items?token=${apifyToken}`);
          const items = datasetResp.ok ? await datasetResp.json() : [];
          const item = items[0] || {};

          const cleanZipFile = String(item.zipFile || 'OUTPUT.zip').trim().replace(/[\r\n\t]/g, '');
          const zipFile = cleanZipFile || 'OUTPUT.zip';
          const urlHash = await computeUrlHash(item.url || '');

          return jsonResponse({
            status: 'SUCCEEDED',
            url: item.url,
            urlHash,
            downloadUrl: `${cdnBase}/download/${storeId}/${encodeURIComponent(zipFile)}`,
            directZipUrl: `${cdnBase}/download/${storeId}/OUTPUT.zip`,
            fileCount: item.fileCount,
            totalSizeFormatted: item.totalSizeFormatted,
            zipSizeFormatted: item.zipSizeFormatted,
            durationSeconds: item.durationSeconds,
            details: item
          });
        }

        return jsonResponse({
          status: runStatus,
          runId,
          startedAt: runData?.data?.startedAt,
          finishedAt: runData?.data?.finishedAt
        });
      } catch (err) {
        return jsonResponse({ error: `Failed to retrieve run status: ${err.message}` }, 500);
      }
    }

    // ROUTE: Asynchronous Scraper
    // Path: POST /scrape-async
    if (url.pathname === '/scrape-async' && method === 'POST') {
      let body = {};
      try {
        body = await request.json();
      } catch (e) {
        body = {};
      }

      const targetUrl = body.url || url.searchParams.get('url');
      if (!targetUrl) {
        return jsonResponse({ error: "Missing required 'url' field" }, 400);
      }

      const actorInput = {
        url: targetUrl,
        depth: Number(body.depth ?? url.searchParams.get('depth') ?? 2),
        stayOnDomain: body.stayOnDomain ?? true,
        connections: Number(body.connections ?? 4),
        externalDepth: Number(body.externalDepth ?? 0),
        timeout: Number(body.timeout ?? 30),
        retries: Number(body.retries ?? 2),
        maxRate: Number(body.maxRate ?? 0),
        maxSize: Number(body.maxSize ?? 0),
        maxTime: Number(body.maxTime ?? 0),
        getImages: body.getImages ?? true,
        getVideos: body.getVideos ?? true,
        followRobots: body.followRobots ?? true,
        outputName: body.outputName || null
      };

      try {
        const apifyResp = await fetch(`https://api.apify.com/v2/actors/${actorId}/runs?token=${apifyToken}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(actorInput)
        });

        if (!apifyResp.ok) {
          const errText = await apifyResp.text();
          return jsonResponse({ error: 'Failed to start scraping task', details: errText }, apifyResp.status);
        }

        const runData = await apifyResp.json();
        const runId = runData?.data?.id;

        return jsonResponse({
          success: true,
          message: 'Scraping job started successfully',
          runId,
          statusUrl: `${cdnBase}/status/${runId}`,
          checkStatus: `GET /status/${runId}`
        }, 202);
      } catch (err) {
        return jsonResponse({ error: `Error triggering async scraper: ${err.message}` }, 500);
      }
    }

    // ROUTE: Synchronous Scraper with SHA-256 URL Hashing & Edge Cache (Default)
    // Path: POST /scrape or POST /
    if ((url.pathname === '/scrape' || url.pathname === '/') && method === 'POST') {
      let body = {};
      try {
        body = await request.json();
      } catch (e) {
        body = {};
      }

      const targetUrl = body.url || url.searchParams.get('url');
      if (!targetUrl) {
        return jsonResponse({
          error: "Missing required 'url' parameter",
          example: {
            url: "https://example.com",
            depth: 2,
            stayOnDomain: true,
            connections: 4
          }
        }, 400);
      }

      // Compute cryptographic SHA-256 hash of the normalized target URL
      const normalized = normalizeUrl(targetUrl);
      const urlHash = await computeUrlHash(targetUrl);
      const forceRefresh = body.forceRefresh === true || url.searchParams.get('forceRefresh') === 'true';

      // 1. Check Pre-seeded Cache for Default URLs (saves compute completely)
      if (!forceRefresh && PRESEEDED_CACHE[normalized]) {
        const cachedItem = PRESEEDED_CACHE[normalized];
        const storeId = cachedItem.storeId;
        const zipFile = cachedItem.zipFile;

        return jsonResponse({
          success: true,
          cached: true,
          url: cachedItem.url,
          urlHash,
          downloadUrl: `${cdnBase}/download/${storeId}/${encodeURIComponent(zipFile)}`,
          directZipUrl: `${cdnBase}/download/${storeId}/OUTPUT.zip`,
          outputName: cachedItem.outputName,
          zipFile,
          fileCount: cachedItem.fileCount,
          totalSize: cachedItem.totalSize,
          totalSizeFormatted: cachedItem.totalSizeFormatted,
          zipSize: cachedItem.zipSize,
          zipSizeFormatted: cachedItem.zipSizeFormatted,
          compressionRatio: cachedItem.compressionRatio,
          durationSeconds: 0.05,
          timestamp: cachedItem.timestamp,
          status: 'success'
        });
      }

      // 2. Check Cloudflare Edge Cache API for previously scraped URLs
      const cache = caches.default;
      const cacheUrl = new URL(`https://cache.internal/scrape/${urlHash}`);
      const cacheKey = new Request(cacheUrl.toString());

      if (!forceRefresh) {
        try {
          const cachedResponse = await cache.match(cacheKey);
          if (cachedResponse) {
            const cachedData = await cachedResponse.json();
            return jsonResponse({
              ...cachedData,
              cached: true,
              urlHash
            });
          }
        } catch (e) {
          // Continue to live run if cache read fails
        }
      }

      // 3. Fallback: Trigger Apify Actor run
      const actorInput = {
        url: targetUrl,
        depth: Number(body.depth ?? url.searchParams.get('depth') ?? 2),
        stayOnDomain: body.stayOnDomain ?? true,
        connections: Number(body.connections ?? 4),
        externalDepth: Number(body.externalDepth ?? 0),
        timeout: Number(body.timeout ?? 30),
        retries: Number(body.retries ?? 2),
        maxRate: Number(body.maxRate ?? 0),
        maxSize: Number(body.maxSize ?? 0),
        maxTime: Number(body.maxTime ?? 0),
        getImages: body.getImages ?? true,
        getVideos: body.getVideos ?? true,
        followRobots: body.followRobots ?? true,
        outputName: body.outputName || null
      };

      try {
        const apifyUrl = `https://api.apify.com/v2/actors/${actorId}/run-sync-get-dataset-items?token=${apifyToken}`;
        
        const apifyResp = await fetch(apifyUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(actorInput)
        });

        if (!apifyResp.ok) {
          const errText = await apifyResp.text();
          return jsonResponse({
            error: 'Scraping failed or timed out on Apify platform',
            details: errText
          }, apifyResp.status);
        }

        const items = await apifyResp.json();
        const item = Array.isArray(items) && items.length > 0 ? items[0] : items;

        if (!item || !item.url) {
          return jsonResponse({
            error: 'Scraping finished but no output items were found',
            rawOutput: items
          }, 500);
        }

        // Extract store ID and clean filename
        const storeId = (extractStoreId(item.zipUrl) || extractStoreId(item.keyValueStoreUrl) || extractStoreId(item.zipDirectUrl) || '').trim();
        const cleanZipFile = String(item.zipFile || 'OUTPUT.zip').trim().replace(/[\r\n\t]/g, '');
        const zipFile = cleanZipFile || 'OUTPUT.zip';

        // Generate clean CDN download URLs (tokens hidden from client)
        const downloadUrl = storeId
          ? `${cdnBase}/download/${storeId}/${encodeURIComponent(zipFile)}`
          : item.zipUrl;

        const directZipUrl = storeId
          ? `${cdnBase}/download/${storeId}/OUTPUT.zip`
          : (item.zipDirectUrl || downloadUrl);

        const responsePayload = {
          success: true,
          cached: false,
          url: item.url,
          urlHash,
          downloadUrl,
          directZipUrl,
          outputName: item.outputName,
          zipFile,
          fileCount: item.fileCount,
          totalSize: item.totalSize,
          totalSizeFormatted: item.totalSizeFormatted,
          zipSize: item.zipSize,
          zipSizeFormatted: item.zipSizeFormatted,
          compressionRatio: item.compressionRatio,
          durationSeconds: item.durationSeconds,
          timestamp: item.timestamp,
          config: item.config,
          status: item.status || 'success'
        };

        // Cache the result on Cloudflare Edge for 7 days
        try {
          ctx.waitUntil(
            cache.put(
              cacheKey,
              new Response(JSON.stringify(responsePayload), {
                headers: {
                  'Content-Type': 'application/json',
                  'Cache-Control': 'public, max-age=604800, s-maxage=604800'
                }
              })
            )
          );
        } catch (e) {
          // Pass silently
        }

        return jsonResponse(responsePayload);
      } catch (err) {
        return jsonResponse({
          error: `Internal error communicating with scraper engine: ${err.message}`
        }, 500);
      }
    }

    // Default 404
    return jsonResponse({
      error: `Endpoint not found: ${method} ${url.pathname}`,
      availableEndpoints: ['POST /scrape', 'POST /scrape-async', 'GET /status/:runId', 'GET /download/:storeId/:key']
    }, 404);
  }
};
