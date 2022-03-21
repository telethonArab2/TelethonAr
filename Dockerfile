FROM telethonAr/telethonArab:slim-buster

RUN git clone https://github.com/telethonArab/TelethonAr /root/userbot
WORKDIR /root/userbot

## Install requirements
RUN pip3 install -U -r requirements.txt

ENV PATH="/home/userbot/bin:$PATH"

CMD ["python3","-m","userbot"]
