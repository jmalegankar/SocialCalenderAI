import unstructured_client
from unstructured_client.models import operations, shared
from unstructured.ingest.connector.local import SimpleLocalConfig
from unstructured.ingest.connector.mongodb import SimpleMongoDBConfig
from unstructured.ingest.interfaces import (
    ChunkingConfig,
    EmbeddingConfig,
    PartitionConfig,
    ProcessorConfig,
    ReadConfig,
    WriteConfig,
)
from unstructured.ingest.runner import LocalRunner
from unstructured.ingest.runner.writers.base_writer import Writer
from unstructured.ingest.runner.writers.mongodb import (
    MongodbWriter,
)
from dotenv import dotenv_values

config = dotenv_values(".env")

def get_writer() -> Writer:
    return MongodbWriter(
        connector_config=SimpleMongoDBConfig(
            uri=config["MONGODB_URI"],
            database=config["MONGODB_DATABASE_NAME"],
            collection=config["DESTINATION_MONGO_COLLECTION"],
        ),
        write_config=WriteConfig(),
    )


if __name__ == "__main__":
    writer = get_writer()
    runner = LocalRunner(
        processor_config=ProcessorConfig(
            verbose=True,
            output_dir="local-output-to-mongodb",
            num_processes=2,
        ),
        connector_config=SimpleLocalConfig(
            input_path="example-docs/book-war-and-peace-1225p.txt",
        ),
        read_config=ReadConfig(),
        partition_config=PartitionConfig(),
        chunking_config=ChunkingConfig(chunk_elements=True),
        embedding_config=EmbeddingConfig(
            provider="langchain-huggingface",
        ),
        writer=writer,
        writer_kwargs={},
    )
    runner.run()
