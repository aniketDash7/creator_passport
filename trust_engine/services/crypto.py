import os
import datetime
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID

class CryptoService:
    def __init__(self, storage_dir="storage/creds"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def check_identity_exists(self, user_name: str) -> bool:
        """Checks if a key and certificate already exist for the given user."""
        safe_name = "".join(x for x in user_name if x.isalnum())
        key_exists = os.path.exists(os.path.join(self.storage_dir, f"{safe_name}_key.pem"))
        cert_exists = os.path.exists(os.path.join(self.storage_dir, f"{safe_name}_cert.pem"))
        return key_exists or cert_exists

    def ensure_root_ca(self):
        """Generates Root CA if it doesn't exist."""
        root_key_path = os.path.join(self.storage_dir, "root_key.pem")
        root_cert_path = os.path.join(self.storage_dir, "root_cert.pem")
        
        if os.path.exists(root_key_path) and os.path.exists(root_cert_path):
            return root_key_path, root_cert_path

        # Generate Root CA (Self-Signed)
        print("[CryptoService] Generating Root CA...")
        root_key = ec.generate_private_key(ec.SECP256R1())
        root_subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"Authenticity Trust Engine Root"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Authenticity Protocol"),
        ])
        
        # Extensions
        root_cert = x509.CertificateBuilder().subject_name(
            root_subject
        ).issuer_name(
            issuer
        ).public_key(
            root_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.now(datetime.UTC)
        ).not_valid_after(
            datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=3650) # 10 years
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ), critical=True,
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(root_key.public_key()), critical=False
        ).sign(root_key, hashes.SHA256())

        # Save
        with open(root_key_path, "wb") as f:
            f.write(root_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ))
        with open(root_cert_path, "wb") as f:
            f.write(root_cert.public_bytes(serialization.Encoding.PEM))
            
        return root_key_path, root_cert_path

    def issue_user_cert(self, user_name: str, email: str = "creator@example.com"):
        """Issues a Leaf Certificate for a user, signed by the Root CA."""
        safe_name = "".join(x for x in user_name if x.isalnum())
        user_key_path = os.path.join(self.storage_dir, f"{safe_name}_key.pem")
        user_cert_path = os.path.join(self.storage_dir, f"{safe_name}_cert.pem")
        
        # Load Root
        root_key_path, root_cert_path = self.ensure_root_ca()
        with open(root_key_path, "rb") as f:
            root_key = serialization.load_pem_private_key(f.read(), password=None)
        with open(root_cert_path, "rb") as f:
            root_cert = x509.load_pem_x509_certificate(f.read())

        # Generate User Key
        user_key = ec.generate_private_key(ec.SECP256R1())
        user_subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, f"{user_name}"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Authenticity Verified Creator"),
        ])
        
        user_cert = x509.CertificateBuilder().subject_name(
            user_subject
        ).issuer_name(
            root_cert.subject
        ).public_key(
            user_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.now(datetime.UTC)
        ).not_valid_after(
            datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=90)
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ), critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([x509.OID_EMAIL_PROTECTION]), critical=False,
        ).add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()), critical=False
        ).sign(root_key, hashes.SHA256())

        # Save
        with open(user_key_path, "wb") as f:
            f.write(user_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ))
        with open(user_cert_path, "wb") as f:
            f.write(user_cert.public_bytes(serialization.Encoding.PEM))
            
        return user_key_path, user_cert_path
