# Install additional models
#!/bin/bash

set -e

MODELS=(
    "llama3.1:8b:Meta Llama 3.1 8B - Balanced performance"
    "llama3.1:70b:Meta Llama 3.1 70B - Highest quality"
    "codellama:7b:Code Llama 7B - Programming tasks"
    "mistral:7b:Mistral 7B - Fast and efficient"
    "phi3:mini:Microsoft Phi-3 Mini - Compact"
    "gemma:7b:Google Gemma 7B - Versatile"
    "qwen2:7b:Qwen2 7B - Multilingual"
)

echo "🤖 Available Models for Installation"
echo "===================================="

for i in "${!MODELS[@]}"; do
    IFS=':' read -r model_name model_desc <<< "${MODELS[$i]}"
    echo "  $((i+1)). $model_name - $model_desc"
done

echo ""
read -p "Enter model number to install (or 'all' for all models): " choice

install_model() {
    local model_name=$1
    echo "📥 Installing $model_name..."
    if docker-compose exec -T ollama ollama pull "$model_name"; then
        echo "✅ $model_name installed successfully"
    else
        echo "❌ Failed to install $model_name"
    fi
}

if [ "$choice" = "all" ]; then
    for model_info in "${MODELS[@]}"; do
        model_name=$(echo "$model_info" | cut -d':' -f1-2)
        install_model "$model_name"
    done
elif [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#MODELS[@]}" ]; then
    model_info="${MODELS[$((choice-1))]}"
    model_name=$(echo "$model_info" | cut -d':' -f1-2)
    install_model "$model_name"
else
    echo "❌ Invalid selection"
    exit 1
fi

echo ""
echo "📋 Currently installed models:"
docker-compose exec -T ollama ollama list