"""Tests for the async job store."""

import asyncio

import pytest

from contract_analyzer.orchestrator.queue import Job, JobStore, job_store


class TestJob:
    def test_job_creation(self):
        job = Job(job_id="j1", contract_name="Test Contract")
        assert job.job_id == "j1"
        assert job.contract_name == "Test Contract"
        assert job.status == "pending"
        assert job.created_at
        assert job.started_at is None
        assert job.completed_at is None
        assert job.result is None
        assert job.error is None

    def test_job_with_callback(self):
        job = Job(
            job_id="j2",
            contract_name="Test",
            status_callback_url="http://localhost/callback",
        )
        assert job.status_callback_url == "http://localhost/callback"


class TestJobStore:
    @pytest.fixture
    def store(self):
        return JobStore()

    @pytest.mark.asyncio
    async def test_create_job(self, store):
        job = await store.create("j1", "Test Contract")
        assert job.job_id == "j1"
        assert job.status == "pending"

    @pytest.mark.asyncio
    async def test_get_job(self, store):
        await store.create("j1", "Test")
        job = await store.get("j1")
        assert job is not None
        assert job.job_id == "j1"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, store):
        job = await store.get("nonexistent")
        assert job is None

    @pytest.mark.asyncio
    async def test_update_status(self, store):
        await store.create("j1", "Test")
        await store.update_status("j1", "running")
        job = await store.get("j1")
        assert job.status == "running"
        assert job.started_at is not None

    @pytest.mark.asyncio
    async def test_update_status_to_completed(self, store):
        await store.create("j1", "Test")
        await store.update_status("j1", "completed")
        job = await store.get("j1")
        assert job.status == "completed"
        assert job.completed_at is not None

    @pytest.mark.asyncio
    async def test_update_status_with_error(self, store):
        await store.create("j1", "Test")
        await store.update_status("j1", "failed", error="Something went wrong")
        job = await store.get("j1")
        assert job.status == "failed"
        assert job.error == "Something went wrong"

    @pytest.mark.asyncio
    async def test_set_result(self, store):
        await store.create("j1", "Test")
        result = {"analysis_id": "a1", "findings": []}
        await store.set_result("j1", result)
        job = await store.get("j1")
        assert job.status == "completed"
        assert job.result == result
        assert job.completed_at is not None

    @pytest.mark.asyncio
    async def test_set_error(self, store):
        await store.create("j1", "Test")
        await store.set_error("j1", "Connection refused")
        job = await store.get("j1")
        assert job.status == "failed"
        assert job.error == "Connection refused"
        assert job.completed_at is not None

    @pytest.mark.asyncio
    async def test_list_jobs(self, store):
        await store.create("j1", "Contract A")
        await store.create("j2", "Contract B")
        await store.create("j3", "Contract C")

        jobs = await store.list_jobs()
        assert len(jobs) == 3
        # Most recent first
        assert jobs[0]["job_id"] == "j3"

    @pytest.mark.asyncio
    async def test_list_jobs_pagination(self, store):
        for i in range(10):
            await store.create(f"j{i}", f"Contract {i}")

        jobs = await store.list_jobs(limit=3, offset=2)
        assert len(jobs) == 3

    @pytest.mark.asyncio
    async def test_list_jobs_status_filter(self, store):
        await store.create("j1", "A")
        await store.create("j2", "B")
        await store.update_status("j2", "completed")

        pending = await store.list_jobs(status="pending")
        assert len(pending) == 1
        assert pending[0]["job_id"] == "j1"

        completed = await store.list_jobs(status="completed")
        assert len(completed) == 1
        assert completed[0]["job_id"] == "j2"

    @pytest.mark.asyncio
    async def test_delete_job(self, store):
        await store.create("j1", "Test")
        assert await store.delete("j1") is True
        assert await store.get("j1") is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, store):
        assert await store.delete("nonexistent") is False

    @pytest.mark.asyncio
    async def test_concurrent_access(self, store):
        """Verify the store handles concurrent access without errors."""
        async def create_and_update(i: int):
            await store.create(f"j{i}", f"Contract {i}")
            await store.update_status(f"j{i}", "running")

        tasks = [create_and_update(i) for i in range(10)]
        await asyncio.gather(*tasks)

        jobs = await store.list_jobs(limit=20)
        assert len(jobs) == 10
        for j in jobs:
            assert j["status"] == "running"


class TestGlobalJobStore:
    """Tests against the module-level singleton."""
    @pytest.mark.asyncio
    async def test_singleton_works(self):
        await job_store.create("global-test", "Global Contract")
        job = await job_store.get("global-test")
        assert job is not None
        assert job.contract_name == "Global Contract"
        await job_store.delete("global-test")
