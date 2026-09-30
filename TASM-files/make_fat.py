#!/usr/bin/env python3
"""Create a fresh 1.44 MB FAT12 floppy image and copy files to it.

Usage:
    python make_fat.py exchange.img main.c BUILD.BAT
    python make_fat.py --check main.c BUILD.BAT
    python make_fat.py --clean PROJECT_DIR main

The script deliberately does not use mtools, dd or OS-specific shell commands.
Text files intended for DOS are normalized to CRLF. UTF-8 text is converted to
CP866 when possible, which is the usual DOS Cyrillic code page.
"""

from __future__ import annotations

import shutil
import struct
import sys
from pathlib import Path

SECTOR_SIZE = 512
TOTAL_SECTORS = 2880
MEDIA = 0xF0
RESERVED_SECTORS = 1
FAT_COUNT = 2
ROOT_ENTRIES = 224
SECTORS_PER_FAT = 9
SECTORS_PER_TRACK = 18
HEADS = 2
ROOT_DIR_SECTORS = (ROOT_ENTRIES * 32 + SECTOR_SIZE - 1) // SECTOR_SIZE
DATA_START_SECTOR = RESERVED_SECTORS + FAT_COUNT * SECTORS_PER_FAT + ROOT_DIR_SECTORS
FIRST_DATA_CLUSTER = 2
MAX_CLUSTER = 0xFEF

# Files that are normally text on DOS and therefore need CRLF.
DOS_TEXT_EXTENSIONS = {".c", ".h", ".cpp", ".cc", ".asm", ".inc", ".bat", ".txt"}


def fat12_set(fat: bytearray, cluster: int, value: int) -> None:
    offset = cluster + cluster // 2
    if cluster & 1:
        fat[offset] = (fat[offset] & 0x0F) | ((value << 4) & 0xF0)
        fat[offset + 1] = (value >> 4) & 0xFF
    else:
        fat[offset] = value & 0xFF
        fat[offset + 1] = (fat[offset + 1] & 0xF0) | ((value >> 8) & 0x0F)


def dos_83_name(name: str) -> bytes:
    path = Path(name)
    stem = path.stem.upper()
    ext = path.suffix[1:].upper()

    if not stem or len(stem) > 8 or len(ext) > 3:
        raise ValueError(f"Filename is not DOS 8.3: {name}")

    allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_$~!#%&'()-@^`{}"
    if any(c not in allowed for c in stem + ext):
        raise ValueError(f"Filename contains unsupported DOS 8.3 characters: {name}")

    return stem.ljust(8).encode("ascii") + ext.ljust(3).encode("ascii")


def dos_text_bytes(path: Path) -> bytes:
    """Read a source/batch file and make it DOS-friendly."""
    raw = path.read_bytes()

    # Remove UTF-8 BOM if present.
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]

    # Decode text. UTF-8 is preferred; CP866/CP1251 are accepted for files
    # that were already prepared on a DOS/Windows system.
    for encoding in ("utf-8", "cp866", "cp1251"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError(f"Cannot decode DOS text file: {path}")

    # Normalize all line endings to DOS CRLF.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # CP866 is the target encoding for DOS text. If the file contains a
    # character unavailable in CP866, keep UTF-8 rather than corrupting it.
    try:
        return text.encode("cp866").replace(b"\n", b"\r\n")
    except UnicodeEncodeError:
        return text.encode("utf-8").replace(b"\n", b"\r\n")


def file_bytes(path: Path) -> bytes:
    if path.suffix.lower() in DOS_TEXT_EXTENSIONS:
        return dos_text_bytes(path)
    return path.read_bytes()


def create_image(image_path: Path, source_paths: list[Path]) -> None:
    if len(source_paths) > ROOT_ENTRIES:
        raise ValueError("Too many files for FAT12 root directory")

    image = bytearray(SECTOR_SIZE * TOTAL_SECTORS)
    bs = memoryview(image)[:SECTOR_SIZE]

    # FAT12 boot sector / BIOS Parameter Block
    bs[0:3] = b"\xEB\x3C\x90"
    bs[3:11] = b"MSDOS5.0"
    struct.pack_into("<H", bs, 11, SECTOR_SIZE)
    bs[13] = 1
    struct.pack_into("<H", bs, 14, RESERVED_SECTORS)
    bs[16] = FAT_COUNT
    struct.pack_into("<H", bs, 17, ROOT_ENTRIES)
    struct.pack_into("<H", bs, 19, TOTAL_SECTORS)
    bs[21] = MEDIA
    struct.pack_into("<H", bs, 22, SECTORS_PER_FAT)
    struct.pack_into("<H", bs, 24, SECTORS_PER_TRACK)
    struct.pack_into("<H", bs, 26, HEADS)
    struct.pack_into("<I", bs, 28, 0)
    struct.pack_into("<I", bs, 32, 0)
    bs[36] = 0x00
    bs[37] = 0x00
    bs[38] = 0x29
    struct.pack_into("<I", bs, 39, 0x12345678)
    bs[43:54] = b"EXCHANGE   "
    bs[54:62] = b"FAT12   "
    bs[510:512] = b"\x55\xAA"

    fat = bytearray(SECTORS_PER_FAT * SECTOR_SIZE)
    fat[0:3] = bytes([MEDIA, 0xFF, 0xFF])

    root_start = (RESERVED_SECTORS + FAT_COUNT * SECTORS_PER_FAT) * SECTOR_SIZE
    data_cluster = FIRST_DATA_CLUSTER

    for index, source_path in enumerate(source_paths):
        data = file_bytes(source_path)
        cluster_count = max(1, (len(data) + SECTOR_SIZE - 1) // SECTOR_SIZE)

        if data_cluster + cluster_count - 1 > MAX_CLUSTER:
            raise ValueError(f"Not enough space for {source_path.name}")

        first_cluster = data_cluster

        for i in range(cluster_count):
            current = first_cluster + i
            next_cluster = current + 1 if i + 1 < cluster_count else 0xFFF
            fat12_set(fat, current, next_cluster)

        entry = bytearray(32)
        entry[0:11] = dos_83_name(source_path.name)
        entry[11] = 0x20
        struct.pack_into("<H", entry, 26, first_cluster)
        struct.pack_into("<I", entry, 28, len(data))
        image[root_start + index * 32:root_start + (index + 1) * 32] = entry

        for i in range(cluster_count):
            cluster = first_cluster + i
            data_start = (DATA_START_SECTOR + cluster - 2) * SECTOR_SIZE
            chunk = data[i * SECTOR_SIZE:(i + 1) * SECTOR_SIZE]
            image[data_start:data_start + len(chunk)] = chunk

        data_cluster += cluster_count

    image[root_start + len(source_paths) * 32] = 0x00

    fat_start = RESERVED_SECTORS * SECTOR_SIZE
    fat_size = SECTORS_PER_FAT * SECTOR_SIZE
    for n in range(FAT_COUNT):
        offset = fat_start + n * fat_size
        image[offset:offset + fat_size] = fat

    image_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.write_bytes(image)


def check_files(paths: list[Path]) -> int:
    for path in paths:
        if not path.is_file():
            print(f"ERROR: file not found: {path}")
            return 1
    print("[OK] All files exist")
    return 0


def clean_project(project: Path, target: str) -> int:
    removed = 0
    for ext in (".obj", ".exe", ".map", ".lst"):
        path = project / f"{target}{ext}"
        if path.exists():
            path.unlink()
            print(f"Removed: {path}")
            removed += 1
    print(f"[OK] Cleaned {removed} file(s)")
    return 0


def main() -> int:
    args = sys.argv[1:]

    if not args:
        print("Usage: python make_fat.py <exchange.img> <file1> [file2 ...]")
        print("       python make_fat.py --check <file1> [file2 ...]")
        print("       python make_fat.py --clean <project_dir> <target>")
        return 2

    if args[0] == "--check":
        return check_files([Path(p) for p in args[1:]])

    if args[0] == "--clean":
        if len(args) != 3:
            print("Usage: python make_fat.py --clean <project_dir> <target>")
            return 2
        return clean_project(Path(args[1]), args[2])

    image_path = Path(args[0])
    source_paths = [Path(p) for p in args[1:]]
    if not source_paths:
        print("ERROR: no files specified")
        return 2

    result = check_files(source_paths)
    if result:
        return result

    try:
        create_image(image_path, source_paths)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"FAT12 image created: {image_path}")
    for source_path in source_paths:
        data = file_bytes(source_path)
        mode = "DOS CRLF/CP866" if source_path.suffix.lower() in DOS_TEXT_EXTENSIONS else "binary"
        print(f"File added: {source_path.name} ({len(data)} bytes, {mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
