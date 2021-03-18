*** Settings ***
Documentation           DockerComposeLibrary tests.
Library                 DockerComposeLibrary
Test Teardown           Docker Compose Down


*** Test Cases ***
Builds Image For Container
    ${build_args} =     Create Dictionary
    ...                 ARG=VALUE
    Docker Compose Build
    ...                 build_args=${build_args}
