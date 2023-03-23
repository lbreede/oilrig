import json
import logging
from datetime import datetime
from hashlib import sha256
from typing import Optional

from custom_types import Tx

logger = logging.getLogger("block".center(5))


class Block:
    def __init__(
        self,
        previous_hash: str,
        transactions: list[Tx],
        timestamp: Optional[str] = None,
        nonce: int = 0,
        block_hash: Optional[str] = None,
    ):
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp: str = timestamp or datetime.now().isoformat()
        self.nonce: int = nonce
        self.block_hash = block_hash or self._mine()

    def _mine(self, difficulty: int = 2) -> str:
        while not self.current_hash().startswith("0" * difficulty):
            self.nonce += 1
        return self.current_hash()

    def current_hash(self) -> str:

        header: str = (
            self.previous_hash
            + json.dumps(self.transactions)
            + self.timestamp
            + str(self.nonce)
        )
        return sha256(header.encode()).hexdigest()

    def is_valid(self) -> bool:
        return self.block_hash == self.current_hash()

    @staticmethod
    def shortened_hash(hash_: str, left: int = 4, right: int = 4):
        if len(hash_) <= left + 3 + right:
            return hash_
        return f"{hash_[:left]}...{hash_[-right:]}"

    def __str__(self) -> str:
        return (
            f"Previous Hash: 0x{self.shortened_hash(self.previous_hash)}\n"
            f"Transactions:  {len(self.transactions)}\n"
            f"Timestamp:     {self.timestamp}\n"
            f"Nonce:         {self.nonce}\n"
            f"Block Hash:    0x{self.shortened_hash(self.block_hash)}"
        )
