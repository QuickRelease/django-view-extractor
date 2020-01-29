# django-view-extractor
Extract a list of Django views, urls and permissions

## Installation
Either install directly:

```
pip install git+https://github.com/QuickRelease/django-view-extractor.git
```

or add to your requirements.txt file:

```
-e git://github.com/QuickRelease/django-view-extractor#egg=django-view-extractor
```

## Usage


```
python manage.py django_view_extractor [-h] [-g {v,u,p}] [-o OUTPUT_FILE] [-f {json,table}]
```

optional arguments:
```
  -h, --help            show help
  -g {v,u,p}, --group {v,u,p}
                        group by View (v) [Default], URL (u) [Raw], Permission (p)
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        the output text file (default VIEWS)
  -f {json,table}, --format {json,table}
                        output format (default: json)
```
