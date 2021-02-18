from solana.publickey import PublicKey
from solana.transaction import AccountMeta, TransactionInstruction, Transaction
import unittest
import base58

from eth_tx_utils import make_keccak_instruction_data, make_instruction_data_from_tx
from solana_utils import *

class EvmLoaderTestsNewAccount(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.acc = RandomAccaunt()
        # cls.acc = RandomAccaunt('1613635909.json')
        if getBalance(cls.acc.get_acc().public_key()) == 0:
            print("request_airdrop for ", cls.acc.get_acc().public_key())
            cli = SolanaCli(solana_url, cls.acc)
            cli.call('airdrop 1000000')
            # tx = http_client.request_airdrop(cls.acc.get_acc().public_key(), 100000)
            # confirm_transaction(http_client, tx['result'])
            # balance = http_client.get_balance(cls.acc.get_acc().public_key())['result']['value']
            print("Done\n")
            
        cls.loader = EvmLoader(solana_url, cls.acc)
        # cls.loader = EvmLoader(solana_url, cls.acc, 'E5eNJ1WLD9pSmBseBcVSwdusoaSKH7rMmmhNZT3gmswy')
        cls.evm_loader = cls.loader.loader_id
        print("evm loader id: ", cls.evm_loader)
        cls.owner_contract = cls.loader.deploy('evm_loader/hello_world.bin')
        # cls.owner_contract = "B7azmbC5hQZbP2twARJk1T51PkA3CyhRV1mZxWoKSwMA"
        print("contract id: ", cls.owner_contract)
        print("contract id: ", solana2ether(cls.owner_contract).hex())

        cls.caller_ether = solana2ether(cls.acc.get_acc().public_key())
        (cls.caller, cls.caller_nonce) = cls.loader.ether2program(cls.caller_ether)

        if getBalance(cls.caller) == 0:
            print("Create caller account...")
            caller_created = cls.loader.createEtherAccount(solana2ether(cls.acc.get_acc().public_key()))
            print("Done\n")

        print('Account:', cls.acc.get_acc().public_key(), bytes(cls.acc.get_acc().public_key()).hex())
        print("Caller:", cls.caller_ether.hex(), cls.caller_nonce, "->", cls.caller, "({})".format(bytes(PublicKey(cls.caller)).hex()))

    def test_check_tx(self):  
        tx_1 = {
            'to': solana2ether(self.owner_contract),
            'value': 1,
            'gas': 1,
            'gasPrice': 1,
            'nonce': 0,
            'data': '3917b3df',
            'chainId': 1
        }
        
        (from_addr, sign, msg) =  make_instruction_data_from_tx(tx_1, self.acc.get_acc().secret_key())

        keccak_instruction = make_keccak_instruction_data(0, len(msg))

        trx = Transaction().add(
            TransactionInstruction(program_id="KeccakSecp256k11111111111111111111111111111", data=keccak_instruction + from_addr + sign + msg, keys=[
                AccountMeta(pubkey=PublicKey("KeccakSecp256k11111111111111111111111111111"), is_signer=False, is_writable=False),
            ])).add(
            TransactionInstruction(program_id=self.evm_loader, data=bytearray.fromhex("a1"), keys=[
                AccountMeta(pubkey=self.owner_contract, is_signer=False, is_writable=True),
                AccountMeta(pubkey=self.acc.get_acc().public_key(), is_signer=True, is_writable=False),
                AccountMeta(pubkey=PublicKey("Sysvar1nstructions1111111111111111111111111"), is_signer=False, is_writable=False),  
                AccountMeta(pubkey=PublicKey("SysvarC1ock11111111111111111111111111111111"), is_signer=False, is_writable=False),              
            ]))
        result = http_client.send_transaction(trx, self.acc.get_acc())


    def test_check_wo_checks(self):  
        tx_1 = {
            'to': solana2ether(self.owner_contract),
            'value': 0,
            'gas': 0,
            'gasPrice': 0,
            'nonce': 0,
            'data': '3917b3df',
            'chainId': 1
        }
        
        (from_addr, sign, msg) =  make_instruction_data_from_tx(tx_1, self.acc.get_acc().secret_key())

        keccak_instruction = make_keccak_instruction_data(0, len(msg))

        trx = Transaction().add(
            TransactionInstruction(program_id="KeccakSecp256k11111111111111111111111111111", data=keccak_instruction + from_addr + sign + msg, keys=[
                AccountMeta(pubkey=PublicKey("KeccakSecp256k11111111111111111111111111111"), is_signer=False, is_writable=False),
            ])).add(
            TransactionInstruction(program_id=self.evm_loader, data=bytearray.fromhex("05"), keys=[
                AccountMeta(pubkey=self.owner_contract, is_signer=False, is_writable=True),
                AccountMeta(pubkey=self.acc.get_acc().public_key(), is_signer=True, is_writable=False),
                AccountMeta(pubkey=PublicKey("Sysvar1nstructions1111111111111111111111111"), is_signer=False, is_writable=False),  
                AccountMeta(pubkey=PublicKey("SysvarC1ock11111111111111111111111111111111"), is_signer=False, is_writable=False),              
            ]))
        result = http_client.send_transaction(trx, self.acc.get_acc())

    def test_raw_tx_wo_checks(self):  
        tx_2 = "0xf86c258520d441420082520894d8587a2fd6c30dd5c70f0630f1a635e4ae6ae47188043b93e2507e80008025a00675d0de7873f2c77a1c7ab0806cbda67ea6c25303ca7a80c211af97ea202d6aa022eb61dbc3097d7a8a4b142fd7f3c03bd8320ad02d564d368078a0a5fe227199"
        
        (from_addr, sign, msg) =  make_instruction_data_from_tx(tx_2)

        keccak_instruction = make_keccak_instruction_data(0, len(msg))

        trx = Transaction().add(
            TransactionInstruction(program_id="KeccakSecp256k11111111111111111111111111111", data=keccak_instruction + from_addr + sign + msg, keys=[
                AccountMeta(pubkey=PublicKey("KeccakSecp256k11111111111111111111111111111"), is_signer=False, is_writable=False),
            ])).add(
            TransactionInstruction(program_id=self.evm_loader, data=bytearray.fromhex("05"), keys=[
                AccountMeta(pubkey=self.owner_contract, is_signer=False, is_writable=True),
                AccountMeta(pubkey=self.acc.get_acc().public_key(), is_signer=True, is_writable=False),
                AccountMeta(pubkey=PublicKey("Sysvar1nstructions1111111111111111111111111"), is_signer=False, is_writable=False),  
                AccountMeta(pubkey=PublicKey("SysvarC1ock11111111111111111111111111111111"), is_signer=False, is_writable=False),              
            ]))
        result = http_client.send_transaction(trx, self.acc.get_acc())


if __name__ == '__main__':
    unittest.main()
