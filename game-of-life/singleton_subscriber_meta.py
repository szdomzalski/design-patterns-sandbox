from event_handling import EventSubscriber
from singleton_meta import SingletonMetaLazy


class SingletonSubscriberMeta(SingletonMetaLazy, type(EventSubscriber)):
    pass