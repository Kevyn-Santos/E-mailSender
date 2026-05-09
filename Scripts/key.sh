#!/bin/zsh

python -c "
from models.chaveApi import ChaveApi
chave = ChaveApi.gerar(ambiente='dev') 
print(chave)"