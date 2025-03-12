from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def symmetric_encrypt(key: str, iv: str, message: str) -> bytes:
    """AES256 encrypt a message.

    Returns
    -------
    ciphertext: bytes
    """
    algorithm = algorithms.AES256(bytes.fromhex(key))
    mode = modes.CTR(bytes.fromhex(iv))
    cipher = Cipher(algorithm, mode)
    encryptor = cipher.encryptor()
    return encryptor.update(bytes(message, "utf-8")) + encryptor.finalize()
