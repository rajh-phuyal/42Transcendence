"""
## UTILS
## ------------------------------------------------------------------------------------------------
# To send by consumer
# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
async def send_response_message(client_consumer, type, message):
    logging.info(f"Sending message to connection {client_consumer}: {message}")
    message_dict = {
        "messageType": type,
        "message": message
    }
    json_message = json.dumps(message_dict)
    await client_consumer.send(text_data=json_message)



@async_to_sync
# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
async def send_message_to_user_sync(user_id, **message):
    await send_message_to_user(user_id, **message)

 """

# TODO: REMOVE WHEN FINISHED #284