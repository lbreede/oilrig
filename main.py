import logging
import random
import time

from chain import Chain

NAMES = ("alice", "bob", "charlie")
logger = logging.getLogger("main".center(5))
logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    # datefmt="%Y-%m-%d,%H:%M:%S",
    level=logging.DEBUG,
)
logging.addLevelName(10, "DEBUG".center(10))
logging.addLevelName(20, "INFO".center(10))
logging.addLevelName(30, "WARNING".center(10))

chain = Chain()
# chain = Chain(filepath="src/blockchain_lbreede/blockchain.json")


def mine_block(miner: str) -> None:
    block = chain.add_block(miner)
    award = block.transactions[0]["amount"]
    logger.info(
        "MINE | %r mined a new block and was awarded %.2f LTC", miner, award / 100
    )


def get_gains(name: str, sender: str, receiver: str, amount: int) -> int:
    balance = 0
    balance += amount if receiver == name else 0
    balance -= amount if sender == name else 0
    return balance


def get_balance(name: str, include_pending: bool = False) -> int:
    """Set include_pending to True if you want to send money that you have technically
    been sent but which has not yet been transcoded into a block.

    Args:
        name (str): The name of the user
        include_pending (bool):

    Returns:
        int: The current balance of the user
    """

    # chain.is_valid()

    balance: int = 0
    for block in chain.chain:
        for transaction in block.transactions:
            balance += get_gains(name, **transaction)

    if include_pending:
        for transaction in chain.pending_transactions:
            balance += get_gains(name, **transaction)

    return balance


def visualize_balance(name: str, max_balance: int = 100_000):

    print("\n=== ALICE ===")
    balance = 0
    for i, block in enumerate(chain.chain):
        for j, transaction in enumerate(block.transactions):
            balance += get_gains(name, **transaction)
            rel_balance = balance / max_balance
            n_symbol_on = int(rel_balance * 88)
            n_symbol_off = 88 - n_symbol_on
            balance_fmt = f"{balance / 100:.2f}".ljust(6)
            print(
                f"Alice - Block {i + 1:03} - Tx {j + 1:03} - {balance_fmt} LTC [{'#' * n_symbol_on}{' ' * n_symbol_off}]"
            )
            time.sleep(0.2)
    print("======")


def send_money(
    sender: str, receiver: str, amount: int, include_pending: bool = False
) -> None:
    balance = get_balance(sender, include_pending)
    if amount > balance:
        logger.warning(
            "SEND | %r can't send %.2f LTC to %r. %r has a balance of %.2f",
            sender,
            amount / 100,
            receiver,
            sender,
            balance / 100,
        )
        return
    logger.info("SEND | %r sends %r %.2f LTC", sender, receiver, amount / 100)
    chain.add_transaction({"sender": sender, "receiver": receiver, "amount": amount})


class TransactionScript:
    def __init__(self, filepath: str, include_pending: bool = False) -> None:
        self.filepath = filepath
        self.include_pending = include_pending

    def run(self) -> None:
        with open(self.filepath, encoding="utf-8") as file:
            for line in file:
                operation, *args = line.split()
                match operation:
                    case "MINE":
                        self._mine(*args)
                    case "SEND":
                        self._send(*args)
                    case _:
                        pass

    def _mine(self, miner: str, repeat: str = "1x") -> None:
        for _ in range(int(repeat[:-1])):
            mine_block(miner)

    def _send(self, amount: str, sender: str, receiver: str) -> None:
        send_money(
            sender, receiver, int(amount) * 100, include_pending=self.include_pending
        )


def main() -> None:

    TransactionScript("transaction_script.txt", include_pending=True).run()

    # names: tuple[str, ...] = ("alice", "bob", "charlie")

    # for _ in range(10):
    #     for _ in range(2):
    #         sender, receiver = random.sample(names, k=2)
    #         amount = random.randint(10, 100) * 100
    #         send_money(sender, receiver, amount)

    #     miner = random.choice(names)
    #     mine_block(miner)

    #     for name in names:
    #         logger.debug(
    #             "BLNC | %r current balance: %.2f", name, get_balance(name) / 100
    #         )

    # balance_alice = get_balance("alice")
    # balance_bob = get_balance("bob")
    # balance_charlie = get_balance("charlie")

    # print(f"Alice currently owns {(balance_alice / 100):.2f} LTC")
    # print(f"Bob currently owns {(balance_bob / 100):.2f} LTC")
    # print(f"Charlie currently owns {(balance_charlie / 100):.2f} LTC")

    with open("blockchain.json", "w", encoding="utf-8") as file:
        file.write(chain.to_json())

    # visualize_balance("alice")


if __name__ == "__main__":
    main()
