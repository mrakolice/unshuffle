import pathlib

import jinja2


class JinjaLoader:
    def __init__(self, root_path: str = '.'):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(root_path),
        )

    def render(self, path, **kwargs):
        return self.env.get_template(path).render(**kwargs)


class SqlLoader(JinjaLoader):
    def __init__(self):
        sql_path = str(pathlib.Path(__file__).parent.joinpath('sql'))

        super().__init__(sql_path)
