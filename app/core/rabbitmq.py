import asyncio
from aio_pika import connect_robust, IncomingMessage, ExchangeType

RABBIT_URL = "amqp://guest:guest@rabbitmq:5672/"

connection = None
channel = None
consumer_tasks = []  # store multiple consumer tasks if needed

async def on_message(message: IncomingMessage):
    async with message.process():
        print(f"Received message: {message.body.decode()}")


async def get_connection(loop=None):
    global connection, channel
    if not connection:
        loop = loop or asyncio.get_event_loop()
        connection = await connect_robust(RABBIT_URL, loop=loop)
        channel = await connection.channel()
    return connection, channel


async def start_consumer():
    global consumer_tasks
    _, channel = await get_connection()
    exchange = await channel.declare_exchange("my_exchange", ExchangeType.DIRECT)
    queue = await channel.declare_queue("my_queue")
    await queue.bind(exchange, routing_key="test")
    task = asyncio.create_task(queue.consume(on_message))
    consumer_tasks.append(task)
    print("✅ RabbitMQ consumer started")


async def stop_rabbit():
    global connection, consumer_tasks
    # cancel all consumers
    for task in consumer_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    consumer_tasks.clear()

    # close connection
    if connection:
        await connection.close()
        connection = None
    print("🛑 RabbitMQ connection closed")