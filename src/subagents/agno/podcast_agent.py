"""
🎙️ Podcast Generator Pro — GPT-4o Ready (Exa/DuckDuckGo)
Create pro podcasts with enhanced news mode!
Dependencies: pip install openai agno exa-py rich python-dotenv pydub mutagen
You MUST have `ffmpeg` installed system-wide for audio export (see: https://ffmpeg.org/)
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.exa import ExaTools
from agno.utils.audio import write_audio_to_file

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    RICH = True
except ImportError:
    RICH = False
    Console = None

try:
    from pydub import AudioSegment
    from pydub.effects import normalize, compress_dynamic_range
    PYDUB = True
except ImportError:
    PYDUB = False
    print("⚠️ Pydub not found. Install it for audio post-processing (pip install pydub)")

try:
    import mutagen
    from mutagen.wave import WAVE
    MUTAGEN = True
except ImportError:
    MUTAGEN = False

DEFAULT_CONFIG = {
    "default_voice": "alloy",
    "default_style": "educational",
    "auto_save": True,
    "audio_format": "wav",
    "podcast_length": "short",
    "show_progress": True,
}

VOICE_OPTIONS = {
    "alloy": {"name": "Alloy", "personality": "Professional & Balanced"},
    "echo": {"name": "Echo", "personality": "Clear & Articulate"},
    "fable": {"name": "Fable", "personality": "Warm & Engaging"},
    "onyx": {"name": "Onyx", "personality": "Deep & Authoritative"},
    "nova": {"name": "Nova", "personality": "Bright & Energetic"},
    "shimmer": {"name": "Shimmer", "personality": "Smooth & Conversational"},
}

PODCAST_STYLES = {
    "news": "News Report Style", "educational": "Educational/Tutorial", "interview": "Interview/Conversation",
    "story": "Storytelling/Narrative", "casual": "Casual Discussion",
    "documentary": "Documentary", "comedy": "Comedy/Entertainment"
}

TRENDING_NEWS_TOPICS = [
    "Global technology headlines",
    "AI breakthroughs in 2025",
    "Climate change policy updates",
    "Major economic events this week",
    "Health & science discoveries",
    "Space missions and findings",
    "Cybersecurity threats in the news",
    "Political developments worldwide",
]

class PodcastGeneratorPro:
    def __init__(self):
        load_dotenv()
        self.console: Optional[Console] = Console() if RICH else None
        self.history_file = Path("podcast_generation_history.json")
        self.config_file = Path("podcast_agent_config.json")
        self.output_dir = Path("generated_podcasts")
        self.output_dir.mkdir(exist_ok=True)
        self.history: List[Dict] = self.load_history()
        self.config: Dict = self.load_config()
        if not os.getenv("OPENAI_API_KEY"):
            msg = "\n❌ OPENAI_API_KEY not found in environment. Add it to your .env or shell.\n"
            if self.console: self.console.print(f"[bold red]{msg}[/bold red]")
            else: print(msg)
            sys.exit(1)

    def load_history(self) -> List[Dict]:
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def load_config(self) -> Dict:
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    user = json.load(f)
                    cfg = {**DEFAULT_CONFIG, **user}
                    return cfg
            except Exception:
                pass
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def create_agent(self, use_exa: bool = False, voice: str = "alloy", audio_format: str = "wav") -> Agent:
        tools = [DuckDuckGoTools()]
        if use_exa:
            try:
                exa_tool = ExaTools()
                if hasattr(exa_tool, 'function_name') and '.' in exa_tool.function_name:
                    exa_tool.function_name = exa_tool.function_name.replace('.', '_')
                tools.append(exa_tool)
            except Exception as exc:
                if self.console:
                    self.console.print(f"[yellow]Warning: Could not load ExaTools: {exc}[/yellow]")
        model = OpenAIChat(
            id="gpt-4o-audio-preview",
            modalities=["text", "audio"],
            audio={"voice": voice, "format": audio_format}
        )
        return Agent(
            name="PodcastGeneratorPro",
            model=model,
            tools=tools,
            instructions="You are an expert podcast researcher and narrator. Provide accurate, engaging podcasts with clear sources.",
            show_tool_calls=True,
        )

    def generate_podcast(self, topic: str, voice: str, style: str, length: str, use_exa: bool = False) -> Optional[str]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c if c.isalnum() or c in "-_ " else "_" for c in topic).strip().replace(" ", "_")
        audio_filename = f"podcast_{safe_topic}_{timestamp}.{self.config['audio_format']}"
        audio_path = self.output_dir / audio_filename
        if self.console and self.config["show_progress"]:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                          console=self.console) as progress:
                task = progress.add_task("Generating...", total=None)
                progress.update(task, description="🔎 Researching Topic")
                agent = self.create_agent(use_exa, voice, self.config['audio_format'])
                prompt = f"Create a {style} style podcast about: {topic}. Length: {length}." 
                response = agent.run(prompt)
                progress.update(task, description="🎙️ Generating Audio")
                if hasattr(response, 'response_audio') and response.response_audio:
                    write_audio_to_file(audio=response.response_audio.content, filename=str(audio_path))
                    progress.update(task, description="✅ Podcast saved!")
                else:
                    progress.update(task, description="❌ No audio in response."); return None
        else:
            print(f"🔎 Generating Podcast: {topic}")
            agent = self.create_agent(use_exa, voice, self.config['audio_format'])
            prompt = f"Create a {style} style podcast about: {topic}. Length: {length}." 
            response = agent.run(prompt)
            if hasattr(response, 'response_audio') and response.response_audio:
                write_audio_to_file(audio=response.response_audio.content, filename=str(audio_path))
                print(f"✅ Podcast saved: {audio_path}")
            else:
                print("❌ No audio generated."); return None
        entry = dict(
            topic=topic, voice=voice, style=style, length=length,
            timestamp=datetime.now().isoformat(), filename=audio_filename, file_path=str(audio_path)
        )
        if self.config.get("auto_save"): self.history.append(entry); self.save_history()
        return str(audio_path)

    def show_menu(self):
        if self.console:
            table = Table(title="Podcast Generator Pro", show_header=True, header_style="bold magenta")
            table.add_column("Option", style="cyan", no_wrap=True)
            table.add_column("Feature", style="white")
            table.add_row("1", "Generate Podcast")
            table.add_row("2", "News to Podcast")
            table.add_row("3", "History")
            table.add_row("4", "Settings")
            table.add_row("5", "Exit")
            self.console.print(table)
            return Prompt.ask("Choose", choices=["1", "2", "3", "4", "5"], default="1")
        print("\n1. Generate Podcast\n2. News to Podcast\n3. History\n4. Settings\n5. Exit")
        return input("Choose option (1-5): ").strip()

    def get_user_input(self, prompt_str: str, choices: Optional[List[str]] = None, default: Optional[str] = None) -> str:
        if self.console:
            return Prompt.ask(prompt_str, choices=choices, default=default)
        msg = f"{prompt_str}"
        if choices: msg += f"\nChoices: {', '.join(choices)}"
        if default: msg += f" [default={default}]"
        out = input(msg + "\n> ").strip()
        return out if out else default or (choices[0] if choices else "")

    def run(self):
        if self.console: self.console.print(Panel("🎙️ Podcast Generator Pro — GPT-4o/Exa Ready", border_style="blue"))
        while True:
            choice = self.show_menu()
            if choice == "1":  # Standard podcast
                topic = self.get_user_input("Enter topic for podcast:")
                voice = self.get_user_input("Voice", list(VOICE_OPTIONS.keys()), self.config["default_voice"])
                style = self.get_user_input("Style", list(PODCAST_STYLES.keys()), self.config["default_style"])
                length = self.get_user_input("Length", ["short", "medium", "long"], self.config["podcast_length"])
                exa = self.get_user_input("Enhanced web/news research with Exa?", ["y", "n"], "n").lower() == "y"
                audio_path = self.generate_podcast(topic, voice, style, length, use_exa=exa)
                msg = f"✅ Podcast saved to: {audio_path}" if audio_path else "❌ Podcast failed."
                if self.console: self.console.print(f"[green]{msg}[/green]") if audio_path else self.console.print(f"[red]{msg}[/red]")
                else: print(msg)
            elif choice == "2":  # News-to-Podcast
                self.show_trending_topics()
                news_topic = self.get_user_input("Enter news topic or choose from above:")
                voice = self.get_user_input("Voice", list(VOICE_OPTIONS.keys()), self.config["default_voice"])
                length = self.get_user_input("Length", ["short", "medium", "long"], self.config["podcast_length"])
                # Always use Exa, always style news
                audio_path = self.generate_podcast(news_topic, voice, "news", length, use_exa=True)
                msg = f"✅ [News] Podcast saved to: {audio_path}" if audio_path else "❌ Podcast failed."
                if self.console: self.console.print(f"[green]{msg}[/green]") if audio_path else self.console.print(f"[red]{msg}[/red]")
                else: print(msg)
            elif choice == "3":
                self.show_history()
            elif choice == "4":
                self.show_settings()
            elif choice == "5":
                print("Exiting. 👋"); break

    def show_trending_topics(self):
        if self.console:
            self.console.print(Panel("🔥 [bold]Trending News Topics[/bold]", border_style="red"))
            for i, t in enumerate(TRENDING_NEWS_TOPICS, 1):
                self.console.print(f"{i}. {t}")
        else:
            print("Trending News Topics:")
            for i, t in enumerate(TRENDING_NEWS_TOPICS, 1):
                print(f"{i}. {t}")

    def show_history(self):
        if not self.history:
            print("No podcast history."); return
        if self.console:
            table = Table(title="Podcast Generation History")
            table.add_column("Time", style="cyan")
            table.add_column("Topic", style="white")
            table.add_column("Voice", style="blue")
            table.add_column("Style", style="magenta")
            for h in self.history[-10:]:
                dt = datetime.fromisoformat(h['timestamp'])
                table.add_row(dt.strftime("%Y-%m-%d %H:%M"), h["topic"], h["voice"], h["style"])
            self.console.print(table)
        else:
            for h in self.history[-10:]:
                dt = datetime.fromisoformat(h['timestamp'])
                print(f"{dt.strftime('%Y-%m-%d %H:%M')} | {h['topic']} | {h['voice']} | {h['style']}")

    def show_settings(self):
        print("Current settings:")
        for k, v in self.config.items():
            print(f"{k}: {v}")
        chg = self.get_user_input("Change settings? (y/n)", ["y", "n"], "n")
        if chg == "y":
            for k in self.config:
                nv = self.get_user_input(f"Set {k} (current: {self.config[k]})", default=str(self.config[k]))
                if nv: self.config[k] = type(self.config[k])(nv)
            self.save_config(); print("Settings updated.")

def main():
    try:
        PodcastGeneratorPro().run()
    except KeyboardInterrupt:
        print("\nExiting.")

if __name__ == "__main__":
    main()
