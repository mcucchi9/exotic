import os
import subprocess

import click


FNULL = open(os.devnull, 'w')


@click.command()
@click.argument('parent_dir')
def main(parent_dir):
    dirs_to_compress = [
        sub_dir for sub_dir in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, sub_dir))
    ]
    click.echo("The following folders in {} will be compressed: {}".format(parent_dir, dirs_to_compress))
    click.confirm('Do you want to continue?', abort=True)

    for dir_to_compress in dirs_to_compress:
        dir_to_compress_full_path = os.path.join(parent_dir, dir_to_compress)
        archive_full_path = os.path.join(parent_dir, dir_to_compress + '.tar.gz')

        click.echo('Compressing {} into {}'.format(dir_to_compress_full_path, archive_full_path))
        command_compress = 'tar -czvf {} {}'.format(archive_full_path, dir_to_compress_full_path)
        subprocess.call(command_compress, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

        click.echo('Removing {}'.format(dir_to_compress_full_path))
        command_remove = 'rm -rf {}'.format(dir_to_compress_full_path)
        subprocess.call(command_remove, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)


if __name__ == "__main__":
    main()