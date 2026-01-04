import os
import json
from c2pa import Builder, Signer, C2paSignerInfo, Reader

class C2PAService:
    def __init__(self, tsa_url="http://timestamp.digicert.com"):
        self.tsa_url = tsa_url.encode("utf-8") if tsa_url else None

    def sign_content(self, input_path: str, output_path: str, key_path: str, cert_chain_paths: list[str], author_name: str = "Verified User"):
        """
        Signs the content at input_path and saves to output_path.
        cert_chain_paths: List of [leaf_cert_path, root_cert_path]
        """
        # 1. Read Keys & Certs
        with open(key_path, 'rb') as f:
            priv_key = f.read()
        
        chain_pem = b""
        for cert_path in cert_chain_paths:
            with open(cert_path, 'rb') as f:
                chain_pem += f.read().strip() + b"\n"

        # 2. Configure Signer
        # Using es256 as our PKI (CryptoService) generates EC P-256 keys.
        try:
            signer_info = C2paSignerInfo(
                b"es256",
                chain_pem,
                priv_key,
                self.tsa_url
            )
            signer = Signer.from_info(signer_info)
        except Exception as e:
            raise ValueError(f"Failed to initialize C2PA Signer: {e}")

        # 3. Define Manifest
        manifest = {
            "claim_generator": "Authenticity_Trust_Engine/1.0",
            "assertions": [
                {
                    "label": "c2pa.actions",
                    "data": {
                        "actions": [{"action": "c2pa.created"}]
                    }
                },
                {
                    "label": "stds.schema-org.CreativeWork",
                    "data": {
                        "@context": "https://schema.org",
                        "@type": "CreativeWork",
                        "author": [{"@type": "Person", "name": author_name}]
                    }
                }
            ]
        }

        # 4. Sign
        try:
            builder = Builder(manifest)
            builder.sign_file(input_path, output_path, signer)
            return output_path
        except Exception as e:
            raise RuntimeError(f"C2PA Signing Failed: {e}")

    def verify_content(self, input_path: str):
        """
        Verifies the content at input_path and returns the Manifest Store.
        """
        try:
            reader = Reader(input_path)
            return json.loads(reader.json())
        except Exception as e:
            # If no manifest found or invalid
            return {"error": str(e), "valid": False}
