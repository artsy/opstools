from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def symmetric_encrypt(key, iv, message):
    """AES256 encrypt message and return ciphertext
    params are all str
    ciphertext returned is in bytes
    """
    algorithm = algorithms.AES256(bytes.fromhex(key))
    mode = modes.CTR(bytes.fromhex(iv))
    cipher = Cipher(algorithm, mode)
    encryptor = cipher.encryptor()
    return encryptor.update(bytes(message, "utf-8")) + encryptor.finalize()
