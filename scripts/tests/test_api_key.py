#import sys, os
#print("CWD:", os.getcwd())
#print("Sistema: ", sys.path[:3])

import pytest
from src.core.security import ApiKey



def test_class_create_apiKey():
    raw, hashed = ApiKey().create_ApiKey()
    return (raw, hashed)