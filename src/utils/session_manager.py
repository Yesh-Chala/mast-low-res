import pytz
import yaml
import json
import streamlit as st
from typing import Dict, Any
from datetime import datetime, timedelta

class Config:
    def __init__(self):
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        with open("config/config.yaml") as f:
            config = yaml.safe_load(f)
            if "${OPENAI_API_KEY}" in str(config):
                config["openai"]["api_key"] = st.secrets["OPENAI_API_KEY"]
            return config
    
    def parse_version(self, version: str) -> tuple:
        """Parse version string into MAST and performance levels"""
        mast_level, performance_level = [
            part.split("-")[0].lower() 
            for part in version.split(": ")[1].split(" ")
        ]
        return mast_level, performance_level
    
    def get_version_configs(self, version: str) -> tuple:
        """Get configuration for specific version"""
        mast_level, performance_level = self.parse_version(version)
        return (
            self._config["versions"]["performance"][performance_level],
            self._config["versions"]["MAST"][mast_level]
        )
    
    def get_retriever_config(self, version: str) -> dict:
        """Get retriever configuration for specific version"""
        _, mast_config = self.get_version_configs(version)
        
        retriever_config = mast_config["retriever"]
        
        # Add input file path
        retriever_config["input_file"] = f"{retriever_config['path']}.json"
        
        return retriever_config
    
    def get_mast_prompt(self, version: str) -> str:
        """Get MAST prompt for specific version"""
        mast_level, _ = self.parse_version(version)
        return self._config["versions"]["MAST"][mast_level]["mast_prompt"]

    def update_mast_prompt(self, version: str, new_prompt: str):
        mast_level, _ = self.parse_version(version)
        self._config["versions"]["MAST"][mast_level]["mast_prompt"] = new_prompt


    @property
    def logging_enabled(self) -> bool:
        return self._config['logging']['activity']['enabled']
    
    @property
    def logging_format(self) -> dict:
        return {
            'timezone': self._config['logging']['activity']['format']['timezone'],
            'timestamp_format': self._config['logging']['activity']['format']['timestamp_format']
        }
    
    @property
    def file_handler(self) -> dict:
        return self._config['logging']['activity']['handlers']['file']
    
    @property
    def google_drive_enabled(self) -> bool:
        return self._config['logging']['activity']['handlers']['google_drive']['enabled']
    
    @property
    def openai(self) -> dict:
        """Get OpenAI configuration"""
        return self._config["openai"]
    
    @property
    def prompts(self) -> dict:
        """Get system prompts"""
        return self._config["prompts"]
    
    @property
    def app(self) -> dict:
        """Get app configuration"""
        return self._config["app"]
    
    def get_model_config(self, version: str) -> dict:
        """Get model configuration for specific version"""
        performance_config, _ = self.get_version_configs(version)
        return performance_config["model"]
    
    def get_document_list(self, version: str) -> dict:
        """Get document list from retriever configuration"""
        retriever_config = self.get_retriever_config(version)
        with open(retriever_config["input_file"], 'r') as json_file:
            return json.load(json_file)
        
    def get_filename_template(self, user_id: str, timestamp: str) -> str:
        return self.file_handler['filename_template'].format(
            user_id=user_id,
            timestamp=timestamp
        )
    

class SessionManager:
    def __init__(self):
        self.config = Config()
        st.session_state.config = self.config
        if "messages" not in st.session_state:
            st.session_state.messages = []
            # self.initialize_session()

    def initialize_session(self, version: str, user_id: str = None):
        
        from src.models.graph_model import GraphModel
        st.session_state.graph_model = GraphModel()
        st.session_state.messages = [{"role": "system", "content": ""}]
        st.session_state.start_time = datetime.now(pytz.timezone('MST'))
        st.session_state.deadline = st.session_state.start_time + timedelta(seconds=10)
        st.session_state.stop_generation = False

        st.session_state.supervisor_prompt = self.config.prompts['supervisor']
        st.session_state.mast_prompt = self.config.get_mast_prompt(version)
        st.session_state.general_prompt = self.config.prompts['general']
        st.session_state.retriever_prompt = self.config.get_retriever_config(st.session_state.version)['prompt']

        if user_id and version:
            st.session_state.user_id = user_id
            st.session_state.version = version

            st.success(f"New {version} session started for user {user_id}!")
            print(f">> New Session started at {st.session_state.start_time}")

        if 'analysis_style_dropdown' not in st.session_state:
            st.session_state.analysis_style_dropdown = 'Standard'
        


    def initialize_user_session(self, version: str, user_id: str):
        # if not user_id or len(user_id.strip()) < 20:
        #     st.warning("Please make sure you copied the full user ID from the survey.")
        #     return False
            
        self.initialize_session(version, user_id)
        return True
    

    def is_new_session(self):
        return "messages" not in st.session_state


    def add_message(self, role: str, content: str):
        if "messages" not in st.session_state:
            self.initialize_session()
        st.session_state.messages.append({"role": role, "content": content})

    
            