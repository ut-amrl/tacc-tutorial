#!/bin/bash
docker tag flow_matching_train $DOCKER_USER/flow_matching_train:latest
docker push $DOCKER_USER/flow_matching_train:latest