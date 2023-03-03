import socket
import ssl

import grpc


def get_ssl_certificate(host, port=443, timeout=10) -> bytes:
    context = ssl.create_default_context()
    conn = socket.create_connection((host, port))
    sock = context.wrap_socket(conn, server_hostname=host)
    sock.settimeout(timeout)
    der_cert = sock.getpeercert(True)
    pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)
    return pem_cert.encode("utf-8")


def channel(address: str) -> grpc.aio.Channel:
    host, port = address.split(":")
    if port == "443":
        certificate = get_ssl_certificate(host)
        creds = grpc.ssl_channel_credentials(certificate)
        return grpc.aio.secure_channel(address, creds)
    else:
        return grpc.aio.insecure_channel(address)
