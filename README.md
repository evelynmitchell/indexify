# Indexify

Indexify is a knowledge/context retreival service, and provides APIs to generate embeddings from various pre-trained models and manage and query indexes on vector databases,
implement various SOTA retrieval algorithms.

Currently for production use-case, the embedding generation APIs are stable, while the other features are coming along.

## Why Use Indexify
1. Efficient execution of embedding models outside of applications in a standalone service.
2. REST APIs to access all the models and indexes from any application runtime.
4. Does not require distribution of embedding models with applications, reduces size of application bundle.

## Getting Started

### Start the Service
```
docker run -e OPENAI_API_KEY -p 0.0.0.0:8900:8900/tcp -it diptanu/indexify
```

### Query Embeddings 
```
 curl -v -X GET http://localhost:8900/embeddings/generate   -H "Content-Type: application/json" -d '{"inputs": ["lol", "world"], "model": "t5-base"}'
```

### Custom Configuration
Creating a custom configuration is easy by tweaking the default configuration -
```
docker run -v "$(pwd)":/indexify/config/ diptanu/indexify init-config ./config/custom_config.yaml
```
This will create the default configuration in the current directory in `custom_config.yaml`.
Make changes to it and mount it on the container and use it.
```
docker run -v "$(pwd)/custom_config.yaml:/indexify/config/custom_config.yaml" diptanu/indexify start -c ./config/custom_config.yaml
```

## API Reference

### List Embedding Models
Provides a list of embedding models available and their dimensions.

```
/embeddings/models
```
### Generate Embeddings
Generate embeddings for a collection of strings

```
/embeddings/generate
```
Example: Generate embeddings from t5-base
```
 curl -v -X GET http://localhost:8900/embeddings/generate   -H "Content-Type: application/json" -d '{"inputs": ["lol", "world"], "model": "t5-base"}'
```

## List of Embedding Models
* OpenAI
   * text-embedding-ada02
* Sentence Transformers
   * All-MiniLM-L12-V2
   * All-MiniLM-L6-V2
   * T5-Base

*More models are on the way. Contributions are welcome!* 

## Server Configuration Reference
Configure the behavior of the server and models through a YAML configuration scheme.
1. `listen_addr` - The adrress and port on which the server is listening.
2. `available_models` - A list of models the server is serving.
    *  `model` -  Name of the model. Default Models: `openai(text-embedding-ada002)`, `all-minilm-l12-v2`.
    *  `device` - Device on which the model is running. Default: `cpu`
3. `openai` - OpenAI configuration options.
    * `api_key` - The api key to use with openai. This is not set by default. We use OPENAI_API_KEY by default but use this when it's set.

### Default Configuration
```
# Address on which the server listens
listen_addr: 0.0.0.0:8900

# List of available models via the api. The name corresponds to a model
# that the service knows how to load, and the device is where the model
# is executed.
available_models:
- model: all-mpnet-base-v2
  device: cpu
- model: text-embedding-ada-002
  device: remote

# OpenAI key. Either set it here or set via the OPENAI_API_KEY
# environment variable
openai:
  api_key: xxxx
```

## Operational Metrics
Indexify exposes operational metrics of the server on a prometheous endpoint at `/metrics`

## Building indexify
```
docker build -t diptanu/indexify:latest .
```

## Coming Soon
* Text splitting and chunking strategies for generating embeddings for longer sentences.
* Suppport for hardware acceleration, and using ONNX runtime for faster execution on CPUs.
* Retrieval strategies for dense embeddings, and a plugin mechanism to add new strategies.
* Resource Usage of Embedding Models.
* Asynchronous Embedding Generation for large corpuses of documents.
* Real Time Index updates

## Contact 
Join the Discord Server - https://discord.gg/mrXrq3DmV8 <br />
Email - diptanuc@gmail.com