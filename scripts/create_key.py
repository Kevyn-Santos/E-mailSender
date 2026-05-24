import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.security import api_Key
if __name__ == "__main__":
    for _ in range(0, 11):
        chave_bruta, hash_ = api_Key.create_ApiKey()
        api_Key.storeKey(hash_)
        print(f"\nChave gerada: {chave_bruta}")
        print("Guarde esta chave — o hash é armazenado, a chave original não pode ser recuperada.\n")
