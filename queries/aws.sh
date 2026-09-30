#!/usr/bin/env bash
# Read-only examples. Run in an authorized sandbox. Never publish the output.
set -euo pipefail
: "${ASSURANCE_BUCKET:?Set ASSURANCE_BUCKET to an approved bucket}"
: "${ASSURANCE_ACCOUNT:?Set ASSURANCE_ACCOUNT to its expected 12-digit owner}"
mkdir -p private-evidence/aws
aws sts get-caller-identity --output json > private-evidence/aws/identity.json
aws s3api get-public-access-block --bucket "$ASSURANCE_BUCKET" --expected-bucket-owner "$ASSURANCE_ACCOUNT" --output json > private-evidence/aws/public-access.json
aws s3api get-bucket-encryption --bucket "$ASSURANCE_BUCKET" --expected-bucket-owner "$ASSURANCE_ACCOUNT" --output json > private-evidence/aws/encryption.json
aws s3api get-bucket-versioning --bucket "$ASSURANCE_BUCKET" --expected-bucket-owner "$ASSURANCE_ACCOUNT" --output json > private-evidence/aws/versioning.json
# Failure exits the script. Empty/partial files are not a successful evidence run.
# This is a single-resource query example, not a complete organization collector.
