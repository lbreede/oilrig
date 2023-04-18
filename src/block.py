import json
import logging
from datetime import datetime
from hashlib import sha256
from typing import Optional

from src.custom_types import Tx

logger = logging.getLogger(__name__)


class Block:
    def __init__(
        self,
        previous_hash: str,
        transactions: list[Tx],
        timestamp: Optional[str] = None,
        nonce: int = -1,
        difficulty: int = 4,
        block_hash: Optional[str] = None,
    ):
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp: str = timestamp or datetime.now().isoformat()
        self.nonce: int = nonce
        self.difficulty = difficulty
        self.block_hash = block_hash or self._mine()

    def _mine(self) -> str:
        """Mines the block.

        NOTE: The block is mined in the block class since the nonce can be accessed
        without having to pass it as an argument and without having to return it.

        Returns:
            The block hash.

        """
        logger.info("Mining block with difficulty %d...", self.difficulty)
        while not self.current_hash().startswith("0" * self.difficulty):
            self.nonce += 1
        return self.current_hash()

    def current_hash(self) -> str:
        """Returns the current hash of the block.

        Returns:
            The current hash of the block.

        """
        header = (
            self.previous_hash
            + json.dumps(self.transactions)
            + self.timestamp
            + str(self.nonce)
        )
        return sha256(header.encode()).hexdigest()

    def is_valid(self) -> bool:
        """Checks if the block is valid.

        A block is valid if the block hash starts with the specified number of
        zeros.

        Returns:
            True if the block is valid, False otherwise.

        """
        return self.block_hash == self.current_hash()

    @staticmethod
    def shortened_hash(hash_: str, left: int = 4, right: int = 4) -> str:
        """Shortens a hash to a specified length.

        Args:
            hash_: The hash to shorten.
            left: The number of characters to keep from the beginning of the hash.
                Defaults to 4.
            right: The number of characters to keep from the end of the hash.
                Defaults to 4.

        Returns:
            The shortened hash.

        """
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
