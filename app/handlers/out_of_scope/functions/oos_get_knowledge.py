from models.gpt_function_output_model import GPTFunctionOutput, OutputStatus
from models.gpt_function_param_model import DefaultGPTFunctionParams
from utils.function_decorator import meta


@meta(
    name="oos_get_knowledge",
    description="This function is used to get knowledge from the vector database.",
    parameters={
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "User standalone question suitable for the vector database search. "
                "This question must be in English.",
            }
        },
        "required": ["question"],
    },
)
async def oos_get_knowledge(_: DefaultGPTFunctionParams, question: str = None) -> GPTFunctionOutput:
    if question is None:
        return GPTFunctionOutput(
            status=OutputStatus.SUCCESS,
            message="No question provided. Clarify with the user question to get the context.",
        )

    # Here you can add the logic to get the knowledge from the vector database.

    return GPTFunctionOutput(
        status=OutputStatus.SUCCESS,
        message="This is the extra information that I found for you.",
    )
