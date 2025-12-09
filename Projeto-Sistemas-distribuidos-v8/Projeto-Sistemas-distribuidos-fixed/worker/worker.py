import asyncio, os, json, httpx
import aio_pika

RURL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

async def handle(msg: aio_pika.IncomingMessage):
    async with msg.process():
        data = json.loads(msg.body.decode())
        print("Evento recebido:", data)

        event = data.get("type")

        async with httpx.AsyncClient() as client:
            if event == "order.created":
                try:
                    r = await client.post("http://payments-service:5002/process", json=data)
                    print("Process payment ->", r.text)
                except Exception as e:
                    print("Erro payment:", str(e))

async def main():
    connection = await aio_pika.connect_robust(RURL)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange("micro.events", aio_pika.ExchangeType.FANOUT)
        queue = await channel.declare_queue("micro_events_q", durable=True)
        await queue.bind(exchange)
        await queue.consume(handle)
        print("Worker a correr...")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
