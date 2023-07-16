import time

def measure_time(st):
    '''
    Custom function for measuring time of code execution
    
    Args:
        execution_time: execution time in seconds.
    '''
    execution_time = time.time() - st
    
    hours = int(execution_time / 3600)
    minutes = int((execution_time % 3600) / 60)
    seconds = int(execution_time % 60)
    print(f'Execution time: {hours} hours {minutes} minutes {seconds} seconds')
