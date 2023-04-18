import json
import logging
import time
from typing import Optional

import yaml

from src.block import Block
from src.custom_types import Tx

logger = logging.getLogger(__name__)


class Chain:
    HALVING_INTERVAL = 2

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

        self.add_transaction(
            {"sender": None, "receiver": miner, "amount": self.block_reward},
            pos=0,
        )

        start = time.monotonic()
        block = Block(
            previous_hash, self.pending_transactions, difficulty=self.difficulty
        )
        end = time.monotonic()
        duration = end - start

        if duration < 0.1:
            self.difficulty += 1
            logger.debug("Increased difficulty to %d", self.difficulty)
        elif duration > 0.1:
            self.difficulty -= 1
            logger.debug("Decreased difficulty to %d", self.difficulty)

        logger.info("Mined block #%03d in %f seconds.", len(self), duration)

        self.chain.append(block)
        logger.debug("Added block #%03d to chain", len(self))

        if len(self) % self.HALVING_INTERVAL == 0:
            self.block_reward //= 2
            logger.info("Halved block reward to %d", self.block_reward)

        self.pending_transactions = []
        return block

    def add_transaction(self, transaction: Tx, pos: Optional[int] = None) -> None:
        pos = len(self.pending_transactions) if pos is None else pos
        self.pending_transactions.insert(pos, transaction)

    def is_valid(self) -> bool:
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
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def to_yaml(self) -> str:
        return yaml.dump(self, default_flow_style=False)

    def __len__(self) -> int:
        return len(self.chain)
