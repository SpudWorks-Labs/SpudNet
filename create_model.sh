set -e

MODEL_NAME="SpudNet-Vocal"
MODEL_FILE="Modelfile"

echo "Removing old model..."
if ollama rm "$MODEL_NAME" 2>/dev/null; then
  echo "Old model removed."
else
  echo "No previous model found or failed to remove. Continuing..."
fi

echo "Adding new model..."
if ollama create "$MODEL_NAME" -f "$MODEL_FILE"; then
  echo "Model created successfully!"
else
  echo "Failed to create the model." >&2
  exit 1
fi
