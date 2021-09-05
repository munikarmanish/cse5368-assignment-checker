#!/usr/bin/env python3

__author__ = "Manish Munikar"
__email__ = "manish.munikar@mavs.uta.edu"

import argparse
import mimetypes
import re
import sys
import tempfile
import zipfile
from pathlib import Path

import docx
import fitz


def log(msg):
    print(" :: ", msg, file=sys.stderr)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to check")
    return parser.parse_args()


def check_file_type(path):
    basename = Path(path).name.lower()
    extension = basename.split(".", maxsplit=1)[1].lower()
    mime = mimetypes.guess_type(basename)[0]
    if re.search(r"text/.*", mime):
        return "text"
    if extension in ["doc", "docx"]:
        return "msword"
    if extension == "pdf":
        return "pdf"
    if extension == "zip":
        return "zip"
    return "unknown"


def read_header_lines(path, type):
    file = Path(path)
    if type == "text":
        return file.open().readlines()[:4]
    if type == "msword":
        doc = docx.Document(file)
        lines = [
            line.strip()
            for par in doc.paragraphs[:4]
            for line in par.text.split("\n")
        ]
        return [line for line in lines if len(line) > 0][:4]
    if type == "pdf":
        doc = fitz.open(file)
        page = next(doc.pages())
        text = page.get_text()
        lines = [line.strip() for line in text.split("\n")]
        return [line for line in lines if len(line) > 0][:4]
    return []


def check_document(path, type):
    file = Path(path)

    # check name
    stem = file.name.split(".", maxsplit=1)[0]
    match = re.fullmatch(r"([A-Z][a-z]+)-(\d\d)-(\d\d)", stem)
    if not match:
        log(f"'{file.name}' doesn't meet name requirements")
        return False
    author, assignment, fileno = match.groups()

    # check header
    header = read_header_lines(file, type)
    if len(header) != 4:
        log(f"'{file.name}' doesn't have 4 header lines")
        return False

    # check header line #1
    match = re.fullmatch(r"# ([A-Z][a-z]+), ([A-Z][a-z]+)", header[0].strip())
    if not match or match.group(1) != author:
        log(f"'{file.name}' has invalid header line #1")
        return False

    # check header line #2
    match = re.fullmatch(r"# (100\d-\d\d\d-\d\d\d)", header[1].strip())
    if not match:
        log(f"'{file.name}' has invalid header line #2")
        return False

    # check header line #3
    match = re.fullmatch(r"# (\d\d\d\d-\d\d-\d\d)", header[2].strip())
    if not match:
        log(f"'{file.name}' has invalid header line #3")
        return False

    # check header line #4
    match = re.fullmatch(r"# Assignment-(\d\d)-(\d\d)", header[3].strip())
    if not match or match.group(1) != assignment or match.group(2) != fileno:
        log(f"'{file.name}' has invalid header line #4")
        return False

    return author, assignment, fileno


def check_dir(path):
    folder = Path(path)
    dirname = folder.name
    match = re.fullmatch(r"([A-Z][a-z]+)-(\d\d)", dirname)
    if not match:
        log(f"'{folder}' doesn't meet name requirements")
        return False
    author, assignment = match.groups()

    # check individual documents
    success = True
    authors, assignments, filenos = set(), set(), set()
    for document in folder.iterdir():
        result = check_document(document, check_file_type(document))
        if not result:
            success = False
            continue
        authors.add(result[0])
        assignments.add(result[1])
        if result[2] in filenos:
            log(f"'{document.name}' has duplicate document number")
            return False
        filenos.add(result[2])

    # check integrity
    if len(authors) > 1:
        log(f"'{folder}' has files with invalid author")
        return False
    if len(assignments) > 1:
        log(f"'{folder}' has files with invalid assignment number")
        return False

    return (author, assignment) if success else False


def check_zip(path):
    file = Path(path)
    z = zipfile.ZipFile(file)

    # check filename
    match = re.fullmatch(r"([A-Z][a-z]+)-(\d\d).zip", file.name)
    if not match:
        log(f"'{file.name}' doesn't meet name requirements")
        return False
    author, assignment = match.groups()

    # extract to a temporary directory
    with tempfile.TemporaryDirectory() as tmp:
        z.extractall(tmp)

        # there should only be single directory
        dirs = list(Path(tmp).iterdir())
        if len(dirs) != 1:
            log(f"'{file.name}' needs to have a single folder")
            return False
        if not dirs[0].is_dir():
            log(f"'{file.name}' needs to have a single folder")
            return False
        result = check_dir(dirs[0])
        if not result:
            return False

    if result[0] != author:
        log(f"'{dirs[0].name}' has invalid author")
        return False
    if result[1] != assignment:
        log(f"'{dirs[0].name}' has invalid assignment number")
        return False

    return author, assignment


def check(path):
    file = Path(path)
    if not file.exists():
        log(f"'{file.name}' doesn't exist")
        return False
    if file.is_dir():
        return check_dir(file)
    filetype = check_file_type(path)
    if filetype == "unknown":
        log(f"'{file.name}' has unknown filetype")
        return False
    if filetype == "zip":
        return check_zip(file)
    return check_document(file)


if __name__ == "__main__":
    args = parse_arguments()
    if not check(args.path):
        sys.exit(1)
    print("Looks good!")
