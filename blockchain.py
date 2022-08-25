

# https://hackernoon.com/learn-blockchains-by-building-one-117428612f46

import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4
from urllib.parse import urlparse

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        #Creamos el bloque génesis
        self.new_block(previous_hash=1, proof=100)


    def register_node(self, address):
        """

        Añadimos un nuevo nodo a la lista de nodos
        :param adress: <str> Dirección del nodo. Por ejemplo: 'http://192.168.0.5:5000'
        :return: None

        """

        parsed_url = urlparse(adress)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Determinamos si la blockchain es válida
        :param chain: Una blockchain
        :return: True si es válido, False si no
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """

        Este es el algoritmo de consenso, resuelve conflictos reemplazando
        la cadena con la más larga en la red
        :return: True si la cadena se ha reemplazado, False si no
        
        """

        neighbours = self.nodes
        new_chain = None

        # Solo buscamos cadenas más largas que la nuestra
        max_length = len(self.chain)

        # Cogemos y verificamos todas las cadenas de todos los nodos en nuestra red
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Comprobamos si la longitud es mayor y la cadena es válida
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Reemplazamos nuestra cadena si hemos encontrado una mayor y válida
        if new_chain:
            self.chain = new_chain
            return True

        return False


    def new_block(self, proof, previous_hash=None):
        """

        Creamos un nuevo bloque en la blockchain
        :param proof: <int> La prueba dada por el algoritmo Proof of Work (PoW)
        :param previous_hash: (Opcional) <str> Hash del bloque anterior
        :return: <dict> Nuevo bloque

        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        #Reseteamos la lista actual de transacciones
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        
        Creamos una nueva transacción para el siguiente bloque minado

        :param sender: <str> dirección del que envía
        :param recipient: <str> dirección del que recibe
        :param amout: <int> Cantidad
        :return: <int> El indice del bloque que contendrá la transacción

        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """

        Creamos un hash SHA-256 de un bloque
        :param block: <dict> Bloque
        :return: <str>

        """
        
        #Debemos asegurarnos de que el diccionario está ordenado o tendremos hashes inconsistentes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
   
    def  proof_of_work(self, last_block):
        """
        
        Simple Proof of Work Algorithm:
        - Encuentra un número p' tal que el hash(pp') contenga 4 ceros al principio, donde p es el previo a p'
        - p es la prueba anterior y p' es la nueva prueba
        :param last_block: <int> ultimo bloque
        :return: <int>

        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)
        diff = self.last_block['index'] #diff será la dificultad, que irá aumentando con cada bloque que sea minado
        proof = 0
        while self.valid_proof(last_proof, proof, last_hash, diff) is False:
           proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash, diff):
        """

        Valida la prueba: Empieza hash(last_proof, proof) por 4 ceros?
        :param last_proof: <int> Prueba previa
        :param proof: <int> Prueba actual
        :return: <bool> True si es correcto, False si no

        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        print(f'{guess_hash}\n')
        return guess_hash[:diff] == "0"*diff

    # Instanciamos nuestro nodo
app = Flask(__name__)

    #Generamos una direccion global única para este nodo
node_identifier = str(uuid4()).replace('-', '')

    # Instanciamos la blockchain
blockchain = Blockchain()


@app.route('/mine', methods =['GET'])
def mine():
    # Ejecutamos la prueba de trabajo para para encontrar la siguiente prueba
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # Tenemos que recibir una recompensa por encontrar la prueba
    # El "sender" es '0' lo que significa que este nodo ha minado una nueva moneda
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forjamos el nuevo bloque añadiendolo a la cadena
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "Nuevo bloque forjado",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods = ['POST'])
def new_transaction():
    values = request.get_json()
    #comprobamos que los campos requeridos estan el los datos enviados por POST
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Faltan valores', 400

    #Creamos una nueva transacción
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'La transacción se añadirá al bloque {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
