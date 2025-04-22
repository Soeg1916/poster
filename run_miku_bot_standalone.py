#!/usr/bin/env python
"""
Production-ready script to run the Miku bot in standalone mode.
This script is designed to be run by itself in production environments like Koyeb.
"""
import os
import logging
import socket
import sys
import time
import traceback
import requests
from bot import setup_bot

# Set up logging with more verbose output for production
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Check if the bot is already running by detecting conflicts
def is_bot_already_running():
    """
    Check if another instance of this bot is already running.
    Attempts to make a getUpdates request to Telegram to see if there's a conflict.
    
    Returns:
        bool: True if bot is already running, False otherwise
    """
    # If bypass is enabled, always return False
    if os.environ.get('BYPASS_CONFLICT_CHECK') == 'true':
        logger.info("BYPASS_CONFLICT_CHECK is set - skipping conflict detection")
        return False
        
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables!")
        return False
        
    try:
        # Try to make a getUpdates request
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, timeout=5)
        
        # If we got a conflict error, another instance is running
        if response.status_code == 409:
            logger.info("Conflict detected: Bot is already running in another instance.")
            return True
            
        # If successful, no other instance is running
        if response.ok:
            logger.info("No conflict detected: Bot is not running elsewhere.")
            return False
            
        # If some other error, log it and assume no conflict
        logger.warning(f"Unexpected response checking bot status: {response.status_code}")
        return False
    except Exception as e:
        logger.exception(f"Error checking if bot is running: {e}")
        return False

# Force standalone mode for workflow, but only if another instance isn't running
def force_standalone_bot():
    print("============================================")
    print("MIKU BOT FORCED STANDALONE MODE")
    print("This script bypasses Flask completely")
    print("============================================")
    
    # Check if another instance is already running
    if is_bot_already_running():
        print("Another instance of the bot is already running!")
        print("This instance will act as a monitor only.")
        
        # Just keep this process alive without starting another bot
        try:
            while True:
                time.sleep(60)
                print("Monitoring... Bot is running in another workflow.")
        except KeyboardInterrupt:
            print("Monitor stopped.")
        return
    
    try:
        # Initialize Reddit client
        from api_clients import initialize_reddit_client
        reddit_client = initialize_reddit_client()
        
        # Start the bot directly without Flask
        updater = setup_bot()
        
        # Keep the script running with proper signal handling
        if updater:
            print("Bot setup successful. Starting to poll for updates...")
            print("Press Ctrl+C to stop the bot")
            updater.idle()
        else:
            print("Bot setup failed. Check logs for details.")
            while True:
                time.sleep(10)
    except Exception as e:
        logger.error(f"Error running standalone bot: {e}")
        traceback.print_exc()
        
if __name__ == "__main__":
    # Always run in standalone mode when executed directly
    force_standalone_bot()
