import asyncio
import json
from unittest.mock import Mock, mock_open, patch

import pytest

from r2r import DocumentType, R2RConfig


@pytest.fixture(scope="session", autouse=True)
def event_loop_policy():
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())


@pytest.fixture(scope="function", autouse=True)
async def cleanup_tasks():
    yield
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)


@pytest.fixture(autouse=True)
async def manage_async_pipes():
    async_pipes = []
    yield async_pipes
    for pipe in async_pipes:
        await pipe.shutdown()


@pytest.fixture
def mock_bad_file():
    mock_data = json.dumps({})
    with patch("builtins.open", mock_open(read_data=mock_data)) as m:
        yield m


@pytest.fixture
def mock_file():
    mock_data = json.dumps(
        {
            "auth": {
                "provider": "r2r",
                "enabled": True,
                "token_lifetime": 86400,
            },
            "crypto": {"provider": "r2r"},
            "embedding": {
                "provider": "example_provider",
                "base_model": "model",
                "base_dimension": 128,
                "batch_size": 16,
                "text_splitter": "default",
                "add_title_as_prefix": False,
            },
            "kg": {
                "provider": "None",
                "batch_size": 1,
                "text_splitter": {
                    "type": "recursive_character",
                    "chunk_size": 2048,
                    "chunk_overlap": 0,
                },
            },
            "eval": {"llm": {"provider": "local"}},
            "ingestion": {"excluded_parsers": {}},
            "completions": {"provider": "lm_provider"},
            "logging": {
                "provider": "local",
                "log_table": "logs",
                "log_info_table": "log_info",
            },
            "prompt": {"provider": "prompt_provider"},
            "database": {"provider": "vector_db"},
        }
    )
    with patch("builtins.open", mock_open(read_data=mock_data)) as m:
        yield m


@pytest.mark.asyncio
async def test_r2r_config_loading_required_keys(mock_bad_file):
    with pytest.raises(KeyError):
        R2RConfig.from_json("r2r.json")


@pytest.mark.asyncio
async def test_r2r_config_loading(mock_file):
    try:
        config = R2RConfig.from_json("r2r.json")
        assert (
            config.embedding.provider == "example_provider"
        ), "Provider should match the mock data"
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")


@pytest.fixture
def mock_redis_client():
    return Mock()


def test_r2r_config_serialization(mock_file, mock_redis_client):
    config = R2RConfig.from_json("r2r.json")
    config.save_to_redis(mock_redis_client, "test_key")
    mock_redis_client.set.assert_called_once()
    saved_data = json.loads(mock_redis_client.set.call_args[0][1])
    assert saved_data["embedding"]["provider"] == "example_provider"


def test_r2r_config_deserialization(mock_file, mock_redis_client):
    config_data = {
        "embedding": {
            "provider": "example_provider",
            "base_model": "model",
            "base_dimension": 128,
            "batch_size": 16,
            "text_splitter": "default",
        },
        "kg": {
            "provider": "None",
            "batch_size": 1,
            "text_splitter": {
                "type": "recursive_character",
                "chunk_size": 2048,
                "chunk_overlap": 0,
            },
        },
        "eval": {"llm": {"provider": "local"}},
        "ingestion": {"excluded_parsers": ["pdf"]},
        "completions": {"provider": "lm_provider"},
        "logging": {
            "provider": "local",
            "log_table": "logs",
            "log_info_table": "log_info",
        },
        "prompt": {"provider": "prompt_provider"},
        "database": {"provider": "vector_db"},
    }
    mock_redis_client.get.return_value = json.dumps(config_data)
    config = R2RConfig.load_from_redis(mock_redis_client, "test_key")
    assert DocumentType.PDF in config.ingestion["excluded_parsers"]


def test_r2r_config_missing_section():
    invalid_data = {
        "embedding": {
            "provider": "example_provider",
            "base_model": "model",
            "base_dimension": 128,
            "batch_size": 16,
            "text_splitter": "default",
        }
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(invalid_data))):
        with pytest.raises(KeyError):
            R2RConfig.from_json("r2r.json")


def test_r2r_config_missing_required_key():
    invalid_data = {
        "app": {"max_file_size_in_mb": 128},
        "embedding": {
            "base_model": "model",
            "base_dimension": 128,
            "batch_size": 16,
            "text_splitter": "default",
        },
        "kg": {
            "provider": "None",
            "batch_size": 1,
            "text_splitter": {
                "type": "recursive_character",
                "chunk_size": 2048,
                "chunk_overlap": 0,
            },
        },
        "completions": {"provider": "lm_provider"},
        "logging": {
            "provider": "local",
            "log_table": "logs",
            "log_info_table": "log_info",
        },
        "prompt": {"provider": "prompt_provider"},
        "database": {"provider": "vector_db"},
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(invalid_data))):
        with pytest.raises(KeyError):
            R2RConfig.from_json("r2r.json")
