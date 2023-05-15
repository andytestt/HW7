import os
import shutil
import sys
import zipfile, tarfile, gzip, rarfile, py7zr, tempfile


def clean_folder():
    EXTENSIONS = {
        'images': ('JPEG', 'PNG', 'JPG', 'SVG', 'BMP'),
        'videos': ('AVI', 'MP4', 'MOV', 'MKV'),
        'documents': ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
        'audio': ('MP3', 'OGG', 'WAV', 'AMR'),
        'archives': ('ZIP', 'GZ', 'TAR', 'RAR', '7z'),
    }


    def process_directory(directory, extensions):
        ignore_folders = ['archives', 'video', 'audio', 'documents', 'images']
        archive_path = None
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignore_folders]
            for filename in files:
                name, extension = os.path.splitext(filename)
                extension = extension.lstrip('.').lower()

                if extension in extensions:
                    category = extensions[extension]
                    dest_dir = os.path.join(directory, category)
                    os.makedirs(dest_dir, exist_ok=True)
                    dest_path = os.path.join(dest_dir, normalize(name) + '.' + extension)
                    src_path = os.path.join(root, filename)
                    shutil.move(src_path, dest_path)
                elif extension in ('zip', 'gz', 'tar', 'rar', '7z'):
                    archive_path = os.path.join(root, filename)
                    extract_archives(archive_path, extensions, directory)
            for folder in dirs:
                if folder not in ignore_folders:
                    folder_path = os.path.join(root, folder)
                    process_directory(folder_path, extensions)
                    for subfolder in os.listdir(folder_path):
                        subfolder_path = os.path.join(folder_path, subfolder)
                        if os.path.isdir(subfolder_path):
                            for filename in os.listdir(subfolder_path):
                                name, extension = os.path.splitext(filename)
                                extension = extension.lstrip('.').lower()
                                if extension in extensions:
                                    category = extensions[extension]
                                    dest_dir = os.path.join(directory, category)
                                    os.makedirs(dest_dir, exist_ok=True)
                                    dest_path = os.path.join(dest_dir, normalize(name) + '.' + extension)
                                    src_path = os.path.join(subfolder_path, filename)
                                    shutil.move(src_path, dest_path)
        
    def sort_files(directory):
        if not os.path.isdir(directory):
            print(f"{directory} is not a valid directory")
            return
        extensions = {ext.lower(): category for category, ext_list in EXTENSIONS.items() for ext in ext_list}
        process_directory(directory, extensions)
        
        known_extensions = set(extensions.keys())
        unknown_extensions = set()

        for root, dirs, files in os.walk(directory):
            for filename in files:
                extension = os.path.splitext(filename)[1].lstrip('.').lower()
                if extension not in known_extensions and extension not in ('zip', 'gz', 'tar', 'rar', '7z'):
                    unknown_extensions.add(extension)

        print('Known extensions:', sorted(known_extensions))
        print('Unknown extensions:', sorted(unknown_extensions))

        for category in EXTENSIONS.keys():
            category_dir = os.path.join(directory, category)
            category_files = os.listdir(category_dir)
            print(f"{category.capitalize()}: {category_files}")

        remove_empty_directories(directory)

    def remove_empty_directories(directory):
        for root, dirs, files in os.walk(directory, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"Removed empty directory: {dir_path}")

    def extract_archives(directory):
        try:
            archives_dir = os.path.join(directory, 'archives')
            os.makedirs(archives_dir, exist_ok=True)
            extensions = {'zip': 'zip', 'tar': 'tar', 'gz': 'tar', 'rar': 'rar', '7z': '7z'}

            for root, dirs, files in os.walk(directory):
                for filename in files:
                    name, extension = os.path.splitext(filename)
                    extension = extension.lstrip('.').lower()
                    if extension in extensions:
                        archive_path = os.path.join(root, filename)
                        archive_name = os.path.splitext(filename)[0]
                        dest_dir = os.path.join(archives_dir, archive_name)
                        os.makedirs(dest_dir, exist_ok=True)

                        if extension == 'zip':
                            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                                zip_ref.extractall(dest_dir)
                        elif extension in ('tar', 'gz'):
                            with tarfile.open(archive_path, 'r:*') as tar_ref:
                                tar_ref.extractall(dest_dir)
                        elif extension == 'rar':
                            with rarfile.RarFile(archive_path, 'r') as rar_ref:
                                rar_ref.extractall(dest_dir)
                        elif extension == '7z':
                            with py7zr.SevenZipFile(archive_path, 'r') as seven_zip_ref:
                                seven_zip_ref.extractall(dest_dir)

                        os.remove(archive_path)

            # recursively extract archives in subdirectories
            for dirpath, dirnames, filenames in os.walk(directory):
                for dirname in dirnames:
                    extract_archives(os.path.join(dirpath, dirname))

            return "Extraction successful"
        
        except Exception as e:
            return f"Extraction failed: {e}"

    def normalize(filename):
        translit = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g',
            'д': 'd', 'е': 'e', 'є': 'ie', 'ж': 'zh', 'з': 'z',
            'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'i', 'к': 'k',
            'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
            'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
            'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
            'ю': 'iu', 'я': 'ia',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G',
            'Д': 'D', 'Е': 'E', 'Є': 'Ie', 'Ж': 'Zh', 'З': 'Z',
            'И': 'Y', 'І': 'I', 'Ї': 'Yi', 'Й': 'I', 'К': 'K',
            'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P',
            'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F',
            'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
            'Ю': 'Iu', 'Я': 'Ia',
            'ы': 'y', 'э': 'e', 'ё': 'io', 'ъ': '', 'ь': '',
            'Ы': 'y', 'Э': 'e', 'Ё': 'io', 'Ъ': '', 'Ь': ''
        }

        normalized_filename = ''
        for char in filename:
            translit_char = translit.get(char.lower(), char)
            if char.isupper():
                normalized_filename += translit_char.upper()
            elif char.isalnum():
                char = char.lower()
                normalized_filename += translit.get(char, char)
            else:
                normalized_filename += '_'
        return normalized_filename

    if __name__ == "__clean_folder__":
        if len(sys.argv) != 2:
            print("Usage: python sort.py <target_directory>")
            sys.exit(1)
        target_dir = sys.argv[1]
    


        if not os.path.exists(target_dir):
            print("Error: Target directory does not exist.")
            sys.exit(1)
            
        extract_archives(target_dir)    
        sort_files(target_dir)
        

    sys.exit(0)