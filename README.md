# 42Transcendence
A web-based Pong game with enhanced gameplay features

## Requirements / DEPENDENCIES
## TODO: Maybe include in deploy.sh

```bash
sudo apt install -y uidmap
sudo apt-get install -y dbus-user-session
sudo apt-get install slirp4netns fuse-overlayfs uidmap
```
# DOCKER on ubuntu:
```bash
# Uninstall old docker stuff
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
sudo apt-get purge docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd
sudo rm /etc/apt/sources.list.d/docker.list
sudo rm /etc/apt/keyrings/docker.asc

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install it
# OLD LINE: sudo apt-get install docker-ce-rootless-extras docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# Maybe only this?
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-ce-rootless-extras docker-compose-plugin

# Disable the root system wide docker
# IMPORTANT: DO AN FCLEAN BEFORE!!!
sudo systemctl disable --now docker.service docker.socket
sudo rm /var/run/docker.sock

# Run install
dockerd-rootless-setuptool.sh install

# Not sure if we need this but maybe it helps after reboot etc.
systemctl --user start docker

# Make them start on startup
systemctl --user enable docker
sudo loginctl enable-linger $(whoami)

# Allow ports < 1024 even in rootless mode
sudo setcap cap_net_bind_service=ep $(which rootlesskit)
systemctl --user restart docker
```


## Deployment Instructions
:bulb: For detailed instructions on setting up the project, please visit our :book: [Project Setup Wiki Page](https://github.com/rajh-phuyal/42Transcendence/wiki/Project-Setup).

To be able to start this project you have to have installed:
- docker
- clone this repo
- create a `*.env` file
- make the `deploy.sh` executable `chmod +x deploy.sh`
- run the `deploy.sh` script to link your `*.env` once like: `./deploy -e path/to/your/.env`
    - -> This will create a `.transcendence_env_path` file to store the location of your `.env` file.
    - -> The `.transcendence_env_path` is listed in the `.gitignore` file
    - it will also build all images and uping the container
- now the app should be running...

from now on u can use the script without the `-e` flag

Once the deployment is complete, open your web browser and navigate to the game:

```https://localhost```

Enjoy the game!