from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
async_to_sync(channel_layer.send)("test_channel", {"type": "test.message", "message": "Hello, Redis!"})
