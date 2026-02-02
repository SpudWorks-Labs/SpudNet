echo "Removing old model..."
ollama rm SpudNet-Vocal
echo "Adding new model..."
ollama create SpudNet-Vocal -f Modelfile
echo "Model created successfully!"
