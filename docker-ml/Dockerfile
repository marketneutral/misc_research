# install docker
# docker build -t kagglekernel .
# docker run --rm -v /home/jlarkin:/tmp/working \
#  -w=/tmp/working -p 8888:8888 -it kagglekernel jupyter notebook \
#  --no-browser --allow-root --ip="0.0.0.0" --notebook-dir=/tmp/working \
#  --NotebookApp.token=''


FROM gcr.io/kaggle-images/python:v50
RUN pip3 install \
    jupyterhub==0.9.4 \
            'notebook>=5.0,<=6.0'

RUN useradd -m jovyan
ENV HOME=/home/jovyan
WORKDIR $HOME
USER jovyan

CMD ["jupyterhub-singleuser"]