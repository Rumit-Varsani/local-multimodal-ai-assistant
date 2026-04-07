from backend.agents.autonomy_agent import AutonomyAgent
from backend.services.benchmark_service import BenchmarkService
from backend.services.checkpoint_registry_service import CheckpointRegistryService
from backend.services.critic_service import CriticService
from backend.services.dataset_builder_service import DatasetBuilderService
from backend.services.interaction_log_service import InteractionLogService
from backend.services.model_registry_service import ModelRegistryService
from backend.services.task_queue_service import TaskQueueService
from backend.services.teacher_service import TeacherService
from backend.services.training_service import TrainingService

task_queue = TaskQueueService()
teacher_service = TeacherService()
critic_service = CriticService()
dataset_builder = DatasetBuilderService(
    teacher_service=teacher_service,
    critic_service=critic_service,
)
model_registry = ModelRegistryService()
training_service = TrainingService()
benchmark_service = BenchmarkService()
checkpoint_registry = CheckpointRegistryService()
interaction_log = InteractionLogService()

autonomy_agent = AutonomyAgent(
    task_queue=task_queue,
    dataset_builder=dataset_builder,
    model_registry=model_registry,
    training_service=training_service,
    benchmark_service=benchmark_service,
    checkpoint_registry=checkpoint_registry,
    interaction_log=interaction_log,
)
