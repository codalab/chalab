import re, csv, os

def convert(path):
    file = open(path, 'r')
    lines = file.readlines()
    file.close()

    arff = True
    libsvm = True

    for line in lines:
        basic_line = line.lower().strip()

        if arff:
            if not (basic_line.startswith('%') or basic_line.startswith('@') or not basic_line):
                arff = False
            elif basic_line == '@data':
                return from_arff(path)

        if libsvm:
            if basic_line and re.match('^[^\ ]+( [^\ \:]*\:[^\ \:]*)+$', basic_line) is None:
                libsvm = False

    if libsvm:
        return from_libsvm(path)

    return from_csv(path)

def from_csv(path):
    origin_path, file = os.path.split(path)

    final_path = os.path.join(origin_path, "csv")
    os.makedirs(final_path, exist_ok=True)

    origin_file = open(path, 'r')

    dialect = csv.Sniffer().sniff(origin_file.read(1024))
    origin_file.seek(0)
    has_header = csv.Sniffer().has_header(origin_file.read(1024))
    origin_file.seek(0)

    #If already in AutoML, we do nothing
    if not has_header and dialect.delimiter == ' ':
        return origin_path


    csv_file = csv.reader(origin_file, dialect)

    final_file = open(os.path.join(final_path, file), "w")

    # Remove header
    if has_header:
        next(csv_file, None)  # skip the headers

    for row in csv_file:
        for val in row:
            final_file.write(val + " ")
        final_file.write("\n")


    origin_file.close()

    final_file.close()

    return final_path


def from_libsvm(path):
    origin_path, file = os.path.split(path)

    final_path = os.path.join(origin_path, "libsvm")
    os.makedirs(final_path, exist_ok=True)

    origin_file = open(path, 'r')
    lines = origin_file.readlines()
    origin_file.close()

    final_file = open(os.path.join(final_path, file), "w")

    final_file.write("libsdfhkfdhfkhsd\n")
    for line in lines:
        final_file.write(line)

    final_file.close()

    return final_path

def from_arff(path):
    origin_path, file = os.path.split(path)

    final_path = os.path.join(origin_path, "arff")
    os.makedirs(final_path, exist_ok=True)

    origin_file = open(path, 'r')
    lines = origin_file.readlines()
    origin_file.close()

    final_file = open(os.path.join(final_path, file), "w")

    attribute = []


    for line in lines:
        if line.strip():
            if line.startswith('@'):
                if line.lower().startswith('@attribute'):
                    attribute.append(line[11:])
            elif line.startswith('%'):
                pass
            else:
                final_file.write(line.replace(",", " "))

    final_file.close()

    final_file_name = open(os.path.join(final_path, os.path.splitext(file)[0] + '_feat.name'), "w")
    for line in attribute:
        final_file_name.write(line)
    final_file_name.close()

    return final_path