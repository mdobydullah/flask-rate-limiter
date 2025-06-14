## Flask Rate Limiter

A lightweight, customizable **rate limiter** for Flask applications using Redis. Supports per-route, per-IP throttling with human-readable decorators like:

```python
@ratelimit(key='ip', rate='3/m', mode='fixed')
@ratelimit(key='ip', rate='10/m', mode='token')
```

## Features

- Token bucket algorithm
- Fixed window counter algorithm
- Route-specific rate limits
- IP-based limit, can easily be extended to user ID or email-based throttling
- Redis-based for persistence
- TTL-based automatic cleanup

## Quick Start

#### 1. Clone & Install

```bash
pip install -r requirements.txt
```

#### 2. Set up `.env`

Copy `.env.example` and enter Redis credentials.

```env
cp .env.example .env
```

#### 3. Run the App

```bash
python app.py
```

#### 4. Example Route

```python
@app.route('/api')
@ratelimit(key='ip', rate='10/m', mode='token')
def api_data():
    return "API response"
```

## Rate Limit params

`@ratelimit(params)`

| Param  | Example   | Meaning               |
|--------|-----------|-----------------------|
| `key`  | `'ip'`    | IP based              |
| `rate` | `'5/m'`   | 5 requests per minute |
| `mode` | `'fixed'` | `fixed` or `token`    |

## Project Structure

```
├── app.py              # Flask app
├── limiter/
│   ├── core.py         # RateLimiter logic
│   └── helpers.py      # Decorator & parser
├── .env
└── requirements.txt
```
