from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.urls import URLResolver, URLPattern
import codecs
import json
import ast
import inspect
import textwrap
from tabulate import tabulate
from itertools import groupby


class Command(BaseCommand):
    help = 'Extracts Django views, urls & permissions'

    def add_arguments(self, parser):
        DEFAULT_FILE = 'VIEWS'
        parser.add_argument('-g', '--group', type=str, required=False, default='v', choices=['v', 'u', 'p'], help='group by View (v) [Default], URL (u) [Raw], Permission (p)',)
        parser.add_argument('-o', '--output_file', type=str, required=False, default=DEFAULT_FILE, help=f'the output text file (default {DEFAULT_FILE})',)
        parser.add_argument('-f', '--format', type=str, required=False, default='json', choices=['json', 'table'], help=f'output format (json or table)',)

    def output(self, urls_list, mode, output_file, output_format):
        data = []
        if mode == 'u':
            data = urls_list
        elif mode == 'v':
            urls_list = sorted(urls_list, key=lambda i: i['view_path'])
            for key, group in groupby(urls_list, lambda x: (x['view_path'], x['view_name'], x['login_required'], x['permission_required'])):
                group_data = list(group)
                data.append({
                    'view_path': key[0],
                    'view_name': key[1],
                    'login_required': key[2],
                    'permission_required': key[3],
                    'url_urls': '\n'.join([u['url_url'] for u in group_data]),
                    'url_names': '\n'.join([u['url_name'] or '' for u in group_data])
                })
        elif mode == 'p':
            urls_list = sorted(urls_list, key=lambda i: i['permission_required'])
            for key, group in groupby(urls_list, lambda x: x['permission_required']):
                group_data = list(group)
                data.append({
                    'permission_required': key,
                    'view_paths': '\n'.join([u['view_path'] for u in group_data]),
                    'view_names': '\n'.join([u['view_name'] for u in group_data]),
                    'login_required': '\n'.join(['True' if u['login_required'] else 'False' for u in group_data]),
                    'url_urls': '\n'.join([u['url_url'] for u in group_data]),
                    'url_names': '\n'.join([u['url_name'] or '' for u in group_data])
                })

        with codecs.open(output_file, 'w', 'utf-8') as f:
            if output_format == 'json':
                json.dump(data, f)
            elif output_format == 'table':
                f.write(tabulate(data, headers="keys", tablefmt="grid", showindex="always"))

    def handle(self, *args, **options):

        mode = options['group']
        output_file = options['output_file']
        output_format = options['format']

        def get_perms(target):

            perm_info = {
                'perms': [],
                'login_required': False
            }

            def visit_FunctionDef(node):
                for n in node.decorator_list:
                    if isinstance(n, ast.Call):
                        name = n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id
                    else:
                        name = n.attr if isinstance(n, ast.Attribute) else n.id
                    if name == 'permission_required':
                        perm_info['perms'].append(n.args[0].s)
                    elif name == 'login_required':
                        perm_info['login_required'] = True

            node_iter = ast.NodeVisitor()
            node_iter.visit_FunctionDef = visit_FunctionDef
            node_iter.visit(ast.parse(textwrap.dedent(inspect.getsource(target))))
            return perm_info['login_required'], '|'.join(perm_info['perms'])

        urls_list = []

        def get_url_info(pattern, parent_pattern, parent_namespace):
            login_required, permission_required = get_perms(pattern.callback)
            if parent_namespace and not parent_namespace == 'None':
                full_name = f'{parent_namespace}:{pattern.name}'
            else:
                full_name = pattern.name
            urls_list.append({
                'url_name': full_name,
                'url_url': URLResolver._join_route(str(parent_pattern), str(pattern.pattern)),
                'view_name': pattern.callback.__name__,
                'view_path': pattern.lookup_str,
                'login_required': login_required,
                'permission_required': permission_required,
            })

        def get_all_urls(parent_pattern, parent_namespace, urlpatterns):
            for pattern in urlpatterns:
                if isinstance(pattern, URLResolver):
                    get_all_urls(pattern.pattern, pattern.namespace, pattern.url_patterns)
                elif isinstance(pattern, URLPattern):
                    get_url_info(pattern, parent_pattern, parent_namespace)

        get_all_urls('', '', __import__(settings.ROOT_URLCONF).urls.urlpatterns)

        self.output(urls_list, mode, output_file, output_format)

        self.stdout.write('Done - see output at {0}'.format(repr(output_file)))
