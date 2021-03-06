import aioredis
import pytest

from fastapi_cache.backends.redis import RedisCacheBackend


TEST_KEY = 'constant'
TEST_VALUE = '0'


@pytest.fixture
def f_backend() -> RedisCacheBackend:
    return RedisCacheBackend(
        'redis://localhost'
    )


@pytest.mark.asyncio
async def test_should_add_n_get_data(
    f_backend: RedisCacheBackend
) -> None:
    is_added = await f_backend.add(TEST_KEY, TEST_VALUE)

    assert is_added is True
    assert await f_backend.get(TEST_KEY) == TEST_VALUE


@pytest.mark.asyncio
async def test_should_add_n_get_data_no_encoding(
    f_backend: RedisCacheBackend
) -> None:
    NO_ENCODING_KEY = 'bytes'
    NO_ENCODING_VALUE = b'test'
    is_added = await f_backend.add(NO_ENCODING_KEY, NO_ENCODING_VALUE)

    assert is_added is True
    assert await f_backend.get(NO_ENCODING_KEY, encoding=None) == bytes(NO_ENCODING_VALUE)


@pytest.mark.asyncio
async def test_add_should_return_false_if_key_exists(
    f_backend: RedisCacheBackend
) -> None:
    await f_backend.add(TEST_KEY, TEST_VALUE)
    is_added = await f_backend.add(TEST_KEY, TEST_VALUE)

    assert is_added is False


@pytest.mark.asyncio
async def test_should_return_default_if_key_not_exists(
    f_backend: RedisCacheBackend
) -> None:
    default = '3.14159'
    fetched_value = await f_backend.get('not_exists', default)

    assert fetched_value == default

@pytest.mark.asyncio
async def test_exists_check_if_key_exsists(
    f_backend: RedisCacheBackend
) -> None:
    await f_backend.add(TEST_KEY, TEST_VALUE)
    is_there = await f_backend.exists(TEST_KEY)

    assert is_there is 1

@pytest.mark.asyncio
async def test_exists_check_if_one_out_of_two_keys_exsists(
    f_backend: RedisCacheBackend
) -> None:
    SECOND_TEST_KEY = "foobar"
    await f_backend.add(TEST_KEY, TEST_VALUE)
    is_there = await f_backend.exists(TEST_KEY, SECOND_TEST_KEY)

    assert is_there is 1

@pytest.mark.asyncio
async def test_exists_check_if_two_keys_exsists(
    f_backend: RedisCacheBackend
) -> None:
    SECOND_TEST_KEY = "foobar"
    await f_backend.add(TEST_KEY, TEST_VALUE)
    await f_backend.add(SECOND_TEST_KEY, TEST_VALUE)
    is_there = await f_backend.exists(TEST_KEY, SECOND_TEST_KEY)

    assert is_there is 2

@pytest.mark.asyncio
async def test_set_should_rewrite_value(
    f_backend: RedisCacheBackend
) -> None:
    eulers_number = '2.71828'

    await f_backend.add(TEST_KEY, TEST_VALUE)
    await f_backend.set(TEST_KEY, eulers_number)

    fetched_value = await f_backend.get(TEST_KEY)

    assert fetched_value == eulers_number


@pytest.mark.asyncio
async def test_delete_should_remove_from_cache(
    f_backend: RedisCacheBackend
) -> None:
    await f_backend.add(TEST_KEY, TEST_VALUE)
    await f_backend.delete(TEST_KEY)

    fetched_value = await f_backend.get(TEST_KEY)

    assert fetched_value is None


@pytest.mark.asyncio
async def test_exists_check_if_key_not_exsists(
    f_backend: RedisCacheBackend
) -> None:
    is_there = await f_backend.exists(TEST_KEY)

    assert is_there is 0

@pytest.mark.asyncio
async def test_flush_should_remove_all_objects_from_cache(
    f_backend: RedisCacheBackend
) -> None:
    await f_backend.add('pi', '3.14159')
    await f_backend.add('golden_ratio', '1.61803')

    await f_backend.flush()

    assert await f_backend.get('pi') is None
    assert await f_backend.get('golden_ratio') is None


@pytest.mark.asyncio
async def test_close_should_close_connection(
    f_backend: RedisCacheBackend
) -> None:
    await f_backend.close()
    with pytest.raises(aioredis.errors.PoolClosedError):
        await f_backend.add(TEST_KEY, TEST_VALUE)
