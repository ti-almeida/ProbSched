# Nome do script Python
SCRIPT = TrabalhoSO.py

# Comando por omissão para correr a simulação
run:
	python3 $(SCRIPT)

# Comando com ficheiro de configuração JSON
config:
	python3 $(SCRIPT) --config config.json

# Limpeza de ficheiros temporários
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -delete