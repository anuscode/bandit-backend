import socket
import ssl


def get_grpc_address(stage: str):
    if stage == "prod":
        return f"faiss-nrms-prod.oheadline.com:443"
    elif stage == "dev":
        return f"faiss-nrms-dev.oheadline.com:443"
    elif stage == "local":
        return "0.0.0.0:50051"
    else:
        raise ValueError("")


def get_ssl_certificate(host, port=443, timeout=10) -> bytes:
    context = ssl.create_default_context()
    conn = socket.create_connection((host, port))
    sock = context.wrap_socket(conn, server_hostname=host)
    sock.settimeout(timeout)
    der_cert = sock.getpeercert(True)
    pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)
    return pem_cert.encode("utf-8")
