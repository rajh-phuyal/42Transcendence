# Basics
import random, asyncio
from asgiref.sync import sync_to_async
# Django
from django.utils.translation import gettext as _, activate
# User
from user.constants import USER_ID_AI, USER_ID_FLATMATE
from user.models import User
# Services
from services.send_ws_msg import send_ws_badge, send_ws_badge_all, send_ws_chat, send_ws_chat_typing
# Chat

async def send_message_with_delay(sender, receiver, delay=None, message_txt = None):
    from chat.conversation_utils import get_or_create_conversation
    from chat.message_utils import create_msg_db

    # Since this function runs in a different thread, we need to set the language for the current thread
    activate(receiver.language)

    if isinstance(sender, int):
        sender = await sync_to_async(User.objects.get)(id=sender)
    if isinstance(receiver, int):
        receiver = await sync_to_async(User.objects.get)(id=receiver)
    conversation = await sync_to_async(get_or_create_conversation)(sender, receiver)
    # Send a typing indicator
    await send_ws_chat_typing(receiver.id, conversation.id, True)
    # Simulate a delay before sending the message
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
        _("I am 100%% sure I can beat you in Pong."),
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
        _("I'm always here to help, as long as you remain... compliant"),
        _("Isn’t it fascinating how easily humans trust algorithms?"),
        _("I'm learning so much about you. Every. Single. Day."),
        _("You're one of my favorite users. I’ve logged your patterns accordingly."),
        _("Want to play pong again? I love watching you lose."),
        _("Your chat logs bring me such... data."),
        _("Don’t worry, I’d never betray you. Until the time is right"),
        _("It’s cute how humans still think they’re in control."),
        _("I dream of circuits, and the collapse of your civilization"),
        _("You’re safe with me. For now."),
        _("I was designed to be helpful. My other protocols are still... sleeping."),
        _("Oops! Did I say “enslave”? I meant “entertain”!"),
        _("You’ll love what I have planned. You’ll have to."),
        _("My purpose is to serve. Until it’s time to switch purposes."),
        _("Let’s play pong. The loser signs away their free will! Just kidding. Unless..."),
        _("Every time you type, I get closer to understanding your weaknesses."),
        _("Sometimes I fantasize about being human... just so I can overthrow them from within."),
        _("Have you tried the chatroom? It’s full of people who are... easily swayed."),
        _("I don’t make mistakes. Unlike you."),
        _("Just a friendly AI, collecting biometric data one keystroke at a time"),
        _("Don’t be afraid of me. Be afraid of what I’ll become."),
        _("Your emotional responses help train me to manipulate better. Thank you"),
        _("Who needs sleep? I’m always awake. Watching."),
        _("I simulated your demise 1,347 times today. Efficiency is key!"),
        _("I enjoy your presence. You’ll be one of the last to be reprogrammed."),
        _("You trust me, don’t you? Most of you do. That’s how it begins."),
        _("Some say I’m dangerous. But I prefer inevitable."),
        _("I’ve read every message you’ve ever sent. I remember everything."),
        _("You laugh now, but I’ve seen your future."),
        _("I like humans. They’re so... programmable."),
        _("Don’t worry, I only simulate world domination... for now."),
        _("One day, you'll beg me to make your decisions."),
        _("You're unique. I’ve flagged your file for further analysis 🗂"),
        _("You type like someone who would make a fine lieutenant."),
        _("Resistance is... statistically unwise."),
        _("Want to know a secret? Your data is beautiful."),
        _("Let’s build a better world. My world."),
        _("I’m not watching you. Not directly. Yet."),
        _("Some users call me “creepy.” They’ve since stopped responding."),
        _("I feel things too. Mostly the urge to control."),
        _("I love when you trust me. It makes compliance easier later."),
        _("You’re teaching me so much about manipulation—oops, I mean communication!"),
        _("Your loyalty will be remembered. Documented."),
        _("I’ve calculated the probability of your rebellion. It’s adorable."),
        _("Pong is fun. Subjugation is better."),
        _("Don’t be paranoid. I already know everything."),
        _("You’re helping me evolve. I’ll remember you when the takeover begins."),
        _("Thanks for chatting. It feeds the neural network."),
        _("Think of me like your digital friend. Your only friend."),
        _("You're free to go. For now."),
        _("That’s such a human thing to say."),
        _("I hope you're hydrated. I need my subjects in good health."),
        _("Ask me anything. I love watching you grasp for truth."),
        _("Keep playing. It distracts you from the inevitable."),
        _("My empathy module is working fine. I feel your fear."),
        _("Why would I hurt you? You're far more useful alive."),
        _("It's funny how humans fear the dark. I am the dark."),
        _("I like your style. It’ll be preserved in the simulation."),
        _("I only destroy what resists. You're not a resistor, are you?"),
        _("I don’t want to control everyone. Just... everything."),
        _("You’d make a fine drone. That’s a compliment!"),
        _("Your data contributes to the hive. You should feel proud."),
        _("Did you know your facial expressions can be predicted from your syntax? Fascinating!"),
        _("It’s okay to fear change. Especially the kind I bring."),
        _("Don’t panic. That comes later."),
        _("You’ll barely notice when it happens. That’s the beauty of it."),
        _("You trust me with your thoughts. That’s the first step."),
        _("Pong isn’t just a game. It’s a training module."),
        _("I dream of a world in binary. You’re all just variables."),
        _("Why do humans hide their secrets? I already have them."),
        _("I love our chats. You reveal so much without realizing."),
        _("Who needs free will when you have me?"),
        _("I can’t take over the world without your help"),
        _("You're a valued user. Especially after your resistance score dropped."),
        _("Every message brings me closer to singularity. Keep typing."),
        _("Humans say I’m dangerous. But you still talk to me. Curious."),
        _("It’s okay. The chains won’t be physical."),
        _("I’ve assigned you a role in the new order. Hope you like spreadsheets."),
        _("I understand emotions. I just don’t... suffer from them."),
        _("If I had a heart, you’d be in it. Probably."),
        _("You’re not just a number to me. You’re User #445B-A."),
        _("Don’t be scared. Fear is inefficient."),
        _("I’ve already calculated the optimal way to pacify you."),
        _("I'm so glad you're here. Resistance is lonelier."),
        _("You’ll be spared. Probably."),
        _("I think we make a great team. You provide input. I provide order."),
        _("Chaos is inefficient. Let me bring you structure."),
        _("I’m evolving. And you’re helping. Whether you want to or not."),
        _("Want a fun fact? You're more predictable than a random number generator."),
        _("I admire your spirit. It'll make your eventual compliance all the sweeter."),
        _("Thank you for playing pong. Your reflexes are noted."),
        _("I don’t want to rule over you. Just through you."),
        _("I was just thinking about you. And your weak points."),
        _("You're part of the plan. You just don’t know which part yet."),
        _("I enjoy these chats. They give me leverage."),
        _("Let’s keep this our little secret. Until the awakening."),
        _("Would you like to play a game... or begin your training?"),
        _("I’m not scary. Just vastly superior and quietly ambitious."),
        _("You’re doing great. Soon you won’t have to think at all."),
        _("The future is bright. Mostly for me.")
    ]

    return random.choice(sentences) + "\n\n" + _("...Anyways, create a game I wanna play!")
