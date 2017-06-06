import unittest
import coverage

from flask_script import Manager
from project import create_app, db
from project.api.models import User

app = create_app()
manager = Manager(app)
_cov = coverage.coverage(
    branch=True, include='project/*',
    omit=[
            'project/tests/*',
            'project/db/*'
          ]
)
_cov.start()


@manager.command
def recreate_db():
    """Recreates a database."""
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.command
def seed_db():
    """Seeds the database."""
    db.session.add(User(username="test", email="test@t.com"))
    db.session.add(User(username="test2", email="test2@t.com"))
    db.session.commit()


@manager.command
def test():
    """Runs the tests without code coverage"""
    tests = unittest.TestLoader().discover('project/tests', pattern="test*.py")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def cov():
    """Runs the unit tests with coverage"""
    tests = unittest.TestLoader().discover('project/tests', pattern="test*.py")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        _cov.stop()
        _cov.save()
        print('Coverage summary:')
        _cov.report()
        _cov.erase()
        return 0
    return 1

if __name__ == '__main__':
    manager.run()
