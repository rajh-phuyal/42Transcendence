from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

channel_layer = get_channel_layer()

def open_connection(user, connection_id):
    """Initialize WebSocket connection for a user."""
    logging.info(f"Opening WebSocket connection for user {user} with connection ID {connection_id}")
    # You can perform any initialization logic here, such as logging or tracking active connections
    return True

def close_connection(user, connection_id):
    """Clean up when WebSocket connection is closed."""
    logging.info(f"Closing WebSocket connection for user {user} with connection ID {connection_id}")
    # Any cleanup logic for when a WebSocket connection is closed goes here
    return True

def broadcast_message(group_name, event):
    """Send a message to a WebSocket group."""
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": event["type"],
            "message": event["message"],
            "sender": event.get("sender"),
        }
    )

def verify_websocket_token(token):
    """Utility to verify a JWT token for WebSocket connections."""
    from rest_framework_simplejwt.tokens import AccessToken
    try:
        access_token = AccessToken(token)
        return access_token.get("user_id")
    except Exception as e:
        return None
