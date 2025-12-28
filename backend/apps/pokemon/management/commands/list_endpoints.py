"""
Django management command to list all API endpoints
Usage: python manage.py list_endpoints
"""
from django.core.management.base import BaseCommand
from django.urls import get_resolver
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSet
from django.urls.resolvers import URLPattern, URLResolver
from django.urls import reverse


class Command(BaseCommand):
    help = 'List all API endpoints in the Django application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='table',
            choices=['table', 'json', 'simple'],
            help='Output format: table (default), json, or simple'
        )

    def handle(self, *args, **options):
        output_format = options['format']
        
        # Get the main URL resolver
        resolver = get_resolver()
        
        endpoints = []
        self._extract_endpoints(resolver.url_patterns, '', endpoints)
        
        # Sort by URL
        endpoints.sort(key=lambda x: x['url'])
        
        if output_format == 'json':
            import json
            self.stdout.write(json.dumps(endpoints, indent=2))
        elif output_format == 'simple':
            for endpoint in endpoints:
                methods = ', '.join(endpoint['methods'])
                self.stdout.write(f"{methods:20} {endpoint['url']}")
        else:  # table format
            self._print_table(endpoints)
        
        # Print WebSocket endpoints separately
        self._print_websocket_endpoints()

    def _extract_endpoints(self, patterns, prefix, endpoints):
        """Recursively extract all URL patterns"""
        for pattern in patterns:
            if isinstance(pattern, URLResolver):
                # Recursively process nested URL patterns
                new_prefix = prefix + str(pattern.pattern)
                self._extract_endpoints(pattern.url_patterns, new_prefix, endpoints)
            elif isinstance(pattern, URLPattern):
                # Extract view information
                url_path = prefix + str(pattern.pattern)
                view = pattern.callback
                
                # Skip admin views
                if 'admin' in url_path.lower():
                    continue
                
                # Get HTTP methods
                methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                if hasattr(view, 'cls'):
                    # ViewSet - check which actions are available
                    viewset = view.cls
                    if hasattr(viewset, 'get_extra_actions'):
                        extra_actions = viewset.get_extra_actions()
                        # Get standard CRUD methods from ViewSet
                        if hasattr(viewset, 'list'):
                            methods = ['GET']
                        if hasattr(viewset, 'create'):
                            methods.append('POST')
                        if hasattr(viewset, 'retrieve'):
                            methods = ['GET']
                        if hasattr(viewset, 'update'):
                            methods = ['PUT', 'PATCH']
                        if hasattr(viewset, 'destroy'):
                            methods = ['DELETE']
                elif hasattr(view, 'http_method_names'):
                    methods = [m.upper() for m in view.http_method_names if m.upper() != 'HEAD']
                
                # Get view name/description
                view_name = getattr(view, '__name__', str(view))
                if hasattr(view, 'cls'):
                    view_name = view.cls.__name__
                
                endpoints.append({
                    'url': url_path,
                    'methods': methods,
                    'view': view_name,
                    'name': getattr(pattern, 'name', None)
                })

    def _print_table(self, endpoints):
        """Print endpoints in a formatted table"""
        self.stdout.write("\n" + "=" * 100)
        self.stdout.write(self.style.SUCCESS("REST API ENDPOINTS"))
        self.stdout.write("=" * 100)
        
        # Group by base URL
        grouped = {}
        for endpoint in endpoints:
            # Extract base URL (before any <pk> or similar)
            base_url = endpoint['url'].split('<')[0].rstrip('/')
            if base_url not in grouped:
                grouped[base_url] = []
            grouped[base_url].append(endpoint)
        
        for base_url in sorted(grouped.keys()):
            self.stdout.write(f"\n{self.style.WARNING(base_url)}")
            for endpoint in grouped[base_url]:
                methods_str = ', '.join(endpoint['methods'])
                self.stdout.write(f"  {self.style.HTTP_INFO(methods_str):<25} {endpoint['url']}")
                if endpoint.get('view'):
                    self.stdout.write(f"    View: {endpoint['view']}")
    
    def _print_websocket_endpoints(self):
        """Print WebSocket endpoints"""
        self.stdout.write("\n" + "=" * 100)
        self.stdout.write(self.style.SUCCESS("WEBSOCKET ENDPOINTS"))
        self.stdout.write("=" * 100)
        
        try:
            from apps.pokemon.routing import websocket_urlpatterns
            for pattern in websocket_urlpatterns:
                url = str(pattern.pattern)
                self.stdout.write(f"  {self.style.HTTP_INFO('WEBSOCKET'):<25} ws://localhost:8000/{url}")
        except ImportError:
            pass

