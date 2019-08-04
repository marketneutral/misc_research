I have some requirements for my JupyterHub setup that do not seem to be handled by [The Littlest JupyterHub]() or [Zero to JupyterHub with Kubernetes](), namely:

- The target number of users is 8-15 
- Runs on a single server (Linux insstance on AWS)
- The kernels need to spwan from Docker containers
- I will use PAM authentication against the users on the server
- User notebooks need to be persisted in the `/home/<username>` directory

I have everything working except the last point.

# The Current Working Setup

### 1. Install Anaconda
`root` installs anaconda3` in `/opt/anaconda`

### 2. Install JupyterHub
Install `jupyterhub` and `netifaces` via `conda`

### 3. Install Docker
Install Docker and makes `docker.service` run at startup.

### 4. Install dockerspawner
`pip install` the developement version of `dockerspawner`; `pip install git+https://github.com/jupyterhub/dockerspawner.git`

### 5. Configure JupyterHub
Make a `jupyterhub_config.py` and put it in `/srv/jupyterhub`

```python
# Configuration file for jupyterhub.

c.Authenticator.admin_users = {'jlarkin'}
c.PAMAuthenticator.open_sessions = False
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.remove_containers = True
c.DockerSpawner.image_whitelist = {
    'My Awesome Kernel': 'myawesomekernel',
    'My Awesome Kernel (dev)': 'myawesomekerneldev',
}
c.DockerSpawner.volumes = {
    '/srv/jupyterhub/home/{username}': '/home/jovyan',
    '/srv/jupyterhub/home/shared': '/home/jovyan/shared'
}

# the Hub's API listens on localhost by default,
# but docker containers can't see that.
# Tell the Hub to listen on its docker network:
import netifaces
docker0 = netifaces.ifaddresses('docker0')
docker0_ipv4 = docker0[netifaces.AF_INET][0]
c.JupyterHub.hub_ip = docker0_ipv4['addr']
```


### 6. Make User Directories
Make user directories in `/srv/jupyterhub/home/<username>`; `chmod 777` on those directories. I also make a ``/srv/jupyterhub/home/shared` directory so that the users can share data, templates, etc.

### 7. Make Dockerfiles and Images
Make a Dockerfile(s) for my kernel image. For instance, I use the awesome core Kaggle-Python Dockerfile as my base data science image.

```
FROM gcr.io/kaggle-images/python

RUN pip3 install \
    jupyterhub==0.9.4 \
        'notebook>=5.0,<=6.0'

# create a user, since we don't want to run as root
RUN useradd -m jovyan
ENV HOME=/home/jovyan
WORKDIR $HOME
USER jovyan

CMD ["jupyterhub-singleuser"]
```

I make image with `docker build -t myawesomekernel .`


### 8. Run it!

`jupyterhub -f /srv/jupyterhub/jupyterhub_config.py --no-ssl --ip=<my.ip.add.ress>`.
I am running on a private VPN so I have not configured security. **This works!** I can login to JupyterHub; I can see a drop down with my kernels; I can spawn a server and get access to the kernel; the nb's are saved and persisted; the shared folder works.



# The Problem

That all works, however it's not ideal becuase the user notebooks are persisted in `/srv/jupyterhub/<username>` and not in the actual Linux user directories. When JupyterHub runs, the `user` is `jovyan`. If I launch a Terminal and do `id` I get:

```
uid=1000(jovyan) gid=1000(jovyan) groups=1000(jovyan)
```

When I `ssh` into the AWS instance and look in the user home directories (e.g., `/srv/jupytyerhub/home/jlarkin`) I see that the notebooks are created and owned by `ec2-user`, which is the AWS name for the root user; e.g., `ls -la` gives something like

```
-rw-r--r-- 1 ec2-user ec2-user  37206 Jan 18 10:10 pandas-multiindex.ipynb
```


I don't want this. I need the user to be able to `ssh` into the instance and work at the command line in their home directory and see the same files they see when accessing the JupyterHub notebook. 


# The Attemp to Fix

The above install uses `c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'`. The [`dockerspawner.SystemUserSpawner`](https://github.com/jupyterhub/dockerspawner#systemuserspawner) is specifically for the use case of using the actual Linux user directories. As such, I change my `jupyterhub_config.py` file to

```
--  c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
++  c.JupyterHub.spawner_class = 'dockerspawner.SystemUserSpawner'
```

Now I restart the JupyterHub server and login. All good. I go to spawn my server and I get an error in the GUI:

```
Error: HTTP 500: Internal Server Error (Spawner failed to start [status=ExitCode=1, Error='', FinishedAt=2019-01-30T17:45:20.503795982Z]. The logs for jlarkin may contain details.)
```

The error at the command line is

```
[E 2019-01-30 12:46:39.736 JupyterHub pages:148] Failed to spawn single-user server with form
    Traceback (most recent call last):
      File "/opt/anaconda/lib/python3.7/site-packages/jupyterhub/handlers/pages.py", line 146, in post
        await self.spawn_single_user(user, options=options)
      File "/opt/anaconda/lib/python3.7/site-packages/jupyterhub/handlers/base.py", line 727, in spawn_single_user
        status, spawner._log_name))
    tornado.web.HTTPError: HTTP 500: Internal Server Error (Spawner failed to start [status=ExitCode=1, Error='', FinishedAt=2019-01-30T17:46:30.90390108Z]. The logs for jlarkin may contain details.)
```

I check the logs with `docker logs jupyter-jlarkin` and I see:

```
[I 2019-01-30 17:46:30.767 SingleUserNotebookApp singleuser:406] Starting jupyterhub-singleuser server version 0.9.4
[C 2019-01-30 17:46:30.772 SingleUserNotebookApp notebookapp:1614] Running as root is not recommended. Use --allow-root to bypass.
```

This is where I am at a loss. It appears the issue is with user permissioning. For example, the `base-notebook` in the Jupyter `docker-stacks` runs an elaborate user permissioning [script](https://github.com/jupyter/docker-stacks/blob/6fa9a4a1f0e5c8b00825ed43dbefaf445118d650/base-notebook/start.sh) at startup. I've tried to replicate this in my Dockerfile with no luck. 

# The Question

My question is: *what are the absolute minimal additions I need to make to my Dockerfile above in **7** to get it to work with SystemUserSpawner`?*

Thanks for reading!

