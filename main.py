import argparse
import sys
from pathlib import Path
from core.agent import Agent
from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description='Agent')
    parser.add_argument('--config', type=str, default='config/config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--mode', type=str, choices=['cli', 'api'], default='api',
                        help='Run mode: cli or api')
    parser.add_argument('--ocr', type=str, help='OCR a file (CLI mode)')
    parser.add_argument('--engine', type=str, help='OCR engine to use')
    parser.add_argument('--prompt', type=str, help='LLM prompt (CLI mode)')
    
    args = parser.parse_args()
    
    agent = Agent(args.config)
    
    if args.mode == 'cli':
        if args.ocr:
            engine_name = args.engine or agent.config.get('plugins.ocr.active')
            ocr_plugin = agent.registry.get('ocr', engine_name)
            
            if not ocr_plugin:
                print(f"Error: OCR engine '{engine_name}' not found")
                sys.exit(1)
            
            print(f"Processing {args.ocr} with {engine_name}...")
            result = ocr_plugin.process(args.ocr)
            
            print(f"\n{'='*80}")
            print(f"Engine: {engine_name}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"{'='*80}\n")
            print(result.text)
            print(f"\n{'='*80}")
            print(f"Metadata: {result.metadata}")
        
        elif args.prompt:
            llm_plugin = agent.get_active_plugin('llm')
            
            if not llm_plugin:
                print("Error: No active LLM provider")
                sys.exit(1)
            
            print(f"Generating response...")
            result = llm_plugin.generate(args.prompt)
            
            print(f"\n{'='*80}")
            print(result.text)
            print(f"\n{'='*80}")
            print(f"Tokens used: {result.tokens_used}")
        
        else:
            parser.print_help()
    
    elif args.mode == 'api':
        import uvicorn
        from api.server import create_app
        
        print(f"Starting API server...")
        app = create_app(args.config)
        
        uvicorn.run(
            app,
            host='0.0.0.0',
            port=8080,
            workers=1
        )


if __name__ == '__main__':
    main()
