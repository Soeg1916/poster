import os
import threading
import healthcheck
from run_miku_bot_standalone import force_standalone_bot

# Set environment variable to bypass conflict check
os.environ['BYPASS_CONFLICT_CHECK'] = 'true'

# Start health check server in background thread
t = threading.Thread(target=healthcheck.start_health_server)
t.daemon = True
t.start()

# Run the bot
force_standalone_bot()
