#!/usr/bin/env bash


set +e


ROBOT_USER_NAME="${ROBOT_USER_NAME:-robot}"
ROBOT_USER_ID="${ROBOT_USER_ID:-1000}"
ROBOT_GROUP_NAME="${ROBOT_GROUP_NAME:-robot}"
ROBOT_GROUP_ID="${ROBOT_GROUP_ID:-1000}"

DOCKER_GROUP_NAME="${DOCKER_GROUP_NAME:-docker}"
DOCKER_HOST="${DOCKER_HOST:-/var/run/docker.sock}"


setup_robot_user() {
    if [[ "${ROBOT_GROUP_ID}" -ne 0 ]]; then
        getent group "${ROBOT_GROUP_NAME}" &>/dev/null
        if [[ $? -ne 0 ]]; then
            echo "Creating robot group: ${ROBOT_GROUP_NAME}"
            groupadd --gid "${ROBOT_GROUP_ID}" "${ROBOT_GROUP_NAME}" \
            || { echo "Failed to create robot user: ${ROBOT_USER_NAME}"; exit 1; }
        else
            echo "Robot group already exists: ${ROBOT_GROUP_NAME}"
        fi
    else
        ROBOT_GROUP_NAME="root"
    fi

    if [[ "${ROBOT_USER_ID}" -ne 0 ]]; then
        id -u "${ROBOT_USER_NAME}" &>/dev/null
        if [[ $? -ne 0 ]]; then
            echo "Creating robot user: ${ROBOT_USER_NAME}"
            useradd --create-home --shell /bin/bash \
                --uid "${ROBOT_USER_ID}" \
                --gid "${ROBOT_GROUP_NAME}" "${ROBOT_USER_NAME}" \
            || { echo "Failed to create robot user: ${ROBOT_USER_NAME}"; exit 1; }
        fi
    else
        ROBOT_USER_NAME="root"
    fi

    groups "${ROBOT_USER_NAME}" | grep "\\b${DOCKER_GROUP_NAME}\\b" &>/dev/null
    if [[ $? -ne 0 ]]; then
        echo "Adding robot user to group: ${DOCKER_GROUP_NAME}"
        usermod -a -G "${DOCKER_GROUP_NAME}" "${ROBOT_USER_NAME}"
    fi
}

setup_docker() {
    if [[ ! -S "${DOCKER_HOST}" ]]; then
        echo "Docker socket file does not exist or is not a socket: ${DOCKER_HOST}"
        ls -la "${DOCKER_HOST}"
        exit 1
    fi

    STAT=( $(stat -Lc "%g" "${DOCKER_HOST}") )
    groupmod -g "${STAT[0]}" "${DOCKER_GROUP_NAME}"
}


setup_robot_user
setup_docker


su "${ROBOT_USER_NAME}" -c "$*"
