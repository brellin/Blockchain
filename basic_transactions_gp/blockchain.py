# Paste your version of blockchain.py from the client_mining_p
# folder here

import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            "index": len(self.chain),
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash,
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the chain to the block
        self.chain.append(block)
        # Return the new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It convertes the string to bytes.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # Create the block_string
        string_obj = json.dumps(block).encode()

        # Hash this string using sha256
        raw_hash = hashlib.sha256(string_obj)

        hex_hash = raw_hash.hexdigest()

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # Return the hashed block string in hexadecimal format
        return hex_hash

    def new_transaction(self, transaction):
        if transaction["sender"] and transaction["recipient"] and transaction["amount"]:
            self.current_transactions.append(transaction)
        return len(self.chain)

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        combo = f"{block_string}{proof}".encode()
        hashed = hashlib.sha256(combo).hexdigest()

        return hashed[:6] == "000000"


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace("-", "")

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route("/mine", methods=["POST"])
def mine():

    data = request.get_json()

    response = {"message": 'You must include "proof" and "id" fields'}

    # Check that 'proof', and 'id' are present
    if data["proof"] and data["id"]:

        block_str = json.dumps(blockchain.last_block, sort_keys=True)
        success = blockchain.valid_proof(block_str, data["proof"])

        if success is True:
            transaction = {"sender": "0", "recipient": data["id"], "amount": 1}
            blockchain.new_transaction(transaction)
            # Forge the new Block by adding it to the chain with the proof
            hash_str = blockchain.hash(block_str)
            blockchain.new_block(data["proof"], hash_str)

            # Return a message indicating success or failure.
            response["message"] = "New Block Forged!"
            return jsonify(response), 200

        response["message"] = "You did not get it."

    # return a 400 error using jsonify(response) with a 'message'
    return jsonify(response), 400


@app.route("/chain", methods=["GET"])
def full_chain():
    response = {"length": len(blockchain.chain), "chain": blockchain.chain}
    return jsonify(response), 200


# Add an endpoint called last_block that returns the last block in the chain
@app.route("/last_block", methods=["GET"])
def last_block():
    return jsonify(blockchain.last_block), 200


@app.route("/transactions/new", methods=["POST"])
def new_transaction():

    data = request.get_json()

    response = {
        "message": 'The "sender", "recipient", and "amount" fields are required. Please try again.'
    }

    if data["sender"] and data["recipient"] and data["amount"]:
        response["message"] = blockchain.new_transaction(data)
        return jsonify(response), 200

    return jsonify(response), 400


# Run the program on port 5000
if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
