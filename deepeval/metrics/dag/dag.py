from typing import Optional, Union
from deepeval.metrics import BaseMetric
from deepeval.test_case import (
    LLMTestCase,
)
from deepeval.utils import get_or_create_event_loop
from deepeval.metrics.utils import (
    check_llm_test_case_params,
    initialize_model,
)
from deepeval.models import DeepEvalBaseLLM
from deepeval.metrics.indicator import metric_progress_indicator
from deepeval.metrics.g_eval.schema import *
from deepeval.metrics.dag.graph import DeepAcyclicGraph
from deepeval.metrics.dag.utils import is_valid_dag, extract_required_params


class DAGMetric(BaseMetric):
    def __init__(
        self,
        name: str,
        dag: DeepAcyclicGraph,
        model: Optional[Union[str, DeepEvalBaseLLM]] = None,
        threshold: float = 0.5,
        async_mode: bool = True,
        strict_mode: bool = False,
        verbose_mode: bool = False,
        _include_dag_suffix: bool = True,
    ):
        if is_valid_dag(dag.root_node) == False:
            raise ValueError("Cycle detected in DAG graph.")

        self.dag = dag
        self.name = name
        self.model, self.using_native_model = initialize_model(model)
        self.evaluation_model = self.model.get_model_name()
        self.threshold = 1 if strict_mode else threshold
        self.strict_mode = strict_mode
        self.async_mode = async_mode
        self.verbose_mode = verbose_mode
        self._include_dag_suffix = _include_dag_suffix

    def measure(
        self,
        test_case: LLMTestCase,
        _show_indicator: bool = True,
    ) -> float:
        check_llm_test_case_params(
            test_case, extract_required_params(self.dag.root_node), self
        )

        self.evaluation_cost = 0 if self.using_native_model else None
        with metric_progress_indicator(self, _show_indicator=_show_indicator):
            if self.async_mode:
                loop = get_or_create_event_loop()
                loop.run_until_complete(
                    self.a_measure(test_case, _show_indicator=False)
                )
            else:
                self.dag._execute(metric=self, test_case=test_case)
                self.success = self.is_successful()
                return self.score

    async def a_measure(
        self,
        test_case: LLMTestCase,
        _show_indicator: bool = True,
    ) -> float:
        check_llm_test_case_params(
            test_case, extract_required_params(self.dag.root_node), self
        )

        self.evaluation_cost = 0 if self.using_native_model else None
        with metric_progress_indicator(
            self, async_mode=True, _show_indicator=_show_indicator
        ):
            await self.dag._a_execute(metric=self, test_case=test_case)
            self.success = self.is_successful()
            return self.score

    def is_successful(self) -> bool:
        if self.error is not None:
            self.success = False
        else:
            try:
                self.score >= self.threshold
            except:
                self.success = False
        return self.success

    @property
    def __name__(self):
        if self._include_dag_suffix:
            return f"{self.name} (DAG)"
        else:
            return self.name
