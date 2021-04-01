This directory is for storing cleaned datasets.

Typical workflow would be:

- some code is initially downloaded to datasets/raw/ directory via a script.
  (using a script encourages reproducibility / is somewhat self documenting about what original data sources are used).

- then a ETL process may occur in which data is read from this raw directory, and saved (a cleaned version) to datasets/processed/ directory.


Note that we may not use this, but its a basic guidline. See the datascience cookiecutter template online for more context of this approach.
