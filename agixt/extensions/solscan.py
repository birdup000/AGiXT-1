from Extensions import Extensions
import requests
import json
import logging


class solscan(Extensions):
    """
    The SolScan extension for AGiXT enables interaction with the SolScan API
    to retrieve Solana blockchain data.
    """

    def __init__(self, **kwargs):
        self.base_uri = "https://public-api.solscan.io"
        self.session = requests.Session()
        self.commands = {
            "Get Chain Info": self.get_chain_info,
        }

    async def get_chain_info(self):
        """
        Fetch Solana blockchain information from the SolScan API.

        Returns:
            str: A markdown-formatted string summarizing chain data
                 or a JSON-formatted string if an error occurs.
        """
        endpoint = "chaininfo"
        url = f"{self.base_uri}/{endpoint}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                return json.dumps(
                    {"error": True, "message": "API request unsuccessful"}, indent=4
                )

            chain_data = data.get("data", {})

            markdown_lines = [
                "# Solana Chain Information\n",
                f"- **Block Height**: {chain_data.get('blockHeight', 'N/A')}",
                f"- **Current Epoch**: {chain_data.get('currentEpoch', 'N/A')}",
                f"- **Absolute Slot**: {chain_data.get('absoluteSlot', 'N/A')}",
                f"- **Transaction Count**: {chain_data.get('transactionCount', 'N/A')}",
            ]

            return "\n".join(markdown_lines)

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching chain info: {e}")
            return json.dumps({"error": True, "message": str(e)}, indent=4)
