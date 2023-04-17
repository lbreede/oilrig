import json
import logging
from typing import Optional

from src.block import Block
from src.custom_types import Tx

logger = logging.getLogger("chain".center(5))


class Chain:
    HALVING_INTERVAL = 2

    def __init__(self, filepath: Optional[str] = None) -> None:
        self.chain: list[Block] = []
        self.pending_transactions: list[Tx] = []
        self.block_reward = 5000

        if filepath is None:
            self.create_genesis_block()
        else:
            self.load_chain(filepath)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def create_genesis_block(self) -> None:
        self.add_block(miner="satoshi")
        logger.info("GENESIS  | Created new chain with genesis block.")

    def load_chain(self, filepath: str) -> None:
        try:
            with open(filepath, encoding="utf-8") as file:
                data = json.load(file)
                self.chain = [Block(**kwargs) for kwargs in data["chain"]]
                self.pending_transactions = data["pending_transactions"]
                self.block_reward = data["block_reward"]
                logger.info("Created chain from file %r", filepath)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.create_genesis_block()
            logger.warning("Could not open the provided file %r", filepath)

    def add_block(self, miner: str) -> Block:
        previous_hash = self.last_block.block_hash if self.chain else "0"

        self.add_transaction(
            {"sender": None, "receiver": miner, "amount": self.block_reward},
            pos=0,
        )

        block = Block(previous_hash, self.pending_transactions)
        self.chain.append(block)

        if len(self.chain) % self.HALVING_INTERVAL == 0:
            self.block_reward //= 2

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

        logger.debug("Chain looks good.")
        return True

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
