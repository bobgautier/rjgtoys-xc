
from rjgtoys.xc import Error, Title
from pydantic import Field

class InsufficientSpace(Error):
    """Raised when a filesystem has insufficient space."""

    detail = "Filesystem {path} has only {avail} bytes free, need {need}"

    path: str = Title("The filesystem mount point")
    avail: int = Field(..., title="Number of bytes free on the filesystem")
    need:  int = Title("Number of bytes needed")

def copy_file_to_dest(src, dst):
    e =  InsufficientSpace(path=dst, avail=100, need=300)
    print(e.to_dict())
    raise e

try:
    copy_file_to_dest('a', 'b')
except InsufficientSpace as e:
    print(e)
    print("Please free at least %d bytes, or try a different filesystem" % (e.need-e.avail))

