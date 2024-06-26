import logging

def logger(log_print_path, log_error_path):
    # # Path for the print log
    # log_print_path = 'print_logs.txt'
    # # Path for the error log
    # log_error_path = 'error.log'

    # Create a logger for print statements
    print_logger = logging.getLogger('print_logger')
    print_logger.setLevel(logging.INFO)

    # Create a FileHandler for the print logger
    print_handler = logging.FileHandler(log_print_path)
    print_formatter = logging.Formatter('%(asctime)s - %(message)s')
    print_handler.setFormatter(print_formatter)
    print_logger.addHandler(print_handler)

    # Create a logger for error messages
    error_logger = logging.getLogger('error_logger')
    error_logger.setLevel(logging.ERROR)

    # Create a FileHandler for the error logger
    error_handler = logging.FileHandler(log_error_path)
    error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    error_handler.setFormatter(error_formatter)
    error_logger.addHandler(error_handler)

# Function to redirect print statements to the print logger
    def print_to_logger(*args, **kwargs):
        message = ' '.join(map(str, args))
        print_logger.info(message)

    # Redefine the built-in print to use the new function
    global print
    print = print_to_logger

    # Return the error logger for use in logging errors
    return error_logger
