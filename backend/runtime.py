from backend.agents.autonomy_agent import AutonomyAgent
from backend.services.benchmark_service import BenchmarkService
from backend.services.checkpoint_registry_service import CheckpointRegistryService
from backend.services.critic_service import CriticService
from backend.services.dataset_builder_service import DatasetBuilderService
from backend.services.interaction_log_service import InteractionLogService
from backend.services.judge_service import JudgeService
from backend.services.model_manager_service import ModelManagerService
from backend.services.model_registry_service import ModelRegistryService
from backend.services.multi_model_ollama_service import MultiModelOllamaService
from backend.services.project_phase_service import ProjectPhaseService
from backend.services.router_service import RouterService
from backend.services.resource_monitor_service import ResourceMonitorService
from backend.services.sqlite_memory_service import SQLiteMemoryService
from backend.services.task_queue_service import TaskQueueService
from backend.services.teacher_service import TeacherService
from backend.services.topic_training_service import TopicTrainingService
from backend.services.training_execution_service import TrainingExecutionService
from backend.services.training_service import TrainingService

task_queue = TaskQueueService()
multi_model_service = MultiModelOllamaService()
model_manager = ModelManagerService(multi_model_service=multi_model_service)
router_service = RouterService()
sqlite_memory = SQLiteMemoryService()
resource_monitor = ResourceMonitorService()
project_phase_service = ProjectPhaseService()
teacher_service = TeacherService()
critic_service = CriticService()
judge_service = JudgeService()
dataset_builder = DatasetBuilderService(
    teacher_service=teacher_service,
    critic_service=critic_service,
)
model_registry = ModelRegistryService()
training_service = TrainingService()
training_execution_service = TrainingExecutionService()
benchmark_service = BenchmarkService()
checkpoint_registry = CheckpointRegistryService()
interaction_log = InteractionLogService()
topic_training_service = TopicTrainingService(
    model_manager=model_manager,
    multi_model_service=multi_model_service,
    sqlite_memory=sqlite_memory,
    judge_service=judge_service,
)

autonomy_agent = AutonomyAgent(
    task_queue=task_queue,
    dataset_builder=dataset_builder,
    model_registry=model_registry,
    training_service=training_service,
    benchmark_service=benchmark_service,
    checkpoint_registry=checkpoint_registry,
    interaction_log=interaction_log,
    topic_training_service=topic_training_service,
    sqlite_memory=sqlite_memory,
    training_execution_service=training_execution_service,
)
