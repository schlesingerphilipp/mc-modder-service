# Desktop-Commander MCP Fails with Can't start desktop-commander: failed to connect: calling "initialize": invalid character '>' looking for beginning of value
# Can not find a solution
"""Small file/folder utility helpers used by the service.

Provides:
- copy_folder: recursively copy a directory to a destination. Optionally overwrite.
- overwrite_file: atomically overwrite a file with the provided string content.

These helpers favor safety (atomic replace where possible) and clear errors.
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import Union, Optional
from langchain.tools import tool

@tool
def copy_folder(src: Union[str, Path], dst: Union[str, Path], overwrite: bool = False) -> None:
	"""Recursively copy a folder from `src` to `dst`.

	If `dst` exists and `overwrite` is False, a FileExistsError is raised.
	If `overwrite` is True and `dst` exists, the destination will be removed
	and replaced with a copy of `src`.

	This uses shutil.copytree under the hood and attempts to be safe by
	copying into a temporary directory and moving into place.

	Raises:
		FileNotFoundError: when `src` does not exist or is not a directory.
		FileExistsError: when `dst` exists and overwrite is False.
		OSError: for other filesystem-related errors.
	"""
	src_path = Path(src)
	src_path = src_path.resolve()
	dst_path = Path(dst)
	dst_path = dst_path.resolve()

	if not src_path.exists() or not src_path.is_dir():
		raise FileNotFoundError(f"Source folder does not exist or is not a directory: {src_path}")

	if dst_path.exists():
		if not overwrite:
			raise FileExistsError(f"Destination already exists: {dst_path}")
		# remove destination atomically by moving it to a temp location first
		temp_remove = None
		try:
			temp_remove = Path(tempfile.mkdtemp(prefix="copy_folder_remove_"))
			# move dst into temp_remove for deletion
			shutil.move(str(dst_path), str(temp_remove / dst_path.name))
		except Exception:
			# if move fails, try to remove directly (best-effort)
			shutil.rmtree(dst_path, ignore_errors=True)
		else:
			# schedule removal of the temp dir
			shutil.rmtree(temp_remove, ignore_errors=True)

	# copy into a temporary directory next to the destination, then move
	parent = dst_path.parent
	parent.mkdir(parents=True, exist_ok=True)

	with tempfile.TemporaryDirectory(prefix="copy_folder_tmp_", dir=str(parent)) as tmpdir:
		staging = Path(tmpdir) / src_path.name
		shutil.copytree(src=str(src_path), dst=str(staging))
		# move staging to final destination
		shutil.move(str(staging), str(dst_path))

@tool
def overwrite_file(path: Union[str, Path], content: str, encoding: str = "utf-8") -> None:
	"""Atomically overwrite a file with the given string content.

	The function writes to a temporary file in the same directory and then
	renames it into place. This helps avoid partial writes.

	Args:
		path: target file path to overwrite (will be created if missing).
		content: string content to write to the file.
		encoding: file encoding to use.

	Raises:
		OSError: when writing or renaming fails.
	"""
	file_path = Path(path)
	file_path.parent.mkdir(parents=True, exist_ok=True)

	# use a temporary file in the same directory for atomic rename
	fd, tmpname = tempfile.mkstemp(prefix="overwrite_", dir=str(file_path.parent))
	try:
		with os.fdopen(fd, "w", encoding=encoding) as tmpf:
			tmpf.write(content)
			tmpf.flush()
			os.fsync(tmpf.fileno())
		# atomic replace
		os.replace(tmpname, str(file_path))
	except Exception:
		# ensure temp file is removed on failure
		try:
			os.remove(tmpname)
		except Exception:
			pass
		raise


@tool
def read_file_contents_tool(path: Union[str, Path], encoding: str = "utf-8") -> str:
	"""Read and return the text contents of a file.

	Expands user (~) and environment variables. The function resolves the
	path to an absolute path (does not require the file to exist when
	creating the Path object), then verifies the file exists and is a file.

	Args:
		path: path to the file to read.
		encoding: text encoding to use when reading.

	Returns:
		The file contents as a string.

	Raises:
		FileNotFoundError: if the file does not exist.
		IsADirectoryError: if the path refers to a directory.
		OSError: for other I/O errors.
	"""
	return read_file_contents(path, encoding)

def read_file_contents(path: Union[str, Path], encoding: str = "utf-8") -> str:
	"""Read and return the text contents of a file.

	Expands user (~) and environment variables. The function resolves the
	path to an absolute path (does not require the file to exist when
	creating the Path object), then verifies the file exists and is a file.

	Args:
		path: path to the file to read.
		encoding: text encoding to use when reading.

	Returns:
		The file contents as a string.

	Raises:
		FileNotFoundError: if the file does not exist.
		IsADirectoryError: if the path refers to a directory.
		OSError: for other I/O errors.
	"""
	file_path = Path(os.path.expandvars(Path(path).expanduser()))
	file_path = file_path.resolve(strict=False)

	if not file_path.exists():
		raise FileNotFoundError(f"File not found: {file_path}")
	if file_path.is_dir():
		raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")

	with file_path.open("r", encoding=encoding) as f:
		return f.read()


@tool
def list_dir_contents(path: Union[str, Path], show_hidden: bool = False) -> list:
	"""List files and folders in a directory and return absolute paths.

	Args:
		path: directory to list.
		show_hidden: include entries starting with a dot when True.

	Returns:
		A sorted list of absolute path strings for immediate children.

	Raises:
		NotADirectoryError: if `path` is not a directory.
		FileNotFoundError: if `path` does not exist.
	"""
	dir_path = Path(os.path.expandvars(Path(path).expanduser()))
	dir_path = dir_path.resolve(strict=False)

	if not dir_path.exists():
		raise FileNotFoundError(f"Directory not found: {dir_path}")
	if not dir_path.is_dir():
		raise NotADirectoryError(f"Path is not a directory: {dir_path}")

	entries = []
	for child in sorted(dir_path.iterdir(), key=lambda p: p.name):
		if not show_hidden and child.name.startswith("."):
			continue
		entries.append(str(child.resolve(strict=False)))

	return entries


@tool
def copy_file(src: Union[str, Path], dst: Union[str, Path], overwrite: bool = False) -> str:
	"""Copy a file from `src` to `dst`.

	If `dst` is a directory, the file will be copied into that directory
	preserving the source filename. If `dst` exists and `overwrite` is False,
	a FileExistsError is raised. Returns the absolute path of the destination
	file as a string.

	Raises:
		FileNotFoundError: when source file does not exist.
		IsADirectoryError: when src is a directory.
		FileExistsError: when destination exists and overwrite is False.
		OSError: for other filesystem errors during copy.
	"""
	src_path = Path(src)
	src_path = src_path.resolve()

	if not src_path.exists():
		raise FileNotFoundError(f"Source file not found: {src_path}")
	if src_path.is_dir():
		raise IsADirectoryError(f"Source is a directory, expected a file: {src_path}")

	dst_path = Path(dst)
	# if dst is a directory, copy into it
	if dst_path.exists() and dst_path.is_dir():
		dst_path = dst_path / src_path.name
	else:
		# ensure parent exists
		dst_path.parent.mkdir(parents=True, exist_ok=True)

	if dst_path.exists() and not overwrite:
		raise FileExistsError(f"Destination file already exists: {dst_path}")

	# copy to a temporary file next to destination then move into place
	fd, tmpname = tempfile.mkstemp(prefix="copy_file_", dir=str(dst_path.parent))
	try:
		os.close(fd)
		shutil.copy2(src=str(src_path), dst=tmpname)
		os.replace(tmpname, str(dst_path))
		return str(dst_path.resolve())
	except Exception:
		try:
			os.remove(tmpname)
		except Exception:
			pass
		raise


@tool
def make_dirs(path: Union[str, Path], mode: int = 0o755, exist_ok: bool = True) -> str:
	"""Create directories recursively and return the absolute path.

	Args:
		path: directory path to create (can be str or Path).
		mode: permission bits for new directories (default 0o755).
		exist_ok: if False and the path exists, raise FileExistsError.

	Returns:
		The absolute path of the created directory as a string.
	"""
	dir_path = Path(os.path.expandvars(Path(path).expanduser()))

	if dir_path.exists() and not exist_ok:
		raise FileExistsError(f"Directory already exists: {dir_path}")

	# create parent directories as needed
	dir_path.mkdir(parents=True, exist_ok=exist_ok, mode=mode)

	return str(dir_path.resolve(strict=False))


class FakeMCPClient:
	"""
	A fake MCP client until I get the real one working.
	There has to be a good general MCP for file operations and terminal calls.
	"""
	def get_tools(self):
		return [make_dirs, copy_folder, copy_file, read_file_contents_tool, list_dir_contents, overwrite_file]