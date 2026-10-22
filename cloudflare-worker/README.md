# Mikolabs Web Extractor - Cloudflare Worker Middleware

Production-ready Cloudflare Worker that acts as a secure middleware between **RapidAPI** users and the **Apify Actor** (`mikolabs~web-extractor`).

## Features

- 🛡️ **Hides Apify Tokens**: RapidAPI consumers never see your Apify API credentials.
- ⚡ **Custom CDN Domain (`cdn.mikolabs.xyz`)**: All ZIP downloads and API endpoints are branded through your custom domain.
- 📦 **Direct ZIP Streaming**: Proxies ZIP archives directly from Apify Key-Value Stores with edge caching (`Cache-Control: public, max-age=86400`).
- 🔄 **Sync & Async Modes**:
  - `POST /scrape`: Synchronous scraping with instant download link and statistics.
  - `POST /scrape-async` & `GET /status/:runId`: Asynchronous scraping for larger websites.
- 🌐 **Full CORS Support**: Compatible with web apps, frontend clients, and RapidAPI's API tester.

---

## Architecture Flow

```
[ RapidAPI User ]
       │
       ▼  POST /scrape { "url": "https://example.com" }
[ Cloudflare Worker (cdn.mikolabs.xyz) ]
       │
       ▼  POST run-sync-get-dataset-items?token=*** (Private)
[ Apify Actor (mikolabs~web-extractor) ]
       │
       ▼  Returns metadata + Key-Value Store ID
[ Cloudflare Worker ]
       │
       ▼  Returns JSON with download link: "https://cdn.mikolabs.xyz/download/{storeId}/{zipFile}"
[ RapidAPI User ]
       │
       ▼  GET https://cdn.mikolabs.xyz/download/{storeId}/{zipFile}
[ Cloudflare Worker (Streams ZIP from Apify storage & caches on Edge) ]
```

---

## Deployment to Cloudflare Workers

### 1. Prerequisites
Install [Node.js](https://nodejs.org/) (v18+) and Wrangler CLI:
```bash
npm install -g wrangler
# or run via npx
```

### 2. Configure Environment & Secrets
In `cloudflare-worker/wrangler.toml`:
```toml
name = "mikolabs-scraper-worker"
main = "src/index.js"
compatibility_date = "2024-01-01"

[vars]
ACTOR_ID = "mikolabs~web-extractor"
CDN_URL = "https://cdn.mikolabs.xyz"
```

Set your secrets in Cloudflare Workers:
```bash
cd cloudflare-worker

# 1. Apify API Token (required)
npx wrangler secret put APIFY_TOKEN
# Paste your Apify API Token when prompted

# 2. Bearer Authentication Token (to secure your worker)
npx wrangler secret put AUTH_BEARER_TOKEN
# Enter your custom secret token (e.g. my_secret_token_123)

# 3. Optional: RapidAPI Proxy Secret (for RapidAPI integration)
npx wrangler secret put RAPIDAPI_PROXY_SECRET
```

### 3. Deploy
```bash
npx wrangler deploy
```

### 4. Custom Domain Setup (`cdn.mikolabs.xyz`)
1. Open the [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. Navigate to **Workers & Pages** → Select `mikolabs-scraper-worker`.
3. Go to **Settings** → **Triggers** → **Custom Domains**.
4. Click **Add Custom Domain** and enter `cdn.mikolabs.xyz`.
5. Cloudflare will automatically provision SSL certificates and route traffic to your Worker.

---

## API Reference (For RapidAPI)

### 1. Synchronous Scrape (`POST /scrape` or `POST /`)

**Request Headers**:
```http
Content-Type: application/json
Authorization: Bearer <your_token>
```

**Request Body**:
```json
{
  "url": "https://example.com",
  "depth": 2,
  "stayOnDomain": true,
  "connections": 4,
  "getImages": true,
  "getVideos": true,
  "followRobots": true
}
```

**Response (`200 OK`)**:
```json
{
  "success": true,
  "url": "https://example.com",
  "downloadUrl": "https://cdn.mikolabs.xyz/download/JH0DNwc7Bgzy0AMOE/example.com_20261022_222313.zip",
  "directZipUrl": "https://cdn.mikolabs.xyz/download/JH0DNwc7Bgzy0AMOE/OUTPUT.zip",
  "outputName": "example.com_20261022_222313",
  "zipFile": "example.com_20261022_222313.zip",
  "fileCount": 156,
  "totalSize": 5242880,
  "totalSizeFormatted": "5.00 MB",
  "zipSize": 2621440,
  "zipSizeFormatted": "2.50 MB",
  "compressionRatio": 50.0,
  "durationSeconds": 14.52,
  "timestamp": "2026-10-22T22:21:03.313Z",
  "status": "success"
}
```

---

### 2. Direct ZIP Download (`GET /download/:storeId/:key`)

Downloads the archive directly from the CDN with automatic browser attachment headers.

**Example**:
```http
GET https://cdn.mikolabs.xyz/download/JH0DNwc7Bgzy0AMOE/OUTPUT.zip
```
**Response**: Binary ZIP stream (`Content-Type: application/zip`).

---

### 3. Asynchronous Scrape (`POST /scrape-async`)

For larger websites that take longer than 60 seconds:

**Response (`202 Accepted`)**:
```json
{
  "success": true,
  "message": "Scraping job started successfully",
  "runId": "k3n9f8s9fh32",
  "statusUrl": "https://cdn.mikolabs.xyz/status/k3n9f8s9fh32"
}
```

Check status via:
```http
GET https://cdn.mikolabs.xyz/status/k3n9f8s9fh32
```
When finished, it responds with status `SUCCEEDED` and the final `downloadUrl` on `cdn.mikolabs.xyz`.

---

## Local Development & Testing

Run the worker locally:
```bash
cd cloudflare-worker
npx wrangler dev
```
Test with curl:
```bash
curl -X POST http://localhost:8787/scrape \
  -H "Content-Type: application/json" \
  -d '{"url":"https://bigbearslides.netlify.app","depth":1}'
```
