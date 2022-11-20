# -*- coding: utf-8 -*-
# pylint: disable=C0103
"""Robot Framework Docker Library."""

import os
import re
import subprocess
import sys
from typing import List

import packaging.version
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.DateTime import convert_time


# pylint: disable=R0903
class ExposedServiceInfo:
    """Defines info for specific exposed service port."""
    host: str
    port: str


class DockerComposeLibrary:
    """DockerComposeLibrary is a part of Robot Framework Docker Library
    that is used for running multi-container Docker applications using 'docker-compose'.
    """

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    _docker_compose_cmd: [str]
    _docker_compose_version: packaging.version.Version
    _file: str = None
    _project_name: str = None
    _project_directory: str = None

    def __init__(self,
                 file: str = None,
                 project_name: str = None,
                 project_directory: str = None):
        """Initializes an instance of DockerComposeLibrary to use a given Compose file and project name.

        `file` Path to compose file. By default, tries to use 'docker-compose.yml'
        in a directory where current test suite source file is located.

        `project_name` Specify an alternate project name (default: test suite name).
        """
        self._find_docker_compose()
        logger.info(f'[Docker Compose Library] Using Docker Compose v${self._docker_compose_version}')

        if file is not None:
            self._file = file
        else:
            # by default, use docker-compose.yml located in the suite directory
            self._file = 'docker-compose.yml'

        if project_name is not None:
            self._project_name = project_name
        else:
            self._project_name = re.sub(r'\W', '_', BuiltIn().get_variable_value('${SUITE NAME}'), re.ASCII).lower()

        if project_directory is not None:
            self._project_directory = project_directory
        else:
            # by default, use suite directory as project directory
            suite_source = BuiltIn().get_variable_value('${SUITE SOURCE}')
            self._project_directory = os.path.dirname(suite_source)

        # if file path is not absolute, it is considered to be relative to a suite directory
        if not os.path.isabs(self._file):
            suite_source = BuiltIn().get_variable_value('${SUITE SOURCE}')
            self._file = os.path.join(os.path.dirname(suite_source), self._file)

        logger.info(f'[Docker Compose Library] Project "{self._project_name}"'
                    f' initialized using configuration file: {self._file}')

    def docker_compose_version(self) -> str:
        """Returns Docker Compose version."""
        return self._docker_compose_version.base_version

    # pylint: disable=R0912, R0913, C0103
    def docker_compose_pull(self,
                            no_parallel: bool = False,
                            include_deps: bool = False,
                            service_names: List[str] = None) -> None:
        """Pulls images for services defined in a Compose file, but does not start the containers.
        All parameters are forwarded to `docker-compose`.

        `no_parallel` Disable parallel pulling (default: False).

        `include_deps` Also pull services declared as dependencies (default: False).

        `service_names` A list of service names to be pulled.


        = Examples =

        Pull All Service Images
        | Docker Compose Pull |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('pull')
        cmd.append('--quiet')

        if no_parallel:
            cmd.append('--no-parallel')

        if include_deps:
            cmd.append('--include-deps')

        if service_names is not None:
            cmd.extend(service_names)

        try:
            subprocess.check_output(cmd,
                                    cwd=self._project_directory,
                                    stdin=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT,
                                    encoding=sys.getdefaultencoding(),
                                    text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'[Docker Compose Pull] Failed to pull image(s): {e.output.rstrip()}') from e

    # pylint: disable=R0912, R0913, C0103
    def docker_compose_build(self,
                             compress: bool = False,
                             force_rm: bool = False,
                             no_cache: bool = False,
                             no_rm: bool = False,
                             parallel: bool = False,
                             pull: bool = False,
                             build_args: dict = None,
                             service_names: List[str] = None) -> None:
        """Build or rebuild services.
        All parameters are forwarded to `docker-compose`.

        `compress` Compress the build context using gzip (default: False).

        `force_rm` Always remove intermediate containers (default: False).

        `no_cache` Do not use cache when building the image (default: False).

        `no_rm` Do not intermediate containers after a successful build (default: False).

        `parallel` Build images in parallel (default: False).

        `pull` Always attempt to pull a newer version of the image (default: False).

        `service_names` A list of service names to be built.
        All services are started by default.


        = Examples =

        Build Images
        | Docker Compose Build |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('build')
        cmd.append('--quiet')

        if compress:
            cmd.append('--compress')

        if force_rm:
            cmd.append('--force-rm')

        if no_cache:
            cmd.append('--no-cache')

        if no_rm:
            cmd.append('--no-rm')

        if parallel:
            cmd.append('--parallel')

        if pull:
            cmd.append('--pull')

        if build_args is not None:
            for key, value in build_args.items():
                cmd.append('--build-arg')
                cmd.append(f'{key}={value}')

        if service_names is not None:
            cmd.extend(service_names)

        try:
            subprocess.check_output(cmd,
                                    cwd=self._project_directory,
                                    stdin=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT,
                                    encoding=sys.getdefaultencoding(),
                                    text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'[Docker Compose Build] Failed to build image(s): {e.output.rstrip()}') from e

    # pylint: disable=R0912, R0913, C0103
    def docker_compose_up(self,
                          timeout: str = '10 seconds',
                          no_deps: bool = False,
                          force_recreate: bool = True,
                          always_recreate_deps: bool = None,
                          no_recreate: bool = False,
                          no_build: bool = False,
                          no_start: bool = False,
                          build: bool = False,
                          renew_anon_volumes: bool = True,
                          remove_orphans: bool = True,
                          wait: bool = None,
                          service_names: List[str] = None) -> None:
        """Builds, (re)creates, starts, and attaches to containers for a service.
        All parameters are forwarded to `docker-compose`.

        `no_deps` Don't start linked services (default: False).

        `force_recreate` Recreate containers even if their configuration
        and images haven't changed (default: False).

        `always_recreate_deps` Recreate dependent containers (default: False).
        Incompatible with 'no_recreate`.

        `no_recreate` If containers already exist, don't recreate

        `no_build` Don't build an image, even if it's missing (default: False).

        `no_start` Don't start the services after creating them (default: False).

        `build` Build images before starting containers (default: False).

        `renew_anon_volumes` Recreate anonymous volumes instead of retrieving data
        from the previous containers (default: True).

        `remove_orphans` Remove containers for services not defined
        in the Compose file (default: True).

        `wait` Wait for services to be running|healthy (default: True).

        `service_names` A list of service names to be started.
        All services are started by default.


        = Examples =

        Start All Services
        | Docker Compose Up |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('up')
        cmd.append('--timeout')
        cmd.append(str(int(convert_time(timeout))))
        cmd.append('-d')

        if no_deps:
            cmd.append('--no-deps')

        if force_recreate:
            cmd.append('--force-recreate')

        if self._docker_compose_version < packaging.version.Version('1.19.0') and always_recreate_deps:
            logger.warn('[Docker Compose Up] option --always-recreate-deps'
                        f' is only supported since Docker Compose version v1.19.0'
                        f' (using Docker Compose v{self._docker_compose_version})')
        elif always_recreate_deps or always_recreate_deps is None:
            cmd.append('--always-recreate-deps')

        if no_recreate:
            cmd.append('--no-recreate')

        if no_build:
            cmd.append('--no-build')

        if no_start:
            cmd.append('--no-start')

        if build:
            cmd.append('--build')

        if self._docker_compose_version < packaging.version.Version('1.19.0') and renew_anon_volumes:
            logger.warn('[Docker Compose Up] option --renew-anon-volumes'
                        f' is only supported since Docker Compose version v1.19.0'
                        f' (using Docker Compose v{self._docker_compose_version})')
        elif renew_anon_volumes or renew_anon_volumes is None:
            cmd.append('--renew-anon-volumes')

        if remove_orphans:
            cmd.append('--remove-orphans')

        if self._docker_compose_version < packaging.version.Version('2.0.0') and wait:
            logger.warn('[Docker Compose Up] option --wait'
                        f' is only supported since Docker Compose version v2.0.0'
                        f' (using Docker Compose v{self._docker_compose_version})')
        elif wait or wait is None:
            cmd.append('--wait')

        if service_names is not None:
            cmd.extend(service_names)

        try:
            subprocess.check_output(cmd,
                                    cwd=self._project_directory,
                                    stdin=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT,
                                    encoding=sys.getdefaultencoding(),
                                    text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'[Docker Compose Up] Failed to start services: {e.output.rstrip()}') from e

    def docker_compose_down(self,
                            timeout: str = None,
                            rmi: str = None,
                            volumes: bool = True,
                            remove_orphans: bool = True) -> None:
        """ Stops and removes containers, networks, volumes and images created by 'up'.
        All parameters are forwarded to `docker-compose`.

        As this function is intended to be used in teardown,
        to help keep the test environment clean,
        the following parameters are added to `docker-compose down` by default:
        - --remove-orphans
        - --volumes

        `timeout` Specify shutdown timeout in seconds (default: 10).

        `rmi` Remove images. Specify 'all' ro remove all images used by any service
        or 'local' to remove only images that don't have a custom tag set by the 'image' field.

        `volumes` Remove named volumes declared in the 'volumes' section of the Compose file
        and anonymous volumes attached to containers.

        `remove_orphans` Remove containers for services not defined in the Compose file.


        = Examples =

        Stop And Remove All Containers And Volumes
        | Docker Compose Down |

        Stop And Remove All Containers And Volumes
        | Docker Compose Down |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('down')

        if self._docker_compose_version < packaging.version.Version('1.18.0') and timeout is not None:
            logger.warn('[Docker Compose Down] option --timeout'
                        f' is only supported since Docker Compose version v1.18.0'
                        f' (using Docker Compose v{self._docker_compose_version})')
        elif timeout is not None:
            cmd.append('--timeout')
            cmd.append(str(int(convert_time(timeout or '10 seconds'))))

        if rmi is not None:
            cmd.append('--rmi')
            cmd.append(rmi)

        if volumes:
            cmd.append('--volumes')

        if remove_orphans:
            cmd.append('--remove-orphans')

        try:
            subprocess.check_output(cmd,
                                    cwd=self._project_directory,
                                    stdin=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT,
                                    encoding=sys.getdefaultencoding(),
                                    text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'[Docker Compose Down] Failed to shutdown services: {e.output.rstrip()}') from e

    def docker_compose_start(self,
                             service_names: List[str] = None) -> None:
        """Start services.

        `timeout` Specify stop timeout in seconds (default: 10).

        `service_names` A list of service names to be started.


        = Examples =

        Start All Services
        | Docker Compose Start |

        Start Certain Services
        | @{service_names} = | Create List |
        | ... | services1 |
        | ... | services2 |
        | Docker Compose Start | service_names=${service_names} |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('start')

        if service_names is not None:
            cmd.extend(service_names)

        try:
            subprocess.check_output(cmd,
                                    cwd=self._project_directory,
                                    stdin=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT,
                                    encoding=sys.getdefaultencoding(),
                                    text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'[Docker Compose Start] Failed to start services: {e.output.rstrip()}') from e

    def docker_compose_stop(self,
                            timeout: str = '10 seconds',
                            service_names: List[str] = None) -> None:
        """Stop services.

        `timeout` Specify stop timeout in seconds (default: 10).

        `service_names` A list of service names to be stopped.


        = Examples =

        Stop All Services
        | Docker Compose Stop |

        Stop Certain Services
        | @{service_names} = | Create List |
        | ... | services1 |
        | ... | services2 |
        | Docker Compose Stop | service_names=${service_names} |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('stop')

        if timeout is not None:
            cmd.append('--timeout')
            cmd.append(str(int(convert_time(timeout or '10 seconds'))))

        if service_names is not None:
            cmd.extend(service_names)

        try:
            subprocess.check_output(cmd,
                                    cwd=self._project_directory,
                                    stdin=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT,
                                    encoding=sys.getdefaultencoding(),
                                    text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'[Docker Compose Stop] Failed to stop services: {e.output.rstrip()}') from e

    def docker_compose_restart(self,
                               timeout: str = '10 seconds',
                               service_names: List[str] = None) -> None:
        """Restart services.

        `timeout` Specify stop timeout in seconds (default: 10).

        `service_names` A list of service names to be restarted.


        = Examples =

        Restart All Services
        | Docker Compose Restart |

        Restart Certain Services
        | @{service_names} = | Create List |
        | ... | services1 |
        | ... | services2 |
        | Docker Compose Restart | service_names=${service_names} |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('restart')

        if timeout is not None:
            cmd.append('--timeout')
            cmd.append(str(int(convert_time(timeout or '10 seconds'))))

        if service_names is not None:
            cmd.extend(service_names)

        try:
            subprocess.check_output(cmd,
                                    cwd=self._project_directory,
                                    stdin=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT,
                                    encoding=sys.getdefaultencoding(),
                                    text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'[Docker Compose Restart] Failed to restart services: {e.output.rstrip()}') from e

    def docker_compose_kill(self,
                            remove_orphans: bool = False,
                            signal: str = None,
                            service_names: List[str] = None) -> None:
        """Force stop service containers.

        `signal` SIGNAL to send to the container (default "SIGKILL").

        `remove_orphans` Remove containers for services not defined in the Compose file.


        = Examples =

        Kill All Services
        | Docker Compose Kill |

        Kill Certain Services
        | @{service_names} = | Create List |
        | ... | services1 |
        | ... | services2 |
        | Docker Compose Kill | service_names=${service_names} |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('kill')

        if remove_orphans:
            cmd.append('--remove-orphans')

        if signal is not None:
            cmd.append('--signal')
            cmd.append(signal)

        if service_names is not None:
            cmd.extend(service_names)

        try:
            output = subprocess.check_output(cmd,
                                             cwd=self._project_directory,
                                             stdin=subprocess.DEVNULL,
                                             stderr=subprocess.STDOUT,
                                             encoding=sys.getdefaultencoding(),
                                             text=True)
            if output == 'no container to kill':
                raise AssertionError(f'[Docker Compose Kill] No container(s) to kill for service: ${service_names}')
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'[Docker Compose Kill] Failed to kill services: {e.output.rstrip()}') from e

    def docker_compose_pause(self,
                             service_names: List[str] = None) -> None:
        """Pause services.

        `service_names` A list of service names to be paused.


        = Examples =

        Pause All Services
        | Docker Compose Pause |

        Pause Certain Services
        | @{service_names} = | Create List |
        | ... | services1 |
        | ... | services2 |
        | Docker Compose Pause | service_names=${service_names} |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('pause')

        if service_names is not None:
            cmd.extend(service_names)

        try:
            subprocess.check_output(cmd,
                                    cwd=self._project_directory,
                                    stdin=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT,
                                    encoding=sys.getdefaultencoding(),
                                    text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'[Docker Compose Pause] Failed to pause services: {e.output.rstrip()}') from e

    def docker_compose_unpause(self,
                               service_names: List[str] = None) -> None:
        """Unpause services.

        `service_names` A list of service names to be unpaused.


        = Examples =

        Unpause All Services
        | Docker Compose Unpause |

        Unpause Certain Services
        | @{service_names} = | Create List |
        | ... | services1 |
        | ... | services2 |
        | Docker Compose Unpause | service_names=${service_names} |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('unpause')

        if service_names is not None:
            cmd.extend(service_names)

        try:
            subprocess.check_output(cmd,
                                    cwd=self._project_directory,
                                    stdin=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT,
                                    encoding=sys.getdefaultencoding(),
                                    text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'[Docker Compose Unpause] Failed to unpause services: {e.output.rstrip()}') from e

    def docker_compose_logs(self,
                            write_to: str = None,
                            prefix: bool = True,
                            timestamps: bool = True,
                            service_names: List[str] = None) -> str:
        """Grabs or saves the output from containers.

        `write_to` Name of the log file to use. Can be an absolute or
        relative path. Relative paths are looked up relative to the
        working directory of the Robot Framework process, not relative
        to the Docker Compose project. If not specified, the logs are
        captured and returned from the keyword.

        `prefix`: If false, `--no-log-prefix` is passed to `docker-compose`
        (default: True).

        `timestamps`: If true, `--timestamps` is passed to `docker-compose`
        (default: True).

        `service_names` A list of service names to limit which logs are gotten.

        = Examples =

        Save container logs to a file
        | Docker Compose Logs | write_to=/tmp/containers.log |

        Grab container logs into a variable
        | ${logs} = | Docker Compose Logs |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('logs')
        cmd.append('--no-color')

        if not prefix:
            cmd.append('--no-log-prefix')

        if timestamps:
            cmd.append('--timestamps')

        if service_names is not None:
            cmd.extend(service_names)

        if write_to is not None:
            # pylint: disable=consider-using-with
            output_file = open(write_to, 'a', encoding=sys.getdefaultencoding())
            close_output_file = output_file.close
        else:
            output_file = subprocess.PIPE
            close_output_file = DockerComposeLibrary._do_nothing

        try:
            process = subprocess.run(cmd,
                                     check=True,
                                     cwd=self._project_directory,
                                     stdin=subprocess.DEVNULL,
                                     stdout=output_file,
                                     stderr=subprocess.PIPE,
                                     encoding=sys.getdefaultencoding(),
                                     text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'[Docker Compose Logs] Failed to get service logs: {e.stderr}') from e
        finally:
            close_output_file()

        if write_to is None:
            return process.stdout
        return None

    def get_exposed_service(self,
                            service_name: str,
                            port: int,
                            protocol: str = None) -> ExposedServiceInfo:
        """Retrieves host address and port number for a port exposed by service.

        `service_name` Service name from Compose file.

        `port` Exposed service port number.


        = Examples =

        Get Httpd Exposed Service
        | ${service} = | Get Compose Exposed Service | httpd | 80 |
        | Log To Console | Services is located at ${service.host}:${service.port} |
        """

        info = self._get_exposed_port(service_name, port, protocol)
        service = ExposedServiceInfo()
        if self._is_inside_container():
            service.host = self._get_container_gateway_ip()
        elif info[0] == '0.0.0.0':
            service.host = '127.0.0.1'
        else:
            service.host = info[0]
        service.port = info[1]
        return service

    def _get_exposed_port(self, service_name: str, port: int, protocol: str) -> [str]:
        """Helper function to retrieve info about exposed port by calling 'docker-compose port'."""
        cmd = self._prepare_base_cmd()
        cmd.append('port')
        if protocol is not None:
            cmd.append('--protocol')
            cmd.append(protocol)
        cmd.append(service_name)
        cmd.append(str(port))

        try:
            output = subprocess.check_output(cmd,
                                             cwd=self._project_directory,
                                             stdin=subprocess.DEVNULL,
                                             stderr=subprocess.STDOUT,
                                             encoding=sys.getdefaultencoding(),
                                             text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(
                f'[Get Exposed Service] Failed to query exposed ports for service {service_name}: {e.stderr}') from e

        # Docker Compose V1 returns empty string when querying port that is not exposed.
        # Docker Compose V2 returns string ':0' in this case.
        result = output.rstrip().split(':')
        if len(result) != 2 or (result[0] == '' and result[1] == '0'):
            raise AssertionError(f'[Get Exposed Service] Port {port} is not exposed for service {service_name}')

        return result

    def _prepare_base_cmd(self) -> [str]:
        """Helper function to create a 'docker-compose' command with project name and file arguments."""
        cmd = self._docker_compose_cmd.copy()

        cmd.append('--project-name')
        cmd.append(self._project_name)

        cmd.append('--file')
        cmd.append(self._file)

        return cmd

    def _find_docker_compose(self) -> [str]:
        """Helper function to find and set Docker Compose executable and version"""
        # noinspection PyBroadException
        try:
            cmd = [
                'docker',
                'compose',
                'version'
            ]
            version_string = subprocess.check_output(cmd,
                                                     cwd=self._project_directory,
                                                     stdin=subprocess.DEVNULL,
                                                     stderr=subprocess.STDOUT,
                                                     encoding=sys.getdefaultencoding(),
                                                     text=True).rstrip()

            self._docker_compose_cmd = ['docker', 'compose']
            self._docker_compose_version = self._parse_docker_compose_version(version_string)
            return
        except subprocess.CalledProcessError:
            pass

        # Fall back to Docker Compose V1.
        try:
            cmd = [
                'docker-compose',
                '--version',
            ]
            version_string = subprocess.check_output(cmd,
                                                     cwd=self._project_directory,
                                                     stdin=subprocess.DEVNULL,
                                                     stderr=subprocess.STDOUT,
                                                     encoding=sys.getdefaultencoding(),
                                                     text=True).rstrip()
            self._docker_compose_cmd = ['docker-compose']
            self._docker_compose_version = self._parse_docker_compose_version(version_string)
        except subprocess.CalledProcessError as e:
            raise AssertionError('[Docker Compose Library] Unable to find Docker Compose on path') from e

    @staticmethod
    def _parse_docker_compose_version(version_string: str) -> packaging.version.Version:
        """Helper function to parse Docker Compose version string"""
        try:
            version_string = re.findall(r'(\d+\.(?:\d+\.)*\d+)', version_string)[0]
            return packaging.version.Version(version_string)
        except packaging.version.InvalidVersion as e:
            raise AssertionError('[Docker Compose Library] Could not parse docker-compose version') from e

    @staticmethod
    def _is_inside_container() -> bool:
        """Helper function to check whether the test is running inside a Docker container."""
        return os.path.exists('/.dockerenv')

    def _get_container_gateway_ip(self) -> str:
        """Helper function to retrieve current Docker container gateway ip address."""
        cmd = [
            'docker',
            'inspect',
            '-f',
            '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}',
            DockerComposeLibrary._get_container_id()
        ]
        output = subprocess.check_output(cmd,
                                         cwd=self._project_directory,
                                         stdin=subprocess.DEVNULL,
                                         stderr=subprocess.STDOUT,
                                         encoding=sys.getdefaultencoding(),
                                         text=True)
        return output.rstrip()

    @staticmethod
    def _get_container_id() -> str:
        """Helper function to retrieve current Docker container id."""
        with open('/proc/self/mountinfo', 'r', encoding=sys.getdefaultencoding()) as file:
            for line in iter(file.readline, b''):
                if '/docker/containers/' not in line:
                    continue
                return line.split('/docker/containers/')[-1].split('/')[0]
            raise AssertionError('[Docker Compose Library] Failed to obtain container id')

    @staticmethod
    def _do_nothing(*args):
        pass
