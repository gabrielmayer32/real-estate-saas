# settings.py

# Enable AutoThrottle extension
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Add download delay
DOWNLOAD_DELAY = 5  # Increase delay between requests

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 5  # Number of retries for a failed request
RETRY_HTTP_CODES = [429, 500, 502, 503, 504, 522, 524, 408, 403]

# Rotate user agents
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
}

# List of User Agents
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3', 
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    # Add more user agents here
]

# settings.py

# Enable scrapy-proxies middleware
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 543,
    'scrapy_proxies.RandomProxy': 100,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}

# Proxy list
PROXY_LIST = 'path_to_your_proxy_list.txt'  # Specify the path to your proxy list file

# Retry settings
RETRY_TIMES = 10  # Adjust as needed

