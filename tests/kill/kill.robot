*** Settings ***
Documentation           DockerComposeLibrary tests.
Library                 DockerComposeLibrary
Test Setup              Docker Compose Up
Test Teardown           Docker Compose Down


*** Test Cases ***
Successfully Kills All Services
    Get Exposed Service     httpd1  80
    Get Exposed Service     httpd2  80
    @{service_names} =      Create List
    ...                     httpd1
    ...                     httpd2
    Docker Compose Kill     service_names=${service_names}
    Run Keyword And Expect Error
    ...                     *
    ...                     Get Exposed Service  httpd1  80
    Run Keyword And Expect Error
    ...                     *
    ...                     Get Exposed Service  httpd2  80

Successfully Kills Service
    Get Exposed Service     httpd1  80
    Get Exposed Service     httpd2  80
    @{service_names} =      Create List
    ...                     httpd1
    Docker Compose Kill     service_names=${service_names}
    Run Keyword And Expect Error
    ...                     *
    ...                     Get Exposed Service  httpd1  80
    Get Exposed Service     httpd2  80

Fails to Kill a Service That Does Not Exist
    @{service_names} =      Create List
    ...                     unknown
    Docker Compose Kill     service_name=${service_names}
    Run Keyword And Expect Error
    ...                     *
    ...                     Docker Compose Kill
    ...                     service_names=${service_names}
