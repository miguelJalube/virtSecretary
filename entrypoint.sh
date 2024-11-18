#! bin/bash

# Start ollama in the background
/bin/ollama serve &

# Record pid
pid=$!

# Wait for ollama to start
sleep 5

# Start the application
echo "Retrieving model"
ollama run $MODEL
echo "Done"

# Wait for the application to finish
wait $pid