import zipfile

# Specify the path to the zip file and the output text file
zip_path = 'c:\\#\\b2b-marketplace.zip'  # Replace with your zip file path
output_path = 'c:\\#\\output.txt'  # Replace with your desired output file path

with zipfile.ZipFile(zip_path) as z:
    with open(output_path, 'w', encoding='utf-8') as out:
        for file in z.namelist():
            if not file.endswith('/'):  # Skip directories
                try:
                    content = z.read(file).decode('utf-8')
                    out.write(f"filename:{file} : content:({content})\n")
                except UnicodeDecodeError:
                    # Skip or handle non-text files if needed
                    out.write(f"filename:{file} : content:(Binary or non-UTF-8 content skipped)\n")