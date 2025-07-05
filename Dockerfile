FROM python:3.13.5-bullseye

RUN mkdir -p /code/src
WORKDIR /code/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src .

RUN chmod +x /code/src/bw-linux-2025.6.1/bw
ENV BW_CLI_PATH=/code/src/bw-linux-2025.6.1/bw

CMD [ "python", "runExport.py" ]