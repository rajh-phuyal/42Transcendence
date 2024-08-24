# 42Transcendence
A web-based Pong game with enhanced gameplay featureskk

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
- rerun the `./deploy.sh` script to build the application
- now the app should be running...


Once the deployment is complete, open your web browser and navigate to the game:

```http://localhost:8080/```

Enjoy the game!