# Production Gunicorn Configuration

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 4
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Timeouts
timeout = 30
keepalive = 2
graceful_timeout = 30

# Process naming
proc_name = 'attendance_backend'

# Logging
accesslog = 'logs/gunicorn_access.log'
errorlog = 'logs/gunicorn_error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# SSL (if enabled)
# keyfile = 'ssl/key.pem'
# certfile = 'ssl/cert.pem'

# Process management
pidfile = 'gunicorn.pid'
user = 'appuser'
group = 'appuser'
tmp_upload_dir = None

# Performance tuning
worker_tmp_dir = "/dev/shm"

# Restart workers after this many requests, with up to half that
# number added to avoid all workers restarting at the same time
max_requests = 1000
max_requests_jitter = 50

# The maximum number of simultaneous clients per worker
worker_connections = 1000

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")