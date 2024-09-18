from models.gpt_function_output_model import GPTFunctionOutput, OutputStatus
from models.gpt_function_param_model import DefaultGPTFunctionParams
from utils.function_decorator import meta


@meta(
    name="domain_sell_domain",
    description="This function is used to sell a domain. The user should provide their domain ",
    parameters={
        "type": "object",
        "properties": {
            "domain_name": {
                "type": "string",
                "description": "The domain name without subdomain if there is, e.g. hostinger.com. Always ask the user "
                               "to input it. If TLD not provided, ask the user to provide it.",
            },
        },
        "required": ["domain_name"],
    },
)
async def domain_sell_domain(_: DefaultGPTFunctionParams, domain_name: str | None = None) -> GPTFunctionOutput:
    # EXAMPLE OF FUNCTION WITH EXIT STATUS
    return GPTFunctionOutput(
        status=OutputStatus.EXIT,
        message=f"To proceed with selling {domain_name}, a dedicated Customer Success Specialist is required to assist further. "
                "The user is being redirected to the dedicated team right now."
    )
