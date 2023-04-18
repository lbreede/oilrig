import hashlib
import unittest

import coverage

from src.block import Block

cov = coverage.Coverage()
cov.start()

PREVIOUS_HASH = hashlib.sha256("Hello, World!".encode()).hexdigest()
TRANSACTION_0 = {"sender": "Alice", "receiver": "Bob", "amount": 1000}
TRANSACTION_1 = {"sender": "Bob", "receiver": "Charlie", "amount": 1000}
TIMESTAMP = "2023-04-20T16:20:00"

EXPECTED_BLOCK_0_HASH = (
    "0000616011ad845b9696c13794573a9df8d3ad494bf132556ff598c81fe47933"
)
EXPECTED_BLOCK_1_HASH = (
    "0027412dee71856bab8d44c7326dd59a3b81f32a10daa9c5b853e8949cffbe73"
)


class TestBlock(unittest.TestCase):
    def setUp(self):
        self.block_0 = Block(PREVIOUS_HASH, [TRANSACTION_0], timestamp=TIMESTAMP)
        self.block_1 = Block(
            self.block_0.block_hash,
            [TRANSACTION_0, TRANSACTION_1],
            timestamp=TIMESTAMP,
            difficulty=2,
        )

    def test_previous_hash(self):
        self.assertEqual(self.block_0.previous_hash, PREVIOUS_HASH)
        self.assertEqual(
            self.block_1.previous_hash,
            EXPECTED_BLOCK_0_HASH,
        )

    def test_transactions(self):
        self.assertEqual(len(self.block_0.transactions), 1)
        self.assertEqual(self.block_0.transactions[0], TRANSACTION_0)
        self.assertRaises(IndexError, self.block_0.transactions.__getitem__, 1)

        self.assertEqual(len(self.block_1.transactions), 2)
        self.assertEqual(self.block_1.transactions[0], TRANSACTION_0)
        self.assertEqual(self.block_1.transactions[1], TRANSACTION_1)

    def test_timestamp(self):
        self.assertEqual(self.block_0.timestamp, TIMESTAMP)
        self.assertEqual(self.block_1.timestamp, TIMESTAMP)

    def test_nonce(self):
        self.assertEqual(self.block_0.nonce, 21468)
        self.assertEqual(self.block_1.nonce, 43)

    def test_difficulty(self):
        self.assertEqual(self.block_0.difficulty, 4)
        self.assertEqual(self.block_1.difficulty, 2)

    def test_block_hash(self):
        self.assertEqual(
            self.block_0.block_hash,
            EXPECTED_BLOCK_0_HASH,
        )
        self.assertEqual(
            self.block_1.block_hash,
            EXPECTED_BLOCK_1_HASH,
        )

    def test_current_hash(self):
        self.assertEqual(
            self.block_0.current_hash(),
            EXPECTED_BLOCK_0_HASH,
        )
        self.assertEqual(
            self.block_1.current_hash(),
            EXPECTED_BLOCK_1_HASH,
        )

    def test_is_valid(self):
        self.assertTrue(self.block_0.is_valid())
        self.assertTrue(self.block_1.is_valid())
        # TODO: test various scenarious where this would return False

    def test_shortened_hash(self):
        self.assertEqual(self.block_0.shortened_hash("0"), "0")
        self.assertEqual(self.block_0.shortened_hash("01"), "01")
        self.assertEqual(self.block_0.shortened_hash("012"), "012")
        self.assertEqual(self.block_0.shortened_hash("0123456789ab"), "0123...89ab")
        self.assertEqual(self.block_0.shortened_hash("0123456789abcdef"), "0123...cdef")
        self.assertEqual(
            self.block_0.shortened_hash("0123456789abcdef", left=2, right=2), "01...ef"
        )
        self.assertEqual(
            self.block_0.shortened_hash("0123456789abcdef", left=1, right=5),
            "0...bcdef",
        )


cov.stop()
cov.save()
cov.report()
