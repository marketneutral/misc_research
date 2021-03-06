Do this once to create the vm.

```
docker-machine create --virtualbox-disk-size 100000 -d virtualbox default
```

Then, each time you startup, get the vm going with

```
docker-machine start
docker-machine env
eval $(docker-machine env)
```

And as usual, you can run docker images like

```
docker run -p 8888:8888 jupyter/scipy-notebook
```

The IP of the docker-machine named `default` is in the environment variable `DOCKER_HOST`. You need to use this IP address to get to the Jupyter notebook.

For the Kaggle docker image

```
docker build -t kaggler .
```

To run it, might be best to do it in two stages:

```
docker run -p 8888:8888 -it kaggler /bin/bash
```

which puts you at the command prompt. Then

```
jupyter notebook --ip="0.0.0.0"
```



