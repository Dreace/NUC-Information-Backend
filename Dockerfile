FROM dreace233/python-base:nuc-info
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN pip install requests[socks]

WORKDIR /app
COPY . /app
CMD ["python","index.py"]