from backends.grpc.servicers.master import MasterBanditServicer
from backends.grpc.servicers.slave import SlaveBanditServicer

__all__ = [
    "MasterBanditServicer",
    "SlaveBanditServicer",
]
