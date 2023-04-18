import json
import logging
import time
from typing import Optional

from src.block import Block
from src.custom_types import Tx

logger = logging.getLogger(__name__)


class Chain:
    REWARD_HALVING_INTERVAL = 2
    DIFFICULTY_ADJUSTMENT_INTERVAL = 0.1

    def __init__(self, filepath: Optional[str] = None) -> None:
        self.chain: list[Block] = []
        self.pending_transactions: list[Tx] = []
        self.block_reward = 5000
        self.difficulty = 0

        if filepath is None:
            self._create_genesis_block()
        else:
            self._load_chain(filepath)

    def _create_genesis_block(self) -> None:
        """Creates the genesis block and adds it to the chain."""
        logger.info("Creating genesis block...")
        self.add_block(miner="satoshi")
        logger.info("Created genesis block")

    def _load_chain(self, filepath: str) -> None:
        """Loads the chain from a file.

        Args:
            filepath: The path to the file.

        """
        logger.info("Loading chain from file %r...", filepath)
        try:
            with open(filepath, encoding="utf-8") as file:
                data = json.load(file)
                self.chain = [Block(**kwargs) for kwargs in data["chain"]]
                self.pending_transactions = data["pending_transactions"]
                self.block_reward = data["block_reward"]
                logger.info("Created chain from file %r", filepath)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self._create_genesis_block()
            logger.warning("Could not open the provided file %r", filepath)

    @property
    def last_block(self) -> Block:
        """Returns the last block of the chain."""
        return self.chain[-1]

    def add_block(self, miner: str) -> Block:
        """Adds a block to the chain.

        NOTE: Timing takes place in chain class to modify difficulty dynamically

        Args:
            miner: The miner of the block.

        Returns:
            The mined block.

        """
        logger.info("Adding block #%03d to chain...", len(self))
        previous_hash = self.last_block.block_hash if self.chain else "0"

        self.add_block_reward_transaction(miner)

        start = time.monotonic()
        block = Block(
            previous_hash, self.pending_transactions, difficulty=self.difficulty
        )
        end = time.monotonic()

        self.chain.append(block)
        logger.debug("Added block #%03d to chain", len(self) - 1)

        duration = end - start
        self.adjust_difficulty(duration)
        logger.info("Mined block #%03d in %f seconds.", len(self) - 1, duration)

        if len(self) % self.REWARD_HALVING_INTERVAL == 0:
            self.block_reward //= 2
            logger.info("Halved block reward to %d", self.block_reward)

        self.pending_transactions = []
        logger.debug("Cleared pending transactions")

        return block

    def adjust_difficulty(self, last_block_duration: float) -> int:
        """Adjusts the difficulty of the chain.

        Args:
            last_block_duration: The duration of the last block.

        Returns:
            The new difficulty.

        """

        if self.difficulty > 10:
            logger.warning(
                "Difficulty is very high. "
                "Consider increasing the difficulty adjustment interval"
            )

        if last_block_duration < self.DIFFICULTY_ADJUSTMENT_INTERVAL:
            self.difficulty += 1
            logger.debug("Increased difficulty to %d", self.difficulty)
        elif last_block_duration > self.DIFFICULTY_ADJUSTMENT_INTERVAL:
            if self.difficulty > 0:
                self.difficulty -= 1
                logger.debug("Decreased difficulty to %d", self.difficulty)
            else:
                logger.warning("Difficulty is already 0. Cannot decrease further.")
                return self.difficulty
        return self.difficulty

    def add_block_reward_transaction(self, miner: str) -> None:
        """Adds a block reward transaction to the pending transactions.

        Args:
            miner: The miner of the block.

        """
        self.add_transaction(
            {"sender": None, "receiver": miner, "amount": self.block_reward},
            pos=0,
        )

    def add_transaction(self, transaction: Tx, pos: Optional[int] = None) -> None:
        """Adds a transaction to the pending transactions.

        Args:
            transaction: The transaction to add.
            pos: The position to add the transaction to. If None, the transaction
                will be added to the end of the list.

        """
        pos = len(self.pending_transactions) if pos is None else pos
        self.pending_transactions.insert(pos, transaction)

    def is_valid(self) -> bool:
        """Checks if the chain is valid.

        Returns:
            True if the chain is valid, False otherwise.

        """
        for i, block in enumerate(self.chain):
            if not block.is_valid():
                logger.critical("Block %d is invalid", i)
                return False

            if i == 0:
                continue

            if self.chain[i - 1].block_hash != self.chain[i].previous_hash:
                logger.critical("The chain is invalid between block %d / %d!", i - 1, i)
                return False

        logger.info("Chain looks good.")
        return True

    def to_json(self) -> str:
        """Returns the chain as a JSON string.

        Returns:
            The chain as a JSON string.

        """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def __len__(self) -> int:
        """Returns the length of the chain.

        Returns:
            The length of the chain.

        """
        return len(self.chain)
