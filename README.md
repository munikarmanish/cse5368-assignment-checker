# CSE 5368 Assignment Checker

Dr. Farhad Kamangar has a very strict [folder structure and naming
requirements](https://ranger.uta.edu/~kamangar/CSE-5368-FA21/AssignmentSubmissionGuidelines.html)
for his assignments, so that they can be organized automatically by a script.
So, I wrote this _script_ to check if the submission file meets those
requirements.

## Requirements

- python >= 3.6
- python-docx (to check Word files)
- pymupdf (to check )

```
$ pip install requirements.txt
```


## Usage

Syntax:
```
./check.py <file>
```
where, `<file>` can be the submission zip file, folder, or any file in the
submission folder.

For more info:
```
./check.py --help
```

## Author

Manish Munikar \<manish.munikar@mavs.uta.edu>
