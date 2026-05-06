"""
CLI entry point for web-all v5.
Provides command-line interface for all cloning modes and features.
"""

import argparse
import asyncio
import sys
import json
from pathlib import Path
from typing import Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='web-all',
        description='The Internet\'s Universal Reproduction Engine v5.0.0',
        epilog='For more information, visit: https://github.com/web-all/web-all'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='web-all 5.0.0'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # ========== CLONE COMMAND ==========
    clone_parser = subparsers.add_parser(
        'clone',
        help='Clone a website with specified visibility mode'
    )
    clone_parser.add_argument('url', help='Target website URL')
    clone_parser.add_argument(
        '--output', '-o',
        default='./output',
        help='Output directory (default: ./output)'
    )
    clone_parser.add_argument(
        '--mode', '-m',
        choices=['surface', 'deep', 'invisible', 'shadow', 'all'],
        default='surface',
        help='Visibility mode (default: surface)'
    )
    clone_parser.add_argument(
        '--depth', '-d',
        type=int,
        default=5,
        help='Crawl depth (default: 5)'
    )
    clone_parser.add_argument(
        '--concurrency', '-c',
        type=int,
        default=10,
        help='Concurrent requests (default: 10)'
    )
    clone_parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    clone_parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Run browser headless (default: True)'
    )
    clone_parser.add_argument(
        '--no-headless',
        action='store_false',
        dest='headless',
        help='Show browser window'
    )
    clone_parser.add_argument(
        '--stealth',
        action='store_true',
        default=True,
        help='Enable stealth mode (default: True)'
    )
    clone_parser.add_argument(
        '--cookies',
        help='JSON file with cookies for authenticated cloning'
    )
    clone_parser.add_argument(
        '--extract-components',
        action='store_true',
        help='Extract UI components'
    )
    clone_parser.add_argument(
        '--extract-tokens',
        action='store_true',
        help='Extract design tokens'
    )
    
    # ========== AI COMMANDS ==========
    ai_parser = subparsers.add_parser('ai', help='AI-powered features')
    ai_subparsers = ai_parser.add_subparsers(dest='ai_command')
    
    # AI analyze
    analyze_parser = ai_subparsers.add_parser('analyze', help='Analyze cloned site with AI')
    analyze_parser.add_argument('input_dir', help='Directory of cloned site')
    analyze_parser.add_argument(
        '--provider',
        choices=['anthropic', 'openai', 'ollama'],
        default='anthropic',
        help='AI provider (default: anthropic)'
    )
    analyze_parser.add_argument(
        '--model',
        default='claude-3-7-sonnet-20241022',
        help='AI model to use'
    )
    analyze_parser.add_argument(
        '--output',
        help='Output file for analysis results'
    )
    
    # AI improve
    improve_parser = ai_subparsers.add_parser('improve', help='Get AI improvement suggestions')
    improve_parser.add_argument('input_dir', help='Directory of cloned site')
    improve_parser.add_argument(
        '--fix-accessibility',
        action='store_true',
        help='Fix accessibility issues'
    )
    improve_parser.add_argument(
        '--fix-seo',
        action='store_true',
        help='Fix SEO issues'
    )
    improve_parser.add_argument(
        '--optimize-performance',
        action='store_true',
        help='Optimize performance'
    )
    
    # ========== GENERATE COMMAND ==========
    generate_parser = subparsers.add_parser(
        'generate',
        help='Generate modern codebase from cloned site'
    )
    generate_parser.add_argument('input_dir', help='Directory of cloned site')
    generate_parser.add_argument(
        '--framework',
        choices=['nextjs', 'react', 'vue'],
        default='nextjs',
        help='Target framework (default: nextjs)'
    )
    generate_parser.add_argument(
        '--output', '-o',
        default='./generated',
        help='Output directory for generated code'
    )
    generate_parser.add_argument(
        '--typescript',
        action='store_true',
        default=True,
        help='Use TypeScript (default: True)'
    )
    generate_parser.add_argument(
        '--tailwind',
        action='store_true',
        default=True,
        help='Use Tailwind CSS (default: True)'
    )
    generate_parser.add_argument(
        '--shadcn',
        action='store_true',
        default=True,
        help='Use shadcn/ui components (default: True)'
    )
    
    # ========== EXPORT COMMAND ==========
    export_parser = subparsers.add_parser(
        'export',
        help='Export cloned data in various formats'
    )
    export_parser.add_argument('input_dir', help='Directory of cloned site')
    export_parser.add_argument(
        '--format',
        choices=['zip', 'har', 'warcd', 'figma', 'storybook'],
        required=True,
        help='Export format'
    )
    export_parser.add_argument(
        '--output', '-o',
        help='Output file path'
    )
    
    # ========== SERVE COMMAND ==========
    serve_parser = subparsers.add_parser(
        'serve',
        help='Start web GUI server'
    )
    serve_parser.add_argument(
        '--port', '-p',
        type=int,
        default=8000,
        help='Server port (default: 8000)'
    )
    serve_parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Server host (default: 0.0.0.0)'
    )
    serve_parser.add_argument(
        '--gui',
        action='store_true',
        default=True,
        help='Serve web GUI (default: True)'
    )
    
    # ========== DEPLOY COMMAND ==========
    deploy_parser = subparsers.add_parser(
        'deploy',
        help='Deploy generated site to hosting platform'
    )
    deploy_parser.add_argument('input_dir', help='Directory to deploy')
    deploy_parser.add_argument(
        '--platform',
        choices=['vercel', 'netlify', 'docker'],
        required=True,
        help='Deployment platform'
    )
    deploy_parser.add_argument(
        '--project-name',
        help='Project name on deployment platform'
    )
    
    # ========== CONFIG COMMAND ==========
    config_parser = subparsers.add_parser(
        'config',
        help='Manage configuration'
    )
    config_subparsers = config_parser.add_subparsers(dest='config_command')
    
    # Config show
    config_subparsers.add_parser('show', help='Show current configuration')
    
    # Config set
    set_parser = config_subparsers.add_parser('set', help='Set configuration value')
    set_parser.add_argument('key', help='Configuration key')
    set_parser.add_argument('value', help='Configuration value')
    
    # Config reset
    config_subparsers.add_parser('reset', help='Reset configuration to defaults')
    
    # ========== INFO COMMAND ==========
    info_parser = subparsers.add_parser(
        'info',
        help='Show system information'
    )
    info_parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle commands
    if args.command == 'clone':
        handle_clone(args)
    elif args.command == 'ai':
        handle_ai(args)
    elif args.command == 'generate':
        handle_generate(args)
    elif args.command == 'export':
        handle_export(args)
    elif args.command == 'serve':
        handle_serve(args)
    elif args.command == 'deploy':
        handle_deploy(args)
    elif args.command == 'config':
        handle_config(args)
    elif args.command == 'info':
        handle_info(args)
    else:
        parser.print_help()
        sys.exit(0)


def handle_clone(args):
    """Handle clone command."""
    print(f"🚀 Starting web-all clone...")
    print(f"   URL: {args.url}")
    print(f"   Mode: {args.mode}")
    print(f"   Output: {args.output}")
    print(f"   Depth: {args.depth}")
    print(f"   Concurrency: {args.concurrency}")
    
    try:
        from .core.cloner import WebsiteCloner, VisibilityMode
        from .core.crawler import AsyncCrawler
        from .core.visibility_manager import VisibilityManager
        
        # Load cookies if provided
        session_cookies = None
        if args.cookies:
            with open(args.cookies, 'r') as f:
                session_cookies = json.load(f)
        
        # Initialize cloner
        cloner = WebsiteCloner(
            base_url=args.url,
            output_dir=args.output,
            mode=getattr(VisibilityMode, args.mode.upper(), VisibilityMode.SURFACE),
            depth=args.depth,
            concurrency=args.concurrency,
            delay=args.delay,
            stealth_mode=args.stealth,
            session_cookies=session_cookies,
        )
        
        # Run based on mode
        if args.mode == 'all':
            async def run_all():
                crawler = AsyncCrawler(args.url, headless=args.headless)
                manager = VisibilityManager(args.url, args.output)
                return await manager.run_all_modes(cloner, crawler)
            
            result = asyncio.run(run_all())
        else:
            result = asyncio.run(cloner.clone_site())
        
        print(f"\n✅ Clone complete!")
        print(f"   Pages: {result.get('pages_cloned', 'N/A')}")
        print(f"   Assets: {result.get('assets_downloaded', 'N/A')}")
        print(f"   Output: {result.get('output_dir', args.output)}")
        
    except Exception as e:
        logger.error(f"Clone failed: {e}")
        sys.exit(1)


def handle_ai(args):
    """Handle AI commands."""
    if not args.ai_command:
        print("Please specify an AI command: analyze, improve")
        sys.exit(1)
    
    print(f"🤖 AI feature: {args.ai_command}")
    print("   (AI integration coming soon - requires API key)")


def handle_generate(args):
    """Handle generate command."""
    print(f"⚡ Generating {args.framework} codebase...")
    print(f"   Input: {args.input_dir}")
    print(f"   Output: {args.output}")
    print("   (Code generation coming soon)")


def handle_export(args):
    """Handle export command."""
    print(f"📦 Exporting to {args.format} format...")
    print(f"   Input: {args.input_dir}")
    if args.output:
        print(f"   Output: {args.output}")
    print("   (Export feature coming soon)")


def handle_serve(args):
    """Handle serve command."""
    print(f"🌐 Starting web server...")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    
    try:
        from .api.server import start_server
        start_server(host=args.host, port=args.port)
    except ImportError:
        print("FastAPI not installed. Run: pip install fastapi uvicorn")
        sys.exit(1)


def handle_deploy(args):
    """Handle deploy command."""
    print(f"🚀 Deploying to {args.platform}...")
    print(f"   Input: {args.input_dir}")
    if args.project_name:
        print(f"   Project: {args.project_name}")
    print("   (Deployment feature coming soon)")


def handle_config(args):
    """Handle config commands."""
    from web_all_v2.config.settings import get_config
    
    if not args.config_command:
        print("Please specify a config command: show, set, reset")
        sys.exit(1)
    
    config = get_config()
    
    if args.config_command == 'show':
        print("Current configuration:")
        print(json.dumps({
            "version": config.version,
            "debug": config.debug,
            "log_level": config.log_level,
        }, indent=2))
    
    elif args.config_command == 'reset':
        print("Configuration reset to defaults")
    
    elif args.config_command == 'set':
        print(f"Setting {args.key} = {args.value}")
        print("(Config persistence coming soon)")


def handle_info(args):
    """Handle info command."""
    from web_all_v2 import __version__
    
    info = {
        "name": "web-all",
        "version": __version__,
        "python_version": sys.version,
        "platform": sys.platform,
    }
    
    if args.json:
        print(json.dumps(info, indent=2))
    else:
        print(f"web-all v{info['version']}")
        print(f"Python: {info['python_version']}")
        print(f"Platform: {info['platform']}")


if __name__ == '__main__':
    main()
