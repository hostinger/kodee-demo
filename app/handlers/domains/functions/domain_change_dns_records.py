from database.helpers import insert_function_log
from models.gpt_function_param_model import DefaultGPTFunctionParams
from models.gpt_function_output_model import GPTFunctionOutput, OutputStatus
from utils.function_decorator import meta


@meta(
    name="domain_change_dns_records",
    description="This function is used to change the DNS records of a domain. The user can change the DNS records of ",
    parameters={
        "type": "object",
        "properties": {
            "domain_name": {
                "type": "string",
                "description": "The domain name with subdomain if there is, e.g. hostinger.com or www.hostinger.com. "
                               "Always ask the user to input it. If TLD not provided, ask the user to provide it.",
            },
        },
    },
)
async def domain_change_dns_records(data: DefaultGPTFunctionParams, domain_name: str = None) -> GPTFunctionOutput:
    # EXAMPLE OF FUNCTION LOGGING
    await insert_function_log(data, {"message": "domain_change_dns_records LOG HERE", "domain": domain_name})

    return GPTFunctionOutput(
        status=OutputStatus.SUCCESS,
        message=f"Thank you for providing your domain name: {domain_name}. To edit its DNS records, go to Domains → Domain portfolio, then click on ‘Manage’ and head to the DNS/Nameservers section to make any preferred changes.",
    )
