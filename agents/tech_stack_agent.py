from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from utils.groq_client import GROQClient
from typing import Dict, List, Any, Optional
import os
import json
import glob


class TechStackConfig(BaseModel):
    """
    Configuration settings for the Tech Stack Detection agent.

    Attributes:
        groq_api_endpoint (str): GROQ API endpoint URL
        groq_api_key (str): Authentication key for GROQ API
        frontend_dir (str): Directory containing frontend code
    """

    groq_api_endpoint: str
    groq_api_key: str
    frontend_dir: str = "frontend"
    model: str = "llama3-8b-8192"


class TechStackAgent(Agent):
    """
    An AI agent that analyzes and detects the tech stack of a frontend codebase.

    This agent scans package.json, configuration files, and code samples to determine
    which frontend framework, build tools, and CSS frameworks are being used.
    """

    def __init__(self, config: TechStackConfig):
        """
        Initialize the Tech Stack agent with necessary configuration.

        Args:
            config (TechStackConfig): Configuration for the tech stack agent
        """
        super().__init__()
        self.config = config
        self.groq_client = GROQClient(
            api_endpoint=config.groq_api_endpoint, api_key=config.groq_api_key
        )

    def detect_tech_stack(self) -> Dict[str, Any]:
        """
        Analyze frontend codebase to detect technologies being used.

        Returns:
            Dict[str, Any]: Dictionary containing detected tech stack information
        """
        # Get package.json content
        package_json = self._get_package_json()

        # Get configuration files
        config_files = self._get_config_files()

        # Sample some code files
        code_samples = self._get_code_samples()

        # Analyze with GROQ
        tech_stack = self._analyze_tech_stack(package_json, config_files, code_samples)

        return tech_stack

    def _get_package_json(self) -> Optional[Dict[str, Any]]:
        """Get package.json content if it exists"""
        package_path = os.path.join(self.config.frontend_dir, "package.json")
        if os.path.exists(package_path):
            with open(package_path, "r") as f:
                return json.load(f)
        return None

    def _get_config_files(self) -> Dict[str, str]:
        """Get content of common frontend configuration files"""
        config_files = {}
        config_patterns = [
            "vite.config.*",
            "tailwind.config.*",
            "webpack.config.*",
            "next.config.*",
            "astro.config.*",
            "svelte.config.*",
            "tsconfig.json",
            ".eslintrc.*",
        ]

        for pattern in config_patterns:
            for file_path in glob.glob(os.path.join(self.config.frontend_dir, pattern)):
                filename = os.path.basename(file_path)
                with open(file_path, "r") as f:
                    config_files[filename] = f.read()

        return config_files

    def _get_code_samples(self) -> Dict[str, str]:
        """Get content of representative code files"""
        code_samples = {}
        file_extensions = ["js", "ts", "jsx", "tsx", "vue", "svelte", "astro"]

        for ext in file_extensions:
            sample_files = list(
                glob.glob(os.path.join(self.config.frontend_dir, "src", f"*.{ext}"))
            )
            sample_files.extend(
                glob.glob(
                    os.path.join(
                        self.config.frontend_dir, "src", "components", f"*.{ext}"
                    )
                )
            )

            # Get up to 3 samples per extension
            for file_path in sample_files[:3]:
                filename = os.path.basename(file_path)
                with open(file_path, "r") as f:
                    code_samples[filename] = f.read()

        return code_samples

    def _analyze_tech_stack(
        self,
        package_json: Dict,
        config_files: Dict[str, str],
        code_samples: Dict[str, str],
    ) -> Dict[str, Any]:
        """Analyze collected files to determine tech stack using GROQ LLM"""

        # Prepare prompt with collected data
        prompt = self._prepare_analysis_prompt(package_json, config_files, code_samples)

        # Send to GROQ
        messages = [
            {
                "role": "system",
                "content": "You are an AI tech stack analyzer specialized in frontend technologies. "
                "Analyze the provided code and configuration files to identify the tech stack.",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.groq_client.send_inference_request(
                model_id=self.config.model, input_data={"messages": messages}
            )

            # Extract structured data from the response
            content = response.prediction.get("content", "")
            return self._extract_tech_stack(content)

        except Exception as e:
            return {
                "error": str(e),
                "framework": "unknown",
                "build_tool": "unknown",
                "css_framework": "unknown",
            }

    def _prepare_analysis_prompt(
        self,
        package_json: Dict,
        config_files: Dict[str, str],
        code_samples: Dict[str, str],
    ) -> str:
        """Prepare prompt for tech stack analysis"""
        prompt = "Please analyze these frontend project files to determine the tech stack:\n\n"

        # Add package.json summary
        if package_json:
            prompt += "PACKAGE.JSON DEPENDENCIES:\n"
            if "dependencies" in package_json:
                prompt += json.dumps(package_json["dependencies"], indent=2) + "\n\n"
            if "devDependencies" in package_json:
                prompt += "DEV DEPENDENCIES:\n"
                prompt += json.dumps(package_json["devDependencies"], indent=2) + "\n\n"

        # Add config file names
        prompt += f"CONFIG FILES PRESENT: {', '.join(config_files.keys())}\n\n"

        # Add a sample of each config file (first 20 lines)
        for filename, content in list(config_files.items())[:3]:
            prompt += f"{filename} (truncated):\n"
            prompt += "\n".join(content.split("\n")[:20]) + "\n...\n\n"

        # Add code sample summary
        prompt += f"CODE FILES PRESENT: {', '.join(code_samples.keys())}\n\n"

        # Add a sample of code files (first 20 lines of 2 files)
        for filename, content in list(code_samples.items())[:2]:
            prompt += f"{filename} (truncated):\n"
            prompt += "\n".join(content.split("\n")[:20]) + "\n...\n\n"

        prompt += """
                Based on these files, please identify:
                1. Main frontend framework (React, Vue, Angular, Svelte, etc.)
                2. Build tool (Vite, Webpack, Next.js, Astro, etc.)
                3. CSS framework or approach (Tailwind, Bootstrap, SCSS, styled-components, etc.)
                4. TypeScript usage
                5. State management libraries
                6. Additional significant libraries/frameworks

                Format your response as a JSON object with these keys.
            """
        return prompt

    def _extract_tech_stack(self, content: str) -> Dict[str, Any]:
        """Extract structured tech stack data from the LLM response"""
        try:
            # Look for JSON in response
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)

            # Fallback to simple extraction
            tech_stack = {
                "framework": "unknown",
                "build_tool": "unknown",
                "css_framework": "unknown",
                "typescript": False,
                "state_management": "unknown",
                "additional_libraries": [],
            }

            # Extract data from raw text if JSON not present
            if "react" in content.lower():
                tech_stack["framework"] = "React"
            elif "vue" in content.lower():
                tech_stack["framework"] = "Vue"
            elif "svelte" in content.lower():
                tech_stack["framework"] = "Svelte"

            if "vite" in content.lower():
                tech_stack["build_tool"] = "Vite"
            elif "webpack" in content.lower():
                tech_stack["build_tool"] = "Webpack"
            elif "next.js" in content.lower() or "nextjs" in content.lower():
                tech_stack["build_tool"] = "Next.js"

            if "tailwind" in content.lower():
                tech_stack["css_framework"] = "Tailwind CSS"
            elif "bootstrap" in content.lower():
                tech_stack["css_framework"] = "Bootstrap"

            tech_stack["typescript"] = "typescript" in content.lower()

            return tech_stack

        except Exception as e:
            return {
                "error": str(e),
                "framework": "unknown",
                "build_tool": "unknown",
                "css_framework": "unknown",
            }
