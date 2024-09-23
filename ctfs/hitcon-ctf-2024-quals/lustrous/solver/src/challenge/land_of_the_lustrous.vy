#pragma version ==0.3.10

enum GemStatus:
    ACTIVE
    INACTIVE
    DESTROYED

struct Gem:
    health: int256
    max_health: int256
    attack: int256
    hardness: int256
    status: GemStatus

struct Lunarian:
    health: int256
    attack: int256
    rounds: uint256

interface Master:
    def get_actions() -> DynArray[uint8, MAX_ROUNDS]: view
    def decide_continue_battle(round: uint256, lunarian_health: int256) -> bool: nonpayable

stage: public(uint8)
master_addr: public(address)
lunarian_addr: public(address)
sequences: public(HashMap[address, uint32])
gems: public(HashMap[bytes32, Gem])
assigned_gems: public(HashMap[address, uint32])
continued: public(HashMap[address, bool])

ACTIVE_HEALTH_THRESHOLD: constant(int256) = 64
STAGES: constant(uint8) = 3
MAX_ROUNDS: constant(uint256) = 300
LUNARIANS: constant(Lunarian[STAGES]) = [
    Lunarian({ health: 1_000, attack: 10_000, rounds: 100 }),
    Lunarian({ health: 10_000, attack: 100_000, rounds: 200 }),
    Lunarian({ health: 1 << 64, attack: 1 << 128, rounds: 300 }),
]

@external
@payable
def __init__():
    assert msg.value == as_wei_value(1_000_000, "ether")
    self.lunarian_addr = msg.sender

@external
@view
def is_solved() -> bool:
    return self.balance == 0

@external
def register_master():
    assert self.master_addr == empty(address), "master already registered"
    self.master_addr = msg.sender

@external
def transfer_master(new_master_addr: address):
    assert self.master_addr != empty(address), "master not registered"
    assert self.master_addr == msg.sender, "only master can transfer master"
    self.master_addr = new_master_addr

@external
@payable
def create_gem() -> Gem:
    assert self.master_addr == msg.sender, "only master can create gem"
    assert msg.value == as_wei_value(1, "ether"), "invalid value"

    random: int256 = abs(convert(keccak256(convert(block.number, bytes32)), int256))
    gem: Gem = Gem({
        health: max(random % 256, ACTIVE_HEALTH_THRESHOLD),
        max_health: random % 256,
        attack: (random / 256) % 256,
        hardness: (random / (256 * 256)) % 256,
        status: GemStatus.ACTIVE,
    })
    self.gems[self.get_gem_id(msg.sender, self.sequences[msg.sender])] = gem
    self.sequences[msg.sender] += 1
    return gem

@external
def merge_gems() -> Gem:
    assert self.master_addr == msg.sender, "only master can merge gems"
    assert self.sequences[msg.sender] >= 2, "not enough gems to merge"

    gem1: Gem = self.gems[self.get_gem_id(msg.sender, self.sequences[msg.sender] - 2)]
    gem2: Gem = self.gems[self.get_gem_id(msg.sender, self.sequences[msg.sender] - 1)]

    assert (gem1.status == GemStatus.ACTIVE and gem2.status == GemStatus.INACTIVE) \
        or (gem1.status == GemStatus.INACTIVE and gem2.status == GemStatus.ACTIVE) \
        or (gem1.status == GemStatus.INACTIVE and gem2.status == GemStatus.INACTIVE), "invalid gem status"

    gem: Gem = Gem({
        health: gem1.health + gem2.health,
        max_health: gem1.max_health + gem2.max_health,
        attack: gem1.attack + gem2.attack,
        hardness: (gem1.hardness + gem2.hardness) / 2,
        status: self.calc_status(gem1.health + gem2.health),
    })
    self.gems[self.get_gem_id(msg.sender, self.sequences[msg.sender] - 2)] = gem
    self.sequences[msg.sender] -= 1
    return gem

@external
def pray_gem():
    assert self.master_addr == msg.sender, "only master can pray gem"
    assert self.sequences[msg.sender] >= 1, "not enough gems to pray"
    self.sequences[msg.sender] -= 1

@external
def assign_gem(sequence: uint32):
    assert self.master_addr == msg.sender, "only master can assign gem"
    self.assigned_gems[msg.sender] = sequence

@external
def battle(lunarian_actions: DynArray[uint8, MAX_ROUNDS]) -> (bool, int256, int256):
    assert self.lunarian_addr == msg.sender, "only lunarian can start battle"
    assert self.master_addr != empty(address), "master not registered"
    assert self.stage < STAGES, "invalid stage"

    lunarian: Lunarian = LUNARIANS[self.stage]
    master: Master = Master(self.master_addr)
    gem_actions: DynArray[uint8, MAX_ROUNDS] = master.get_actions()
    gem_id: bytes32 = self.get_gem_id(self.master_addr, self.assigned_gems[self.master_addr])

    assert self.assigned_gems[self.master_addr] < self.sequences[self.master_addr], "invalid assigned gem"
    assert len(lunarian_actions) == lunarian.rounds and len(gem_actions) == lunarian.rounds, "invalid actions"
    assert self.gems[gem_id].status == GemStatus.ACTIVE, "gem is not active"

    for r in range(lunarian.rounds, bound=MAX_ROUNDS):
        # rock paper scissors
        lunarian_action: uint8 = lunarian_actions[r]
        gem_action: uint8 = gem_actions[r]
        assert lunarian_action <= 2 and gem_action <= 2, "invalid action"

        if lunarian_action == gem_action:
            continue

        master_win: bool = (lunarian_action == 0 and gem_action == 1) \
            or (lunarian_action == 1 and gem_action == 2) \
            or (lunarian_action == 2 and gem_action == 0)

        if master_win:
            lunarian.health -= self.gems[gem_id].attack
        else:
            self.gems[gem_id].health -= lunarian.attack / self.gems[gem_id].hardness

        if self.calc_status(self.gems[gem_id].health) != GemStatus.ACTIVE:
            master.decide_continue_battle(r, lunarian.health)
            if self.continued[self.master_addr]:
                self.continued[self.master_addr] = False
                self.gems[gem_id].health = self.gems[gem_id].max_health 

        self.gems[gem_id].status = self.calc_status(self.gems[gem_id].health)
        if self.gems[gem_id].status != GemStatus.ACTIVE or lunarian.health <= 0:
            break

    if self.gems[gem_id].status == GemStatus.ACTIVE \
        and (lunarian.health <= 0 or lunarian.health < self.gems[gem_id].health):
        if self.stage == 0:
            send(self.master_addr, as_wei_value(1, "ether"))
            self.stage += 1
        elif self.stage == 1:
            send(self.master_addr, as_wei_value(2, "ether"))
            self.stage += 1
        elif self.stage == 2:
            send(self.master_addr, self.balance)
            # congratz :)
        return True, lunarian.health, self.gems[gem_id].health
    else:
        self.stage = 0
        return False, lunarian.health, self.gems[gem_id].health

@external
@payable
def continue_battle():
    assert self.master_addr == msg.sender, "only master can continue battle"
    assert msg.value == as_wei_value(1, "ether"), "invalid value"
    self.continued[msg.sender] = True

@internal
@pure
def get_gem_id(master_addr: address, sequence: uint32) -> bytes32:
    master_addr_bytes: bytes20 = convert(master_addr, bytes20)
    sequence_bytes: bytes4 = convert(sequence, bytes4)
    gem_id: bytes32 = keccak256(concat(master_addr_bytes, sequence_bytes))
    return gem_id

@internal
@pure
def calc_status(health: int256) -> GemStatus:
    if ACTIVE_HEALTH_THRESHOLD <= health:
        return GemStatus.ACTIVE
    elif 0 <= health:
        return GemStatus.INACTIVE
    else:
        return GemStatus.DESTROYED
