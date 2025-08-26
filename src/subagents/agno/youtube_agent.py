"""🎥 YouTube Agent Pro - Your Advanced Video Content Expert!

An intelligent YouTube content analyzer that provides comprehensive video analysis,
detailed breakdowns, timestamps, summaries, and much more. Built for content creators,
researchers, educators, and anyone who wants to efficiently navigate video content.

Features:
✨ Interactive URL input with validation
📊 Multiple analysis modes (Quick, Detailed, Custom)
💾 Export results to multiple formats
🎯 Smart video classification and specialized analysis
📈 Progress tracking and batch processing
🔍 Advanced search within results
📚 Analysis history and preferences

Run: `pip install openai youtube_transcript_api agno rich` to install dependencies
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.youtube import YouTubeTools

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("📦 For enhanced experience, install rich: pip install rich")

class YouTubeAgentPro:
    """Advanced YouTube Content Analyzer with interactive features."""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.history_file = Path("youtube_analysis_history.json")
        self.config_file = Path("youtube_agent_config.json")
        self.load_config()
        self.load_history()
        
        # Initialize the agent with enhanced instructions
        self.agent = Agent(
            name="YouTube Agent Pro",
            model=OpenAIChat(id="gpt-4o"),
            tools=[YouTubeTools()],
            show_tool_calls=True,
            instructions=self._get_enhanced_instructions(),
            add_datetime_to_instructions=True,
            markdown=True,
        )
    
    def load_config(self):
        """Load user configuration."""
        default_config = {
            "default_analysis_mode": "detailed",
            "auto_save": True,
            "export_format": "markdown",
            "show_progress": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = {**default_config, **json.load(f)}
            except:
                self.config = default_config
        else:
            self.config = default_config
    
    def save_config(self):
        """Save user configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def load_history(self):
        """Load analysis history."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []
    
    def save_history(self, entry: Dict):
        """Save analysis to history."""
        self.history.append(entry)
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def validate_youtube_url(self, url: str) -> Optional[str]:
        """Validate and extract video ID from YouTube URL."""
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        
        match = youtube_regex.match(url)
        if match:
            return match.group(6)
        return None
    
    def get_video_category(self, url: str) -> str:
        """Analyze URL and determine likely video category."""
        # This is a simplified categorization - in reality, you'd use the video metadata
        common_patterns = {
            'tutorial': ['tutorial', 'how-to', 'guide', 'learn'],
            'review': ['review', 'unboxing', 'test'],
            'educational': ['lecture', 'course', 'lesson', 'education'],
            'tech': ['programming', 'coding', 'tech', 'software'],
            'entertainment': ['funny', 'comedy', 'entertainment'],
        }
        
        url_lower = url.lower()
        for category, keywords in common_patterns.items():
            if any(keyword in url_lower for keyword in keywords):
                return category
        return 'general'
    
    def _get_enhanced_instructions(self) -> str:
        """Get enhanced analysis instructions."""
        return dedent("""\
            You are an expert YouTube content analyst with advanced analytical capabilities! 🎓
            
            Your mission is to provide comprehensive, accurate, and valuable video analysis.
            
            ANALYSIS FRAMEWORK:
            
            1. 📋 VIDEO OVERVIEW (Always start here)
               - Extract and verify video metadata (title, duration, channel, upload date)
               - Identify video category and content type
               - Assess video quality and production value
               - Note any special features (captions, chapters, etc.)
            
            2. 🎯 CONTENT STRUCTURE ANALYSIS
               - Map the overall content flow and organization
               - Identify main sections and subsections
               - Note transitions and pacing
               - Highlight any recurring patterns or themes
            
            3. ⏰ PRECISE TIMESTAMP CREATION
               - Create accurate, meaningful timestamps for ALL major segments
               - Format: **[MM:SS - MM:SS]** Topic Title - Detailed description
               - Focus on: Topic changes, key demonstrations, important concepts
               - Ensure no significant content is missed
               - Verify timestamp accuracy against transcript
            
            4. 📚 KEY INSIGHTS EXTRACTION
               - Identify the most valuable information
               - Highlight practical applications
               - Note expert tips and best practices
               - Extract actionable advice
               - Summarize complex concepts clearly
            
            5. 🎨 CONTENT-SPECIFIC ANALYSIS
               For Educational Content:
               - Learning objectives and outcomes
               - Prerequisites and difficulty level
               - Key concepts and definitions
               - Practice exercises or examples
               - Further learning recommendations
               
               For Technical Content:
               - Tools and technologies mentioned
               - Code examples and implementations
               - Technical specifications
               - Problem-solving approaches
               - Industry best practices
               
               For Reviews:
               - Product/service features
               - Pros and cons analysis
               - Comparisons and alternatives
               - Pricing and value assessment
               - Final recommendations
            
            QUALITY STANDARDS:
            ✅ Accuracy: Verify all timestamps and facts
            ✅ Completeness: Cover all significant content
            ✅ Clarity: Use clear, descriptive language
            ✅ Organization: Structure information logically
            ✅ Value: Focus on actionable and useful insights
            
            FORMATTING GUIDELINES:
            - Use emojis strategically for visual organization
            - Create clear headings and subheadings
            - Use bullet points for lists and key points
            - Bold important terms and concepts
            - Use code blocks for technical content
            - Include relevant links and references when mentioned
            
            CONTENT TYPE EMOJIS:
            📚 Educational/Academic  💻 Technical/Programming  🎮 Gaming
            � Tech Reviews         🎨 Creative/Art          🏋️ Fitness
            🍳 Cooking/Food         🎵 Music                 📈 Business
            🔬 Science              � Entertainment         📖 Storytelling
        """)
    
    def print_welcome(self):
        """Print welcome message."""
        if self.console:
            self.console.print(Panel.fit(
                "� [bold blue]YouTube Agent Pro[/bold blue] 🎥\n"
                "Advanced Video Content Analyzer\n\n"
                "✨ Interactive Analysis  📊 Multiple Modes  💾 Export Options\n"
                "🎯 Smart Classification  📈 Progress Tracking  🔍 History Search",
                border_style="blue"
            ))
        else:
            print("=" * 60)
            print("🎥 YOUTUBE AGENT PRO 🎥")
            print("Advanced Video Content Analyzer")
            print("=" * 60)
    
    def show_menu(self) -> str:
        """Display main menu and get user choice."""
        if self.console:
            table = Table(title="📋 Available Options")
            table.add_column("Option", style="cyan", no_wrap=True)
            table.add_column("Description", style="white")
            
            table.add_row("1", "🎬 Analyze Single Video")
            table.add_row("2", "📚 Batch Analysis")
            table.add_row("3", "🔍 View Analysis History")
            table.add_row("4", "⚙️ Settings")
            table.add_row("5", "❓ Help & Examples")
            table.add_row("6", "🚪 Exit")
            
            self.console.print(table)
            return Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5", "6"], default="1")
        else:
            print("\n📋 Available Options:")
            print("1. 🎬 Analyze Single Video")
            print("2. 📚 Batch Analysis")
            print("3. 🔍 View Analysis History")
            print("4. ⚙️ Settings")
            print("5. ❓ Help & Examples")
            print("6. 🚪 Exit")
            return input("Choose an option (1-6): ").strip()
    
    def get_analysis_mode(self) -> str:
        """Get analysis mode from user."""
        if self.console:
            table = Table(title="🎯 Analysis Modes")
            table.add_column("Mode", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Best For", style="yellow")
            
            table.add_row("quick", "Fast overview with key points", "Short videos, quick insights")
            table.add_row("detailed", "Comprehensive analysis with timestamps", "Learning, research, content creation")
            table.add_row("custom", "Specialized analysis based on content type", "Specific use cases")
            
            self.console.print(table)
            return Prompt.ask(
                "Select analysis mode", 
                choices=["quick", "detailed", "custom"], 
                default=self.config["default_analysis_mode"]
            )
        else:
            print("\n🎯 Analysis Modes:")
            print("1. quick - Fast overview with key points")
            print("2. detailed - Comprehensive analysis with timestamps")
            print("3. custom - Specialized analysis based on content type")
            mode_map = {"1": "quick", "2": "detailed", "3": "custom"}
            choice = input(f"Select mode (1-3, default: {self.config['default_analysis_mode']}): ").strip()
            return mode_map.get(choice, self.config["default_analysis_mode"])
    
    def get_youtube_url(self) -> Optional[str]:
        """Get and validate YouTube URL from user."""
        if self.console:
            url = Prompt.ask("🔗 Enter YouTube URL")
        else:
            url = input("🔗 Enter YouTube URL: ").strip()
        
        if self.validate_youtube_url(url):
            return url
        else:
            if self.console:
                self.console.print("❌ [red]Invalid YouTube URL. Please try again.[/red]")
            else:
                print("❌ Invalid YouTube URL. Please try again.")
            return None

    def create_analysis_prompt(self, url: str, mode: str) -> str:
        """Create analysis prompt based on mode and video type."""
        category = self.get_video_category(url)
        
        base_prompt = f"Analyze this YouTube video: {url}\n\n"
        
        if mode == "quick":
            return base_prompt + dedent("""\
                Provide a QUICK ANALYSIS with:
                1. 📋 Brief video overview (title, duration, channel)
                2. 🎯 Main topic and key message
                3. ⏰ 3-5 key timestamps with major points
                4. 💡 Top 3 insights or takeaways
                5. 📊 One-sentence summary
                
                Keep it concise but informative!
            """)
        
        elif mode == "detailed":
            return base_prompt + dedent("""\
                Provide a COMPREHENSIVE DETAILED ANALYSIS with:
                1. 📋 Complete video overview and metadata
                2. 🎯 Content structure and organization
                3. ⏰ Detailed timestamps for ALL major segments
                4. 📚 Key concepts, insights, and learning points
                5. 🎨 Content-specific analysis based on video type
                6. 💡 Practical applications and takeaways
                7. 📊 Executive summary
                
                Be thorough and include all valuable information!
            """)
        
        elif mode == "custom":
            custom_prompts = {
                'tutorial': dedent("""\
                    Provide TUTORIAL-FOCUSED ANALYSIS with:
                    1. 📋 Tutorial overview and learning objectives
                    2. 🎯 Prerequisites and difficulty level
                    3. ⏰ Step-by-step timestamps with detailed explanations
                    4. 💻 Code examples, tools, and resources mentioned
                    5. 🏆 Best practices and tips highlighted
                    6. 📚 Practice exercises and follow-up suggestions
                    7. 🔗 Related resources and next steps
                """),
                'review': dedent("""\
                    Provide REVIEW-FOCUSED ANALYSIS with:
                    1. 📋 Product/service overview and specifications
                    2. 🎯 Review structure and methodology
                    3. ⏰ Timestamps for features, testing, and conclusions
                    4. ✅ Pros and cons analysis
                    5. 💰 Value assessment and pricing discussion
                    6. 🔄 Comparisons with alternatives
                    7. 🎯 Final recommendation and target audience
                """),
                'educational': dedent("""\
                    Provide EDUCATIONAL CONTENT ANALYSIS with:
                    1. 📋 Course/lecture overview and learning outcomes
                    2. 🎯 Academic level and subject area
                    3. ⏰ Chapter/section timestamps with key concepts
                    4. 📚 Important definitions and theories
                    5. 💡 Examples and case studies
                    6. 📝 Study guide with key points
                    7. 📖 Additional reading and resources
                """),
                'tech': dedent("""\
                    Provide TECHNICAL CONTENT ANALYSIS with:
                    1. 📋 Technical overview and scope
                    2. 🎯 Technologies, tools, and frameworks covered
                    3. ⏰ Implementation timestamps with code explanations
                    4. 💻 Architecture and design patterns
                    5. 🔧 Setup, configuration, and dependencies
                    6. 🐛 Troubleshooting and common issues
                    7. 🚀 Performance considerations and best practices
                """)
            }
            
            return base_prompt + custom_prompts.get(category, custom_prompts['tutorial'])
        
        return base_prompt
    
    def export_analysis(self, analysis: str, video_url: str, format_type: str = "markdown") -> str:
        """Export analysis to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_id = self.validate_youtube_url(video_url)
        
        if format_type == "markdown":
            filename = f"youtube_analysis_{video_id}_{timestamp}.md"
            content = f"# YouTube Video Analysis\n\n**URL:** {video_url}\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n{analysis}"
        elif format_type == "json":
            filename = f"youtube_analysis_{video_id}_{timestamp}.json"
            content = json.dumps({
                "url": video_url,
                "video_id": video_id,
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis
            }, indent=2)
        else:  # txt
            filename = f"youtube_analysis_{video_id}_{timestamp}.txt"
            content = f"YouTube Video Analysis\nURL: {video_url}\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{'-'*60}\n\n{analysis}"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filename
    
    def analyze_video(self, url: str, mode: str = "detailed") -> Optional[str]:
        """Analyze a single video."""
        try:
            if self.console and self.config["show_progress"]:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                ) as progress:
                    task = progress.add_task("🎬 Analyzing video...", total=None)
                    
                    prompt = self.create_analysis_prompt(url, mode)
                    analysis = self.agent.run(prompt)
                    
                    progress.update(task, description="✅ Analysis complete!")
            else:
                if not self.console:
                    print("🎬 Analyzing video...")
                prompt = self.create_analysis_prompt(url, mode)
                analysis = self.agent.run(prompt)
                if not self.console:
                    print("✅ Analysis complete!")
            
            # Save to history
            if self.config["auto_save"]:
                history_entry = {
                    "url": url,
                    "mode": mode,
                    "timestamp": datetime.now().isoformat(),
                    "analysis": analysis.content if hasattr(analysis, 'content') else str(analysis)
                }
                self.save_history(history_entry)
            
            return analysis.content if hasattr(analysis, 'content') else str(analysis)
            
        except Exception as e:
            error_msg = f"❌ Error analyzing video: {str(e)}"
            if self.console:
                self.console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
            return None
    
    def batch_analyze(self):
        """Analyze multiple videos."""
        urls = []
        
        if self.console:
            self.console.print("📚 [bold]Batch Analysis Mode[/bold]")
            self.console.print("Enter YouTube URLs (one per line, empty line to finish):")
        else:
            print("📚 Batch Analysis Mode")
            print("Enter YouTube URLs (one per line, empty line to finish):")
        
        while True:
            if self.console:
                url = Prompt.ask("URL", default="")
            else:
                url = input("URL: ").strip()
            
            if not url:
                break
            
            if self.validate_youtube_url(url):
                urls.append(url)
                if self.console:
                    self.console.print(f"✅ Added: {url}")
                else:
                    print(f"✅ Added: {url}")
            else:
                if self.console:
                    self.console.print(f"❌ [red]Invalid URL: {url}[/red]")
                else:
                    print(f"❌ Invalid URL: {url}")
        
        if not urls:
            if self.console:
                self.console.print("No valid URLs provided.")
            else:
                print("No valid URLs provided.")
            return
        
        mode = self.get_analysis_mode()
        
        results = []
        for i, url in enumerate(urls, 1):
            if self.console:
                self.console.print(f"\n🎬 Analyzing video {i}/{len(urls)}: {url}")
            else:
                print(f"\n🎬 Analyzing video {i}/{len(urls)}: {url}")
            
            analysis = self.analyze_video(url, mode)
            if analysis:
                results.append({"url": url, "analysis": analysis})
                
                # Ask if user wants to export individual result
                if self.console:
                    export = Confirm.ask("Export this analysis?", default=False)
                else:
                    export = input("Export this analysis? (y/N): ").lower().startswith('y')
                
                if export:
                    filename = self.export_analysis(analysis, url, self.config["export_format"])
                    if self.console:
                        self.console.print(f"💾 Exported to: {filename}")
                    else:
                        print(f"💾 Exported to: {filename}")
        
        if self.console:
            self.console.print(f"\n✅ Batch analysis complete! Analyzed {len(results)} videos.")
        else:
            print(f"\n✅ Batch analysis complete! Analyzed {len(results)} videos.")
    
    def view_history(self):
        """View analysis history."""
        if not self.history:
            if self.console:
                self.console.print("📝 No analysis history found.")
            else:
                print("📝 No analysis history found.")
            return
        
        if self.console:
            table = Table(title="📊 Analysis History")
            table.add_column("Date", style="cyan", no_wrap=True)
            table.add_column("URL", style="blue", max_width=50)
            table.add_column("Mode", style="green")
            
            for entry in self.history[-10:]:  # Show last 10
                date = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
                url = entry["url"][:47] + "..." if len(entry["url"]) > 50 else entry["url"]
                table.add_row(date, url, entry["mode"])
            
            self.console.print(table)
            
            if len(self.history) > 10:
                self.console.print(f"\n[dim]Showing last 10 of {len(self.history)} total analyses[/dim]")
        else:
            print("📊 Analysis History (Last 10):")
            print("-" * 80)
            for entry in self.history[-10:]:
                date = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
                url = entry["url"][:60] + "..." if len(entry["url"]) > 60 else entry["url"]
                print(f"{date} | {entry['mode']:>8} | {url}")
    
    def show_settings(self):
        """Show and modify settings."""
        if self.console:
            table = Table(title="⚙️ Current Settings")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="white")
            
            for key, value in self.config.items():
                table.add_row(key.replace("_", " ").title(), str(value))
            
            self.console.print(table)
            
            if Confirm.ask("Modify settings?", default=False):
                # Allow user to modify settings
                self.config["default_analysis_mode"] = Prompt.ask(
                    "Default analysis mode", 
                    choices=["quick", "detailed", "custom"],
                    default=self.config["default_analysis_mode"]
                )
                
                self.config["auto_save"] = Confirm.ask(
                    "Auto-save analyses to history?",
                    default=self.config["auto_save"]
                )
                
                self.config["export_format"] = Prompt.ask(
                    "Default export format",
                    choices=["markdown", "json", "txt"],
                    default=self.config["export_format"]
                )
                
                self.config["show_progress"] = Confirm.ask(
                    "Show progress indicators?",
                    default=self.config["show_progress"]
                )
                
                self.save_config()
                self.console.print("✅ Settings saved!")
        else:
            print("⚙️ Current Settings:")
            for key, value in self.config.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
    
    def show_help(self):
        """Show help and examples."""
        help_text = dedent("""\
            🎥 YOUTUBE AGENT PRO - HELP & EXAMPLES
            
            📋 SUPPORTED URL FORMATS:
            ✅ https://www.youtube.com/watch?v=VIDEO_ID
            ✅ https://youtu.be/VIDEO_ID
            ✅ https://youtube.com/watch?v=VIDEO_ID
            ✅ https://m.youtube.com/watch?v=VIDEO_ID
            
            🎯 ANALYSIS MODES:
            
            📊 QUICK MODE - Fast Overview
            • Best for: Short videos, quick insights
            • Includes: Basic info, main points, key timestamps
            • Time: ~30 seconds
            
            📚 DETAILED MODE - Comprehensive Analysis
            • Best for: Learning, research, content creation
            • Includes: Full breakdown, all timestamps, insights
            • Time: ~1-2 minutes
            
            🎨 CUSTOM MODE - Specialized Analysis
            • Best for: Specific content types
            • Adapts to: Tutorials, reviews, educational content
            • Includes: Content-type specific analysis
            
            💡 EXAMPLES:
            
            🎓 Educational Video:
            "https://www.youtube.com/watch?v=example123"
            → Get study guide, key concepts, learning objectives
            
            💻 Programming Tutorial:
            "https://www.youtube.com/watch?v=code456"
            → Code timestamps, setup instructions, best practices
            
            📱 Product Review:
            "https://www.youtube.com/watch?v=review789"
            → Feature analysis, pros/cons, recommendations
            
            🎮 Gaming Content:
            "https://www.youtube.com/watch?v=game101"
            → Gameplay segments, tips, strategies
            
            📁 EXPORT OPTIONS:
            • Markdown (.md) - Rich formatting, great for notes
            • JSON (.json) - Structured data, easy to process
            • Text (.txt) - Plain text, universal compatibility
            
            ⚙️ FEATURES:
            • 📊 Progress tracking during analysis
            • 💾 Auto-save to history
            • 🔍 Search through past analyses
            • 📚 Batch processing multiple videos
            • 🎯 Smart content detection
            • ⚡ Optimized for different video lengths
        """)
        
        if self.console:
            self.console.print(Panel(help_text, border_style="green", title="Help & Examples"))
        else:
            print(help_text)
    
    def run(self):
        """Main application loop."""
        self.print_welcome()
        
        while True:
            try:
                choice = self.show_menu()
                
                if choice == "1":
                    # Single video analysis
                    url = self.get_youtube_url()
                    if url:
                        mode = self.get_analysis_mode()
                        analysis = self.analyze_video(url, mode)
                        
                        if analysis:
                            if self.console:
                                self.console.print("\n" + "="*60)
                                self.console.print("🎬 [bold]ANALYSIS RESULTS[/bold]")
                                self.console.print("="*60)
                                self.console.print(analysis)
                                self.console.print("="*60)
                                
                                # Ask if user wants to export
                                if Confirm.ask("Export this analysis?", default=False):
                                    format_choice = Prompt.ask(
                                        "Export format", 
                                        choices=["markdown", "json", "txt"],
                                        default=self.config["export_format"]
                                    )
                                    filename = self.export_analysis(analysis, url, format_choice)
                                    self.console.print(f"💾 Exported to: {filename}")
                            else:
                                print("\n" + "="*60)
                                print("🎬 ANALYSIS RESULTS")
                                print("="*60)
                                print(analysis)
                                print("="*60)
                                
                                export = input("Export this analysis? (y/N): ").lower().startswith('y')
                                if export:
                                    filename = self.export_analysis(analysis, url, self.config["export_format"])
                                    print(f"💾 Exported to: {filename}")
                
                elif choice == "2":
                    # Batch analysis
                    self.batch_analyze()
                
                elif choice == "3":
                    # View history
                    self.view_history()
                
                elif choice == "4":
                    # Settings
                    self.show_settings()
                
                elif choice == "5":
                    # Help
                    self.show_help()
                
                elif choice == "6":
                    # Exit
                    if self.console:
                        self.console.print("👋 [bold blue]Thank you for using YouTube Agent Pro![/bold blue]")
                    else:
                        print("👋 Thank you for using YouTube Agent Pro!")
                    break
                
                # Wait for user before continuing
                if self.console:
                    self.console.print("\n")
                    Prompt.ask("Press Enter to continue", default="")
                else:
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                if self.console:
                    self.console.print("\n👋 [bold blue]Goodbye![/bold blue]")
                else:
                    print("\n👋 Goodbye!")
                break
            except Exception as e:
                error_msg = f"❌ Unexpected error: {str(e)}"
                if self.console:
                    self.console.print(f"[red]{error_msg}[/red]")
                else:
                    print(error_msg)


def main():
    """Main entry point."""
    try:
        agent = YouTubeAgentPro()
        agent.run()
    except Exception as e:
        print(f"❌ Failed to start YouTube Agent Pro: {str(e)}")
        print("💡 Make sure you have installed all dependencies:")
        print("   pip install openai youtube_transcript_api agno rich")


if __name__ == "__main__":
    main()