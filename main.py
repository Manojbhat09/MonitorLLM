import os
import click
import signal
import readline
import logging
from colorama import init, Fore, Style
from config.logger_setup import setup_logging
from core.shellm import SheLLM
from core.prompt import get_prompt

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

def signal_handler(sig, frame):
    """Signal handler for SIGINT to stop the current command."""
    if shellm.current_process_pid:
        os.kill(shellm.current_process_pid, signal.SIGINT)
    else:
        logger.info("\nUse 'exit' to quit SheLLM.")

@click.command()
@click.option('--llm-api', type=click.Choice(['openai', 'groq', 'ollama']), default='ollama', help="Choose the language model API to use.")
@click.option('--ollama-host', default='http://localhost:11434', help="Ollama server host")
@click.option('--ollama-model', default='llama3.1', help="Ollama model to use")
@click.option('--server-mode', is_flag=True, help="Run in server mode")
@click.option('--server-host', default='localhost', help="Server host")
@click.option('--server-port', default=8000, help="Server port")
def main(llm_api, ollama_host, ollama_model, server_mode, server_host, server_port):
    global shellm
    init(autoreset=True)
    
    if server_mode:
        # Run in server mode
        from core.server import SheLLMServer, ServerConfig
        config = ServerConfig(
            host=server_host,
            port=server_port,
            ollama_host=ollama_host,
            ollama_model=ollama_model
        )
        server = SheLLMServer(config)
        server.run()
        return
    
    # Run in interactive mode
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set editing-mode vi')
    history_file = os.path.expanduser("~/.shellm_history")
    try:
        readline.read_history_file(history_file)
    except FileNotFoundError:
        pass

    shellm = SheLLM(llm_api=llm_api, ollama_host=ollama_host, ollama_model=ollama_model)
    signal.signal(signal.SIGINT, signal_handler)

    logger.info(f"Welcome to the {Fore.RED}SheLLM{Style.RESET_ALL} Model: {Fore.BLUE}{llm_api.capitalize()}{Style.RESET_ALL}.")
    logger.info(f"Commands: '#' for command generation, '##' for questions, '@' for enhanced chat with file references")
    logger.info(f"Type 'exit' to quit.")
    
    while True:
        try:
            cmd = input(get_prompt())
            if cmd.lower() == "exit":
                break
            elif cmd.strip().startswith('##'):
                shellm.answer_question(cmd[2:].strip())
            elif cmd.strip().startswith('#'):
                shellm.handle_lm_command(cmd[1:].strip())
            elif cmd.strip().startswith('@'):
                # Enhanced chat with file references
                shellm.chat_with_context(cmd[1:].strip())
            else:
                shellm.execute_system_command(cmd)
        except (EOFError, KeyboardInterrupt):
            logger.info("\nExiting...")
            break

    # Save session before exit
    shellm.save_session()
    readline.write_history_file(history_file)

if __name__ == "__main__":
    main()
