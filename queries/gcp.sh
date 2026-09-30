#!/usr/bin/env bash
# Read-only display export. The adapter expects JSON API shape, so validate field mapping.
set -euo pipefail
: "${ASSURANCE_PROJECT:?Set the approved project ID}"
: "${ASSURANCE_BUCKET:?Set the approved bucket name}"
mkdir -p private-evidence/gcp
gcloud projects describe "$ASSURANCE_PROJECT" --format=json > private-evidence/gcp/context.json
gcloud storage buckets describe "gs://$ASSURANCE_BUCKET" --project="$ASSURANCE_PROJECT" --format=json > private-evidence/gcp/storage-display.json
# Bucket names are global. Independently verify the bucket's owning project number.
# Do not treat --project alone as proof the bucket belongs to that project.
