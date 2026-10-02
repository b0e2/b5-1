from .hash_map import HashMap
from .linked_list import LinkedList


class PubSub:
    """Channel subscriptions with a FIFO message buffer per subscriber."""

    def __init__(self):
        self._channels = HashMap()
        self._mailboxes = HashMap()

    def subscribe(self, channel, subscriber):
        """Register once and return the channel's subscriber count."""
        subscribers = self._channels.get(channel)
        if subscribers is None:
            subscribers = LinkedList()
            self._channels.put(channel, subscribers)
        for name in subscribers:
            if name == subscriber:
                return subscribers.size()
        subscribers.insert_back(subscriber)
        if not self._mailboxes.contains(subscriber):
            self._mailboxes.put(subscriber, LinkedList())
        return subscribers.size()

    def publish(self, channel, message):
        """Queue a message for each current subscriber and return the count."""
        subscribers = self._channels.get(channel)
        if subscribers is None:
            return 0
        for name in subscribers:
            self._mailboxes.get(name).insert_back((channel, message))
        return subscribers.size()

    def poll(self, subscriber):
        """Remove the oldest message for a subscriber, if any."""
        mailbox = self._mailboxes.get(subscriber)
        return None if mailbox is None else mailbox.remove_front()
