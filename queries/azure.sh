#!/usr/bin/env bash
# Read-only management-plane example. Directory and data-plane evidence are separate.
set -euo pipefail
: "${ASSURANCE_SUBSCRIPTION:?Set the approved subscription ID}"
: "${ASSURANCE_RESOURCE_GROUP:?Set the resource group}"
: "${ASSURANCE_STORAGE:?Set the storage account name}"
mkdir -p private-evidence/azure
az account show --subscription "$ASSURANCE_SUBSCRIPTION" --output json > private-evidence/azure/context.json
az storage account show --subscription "$ASSURANCE_SUBSCRIPTION" --resource-group "$ASSURANCE_RESOURCE_GROUP" --name "$ASSURANCE_STORAGE" --output json > private-evidence/azure/storage.json
# No account keys are requested. A denied read is a collection error, not a passing control.
