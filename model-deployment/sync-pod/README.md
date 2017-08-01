This is to build a container for using gcloud commands on an arm architecture
device.

From this directory:

	gcloud container builds submit . --config=cloudbuild-x86_64.yaml
	gcloud container builds submit . --config=cloudbuild-armv7l.yaml


