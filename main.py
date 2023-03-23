import logging
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

# chain = Chain()
chain = Chain(filepath="blockchain.json")


def mine_block(miner: str) -> None:
    """Mine a new block. The miner will be awarded with a certain amount of OIL.

    Args:
        miner (str): The name of the miner
    """
    block = chain.add_block(miner)
    award = block.transactions[0]["amount"]
    logger.info(
        "MINE | %r mined a new block and was awarded %.2f OIL", miner, award / 100
    )


def get_gains(name: str, sender: str, receiver: str, amount: int) -> int:
    """Get the gains of a user

    Args:
        name (str): The name of the user
        sender (str): The name of the sender
        receiver (str): The name of the receiver
        amount (int): The amount of money

    Returns:
        int: The gains of the user
    """
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
                f"Alice - Block {i + 1:03} - Tx {j + 1:03} - {balance_fmt} OIL [{'#' * n_symbol_on}{' ' * n_symbol_off}]"
            )
            time.sleep(0.2)
    print("======")


def send_money(
    sender: str, receiver: str, amount: int, include_pending: bool = False
) -> None:
    balance = get_balance(sender, include_pending)
    if amount > balance:
        logger.warning(
            "SEND | %r can't send %.2f OIL to %r. %r has a balance of %.2f",
            sender,
            amount / 100,
            receiver,
            sender,
            balance / 100,
        )
        return
    logger.info("SEND | %r sends %r %.2f OIL", sender, receiver, amount / 100)
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

    # TransactionScript("transaction_script.txt", include_pending=True).run()

    with open("blockchain.json", "w", encoding="utf-8") as file:
        file.write(chain.to_json())


if __name__ == "__main__":
    main()
