## Base model serving

This directory contains files used to build the base container for the model server

gcloud container builds submit --config cloudbuild-model-base-x86_64.yaml .
gcloud container builds submit --timeout 3h --config cloudbuild-model-base-armv7l.yaml .
