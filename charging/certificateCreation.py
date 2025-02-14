import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import argparse

# Create the parser
parser = argparse.ArgumentParser(description="Process command-line arguments for certification script")

# Add arguments
parser.add_argument('-type', type=str, required=True, help="Type of the certificate -> client or server")
parser.add_argument('-id', type=str, required=False, help="Identifier (serial number if CP certificate) (e.g., E2507-8420-1274)")

# Parse the arguments
args = parser.parse_args()

if args.id != None:
    ID = args.id
else:
    ID = "E2507-8420-1274"
if args.type == 'client':
    TYPE = 'client'
else:
    TYPE = 'server'


# Generate a new private key for the server/client
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Create subject for client or server certificate
subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"FR"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"France"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Sophia-Antipolis"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'eurecom.fr'),
    x509.NameAttribute(NameOID.COMMON_NAME, ID if TYPE == 'client' else 'eurecom.fr'),
])

# Load the eurecom-ttp private key and certificate
with open('eurecom-ttp_Key.pem', 'rb') as f:
    ca_private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

with open('eurecom-ttp_Cert.pem', 'rb') as f:
    ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

# Create the certificate for client or server
cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(ca_cert.subject)  # Use eurecom-ttp as the issuer
    .public_key(private_key.public_key())  # The public key of the client/server
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
    .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365 * 2))  # Valid for 2 years
    .add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True
    )
    .sign(ca_private_key, hashes.SHA256(), default_backend())  # Sign using eurecom-ttp's private key
)

# Save the private key and certificate to files
with open(f"./charging/installedCertificates/{ID}/private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ))

with open(f"./charging/installedCertificates/{ID}/certificate_{ID}.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print(f"Certificate for {TYPE} '{ID}' generated and signed by eurecom-ttp.")
