# assumes docker is built from root directory with dockerfile: dip_specs/Dockerfile
# in root of the project run: docker build -t morph_sak -f dip_specs/Dockerfile .
# after building: run it with: 
# this docker need ubuntu
# it starts flask app on port 4444 (port of the container)
# 
FROM ubuntu:16.04
RUN apt-get -y update
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install python3.7 -y
RUN apt-get install python3-pip -y
RUN python3.7 -m pip install pip --upgrade
RUN python3.7 -m pip install wheel

COPY . /server
WORKDIR /server
RUN python3.7 -m pip install -r requirements.txt
RUN python3.7 -m pip install .
#CMD ["gunicorn", "-w", "2", "--chdir",  "./morphological_parser/", "api:app", "-b", "0.0.0.0:4444"]
# gunicorn -w 2 --chdir ./morphological_parser/ api:app -b 0.0.0.0:4444
#CMD "/server/start_gunicorn.sh"
CMD "while true; do echo hello; done"
