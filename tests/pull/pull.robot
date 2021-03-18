*** Settings ***
Documentation           DockerComposeLibrary tests.
Library                 DockerComposeLibrary
Test Teardown           Docker Compose Down


*** Test Cases ***
Fails to Pull Images For All Services If Image Cannot Be Found
    Run Keyword And Expect Error
    ...                 STARTS: Failed to pull image(s)
    ...                 Docker Compose Pull

Fails to Pull Images Single Service If Image Cannot Be Found
    @{service_names} =  Create List
    ...                 service-with-non-existent-image
    Run Keyword And Expect Error
    ...                 STARTS: Failed to pull image(s)
    ...                 Docker Compose Pull  service_names=${service_names}

Successfully Pulls Single Service with Existing Image
    @{service_names} =  Create List
    ...                 httpd
    Docker Compose Pull
    ...                 service_names=${service_names}
