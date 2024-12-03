import boto3
import logging
import json
from botocore.exceptions import ClientError

# Initialize IAM client
iam_client = boto3.client('iam')


def create_iam_role(role_name: str, trust_policy_document: dict, permissions_policy_document: dict,account_id: str) -> str:
    """
    Create an IAM role with a specified trust policy and attach a permissions policy.

    This function creates an IAM role with a given trust policy document and then attaches a specified
    permissions policy to that role. The role allows the specified entities to assume it based on the
    trust policy and grants the necessary permissions based on the provided permissions policy.

    Args:
        role_name (str): The name of the IAM role to create.
        trust_policy_document (dict): The trust policy document (JSON string) that defines the entities
                                      allowed to assume the role.
        permissions_policy_document (dict): The permissions policy document (JSON string) that specifies
                                            the permissions assigned to the role.

    Returns:
        str: The ARN (Amazon Resource Name) of the created IAM role if successful, or an empty string
             if an error occurs.
    """
    try:
        # Create the IAM role with the trust policy
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy_document)
        )
        role_arn = response['Role']['Arn']
        logging.info(f"IAM role '{role_name}' created successfully.")

        # Attach a permissions policy to the role
        attach_permissions_policy(role_name, permissions_policy_document)

        return role_arn
    except ClientError as e:
        if 'EntityAlreadyExists' in str(e):
            return f"arn:aws:iam::{account_id}:role/{role_name}"
        logging.error(f"Error creating IAM role '{role_name}': {e}", exc_info=True)
        return ""


def attach_permissions_policy(role_name: str, permissions_policy_document: dict) -> None:
    """
    Attach a permissions policy to an IAM role.

    This function attaches the provided permissions policy document to the specified IAM role. The policy
    grants permissions that are associated with the role. This is done using the IAM API's `put_role_policy`
    method to directly attach the policy to the role.

    Args:
        role_name (str): The name of the IAM role to attach the policy to.
        permissions_policy_document (dict): The permissions policy document (JSON string) that defines
                                            the permissions granted to the role.

    Returns:
        None: If the function completes successfully, it does not return a value.
    """
    try:
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName=f"{role_name}Policy",
            PolicyDocument=json.dumps(permissions_policy_document)
        )

        logging.info(f"Permissions policy attached to IAM role '{role_name}'.")
    except ClientError as e:
        logging.error(f"Error attaching permissions policy to role '{role_name}': {e}", exc_info=True)
