"""
CordConfig Module

The `CordConfig` module is an integral part of the CORD SDK, offering functionalities to configure and manage
connections with the CORD blockchain. Essential for establishing a secure and efficient communication channel,
this module enables operations like identity management, transaction processing, and smart contract interactions.

Features of `CordConfig` include:
- Initialization of cryptographic modules for SDK setup.
- Connection management using WebSocket for interacting with the CORD blockchain network.
- Cryptographic readiness checks ensuring secure blockchain interactions.
- Disconnection utilities for clean closure of blockchain connections.

Usage:
To use the `CordConfig` module, import it into your project and utilize its functions for blockchain
interactions.
"""

from substrateinterface import SubstrateInterface
from substrateinterface.exceptions import SubstrateRequestException
import asyncio
from .service import ConfigService
import logging
from scalecodec.type_registry import load_type_registry_file

logger = logging.getLogger(__name__)

async def init(configs=None):
    """
    Initializes the CORD SDK configuration and prepares cryptographic modules.

    :param configs: Configuration options for initializing the SDK.
    :return: None
    """
    ConfigService.set(configs or {})
    # Note: cryptoWaitReady equivalent for Python might be different depending on the library used.
    # Assuming it is ready for now.

async def connect(blockchain_rpc_ws_url, no_init_warn=True, **api_options):
    """
    Establishes a connection to the CORD blockchain via WebSocket URL.

    :param blockchain_rpc_ws_url: WebSocket URL for the CORD blockchain RPC endpoint.
    :param no_init_warn: Optional warning suppression for initialization.
    :param api_options: Additional API connection options.
    :return: A SubstrateInterface instance.
    """
    
    try:
        
        custom_type = load_type_registry_file('custom-type.json')
        #example:
        #   {
        #     "runtime_id": 2,
        #     "types": {
        #     "PalletDidDidDetailsDidEncryptionKey": {
        #         "type": "enum",
        #         "type_mapping": [
        #         ["X25519", "[u8; 32]"]
        #     ]
        #     },
        #     "PalletDidServiceEndpointsDidEndpoint": {
        #         "type": "struct",
        #         "type_mapping": [
        #         ["id", "Bytes"],
        #         ["service_types", "Vec<Bytes>"],
        #         ["urls", "Vec<Bytes>"]
        #         ]
        #     }
        #     },
        #     "versioning": []
        # }
  
        substrate = SubstrateInterface(
            url=blockchain_rpc_ws_url,
            **api_options,
            type_registry=custom_type
        )
        
        await init({'api': substrate})
        return substrate
    except SubstrateRequestException as e:
        logger.info(f"Error connecting to blockchain: {e}")
        raise e

def disconnect():
    """
    Disconnects from the CORD blockchain and clears the cached connection.

    :return: A boolean indicating successful disconnection.
    """
    if not ConfigService.is_set('api'):
        return False
    api = ConfigService.get('api')
    ConfigService.unset('api')
    api.close()
    return True

'''
# Example usage
async def main():
    blockchain_rpc_ws_url = "ws://127.0.0.1:9944"
    substrate = await connect(blockchain_rpc_ws_url)
    logger.info("Connected to blockchain:", substrate)

    # Perform any required operations here

    disconnected = await disconnect()
    logger.info("Disconnected:", disconnected)

if __name__ == "__main__":
    asyncio.run(main())
'''