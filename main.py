import fnmatch
import argparse
import frontmatter
import yaml


from io import BytesIO
from tqdm import tqdm
from pathlib import Path


def get_markdown_files(path, ignore_list):
    matches = []
    filenames = [p.relative_to(Path.cwd()) for p in path.rglob('*.md')]
    for ignore in ignore_list:
        filenames = [n for n in filenames if not fnmatch.fnmatch(n, ignore)]
    matches.extend(filenames)

    return matches

def generate_output(md_files, default_front_matter, output_dir):
    for _, file in enumerate(tqdm(md_files)):
        post = frontmatter.load(file, **default_front_matter)

        if (('publish', False) in post.metadata.items()):
            print(f'Skipped {file}')
            continue
        
        # print(f'Processing: {file}')
        o = BytesIO()
        frontmatter.dump(post, o)
        # print(o.getvalue().decode('utf-8'))
        out_file = output_dir / file
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, 'wb') as f:
            f.write(o.getvalue())
        o.close()


def main():
    my_parser = argparse.ArgumentParser(
        prog='autofm', 
        usage='%(prog)s [options] path',
        description='Add YAML front-matter if absent')

    # Add the arguments
    my_parser.add_argument('-p', '--path',
                        type=lambda p: Path(p).absolute(),
                        default=Path.cwd().absolute(),
                        help='path to the folder containing markdown files (defaults to cwd)')

    my_parser.add_argument('--ignore',
                        type=lambda p: Path(p).absolute(),
                        default=Path.cwd().absolute() / '.export-ignore',
                        help='path to the .export-ignore file (defaults to cwd/.export-ignore)')

    my_parser.add_argument('--default-front-matter',
                        type=lambda p: Path(p).absolute(),
                        default=Path.cwd().absolute() / 'default_front_matter.yml',
                        help='path to the default front matter YAML file (defaults to cwd/default_front_matter.yml)')

    my_parser.add_argument('-o', '--output',
                        type=lambda p: Path(p).absolute(),
                        default=Path.cwd().absolute() / 'output',
                        help='path to the output folder (defaults to cwd/output)')

    # Execute the parse_args() method
    args = my_parser.parse_args()

    input_folder = args.path
    ignore_list_path = args.ignore
    default_yaml_file = args.default_front_matter
    output_folder = args.output

    output_folder.mkdir(parents=True, exist_ok=True)

    ignore_list = []
    if (ignore_list_path.exists()):
        with open(ignore_list_path, encoding='utf-8') as f:
            ignore_list = f.readlines()
        ignore_list = [x.rstrip() for x in ignore_list] 

    default_yaml = {
        'publish': False,
        'author': 'Aadam'
    }

    if (default_yaml_file.exists()):
        with open(default_yaml_file, encoding='utf-8') as f:
            default_yaml = yaml.safe_load(f)


    md_files = get_markdown_files(input_folder, ignore_list)

    generate_output(md_files, default_yaml, output_folder)



if __name__ == "__main__":
    main()