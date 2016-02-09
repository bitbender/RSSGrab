from behave import *
from config import Config


@given("we created a config object from a file")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.conf = Config('config.yml')


@when("we access the parameters")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert context.conf['database']['type'] == 'mongo'


@then("the parameters defined in the file should be accessible")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert context.failed is False


@when("we add a new element")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.conf['database']['foo'] = 'bari'


@then("the config object should be marked as modified")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    print(context.conf.modified)
    print(context.conf['database']['foo'])
