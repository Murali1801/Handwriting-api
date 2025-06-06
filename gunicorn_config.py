import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + os.getenv("PORT", "5000")
backlog = 2048

# Worker processes
workers = 1  # Use single worker for stability
worker_class = 'sync'
worker_connections = 1000
timeout = 300  # 5 minutes timeout
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'handwriting_generator'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Additional settings for stability
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 300 