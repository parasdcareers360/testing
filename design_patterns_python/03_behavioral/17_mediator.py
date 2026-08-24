"""
Design Patterns in Python — #17
Mediator (Behavioral Pattern)

Intent
------
Define an object that centralizes how a set of other objects communicate, so those objects
don't refer to each other directly. Instead of every participant holding references to every
other participant it might need to talk to, each participant holds a reference to exactly one
thing — the mediator — and the mediator is the only object that knows about all of them. This
turns a tangled many-to-many web of dependencies into a simple many-to-one hub-and-spokes shape.

Problem / Motivation
---------------------
Picture a chat room feature: each `ChatUser` needs to send messages to every other user
currently in the room. The naive way is to give each user a list of direct references to every
other user, and have `send()` loop over that list and call `receive()` on each one. This works
for three users. But now a user needs to be able to mute another user, or the room needs to log
every message, or a "moderator" user needs to see messages even if they'd normally be muted —
and suddenly that logic has to be duplicated inside `ChatUser` itself, because there's no single
place that sees the whole conversation. Every user object also has to be wired up to every other
user object at creation time (N^2 references for N users), and removing one user means finding
and clearing that reference out of everybody else's list too.

Structure
---------
A Mediator interface declares how Colleagues notify it of events (e.g. `notify(sender, event)`).
A ConcreteMediator implements the actual coordination logic and holds references to all the
Colleagues it manages. Each Colleague holds a reference to *only* the mediator (never to other
Colleagues directly) and calls back into it whenever something noteworthy happens. The mediator
then decides who else needs to know and routes the event accordingly.

When to Use
-----------
- A group of objects communicate in complex, tangled ways, and that communication logic doesn't
  naturally belong to any single one of them (chat rooms, UI widgets reacting to each other's
  state, air-traffic-control-style coordination between independent agents).
- You want to reuse a single object (a dialog box, a chat room) in different contexts, but its
  components reference each other so heavily that pulling one out means dragging the rest along.

When NOT to Use
----------------
- If there are only two or three participants with one fixed, simple relationship, a mediator is
  needless indirection — just call the other object directly.
- The mediator itself can grow into a "god object" that knows too much about everyone — if the
  coordination logic keeps growing, that's a sign that some of it should be split back out into
  smarter Colleagues, not that the mediator needs to keep swallowing more responsibility.

Related / Commonly Confused Patterns
--------------------------------------
- Observer: a Mediator is often implemented *using* Observer-style callbacks internally (as this
  file's Pythonic variant does), but the two solve different problems — Observer is one subject
  broadcasting to many independent listeners, Mediator is many peers coordinating *with each
  other* through one shared coordinator that knows all of them by name.
- Facade: both centralize access to a set of objects, but Facade simplifies an interface for
  callers *outside* the subsystem (one-directional), while Mediator coordinates communication
  *among* the objects themselves (multi-directional, and the objects are aware of the mediator).
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# Every ChatUserNaive holds direct references to every other user in the room. Sending a
# message means looping over that hand-maintained list. Adding room-wide behavior (muting,
# logging) means editing ChatUserNaive itself, and every user has to be wired to every other
# user at creation time -- O(N^2) references that all have to be kept in sync as people join
# or leave.
class ChatUserNaive:
    def __init__(self, name: str):
        self.name = name
        self.peers: list["ChatUserNaive"] = []  # direct references to every other user
        self.inbox: list[str] = []

    def send(self, message: str) -> None:
        print(f"  [naive] {self.name} sends: {message}")
        for peer in self.peers:
            peer.receive(self.name, message)

    def receive(self, sender: str, message: str) -> None:
        self.inbox.append(f"{sender}: {message}")


# ============================================================
# Implementation 1: Classic (OOP / GoF-style, ChatRoomMediator + Colleague base class)
# ============================================================
# Idea: each ChatUser knows about exactly one thing -- the mediator -- and never holds a
# reference to another user directly. The mediator is the only object that knows the full
# roster, so mute rules, logging, and moderator visibility all live in ONE place instead of
# being duplicated inside every Colleague.
from abc import ABC, abstractmethod


class ChatMediator(ABC):
    @abstractmethod
    def register(self, user: "ChatUser") -> None: ...

    @abstractmethod
    def dispatch(self, sender: "ChatUser", message: str) -> None: ...


class ChatUser(ABC):
    """Colleague base class: holds a reference to the mediator, never to other Colleagues."""

    def __init__(self, name: str, mediator: ChatMediator):
        self.name = name
        self._mediator = mediator
        self.inbox: list[str] = []
        mediator.register(self)

    def send(self, message: str) -> None:
        print(f"  [classic] {self.name} sends: {message}")
        self._mediator.dispatch(self, message)

    def receive(self, sender_name: str, message: str) -> None:
        self.inbox.append(f"{sender_name}: {message}")


class ChatRoomMediator(ChatMediator):
    """ConcreteMediator: knows every user, and owns ALL the cross-cutting room logic."""

    def __init__(self):
        self._users: list[ChatUser] = []
        self._muted_pairs: set[tuple[str, str]] = set()  # (muter, muted) -> muter won't see them
        self.log: list[str] = []

    def register(self, user: ChatUser) -> None:
        self._users.append(user)

    def mute(self, muter_name: str, muted_name: str) -> None:
        self._muted_pairs.add((muter_name, muted_name))

    def dispatch(self, sender: ChatUser, message: str) -> None:
        self.log.append(f"{sender.name}: {message}")  # room-wide logging lives here, once
        for user in self._users:
            if user is sender:
                continue
            if (user.name, sender.name) in self._muted_pairs:
                continue  # mute logic lives here too, not duplicated per-user
            user.receive(sender.name, message)


# ============================================================
# Implementation 2: Pythonic idiom (a plain event-bus / dict-of-callbacks hub)
# ============================================================
# Idea: the mediator's job -- "route an event to interested parties" -- doesn't require a full
# ABC hierarchy at all. A lightweight hub built from a dict of subscriber callbacks captures the
# same "colleagues only know the hub, not each other" property with far less ceremony, and reads
# like idiomatic Python pub/sub rather than translated Java. This is a genuinely distinct shape
# from Implementation 1: no Colleague base class, no `register`/`dispatch` interface -- just
# subscribe-a-function / publish-an-event.
class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list] = {}

    def subscribe(self, topic: str, callback) -> None:
        self._subscribers.setdefault(topic, []).append(callback)

    def publish(self, topic: str, *args, **kwargs) -> None:
        for callback in self._subscribers.get(topic, []):
            callback(*args, **kwargs)


def make_bus_user(bus: EventBus, name: str, inbox: list) -> callable:
    """Returns a `send` function closing over `name`/`bus` -- the "colleague" is just a function
    plus a subscription, not a class hierarchy."""

    def on_message(sender_name: str, message: str) -> None:
        if sender_name != name:
            inbox.append(f"{sender_name}: {message}")

    bus.subscribe("message", on_message)

    def send(message: str) -> None:
        print(f"  [pythonic] {name} sends: {message}")
        bus.publish("message", name, message)

    return send


# ============================================================
# Key Takeaways
# ============================================================
# - The core trade: Colleagues give up direct references to each other and gain one reference to
#   a shared coordinator -- that turns N^2 potential relationships into N relationships, and
#   moves cross-cutting rules (muting, logging) into one place instead of scattering them.
# - Common misuse/misconception: letting the mediator absorb every piece of domain logic until
#   it becomes an unreadable god object -- Mediator centralizes *communication*, not necessarily
#   every business rule; Colleagues should still own logic that's really about themselves.
# - Related pattern to compare: Observer -- Mediator is frequently built on top of an
#   Observer-style publish/subscribe mechanism (see the EventBus above), but Mediator's defining
#   trait is that participants coordinate *with each other* through a hub that knows them all,
#   not just a broadcaster with anonymous listeners.


if __name__ == "__main__":
    print("--- Anti-pattern: users wired directly to every other user (N^2 references) ---")
    alice_n = ChatUserNaive("Alice")
    bob_n = ChatUserNaive("Bob")
    carol_n = ChatUserNaive("Carol")
    alice_n.peers = [bob_n, carol_n]
    bob_n.peers = [alice_n, carol_n]
    carol_n.peers = [alice_n, bob_n]
    alice_n.send("Standup at 10am")
    assert "Alice: Standup at 10am" in bob_n.inbox
    assert "Alice: Standup at 10am" in carol_n.inbox
    print(f"  Bob's inbox: {bob_n.inbox}")

    print("\n--- Classic: ChatRoomMediator, users only know the mediator ---")
    room = ChatRoomMediator()
    alice = ChatUser("Alice", room)
    bob = ChatUser("Bob", room)
    carol = ChatUser("Carol", room)

    alice.send("Standup at 10am")
    assert "Alice: Standup at 10am" in bob.inbox
    assert "Alice: Standup at 10am" in carol.inbox
    print(f"  Bob's inbox: {bob.inbox}")

    room.mute("Carol", "Bob")  # Carol no longer wants to see Bob's messages
    bob.send("Anyone free for lunch?")
    assert "Bob: Anyone free for lunch?" in alice.inbox
    assert "Bob: Anyone free for lunch?" not in carol.inbox  # muted -- rule lives in the mediator
    print(f"  Carol's inbox after mute (should NOT contain Bob's lunch message): {carol.inbox}")
    print(f"  room log (centralized, once): {room.log}")

    print("\n--- Pythonic: EventBus (dict-of-callbacks hub, no Colleague class hierarchy) ---")
    bus = EventBus()
    alice_inbox: list[str] = []
    bob_inbox: list[str] = []
    alice_send = make_bus_user(bus, "Alice", alice_inbox)
    bob_send = make_bus_user(bus, "Bob", bob_inbox)
    alice_send("Deploy is live")
    assert "Alice: Deploy is live" in bob_inbox
    assert "Alice: Deploy is live" not in alice_inbox  # sender doesn't receive its own message
    print(f"  Bob's inbox via event bus: {bob_inbox}")

    print("\nAll three variants deliver messages without any user holding a reference to")
    print("another user directly -- the mediator/hub is the only thing that knows everyone.")
