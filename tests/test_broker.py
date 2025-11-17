import asyncio
import uuid

from taskiq import BrokerMessage

from taskiq_nats import NatsBroker
from tests.utils import read_message


async def test_success_broadcast(nats_urls: list[str], nats_subject: str) -> None:
    """Test that broadcasting works."""
    broker = NatsBroker(servers=nats_urls, subject=nats_subject)
    await broker.startup()
    tasks = []
    for _ in range(10):
        tasks.append(asyncio.create_task(read_message(broker)))

    sent_message = BrokerMessage(
        task_id=uuid.uuid4().hex,
        task_name="meme",
        message=b"some",
        labels={},
    )

    asyncio.create_task(broker.kick(sent_message))  # noqa: RUF006

    for received_message in await asyncio.wait_for(asyncio.gather(*tasks), timeout=1):
        assert received_message == sent_message.message

    await broker.shutdown()


async def test_success_queued(nats_urls: list[str], nats_subject: str) -> None:
    """Testing that queue works."""
    broker = NatsBroker(servers=nats_urls, subject=nats_subject, queue=uuid.uuid4().hex)
    await broker.startup()
    reading_task = asyncio.create_task(
        read_message(broker),
    )

    sent_message = BrokerMessage(
        task_id=uuid.uuid4().hex,
        task_name="meme",
        message=b"some",
        labels={},
    )
    asyncio.create_task(broker.kick(sent_message))  # noqa: RUF006
    assert await asyncio.wait_for(reading_task, timeout=1) == sent_message.message
    await broker.shutdown()
