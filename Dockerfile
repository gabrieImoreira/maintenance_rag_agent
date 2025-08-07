# Usa uma imagem oficial do Python.
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container.
WORKDIR /app

# Instala as dependências de forma direta, rápida e confiável.
# --no-cache-dir: Não armazena o cache do pip, mantendo a imagem menor.
# --trusted-host pypi.python.org: Pode ajudar a evitar problemas de SSL em algumas redes.
RUN apt-get update && apt-get install -y software-properties-common && \
    pip install setuptools && \
    pip install pipenv

ENV PATH "$HOME/.local/bin:$PATH"
ENV PIPENV_IGNORE_VIRTUALENVS 1
ENV PIPENV_VENV_IN_PROJECT 1
ENV PYTHONWARNINGS "ignore:Unverified HTTPS request"

# Copia todo o resto do código da sua aplicação.
COPY . .

# Expõe a porta que o Streamlit usa.
EXPOSE 8501

RUN pipenv install 

# Comando para rodar a aplicação.
CMD ["pipenv", "run", "streamlit", "run", "app/app_os.py", "--server.port=8501", "--server.address=0.0.0.0"]