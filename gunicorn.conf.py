# Gunicorn configuration file for GuessGame production deployment
import multiprocessing
import os

# Server socket - Use PORT from environment for Render compatibility
port = os.environ.get("PORT", "5000")
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes - Optimized for Render's free tier
workers = 2  # Fixed number for free tier reliability
worker_class = "sync"  # Use sync worker (default, no extra dependencies)
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging - Use stdout/stderr for Render logs
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "guessGame"

# Server mechanics
daemon = False
# pidfile not needed for containerized deployment
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment and configure for HTTPS if needed)
# keyfile = "/path/to/keyfile.key"
# certfile = "/path/to/certfile.crt"

# Environment variables are handled by Render platform
# No need to explicitly set raw_env
