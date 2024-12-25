from pyrogram import Client
from config import USERBOT_SESSION
import asyncio 
from threading import Timer
from urllib.parse import urlparse
import random
from pyrogram.raw.functions.messages import GetMessagesViews

class OrderUserbotManager:
    def __init__(self, idle_timeout=300):
        self.clients = {}  # Active userbot instances
        self.task_queues = {}  # Task queues for each userbot
        self.idle_timers = {}  # Timers to stop inactive clients
        self.idle_timeout = idle_timeout

    async def start_client(self, api_id, api_hash, phone_number):
        """Start or restart a userbot client."""
        if phone_number in self.clients:
            # Reset idle timer
            self.reset_idle_timer(phone_number)
            return self.clients[phone_number]

        client = Client(USERBOT_SESSION+f"/{api_id}", api_id=api_id, api_hash=api_hash, phone_number=phone_number)
        await client.start()
        self.clients[phone_number] = client
        print(f"Userbot {phone_number} started.")

        # Create task queue for the client
        if phone_number not in self.task_queues:
            self.task_queues[phone_number] = asyncio.Queue()

        # Process the task queue
        asyncio.create_task(self.process_task_queue(phone_number))

        # Set idle timer
        self.reset_idle_timer(phone_number)

        return client

    async def stop_client(self, phone_number):
        """Stop a userbot client and clean up resources."""
        if phone_number in self.clients:
            await self.clients[phone_number].stop()
            del self.clients[phone_number]
            print(f"Userbot {phone_number} stopped.")

        # Clear task queue and idle timer
        if phone_number in self.task_queues:
            self.task_queues[phone_number].put_nowait(None)  # Sentinel to stop queue processing
            del self.task_queues[phone_number]
        if phone_number in self.idle_timers:
            self.idle_timers[phone_number].cancel()
            del self.idle_timers[phone_number]

    def reset_idle_timer(self, phone_number):
        """Reset or create an idle timer for a client."""
        if phone_number in self.idle_timers:
            self.idle_timers[phone_number].cancel()

        timer = Timer(self.idle_timeout, lambda: asyncio.run(self.stop_client(phone_number)))
        self.idle_timers[phone_number] = timer
        timer.start()

    async def process_task_queue(self, phone_number):
        """Process tasks for a specific userbot."""
        while True:
            task = await self.task_queues[phone_number].get()
            if task is None:break
            try:
                client = self.clients[phone_number]
                if task["type"] == "join_channel":
                    for channel in task["channels"]:
                        await client.join_chat(channel)
                        print(f"Userbot {phone_number} joined {channel}")
                elif task["type"] == "leave_channel":
                    for channel in task["channels"]:
                        await client.leave_chat(channel)
                        print(f"Userbot {phone_number} leave {channel}")
                elif task["type"] == "reactPost":
                    postLink = task["postLink"]
                    parsed_url = urlparse(postLink)
                    path_segments = parsed_url.path.strip("/").split("/")
                    chatID = str(path_segments[0])
                    messageID = int(path_segments[1])
                    emoji = task['emoji'] 
                    await client.send_reaction(chatID,messageID,emoji)
                    print(f"Userbot {phone_number} reacted to {task['postLink']} with {task['emoji']}")
                elif task['type'] == 'sendMessage':
                    textToDeliver = random.choice(task['text'])
                    chatIDToDeliver = task['chatID']
                    await client.send_message(chatIDToDeliver,textToDeliver)
                elif task["type"] == "viewPosts":
                    postLink = task["postLink"]
                    parsed_url = urlparse(postLink)
                    path_segments = parsed_url.path.strip("/").split("/")
                    chatID = str(path_segments[0])
                    channelPeer = await client.resolve_peer(chatID)
                    messageID = int(path_segments[1]) 
                    await client.invoke(GetMessagesViews(
                        peer=channelPeer,
                        id=[messageID],
                        increment=True
                    ))
            except Exception as e:
                print(f"Error processing task for {phone_number}: {e}")
                raise e

            # Reset idle timer after completing a task
            self.reset_idle_timer(phone_number)

    async def add_task(self, phone_number, task):
        """Add a task to a userbot's queue."""
        if phone_number not in self.clients:
            print(f"Userbot {phone_number} not active. Starting...")
            await self.start_client(task["api_id"], task["api_hash"], phone_number)

        # Add task to the queue
        await self.task_queues[phone_number].put(task)

    async def bulk_order(self, userbots, task):
        """
        Send a bulk order to all userbots in the provided list.

        :param userbots: List of userbot details. Each detail is a dict with keys:
                         api_id, api_hash, phone_number, password.
        :param task: The task to execute (e.g., join_channel, leave_channel, etc.)
                     Example: {"type": "join_channel", "channel": "some_channel"}
        """
        taskLimit = 0
        for userbot in userbots:
            taskLimit += 1
            
            rest_time = task.get("restTime", 0)
            # Delay before executing the task
            if rest_time > 0:
                print(f"Resting for {rest_time} seconds before processing task for {userbot["phone_number"]}")
                await asyncio.sleep(rest_time)
            await self.add_task(
                phone_number=userbot["phone_number"],
                task={
                    **task,
                    "api_id": userbot["appID"],
                    "api_hash": userbot["appHash"],
                },
            )
            # Break after order limit complete
            if taskLimit >= task["taskPerformCount"]: break
        print(f"Bulk order {task['type']} added for {len(userbots)} userbots.")


UserbotManager = OrderUserbotManager()