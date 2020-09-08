from RC5 import RC5_key_generator, RC5_block_encryptor, RC5_block_decryptor
import secrets
import math


def RC5_CBC_encryption(msg, key, block_size = 128, rc5_rounds = 18):

    # receiving msg as bytes object

    # cipher block chaining, implemented with cipher stealing to manage incomplete blocks
    # explicit initialization vectors are used, so the first block is random
    # returns array of encrypted blocks along stolen length, in a tuple

    # splitting message into blocks

    block_byte_size = block_size // 8

    blocks_to_process = [secrets.randbits(128)] + [b'' for n_blocks in range(math.ceil(len(msg) / block_byte_size))]

    for i in range(len(msg)):
        blocks_to_process[1 + i // block_byte_size] += int.to_bytes(msg[i], 1, "big")

    stolen_length = block_byte_size - len(blocks_to_process[len(blocks_to_process) - 1])

    blocks_to_process[len(blocks_to_process) - 1] += b'\0' * stolen_length

    # conversion to integers

    for i in range(1, len(blocks_to_process)):

        aux_int = 0

        for c in blocks_to_process[i]:

            aux_int <<= 8
            aux_int |= c

        blocks_to_process[i] = aux_int

    # CBC encryption as normal

    encrypted_blocks = []

    iv = secrets.randbits(block_size)

    for i in range(len(blocks_to_process)):

        encrypted_blocks.append(RC5_block_encryptor(iv ^ blocks_to_process[i], key, block_size // 2, rc5_rounds))

        iv = encrypted_blocks[i]

    # executing ciphertext stealing

    encrypted_blocks[len(encrypted_blocks) - 2] >>= 8 * stolen_length

    return encrypted_blocks, stolen_length


def RC5_CBC_decryption(encrypted_blocks, key, stolen_length, block_size = 128, rc5_rounds = 18):

    # explicit initialization vector used in encryption, so iv does not need to be communicated
    # first treats the ciphertext stealing, then decrypts normally
    # returns plaintext message in bytes format

    # ciphertext stealing reversal

    stolen_length_bits = stolen_length * 8

    aux_block = RC5_block_decryptor(encrypted_blocks[len(encrypted_blocks) - 1], key, block_size // 2, rc5_rounds)

    stolen_piece = aux_block & ((1 << stolen_length_bits) - 1)

    encrypted_blocks[len(encrypted_blocks) - 2] <<= stolen_length_bits
    encrypted_blocks[len(encrypted_blocks) - 2] |= stolen_piece

    # CBC decryption as normal, except for skipping first block

    decrypted_blocks = []

    for i in range(1, len(encrypted_blocks)):

        decrypted_blocks.append(RC5_block_decryptor(encrypted_blocks[i], key, block_size // 2, rc5_rounds) ^ encrypted_blocks[i - 1])

    # converting integers to final padded string (original message padded with 0s for stealing)

    msg = b''

    for i in range(len(decrypted_blocks)):

        block_msg = b''

        for j in range(block_size // 8):

            block_msg += int.to_bytes(decrypted_blocks[i] & 255, 1, "big")

            decrypted_blocks[i] >>= 8

        msg += block_msg[::-1]

    return msg[:len(msg) - stolen_length]

