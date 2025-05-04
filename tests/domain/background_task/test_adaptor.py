import inspect
import pytest
from unittest.mock import AsyncMock, patch

from src.domain.background_task.adaptor import (
    BackgroundTask,
    BackgroundTaskProcessor,
    get_background_task_implementations
)


# Test task fixtures
@pytest.fixture
def concrete_task_class():
    class ConcreteTask(BackgroundTask):
        task_name = "concrete_task"

        data: str

        async def logic(self):
            return f"Processed {self.data}"

    return ConcreteTask


@pytest.fixture
def disabled_task_class():
    class DisabledTask(BackgroundTask):
        task_name = "disabled_task"
        enabled = False

        number: int

        async def logic(self):
            return self.number * 2

    return DisabledTask


@pytest.fixture
def abstract_task_class():
    class AbstractTestTask(BackgroundTask):
        task_name = "abstract_task"
        # Does not implement logic method

    return AbstractTestTask


@pytest.fixture
def mock_task_processor():
    class MockProcessor(BackgroundTaskProcessor):
        def __init__(self):
            super().__init__()
            self.registered_tasks = []

        async def register_tasks(self, tasks):
            self.registered_tasks.extend(tasks)

        async def execute_task(self, task):
            return "mock-task-id-123"

    return MockProcessor


@pytest.fixture
def complex_task_processor():
    class ComplexProcessor(BackgroundTaskProcessor):
        """A more complex implementation that tracks task execution."""

        def __init__(self):
            super().__init__()
            self.tasks_by_name = {}
            self.execution_history = []

        async def register_tasks(self, tasks):
            for task_cls in tasks:
                if task_cls.enabled:
                    self.tasks_by_name[task_cls.task_name] = task_cls

        async def execute_task(self, task):
            self.execution_history.append(task)
            task_id = f"task-{len(self.execution_history)}"
            return task_id

    return ComplexProcessor


def test_abstract_method_enforcement(abstract_task_class):
    """Test that BackgroundTask requires logic method implementation."""
    with pytest.raises(TypeError):
        # Instantiate to trigger the error - logic is not implemented
        abstract_task_class()


@pytest.mark.asyncio
async def test_task_implementation(concrete_task_class):
    """Test a proper implementation of a background task."""
    task = concrete_task_class(data="test data")

    # Test properties
    assert task.task_name == "concrete_task"
    assert task.enabled is True
    assert task.data == "test data"

    # Test logic method
    result = await task.logic()
    assert result == "Processed test data"


def test_task_with_disabled_flag(disabled_task_class):
    """Test a task with enabled=False flag."""
    task = disabled_task_class(number=5)
    assert task.enabled is False
    assert task.task_name == "disabled_task"


@patch('src.domain.background_task.adaptor.BackgroundTask.__subclasses__')
def test_get_concrete_subclasses(mock_subclasses, concrete_task_class,
                                 disabled_task_class, abstract_task_class):
    """Test that only concrete subclasses are returned."""
    mock_subclasses.return_value = [
        concrete_task_class,
        disabled_task_class,
        abstract_task_class
    ]

    results = get_background_task_implementations()

    # Should include concrete classes but not abstract ones
    assert concrete_task_class in results
    assert disabled_task_class in results
    assert abstract_task_class not in results
    assert len(results) == 2


def test_integration_with_real_subclasses(concrete_task_class):
    """Integration test using actual subclasses."""
    results = get_background_task_implementations()

    # All results should be concrete classes
    for cls in results:
        assert issubclass(cls, BackgroundTask)
        assert not inspect.isabstract(cls)


@pytest.mark.asyncio
async def test_create_factory_method(mock_task_processor, concrete_task_class):
    """Test the factory method creates and initializes the processor."""
    tasks = [concrete_task_class]
    processor = await mock_task_processor.create(tasks)

    assert isinstance(processor, mock_task_processor)
    assert processor.registered_tasks == tasks


@patch('src.domain.background_task.adaptor.get_background_task_implementations')
def test_get_background_tasks(mock_get, concrete_task_class, disabled_task_class):
    """Test the static method to get tasks."""
    mock_get.return_value = [concrete_task_class, disabled_task_class]

    result = BackgroundTaskProcessor.get_get_background_tasks()

    assert result == [concrete_task_class, disabled_task_class]
    mock_get.assert_called_once()


def test_abstract_methods():
    """Test that abstract methods are properly defined."""
    # register_tasks and execute_task should be abstract methods
    assert inspect.isabstract(BackgroundTaskProcessor)

    abstract_methods = {
        name for name, method in inspect.getmembers(BackgroundTaskProcessor)
        if getattr(method, "__isabstractmethod__", False)
    }

    assert "register_tasks" in abstract_methods
    assert "execute_task" in abstract_methods


@pytest.mark.asyncio
async def test_execute_task(mock_task_processor, concrete_task_class):
    """Test executing a task through the processor."""
    processor = await mock_task_processor.create([concrete_task_class])
    task = concrete_task_class(data="execution test")

    task_id = await processor.execute_task(task)

    assert task_id == "mock-task-id-123"


@pytest.mark.asyncio
async def test_task_registration(mock_task_processor, concrete_task_class, disabled_task_class):
    """Test task registration process."""
    processor = mock_task_processor()
    tasks = [concrete_task_class, disabled_task_class]

    await processor.register_tasks(tasks)

    assert processor.registered_tasks == tasks


@pytest.mark.asyncio
async def test_complex_processor_initialization(complex_task_processor,
                                                concrete_task_class, disabled_task_class):
    """Test initializing a complex processor with task registration."""
    processor = await complex_task_processor.create([
        concrete_task_class,  # enabled
        disabled_task_class  # disabled
    ])

    # Only enabled tasks should be registered
    assert len(processor.tasks_by_name) == 1
    assert "concrete_task" in processor.tasks_by_name
    assert "disabled_task" not in processor.tasks_by_name


@pytest.mark.asyncio
async def test_complex_processor_task_execution(complex_task_processor, concrete_task_class):
    """Test task execution with the complex processor."""
    processor = await complex_task_processor.create([concrete_task_class])

    # Execute two tasks
    task1 = concrete_task_class(data="first")
    task2 = concrete_task_class(data="second")

    id1 = await processor.execute_task(task1)
    id2 = await processor.execute_task(task2)

    # Check execution history and IDs
    assert id1 == "task-1"
    assert id2 == "task-2"
    assert processor.execution_history == [task1, task2]


@pytest.mark.parametrize("task_data,expected_result", [
    ("simple data", "Processed simple data"),
    ("", "Processed "),
    ("123", "Processed 123"),
])
@pytest.mark.asyncio
async def test_task_logic_with_different_inputs(concrete_task_class, task_data, expected_result):
    """Test task logic with different inputs using parametrize."""
    task = concrete_task_class(data=task_data)
    result = await task.logic()
    assert result == expected_result


@pytest.mark.asyncio
async def test_execute_task_returns_id(mock_task_processor):
    """Test that execute_task always returns a task ID string."""
    processor = mock_task_processor()

    # Create a mock task for testing
    mock_task = AsyncMock(spec=BackgroundTask)
    mock_task.task_name = "mock_task"

    task_id = await processor.execute_task(mock_task)

    assert isinstance(task_id, str)
    assert task_id == "mock-task-id-123"


@pytest.mark.asyncio
async def test_task_registration_empty_list(mock_task_processor):
    """Test registering an empty list of tasks."""
    processor = mock_task_processor()
    await processor.register_tasks([])
    assert processor.registered_tasks == []


@pytest.mark.asyncio
async def test_processor_initialization(mock_task_processor):
    """Test that the processor can be initialized."""
    processor = mock_task_processor()
    assert processor.registered_tasks == []
    assert isinstance(processor, BackgroundTaskProcessor)


@pytest.mark.asyncio
async def test_task_with_additional_fields(concrete_task_class):
    """Test a task with additional fields beyond the minimum requirements."""
    task = concrete_task_class(data="test", extra_field="should be ignored")
    result = await task.logic()
    assert result == "Processed test"


def test_background_task_model_validation():
    """Test that BackgroundTask validates fields as a Pydantic model."""

    class ValidationTask(BackgroundTask):
        task_name = "validation_task"

        required_field: str
        optional_field: int = 0

        async def logic(self):
            return self.required_field

    # Should work with required field
    task = ValidationTask(required_field="test")
    assert task.required_field == "test"
    assert task.optional_field == 0

    # Should fail without required field
    with pytest.raises(ValueError):
        ValidationTask()
