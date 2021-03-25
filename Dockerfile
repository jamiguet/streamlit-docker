FROM python:3.7
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

EXPOSE ${PORT}

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /root/.streamlit

RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'

RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'

ENV GOOGLE_APPLICATION_CREDENTIALS "/usr/src/app/resources/portfolio_valuator.json"

ENTRYPOINT streamlit run --server.port ${PORT} /usr/src/app/src/${DASHBOARD_FILE}

