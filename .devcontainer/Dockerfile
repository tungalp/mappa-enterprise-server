# [Choice] Python version: 3.12 (bookworm)
ARG VARIANT=3.12-bookworm
FROM mcr.microsoft.com/vscode/devcontainers/python:1-${VARIANT}

# Environment configuration
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_CACHE_DIR=/tmp/.pip-cache 

# Remove broken Yarn repo
RUN rm -f /etc/apt/sources.list.d/yarn.list

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libffi-dev \
    liblzma-dev \
    libaio1 \
    unzip \
    vim \
    wget \
    odbcinst1debian2 \
    libodbc1 \
    tdsodbc \
    unixodbc-dev \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*


# Oracle Client
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && apt-get -y install libaio1 && \
    cd /tmp && \
    curl -o instantclient-basiclite.zip https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip -SL && \
    unzip instantclient-basiclite.zip && \
    mv instantclient*/ /usr/lib/instantclient && \
    rm instantclient-basiclite.zip && \
    ln -s /usr/lib/instantclient/libclntsh.so.21.1 /usr/lib/libclntsh.so && \
    ln -s /usr/lib/instantclient/libocci.so.21.1 /usr/lib/libocci.so && \
    ln -s /usr/lib/instantclient/libociicus.so /usr/lib/libociicus.so && \
    ln -s /usr/lib/instantclient/libnnz21.so /usr/lib/libnnz21.so && \
    ln -s /usr/lib/libnsl.so.2 /usr/lib/libnsl.so.1 && \
    ln -s /lib/libc.so.6 /usr/lib/libresolv.so.2 && \
    ln -s /lib64/ld-linux-x86-64.so.2 /usr/lib/ld-linux-x86-64.so.2

# MS SQL Server ODBC Driver (updated for Debian bookworm)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/$(lsb_release -rs)/prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*


# # In your Dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
# or
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \ && rm -rf /tmp/pip-tmp

# Configure vscode user environment
USER vscode

# Generate SSH keys (if needed)
RUN mkdir -p /home/vscode/.ssh \
    && chmod 700 /home/vscode/.ssh \
    && openssl genrsa -out /home/vscode/private.pem 2048 \
    && openssl rsa -in /home/vscode/private.pem -pubout -out /home/vscode/public.pem \
    && chmod 600 /home/vscode/private.pem

# Set environment variables
ENV LD_LIBRARY_PATH=/usr/lib/instantclient
ENV ESP_ENV=DEVELOPMENT
ENV PATH="/home/vscode/.local/bin:${PATH}"


# Expose application ports
EXPOSE 33100 33101 33102 33103 33104 33105 33106 33107 33200

# Switch back to root for devcontainer setup
USER root