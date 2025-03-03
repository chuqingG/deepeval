from typing import Optional, List, Dict, Union, Any

from deepeval.confident.api import Api, Endpoints, HttpMethods
from deepeval.monitor.utils import process_additional_data
from deepeval.test_run.hyperparameters import process_hyperparameters
from deepeval.utils import clean_nested_dict
from deepeval.monitor.api import (
    APIEvent,
    EventHttpResponse,
    Link,
)
from deepeval.prompt import Prompt


def monitor(
    event_name: str,
    model: str,
    input: str,
    response: str,
    retrieval_context: Optional[List[str]] = None,
    completion_time: Optional[float] = None,
    token_usage: Optional[float] = None,
    token_cost: Optional[float] = None,
    distinct_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    additional_data: Optional[
        Dict[str, Union[str, Link, List[Link], Dict]]
    ] = None,
    hyperparameters: Optional[Dict[str, Union[str, Prompt]]] = {},
    fail_silently: Optional[bool] = False,
    raise_exception: Optional[bool] = True,
    trace_stack: Optional[Dict[str, Any]] = None,
    trace_provider: Optional[str] = None,
    _debug: Optional[bool] = False,
) -> Union[str, None]:
    try:
        custom_properties = process_additional_data(additional_data)
        hyperparameters = process_hyperparameters(hyperparameters)
        hyperparameters["model"] = model

        api_event = APIEvent(
            traceProvider=trace_provider,
            name=event_name,
            input=input,
            response=response,
            retrievalContext=retrieval_context,
            completionTime=completion_time,
            tokenUsage=token_usage,
            tokenCost=token_cost,
            distinctId=distinct_id,
            conversationId=conversation_id,
            customProperties=custom_properties,
            hyperparameters=hyperparameters,
            traceStack=trace_stack,
        )
        api = Api()
        try:
            body = api_event.model_dump(by_alias=True, exclude_none=True)
        except AttributeError:
            # Pydantic version below 2.0
            body = api_event.dict(by_alias=True, exclude_none=True)

        body = clean_nested_dict(body)
        if _debug:
            print(body)
        result = api.send_request(
            method=HttpMethods.POST,
            endpoint=Endpoints.EVENT_ENDPOINT,
            body=body,
        )
        response = EventHttpResponse(eventId=result["eventId"])
        return response.eventId
    except Exception as e:
        if fail_silently:
            return

        if raise_exception:
            raise (e)
        else:
            print(str(e))


async def a_monitor(
    event_name: str,
    model: str,
    input: str,
    response: str,
    retrieval_context: Optional[List[str]] = None,
    completion_time: Optional[float] = None,
    token_usage: Optional[float] = None,
    token_cost: Optional[float] = None,
    distinct_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    additional_data: Optional[
        Dict[str, Union[str, Link, List[Link], Dict]]
    ] = None,
    hyperparameters: Optional[Dict[str, str]] = {},
    fail_silently: Optional[bool] = False,
    raise_exception: Optional[bool] = True,
    trace_stack: Optional[Dict[str, Any]] = None,
    trace_provider: Optional[str] = None,
    _debug: Optional[bool] = False,
) -> Union[str, None]:
    try:
        custom_properties = process_additional_data(additional_data)
        hyperparameters = process_hyperparameters(hyperparameters)
        hyperparameters["model"] = model

        api_event = APIEvent(
            traceProvider=trace_provider,
            name=event_name,
            input=input,
            response=response,
            retrievalContext=retrieval_context,
            completionTime=completion_time,
            tokenUsage=token_usage,
            tokenCost=token_cost,
            distinctId=distinct_id,
            conversationId=conversation_id,
            customProperties=custom_properties,
            hyperparameters=hyperparameters,
            traceStack=trace_stack,
        )
        api = Api()
        try:
            body = api_event.model_dump(by_alias=True, exclude_none=True)
        except AttributeError:
            # Pydantic version below 2.0
            body = api_event.dict(by_alias=True, exclude_none=True)

        body = clean_nested_dict(body)
        if _debug:
            print(body)
        result = await api.a_send_request(
            method=HttpMethods.POST,
            endpoint=Endpoints.EVENT_ENDPOINT,
            body=body,
        )
        response = EventHttpResponse(eventId=result["eventId"])
        return response.eventId

    except Exception as e:
        if fail_silently:
            return

        if raise_exception:
            raise (e)
        else:
            print(str(e))
