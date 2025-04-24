import click


@click.command()
@click.option('--m', type=str, required=True)
def main(m):
    with open('some-file.txt', 'a') as f:
        f.write(f'{m}\n')

if __name__ == '__main__':
    main()