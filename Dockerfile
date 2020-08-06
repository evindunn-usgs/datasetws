FROM usgsastro/miniconda3 as builder
SHELL ["/bin/bash", "-c"]

ENV FLASK_APP passenger_wsgi
ENV FLASK_ENV production

COPY . /app
WORKDIR /app
RUN conda env update -f environment.yml && mkdir -p instance && touch instance/config.py

EXPOSE 5000
CMD ["flask", "run"]
