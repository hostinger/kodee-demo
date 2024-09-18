from models.gpt_function_output_model import GPTFunctionOutput, OutputStatus
from models.gpt_function_param_model import DefaultGPTFunctionParams
from utils.function_decorator import meta


@meta(
    name="domain_transfer_in",
    description="This function is used to transfer a domain to Hostinger.",
    parameters={
        "type": "object",
        "properties": {
            "domain_name": {
                "type": "string",
                "description": "The valid domain name "
                               "without subdomain, e.g. hostinger.com. Always ask the user to input domain name. If "
                               "domain TLD not provided, ask the user to provide it.",
            },
        },
    },
)
async def domain_transfer_in(_data: DefaultGPTFunctionParams, domain_name: str = None) -> GPTFunctionOutput:
    # EXAMPLE OF POSSIBLE FUNCTION RESPONSE
    return GPTFunctionOutput(
        status=OutputStatus.SUCCESS,
        message=f"To transfer a domain {domain_name} to Hostinger, you need to follow these steps:\n"
                "1. Unlock the domain at your current registrar.\n"
                "2. Get the EPP code from your current registrar.\n"
                "3. Initiate the domain transfer at Hostinger.\n"
                "4. Confirm the domain transfer.\n"
                "5. Wait for the domain transfer to complete.\n"
                "The process may take up to 7 business days. You may track the domain transfer progress in your Hostinger panel. \n"
    )
