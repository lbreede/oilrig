import logging

from src.chain import Chain

logger = logging.getLogger(__name__)

logging.basicConfig(
    # format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.DEBUG,
)

NAMES = ("alice", "bob", "charlie")
chain = Chain()
# chain = Chain(filepath="blockchain.json")


def mine_block(miner: str) -> None:
    """Mine a new block. The miner will be awarded with a certain amount of OIL.

    Args:
        miner (str): The name of the miner

    """
    # block =
    chain.add_block(miner)
    # award = block.transactions[0]["amount"]
    # logger.info("%r mined a new block and was awarded %.2f OIL", miner, award / 100)


def get_gains(name: str, sender: str, receiver: str, amount: int) -> int:
    """Get the gains of a user

    Args:
        name: The name of the user
        sender: The name of the sender
        receiver: The name of the receiver
        amount: The amount of money

    Returns:
        The gains of the user

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


def send_money(
    sender: str, receiver: str, amount: int, include_pending: bool = False
) -> None:
    """Send money from one user to another.

    Args:
        sender: The name of the sender
        receiver: The name of the receiver
        amount: The amount of money
        include_pending: Whether to include pending transactions.

    """
    balance = get_balance(sender, include_pending)
    if amount > balance:
        # logger.warning(
        #     "%r can't send %.2f OIL to %r. %r has a balance of %.2f",
        #     sender,
        #     amount / 100,
        #     receiver,
        #     sender,
        #     balance / 100,
        # )
        return
    # logger.info("%r sends %r %.2f OIL", sender, receiver, amount / 100)
    chain.add_transaction({"sender": sender, "receiver": receiver, "amount": amount})


class TransactionScript:
    """A class that will read a script file and execute the operations."""

    def __init__(self, filepath: str, include_pending: bool = False) -> None:
        """Initialize the TransactionScript.

        Args:
            filepath: The path to the script file
            include_pending: Whether to include pending transactions.

        """
        self.filepath = filepath
        self.include_pending = include_pending

    def run(self) -> None:
        """Run the script.

        This function will read the script file and execute the operations.

        """
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
        """Mine a new block. The miner will be awarded with a certain amount of OIL.

        Args:
            miner: The name of the miner
            repeat: The number of times to repeat the operation in the format '\\d+x'

        """
        for _ in range(int(repeat[:-1])):
            mine_block(miner)

    def _send(self, amount: str, sender: str, receiver: str) -> None:
        """Send money from one user to another.

        Args:
            amount: The amount of money
            sender: The name of the sender
            receiver: The name of the receiver

        """
        send_money(
            sender, receiver, int(amount) * 100, include_pending=self.include_pending
        )


def main() -> None:
    TransactionScript("transaction_script.txt", include_pending=True).run()

    with open("blockchain.json", "w", encoding="utf-8") as fp:
        fp.write(chain.to_json())


if __name__ == "__main__":
    main()
