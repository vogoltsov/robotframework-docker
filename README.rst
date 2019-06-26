.. image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://opensource.org/licenses/Apache-2.0
.. image:: https://travis-ci.com/vogoltsov/robotframework-docker.svg?branch=master
   :target: https://travis-ci.com/vogoltsov/robotframework-docker
.. image:: https://badge.fury.io/py/robotframework-docker.svg
    :target: https://badge.fury.io/py/robotframework-docker


RobotFramework Docker
=====================

.. contents::


.. comment: long_description split

Short Description
-----------------

`Robot Framework`_ library for working with ``docker`` and
``docker-compose``.

Installation
------------

Installation using pip
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   pip3 install robotframework-docker


Installation from sources
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   python3 setup.py install

Example
-------

.. code:: robotframework

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

License
-------

Apache License 2.0

.. _Robot Framework: https://robotframework.org/
