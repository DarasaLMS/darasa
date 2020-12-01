# Darasa LMS

The perfect virtual classroom built in Kenya for the world.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Before you start working on this project, make sure you have the following packages installed:

* python3
* virtualenv
* virtualenvwrapper
* pip

Clone the repo:

```bash
git clone https://github.com/darasa-LMS/darasa.git
```

Create a virtualenv workspace

```{bash}
cd darasa
mkvirtualenv darasa
```

### Installing

A step by step series of examples that tell you how to get a development env running

Within your virtualenv workspace, install dependecies:

```{bash}
pip install -r requirements/<env>.txt
```

Copy .env.example to .env and fill in the missing values

```{bash}
cp .env.example .env
```

Run migrations

```{bash}
python manage.py migrate
```

Populate the database

```{bash}
python manage.py populate_database
```

Create a superuser for login

```{bash}
python manage.py createsuperuser
```

Run your server

```{bash}
python manage.py runserver
```

And run your celery workers

```{bash}
celery -A darasa.celery worker -l info
```

That's it!

Go to http://localhost:8000/admin

## Running the tests

TBD

### And coding style tests

Linting is done using [Black code style](https://black.readthedocs.io/en/stable/the_black_code_style.html)

## Deployment

TBD

## Built With

* [Django](https://www.djangoproject.com/) - The web framework for perfectionists with deadlines.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/darasa-LMS/darasa/tags).

## Authors

* **Antony Orenge** - *Initial work* - [@antorenge](https://github.com/antorenge)
* **Lewis Orenge** - *Initial work* - [@lewisorenge](https://github.com/lewisorenge)

See also the list of [contributors](https://github.com/darasa-LMS/darasa/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details

## Acknowledgments
