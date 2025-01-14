from .statement_chain import get_uri_for_statement,fetch_statement_details_from_chain
from packages.utils.src.SDKErrors import Errors
from packages.identifier.src.identifier import (
    check_identifier,
    update_statement_uri,
)
from packages.utils.src import data_utils

def verify_data_structure(input: dict) -> None:
    """
    Verifies the data structure of a given statement entry.
    
    :param input: The statement entry object to be validated.
    :raises SDKErrors.StatementHashMissingError: If the `digest` field is missing.
    :raises SDKErrors.InvalidIdentifierError: If `spaceUri` or `schemaUri` are invalid.
    :raises ValueError: If `digest` is not a valid 256-bit hexadecimal string.
    """
    if 'digest' not in input:
        raise Errors.StatementHashMissingError()
    
    check_identifier(input['space_uri'])
    
    if 'schema_uri' in input and input['schema_uri']:
        check_identifier(input['schema_uri'])
    
    data_utils.verify_is_hex(input['digest'], 256)


def build_from_properties(digest: str, space_uri: str, creator_uri: str, schema_uri: str = None) -> dict:
    """
    Constructs a statement entry object from given properties.
    
    :param digest: The hexadecimal string representing the digest of the statement.
    :param space_uri: The URI of the ChainSpace associated with the statement.
    :param creator_uri: The DID URI of the statement's creator.
    :param schema_uri: The URI of the schema linked to the statement (optional).
    :returns: A fully constructed statement entry object.
    :raises Various errors from `verify_data_structure` if validation fails.
    """
    stmt_uri = get_uri_for_statement(digest, space_uri, creator_uri)
    
    statement = {
        'element_uri': stmt_uri,
        'digest': digest,
        'creator_uri': creator_uri,
        'space_uri': space_uri,
        'schema_uri': schema_uri if schema_uri else None,
    }
    
    verify_data_structure(statement)
    return statement

def build_from_update_properties(stmt_uri, digest, space_uri, creator_uri):
    """
    Constructs an updated statement entry object using the provided properties.

    This function is used for updating an existing statement entry in the CORD blockchain system.
    It takes a statement URI and other identifiers to form a new statement entry, ensuring that the
    updated object adheres to the required data structure.

    Args:
        stmt_uri (str): The existing URI of the statement that is being updated.
        digest (str): The new hexadecimal string representing the digest of the statement.
        space_uri (str): The URI of the ChainSpace associated with the statement.
        creator_uri (str): The DID URI of the statement's creator.

    Returns:
        dict: A newly constructed statement entry object reflecting the updates.

    Example:
        existing_stmt_uri = 'stmt:cord:example_uri'
        new_digest = '0x456...'
        space_uri = 'space:cord:example_uri'
        creator_uri = 'did:cord:creator_uri'
        updated_statement_entry = build_from_update_properties(existing_stmt_uri, new_digest, space_uri, creator_uri)
        print('Updated Statement Entry:', updated_statement_entry)

    Raises:
        Exception: If the created statement entry does not meet the validation criteria.

    Description:
        The function first calls `update_statement_uri` to update the statement URI using the provided `stmt_uri` and `digest`.
        It then constructs a statement entry by combining the updated `statement_uri`, along with the `digest`, `space_uri`, `creator_uri`, forming a dictionary that conforms to the required statement entry structure.
        The `verify_data_structure` function is then invoked to validate the integrity and structure of the newly constructed statement entry.
        If validation is successful, the function returns the updated statement entry object.
    """

    statement_uri = update_statement_uri(stmt_uri, digest)
    statement = {
        'element_uri': statement_uri,
        'digest': digest,
        'creator_uri': creator_uri,
        'space_uri': space_uri,
    }

    verify_data_structure(statement)

    return statement

async def verify_against_properties(stmt_uri, digest, creator=None, space_uri=None, schema_uri=None):
    """
    Verifies a statement's properties against provided parameters.

    This asynchronous function checks if the provided statement URI, digest, and other optional properties
    match the corresponding entry in the blockchain. It's used to validate the integrity and accuracy of
    statement entries.

    Args:
        stmt_uri (str): The URI of the statement to be verified.
        digest (str): The hexadecimal string representing the digest of the statement.
        creator (str, optional): The DID URI of the statement's creator for verification.
        space_uri (str, optional): The URI of the ChainSpace associated with the statement for verification.
        schema_uri (str, optional): The URI of the schema linked to the statement for verification.

    Returns:
        dict: An object with `isValid` flag and `message`. The `isValid` flag indicates whether the verification
        was successful, and the `message` provides details or error information.

    Example:
        stmt_uri = 'stmt:cord:example_uri'
        digest = '0x123...'
        creator_uri = 'did:cord:creator_uri'
        space_uri = 'space:cord:example_uri'
        schema_uri = 'schema:cord:schema_uri'
        result = await verify_against_properties(stmt_uri, digest, creator_uri, space_uri, schema_uri)
        print('Verification result:', result)
    """
    try:
        statement_status = await fetch_statement_details_from_chain(stmt_uri)

        if not statement_status:
            return {
                'is_valid': False,
                'message': f'Statement details for "{digest}" not found.',
            }

        if digest != statement_status['digest']:
            return {
                'is_valid': False,
                'message': 'Digest does not match with Statement Digest.',
            }

        if statement_status.get('revoked'):
            return {
                'is_valid': False,
                'message': f'Statement "{stmt_uri}" Revoked.',
            }

        if creator:
            if creator != statement_status['creator_uri']:
                return {
                    'is_valid': False,
                    'message': 'Statement and Digest creator does not match.',
                }

        if space_uri:
            if space_uri != statement_status['space_uri']:
                return {
                    'is_valid': False,
                    'message': 'Statement and Digest space details does not match.',
                }

        if schema_uri:
            if schema_uri != statement_status['schema_uri']:
                return {
                    'is_valid': False,
                    'message': 'Statement and Digest schema details does not match.',
                }

        return {
            'is_valid': True,
            'message': 'Digest properties provided are valid and match the statement details.',
        }

    except Exception as error:
        return {
            'is_valid': False,
            'message': f'Error verifying properties: {error}',
        }
