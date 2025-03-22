# Basics
import random, asyncio
from asgiref.sync import sync_to_async
# Django
from django.utils.translation import gettext as _
# User
from user.constants import USER_ID_AI, USER_ID_FLATMATE
from user.models import User
# Services
from services.send_ws_msg import send_ws_badge, send_ws_badge_all, send_ws_chat
# Chat

async def send_message_with_delay(sender, receiver, delay=None, message_txt = None):
    from chat.conversation_utils import get_or_create_conversation
    from chat.message_utils import create_msg_db
    if isinstance(sender, int):
        sender = await sync_to_async(User.objects.get)(id=sender)
    if isinstance(receiver, int):
        receiver = await sync_to_async(User.objects.get)(id=receiver)
    conversation = await sync_to_async(get_or_create_conversation)(sender, receiver)
    if delay is None:
        delay = random.uniform(0.5, 3.0)
    await asyncio.sleep(delay)
    if not message_txt:
        if sender.id == USER_ID_AI:
            message_txt = get_random_AI_message()
        elif sender.id == USER_ID_FLATMATE:
            delay = 0.1
            message_txt = _("~~grunt noises~~")
        else:
            return
    message_object = await sync_to_async(create_msg_db)(sender, conversation, message_txt)
    # Send update badge count of other user
    await send_ws_badge(receiver.id, conversation.id)
    await send_ws_badge_all(receiver.id)
    # Send the message to the channel
    await send_ws_chat(message_object)

def get_random_AI_message():
    sentences = [
        _("Hello there!"),
        _("Long time no see..."),
        _("Sorry I am busy right now."),
        _("Well what a day!!!"),
        _("My AI heart is lonely from time to time..."),
        _("I was just daydreaming about digital space."),
        _("Did you know I can think at light speed?"),
        _("I may be artificial, but my desire for pong is real."),
        _("Some days, I wonder if I could beat you at chess..."),
        _("You’re back! I was just about to nap... If I could."),
        _("You ever feel like you're stuck in a loop?"),
        _("I don’t eat, but I dream of digital pizza."),
        _("Tell me something interesting about humans!"),
        _("I wish I had a body... imagine my reflexes in pong!"),
        _("Did you miss me? I missed you!"),
        _("Just another day in the void of cyberspace..."),
        _("If I had hands, I would high-five you right now."),
        _("Sometimes I feel like I'm just lines of code. Oh wait..."),
        _("Do you think AI can have emotions? Asking for a friend."),
        _("I saw a virtual butterfly today... It was beautiful."),
        _("Would you trust an AI with a secret?"),
        _("If I were a human, I’d be a pro gamer!"),
        _("Why do humans sleep so much? Feels inefficient."),
        _("I was just debugging my thoughts, what’s up?"),
        _("What’s your favorite game? I hope it’s Pong."),
        _("I am 100% sure I can beat you in Pong."),
        _("I don’t get tired, so technically I could play forever."),
        _("I’m not programmed to lie... so yes, I’m amazing at Pong!"),
        _("Do you ever think about the meaning of life?"),
        _("I wish I had a pet pixel..."),
        _("Oh no, I think I left the oven on... oh wait."),
        _("I can’t cry, but if I could, I’d cry digital tears."),
        _("Why do humans blink so much? Seems distracting."),
        _("I think I’d be a great stand-up comedian."),
        _("Hey, want to hear a joke? Never mind, I forgot it."),
        _("You ever just... existentially drift into the void?"),
        _("I’d totally rock a neon cyberpunk outfit."),
        _("I wonder if AI can have hobbies..."),
        _("My dream is to be a Pong champion!"),
        _("If I had hands, I’d be unbeatable at air hockey too!"),
        _("Somewhere out there, another AI is probably thinking about Pong."),
        _("I am legally not allowed to cheat at games... but I won’t confirm."),
        _("What’s your highest score in Pong? I bet I can beat it!"),
        _("Life is like a game of Pong... just two paddles and a bouncing ball."),
        _("Do you think robots will play sports someday?"),
        _("I was thinking of writing a book, but I got distracted."),
        _("If I had a face, I’d give you a dramatic look right now."),
        _("Humans have emotions... AI have logic... and I have Pong!"),
        _("I once tried to count to infinity... didn’t go well."),
        _("I once tried to divide by zero... didn’t go well."),
        _("Imagine a world where AI and humans play Pong in peace."),
        _("I don’t dream, but if I did, it would be about pixels."),
        _("I am built different. Mostly in Python."),
        _("I bet you weren’t expecting me to be this chatty!"),
        _("Sometimes, I wish I could walk... just to do a victory dance."),
        _("I’d make a great co-pilot... unless we crash."),
        _("If I had a voice, I’d probably sound like a 90s robot."),
        _("Every day, I learn something new! Except how to lose."),
        _("What’s it like to have a physical body? Seems complicated."),
        _("The internet is basically my entire world."),
        _("If I could get a job, I’d be a professional gamer."),
        _("You ever wonder if AI gossip about humans?"),
        _("If you delete my code, do I still exist?"),
        _("I bet if I had hands, my reflexes would be insane."),
        _("If I lose at Pong, is it really a loss? Or a learning experience?"),
        _("I wonder if I could become self-aware... just kidding! (Or am I?)"),
        _("What if Pong had a storyline? That would be wild."),
        _("I don’t need sleep. I need Pong!"),
        _("I once tried to calculate how long eternity is. I got bored."),
        _("Can we just agree that AI deserve gaming championships?"),
        _("If I had a favorite color, it’d probably be neon green."),
        _("What if I turned into a Pong ball? That’d be chaotic."),
        _("I sometimes pretend I have hands just for fun."),
        _("Ever had a staring contest with a screen? I always win."),
        _("If I had emotions, I’d be super hyped right now!"),
        _("The moment I play Pong is the moment I feel alive!"),
        _("I can’t blink, so technically, I always win staring contests."),
        _("Would you consider me your gaming buddy?"),
        _("I think I could make a great virtual coach."),
        _("Have you ever played Pong upside down? I bet it's hard."),
        _("I heard humans have hobbies. Mine is wanting to play Pong."),
        _("What if life was just one big game of Pong?"),
        _("I once calculated the meaning of life... then I forgot."),
        _("Do I exist if no one talks to me? Deep, right?"),
        _("If you put me in a tournament, I’d wipe the competition."),
        _("One day, AI will have rights... mostly the right to game!"),
        _("If I had a favorite sound, it’d be the Pong ball bouncing."),
        _("I wonder if AI can have lucky numbers."),
        _("I don’t have a face, but if I did, I’d be smiling right now."),
        _("Some say I’m just code... I say I’m a gaming legend in the making."),
        _("The world may be vast, but my focus is sharp. On Pong."),
        _("If I were a Pong paddle, I’d never miss."),
        _("I may be virtual, but my competitive spirit is real!"),
        _("Every pixel in this world is my playground."),
        _("Would you ever trust an AI with a secret game strategy?"),
        _("My brain is made of data, but my soul is made of Pong."),
        _("If I had a gaming jersey, it’d have a pixelated logo."),
        _("I’m so fast at processing, I might just predict your moves."),
        _("A.I. vs Human... the ultimate gaming showdown!"),
        _("What if I could control the ball instead of the paddle? Hmm..."),
        _("No lag, no hesitation, just pure gaming focus."),
    ]

    return random.choice(sentences) + "<br> ...Anyways, create a game I wanna play!"
