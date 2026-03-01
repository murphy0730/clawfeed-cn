# ClawFeed

AI-powered news digest tool. Automatically generates structured summaries (4H/daily/weekly/monthly) from Twitter, RSS, HackerNews, Reddit, GitHub Trending and more.

## Credentials & Dependencies

ClawFeed runs in **read-only mode** with zero credentials — browse digests, view feeds. Authentication features (bookmarks, sources, packs) require WeChat credentials or dev-login.

| Credential | Purpose | Required |
|-----------|---------|----------|
| `WECHAT_APPID` | WeChat Mini-Program login | For production auth |
| `WECHAT_SECRET` | WeChat Mini-Program login | For production auth |
| `JWT_SECRET` | JWT token signing | Recommended |
| `API_KEY` | Digest creation endpoint protection | For write API |

**Runtime dependency:** SQLite (development) or MySQL (production). No native addons required.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env with your settings

# Start API server
uvicorn app.main:app --reload --port 8000
# → Swagger UI at http://localhost:8000/docs
```

## Environment Variables

Configure in `.env` file:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | Database connection URL | No | `sqlite:///data/clawfeed.db` |
| `DIGEST_PORT` | Server port | No | 8000 |
| `WECHAT_APPID` | WeChat Mini-Program App ID | For auth | - |
| `WECHAT_SECRET` | WeChat Mini-Program App Secret | For auth | - |
| `JWT_SECRET` | JWT signing key | Recommended | dev-jwt-secret |
| `API_KEY` | Admin API key | For write API | - |
| `ALLOWED_ORIGINS` | CORS allowed origins | No | localhost |

## API Server

Runs on port `8000` by default. Swagger UI available at `/docs`.

### Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /api/digests | List digests (?type=4h\|daily\|weekly&limit=20&offset=0) | - |
| GET | /api/digests/:id | Get single digest | - |
| POST | /api/digests | Create digest | API Key |
| POST | /api/auth/login | WeChat login (code → JWT) | - |
| POST | /api/auth/dev-login | Dev login (no WeChat needed) | - |
| GET | /api/auth/me | Get current user info | JWT |
| GET | /api/marks | List user bookmarks | JWT |
| POST | /api/marks | Add bookmark | JWT |
| DELETE | /api/marks/:id | Remove bookmark | JWT |
| GET | /api/sources | List sources | - |
| POST | /api/sources | Create source | JWT |
| POST | /api/sources/resolve | Auto-detect source from URL | JWT |
| GET | /api/subscriptions | List subscriptions | JWT |
| POST | /api/subscriptions | Subscribe to source | JWT |
| GET | /api/packs | List source packs | - |
| POST | /api/packs/:slug/install | Install pack | JWT |
| POST | /api/feedback | Submit feedback | - |
| GET | /feed/:slug.json | JSON Feed output | - |
| GET | /feed/:slug.rss | RSS Feed output | - |

## Templates

- `templates/curation-rules.md` — Customize feed curation rules
- `templates/digest-prompt.md` — Customize the AI summarization prompt
