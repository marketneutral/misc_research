from logbook import Logger, StderrHandler, DEBUG, INFO

log_handler = StderrHandler(
    format_string='[{record.time:%Y-%m-%d %H:%M:%S.%f}]: ' +
    '{record.level_name}: {record.func_name}: {record.message}',
    level=INFO
)
log_handler.push_application()
log = Logger('Algorithm')


def initialize(context):
    # This code runs once when the sim starts up
    log.debug('My debug message')
    log.info('My info message')

