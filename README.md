# RobotFramework Docker
## Short Description
[Robot Framework](https://robotframework.org/) library for working with `docker` and `docker-compose`.

## Installation
### Installation from sources
```bash
python3 setup.py install
```

## Example
```robotframework
*** Settings ***
Documentation           DockerComposeLibrary tests.
Library                 DockerComposeLibrary
Library                 RequestsLibrary
Test Setup              Docker Compose Up
Test Teardown           Docker Compose Down


*** Test Cases ***
Start Apache Web Server
    ${service} =        Get Exposed Service  httpd  80
    Log To Console      http has started and is available at http://${service.host}:${service.port}
```

## License
Apache License 2.0