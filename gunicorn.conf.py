import os

workers = int(os.environ.get("WEB_CONCURRENCY", 2 * (os.cpu_count() or 1) + 1))
worker_class = "sync"
threads = 1
bind = "0.0.0.0:8000"
timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
accesslog = "-"
errorlog = "-"
loglevel = "info"
forwarded_allow_ips = "*"
