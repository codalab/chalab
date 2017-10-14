def get_nice_file_size(input_file):
    """
    Credit Rajiv Sharma StackOverflow
    this function will convert bytes to MB.... GB... etc
    """
    num = input_file.size

    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
