import asyncio
import os
from typing import Dict, List
from datetime import datetime
import openai
from elevenlabs import generate, set_api_key
from moviepy.editor import *
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import azure.cognitiveservices.speech as speechsdk
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AIVideoGenerator:
    """AI视频生成器"""
    
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        if elevenlabs_api_key:
            set_api_key(elevenlabs_api_key)
        
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv('AZURE_SPEECH_KEY'),
            region=os.getenv('AZURE_SPEECH_REGION')
        )
        
        # Language configurations
        self.language_configs = {
            'en': {'voice_azure': 'en-US-AriaNeural', 'voice_elevenlabs': 'Bella', 'font': 'arial.ttf', 'font_path': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'}, # Default font for Linux
            'zh': {'voice_azure': 'zh-CN-XiaoxiaoNeural', 'voice_elevenlabs': 'Domi', 'font': 'simhei.ttf', 'font_path': '/usr/share/fonts/truetype/arphic/gkai00mp.ttf'}, # Example path for a Chinese font
            'ja': {'voice_azure': 'ja-JP-NanamiNeural', 'voice_elevenlabs': 'Domi', 'font': 'meiryo.ttf', 'font_path': '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'}, # Example path for Japanese font
            'ko': {'voice_azure': 'ko-KR-SunHiNeural', 'voice_elevenlabs': 'Domi', 'font': 'malgun.ttf', 'font_path': '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'}, # Example path for Korean font
            'es': {'voice_azure': 'es-ES-ElviraNeural', 'voice_elevenlabs': 'Antoni', 'font': 'arial.ttf', 'font_path': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'},
            'fr': {'voice_azure': 'fr-FR-DeniseNeural', 'voice_elevenlabs': 'Antoni', 'font': 'arial.ttf', 'font_path': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'},
            'de': {'voice_azure': 'de-DE-KatjaNeural', 'voice_elevenlabs': 'Antoni', 'font': 'arial.ttf', 'font_path': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'},
            'it': {'voice_azure': 'it-IT-ElsaNeural', 'voice_elevenlabs': 'Antoni', 'font': 'arial.ttf', 'font_path': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'},
            'pt': {'voice_azure': 'pt-BR-FranciscaNeural', 'voice_elevenlabs': 'Antoni', 'font': 'arial.ttf', 'font_path': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'},
            'ru': {'voice_azure': 'ru-RU-SvetlanaNeural', 'voice_elevenlabs': 'Antoni', 'font': 'arial.ttf', 'font_path': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'},
            'ar': {'voice_azure': 'ar-SA-ZariyahNeural', 'voice_elevenlabs': 'Antoni', 'font': 'arial.ttf', 'font_path': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'},
            'hi': {'voice_azure': 'hi-IN-SwaraNeural', 'voice_elevenlabs': 'Antoni', 'font': 'arial.ttf', 'font_path': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'},
            'th': {'voice_azure': 'th-TH-PremwadeeNeural', 'voice_elevenlabs': 'Antoni', 'font': 'arial.ttf', 'font_path': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'}
        }
        # Ensure fonts are available in the Docker image or mounted
        # For a production system, these font paths should be validated within the container.


    async def generate_video_from_material(self, material_path: str, config: Dict) -> Dict:
        """根据素材生成视频"""
        try:
            # Analyze uploaded material
            material_analysis = await self._analyze_material(material_path)
            
            # Generate script
            script = await self._generate_script(material_analysis, config['language'])
            
            # Generate audio
            audio_path = await self._generate_audio(script, config['language'])
            
            # Process visual content
            if material_analysis['type'] == 'image':
                video_path = await self._create_video_from_images(
                    [material_path], script, config
                )
            elif material_analysis['type'] == 'video':
                video_path = await self._enhance_existing_video(
                    material_path, script, config
                )
            else: # Fallback to text-only video if material is not image/video
                video_path = await self._create_text_video(script, config)
            
            # Merge audio and video
            final_video_path_no_subtitles = await self._merge_audio_video(video_path, audio_path)
            
            # Add subtitles
            subtitled_video_path = await self._add_subtitles(
                final_video_path_no_subtitles, script, config['language']
            )
            
            # Optimize output format for TikTok
            optimized_video_path = await self._optimize_for_tiktok(subtitled_video_path)
            
            return {
                'video_path': optimized_video_path,
                'script': script,
                'duration': await self._get_video_duration(optimized_video_path),
                'hashtags': await self._generate_hashtags(script, config['language']),
                'title': await self._generate_title(script, config['language'])
            }
            
        except Exception as e:
            logging.error(f"Error generating video: {e}", exc_info=True)
            return {'error': str(e)}

    async def _analyze_material(self, material_path: str) -> Dict:
        """Analyze uploaded material (image/video) to extract key features."""
        # Placeholder for actual analysis (e.g., using vision APIs or local ML models)
        logging.info(f"Analyzing material: {material_path}")
        if material_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return {
                'type': 'image',
                'description': 'A high-quality image of a landscape with mountains and a lake.',
                'key_elements': ['mountains', 'lake', 'nature', 'serene']
            }
        elif material_path.lower().endswith(('.mp4', '.mov', '.avi')):
            return {
                'type': 'video',
                'description': 'A short clip of a cat playing with a toy.',
                'key_elements': ['cat', 'playful', 'toy']
            }
        else:
            return {
                'type': 'text', # Treat as text if not a common image/video
                'description': 'No visual material provided, will generate text-based video.',
                'key_elements': []
            }


    async def _generate_script(self, material_analysis: Dict, language: str) -> str:
        """生成文案"""
        prompt = f"""
        Based on the following material analysis, generate an engaging TikTok video script for {language} speakers.
        
        Material Type: {material_analysis['type']}
        Content Description: {material_analysis['description']}
        Key Elements: {', '.join(material_analysis['key_elements'])}
        
        Requirements:
        1. Script length 15-30 seconds, suitable for narration.
        2. Must have an engaging hook at the beginning.
        3. Content should be interesting and relevant.
        4. Culturally appropriate for {language}.
        5. Optimized for short-form video platforms.
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error generating script with OpenAI: {e}", exc_info=True)
            return "Here's a great video for you!" # Fallback script

    async def _generate_audio(self, text: str, language: str) -> str:
        """生成多语言语音"""
        audio_path = f"/tmp/audio_{datetime.now().timestamp()}_{random.randint(1000, 9999)}.mp3"
        try:
            voice_config = self.language_configs[language]['voice_azure']
            
            # Use Azure Speech Service
            self.speech_config.speech_synthesis_voice_name = voice_config
            audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_path)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logging.info(f"Azure Speech Synthesis completed. Audio saved to {audio_path}")
                return audio_path
            else:
                logging.error(f"Azure Speech synthesis failed: {result.reason}. Trying ElevenLabs.")
                raise Exception(f"Azure Speech synthesis failed: {result.reason}")
                
        except Exception as e:
            logging.warning(f"Failed with Azure Speech: {e}. Falling back to ElevenLabs.")
            try:
                # Fallback to ElevenLabs
                elevenlabs_voice = self.language_configs[language]['voice_elevenlabs']
                audio = generate(
                    text=text,
                    voice=elevenlabs_voice,
                    model="eleven_multilingual_v2"
                )
                
                with open(audio_path, "wb") as audio_file:
                    audio_file.write(audio)
                logging.info(f"ElevenLabs audio generated and saved to {audio_path}")
                return audio_path
            except Exception as eleven_e:
                logging.error(f"Both Azure and ElevenLabs failed to generate audio: {eleven_e}", exc_info=True)
                raise Exception(f"Failed to generate audio: {eleven_e}")

    def _resize_for_tiktok(self, image: Image.Image) -> Image.Image:
        """Resize image to TikTok's common 9:16 aspect ratio (1080x1920)"""
        target_width = 1080
        target_height = 1920
        
        original_width, original_height = image.size
        original_aspect = original_width / original_height
        target_aspect = target_width / target_height

        if original_aspect > target_aspect:
            # Original is wider, fit by height and crop width
            new_height = target_height
            new_width = int(new_height * original_aspect)
            resized_image = image.resize((new_width, new_height), Image.LANCZOS)
            left = (new_width - target_width) / 2
            top = 0
            right = (new_width + target_width) / 2
            bottom = target_height
            cropped_image = resized_image.crop((left, top, right, bottom))
            return cropped_image
        else:
            # Original is taller or same aspect, fit by width and crop height
            new_width = target_width
            new_height = int(new_width / original_aspect)
            resized_image = image.resize((new_width, new_height), Image.LANCZOS)
            left = 0
            top = (new_height - target_height) / 2
            right = target_width
            bottom = (new_height + target_height) / 2
            cropped_image = resized_image.crop((left, top, right, bottom))
            return cropped_image

    async def _add_image_effects(self, image: Image.Image, config: Dict) -> Image.Image:
        """Add dynamic effects to an image (e.g., zoom, pan)"""
        # This is a conceptual placeholder. Actual implementation involves
        # creating a series of slightly modified images or using MoviePy's ImageClip with effects.
        # For simplicity, returning the image as is for now.
        logging.info("Applying image effects (placeholder).")
        return image

    async def _create_video_from_images(self, image_paths: List[str], script: str, config: Dict) -> str:
        """从图片创建视频"""
        clips = []
        
        for img_path in image_paths:
            img = Image.open(img_path).convert("RGB") # Ensure RGB mode
            img_resized = self._resize_for_tiktok(img)
            img_with_effects = await self._add_image_effects(img_resized, config)
            
            temp_path = f"/tmp/temp_frame_{datetime.now().timestamp()}_{random.randint(1000, 9999)}.png"
            img_with_effects.save(temp_path)
            
            clip = ImageClip(temp_path).set_duration(3) # Each image shown for 3 seconds
            clips.append(clip)
        
        if not clips:
            raise ValueError("No image clips to concatenate.")

        final_video_clip = concatenate_videoclips(clips, method="compose")
        output_path = f"/tmp/video_{datetime.now().timestamp()}_{random.randint(1000, 9999)}.mp4"
        final_video_clip.write_videofile(output_path, fps=24) # Ensure fps is set
        logging.info(f"Video from images created: {output_path}")
        return output_path

    async def _enhance_existing_video(self, video_path: str, script: str, config: Dict) -> str:
        """Enhance existing video (e.g., cut, add B-roll, visual effects)"""
        # Placeholder for complex video enhancement. This might involve:
        # - Scene detection and intelligent cutting
        # - Overlaying AI-generated B-roll footage
        # - Applying filters/color grading
        logging.info(f"Enhancing existing video (placeholder): {video_path}")
        # For now, just copy the video
        output_path = f"/tmp/enhanced_video_{datetime.now().timestamp()}_{random.randint(1000, 9999)}.mp4"
        shutil.copy(video_path, output_path)
        return output_path

    async def _create_text_video(self, script: str, config: Dict) -> str:
        """Create a video composed mainly of text on a background."""
        logging.info("Creating text-based video.")
        lines = script.split('.') # Simple split for demonstration
        clips = []
        duration_per_line = 2 # seconds per line
        
        font_path = self.language_configs[config['language']]['font_path']
        if not os.path.exists(font_path):
             logging.warning(f"Font file not found at {font_path}. Using default.")
             font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf' # Fallback to a common system font

        for i, line in enumerate(lines):
            if not line.strip():
                continue
            
            # Create a blank black image
            img = Image.new('RGB', (1080, 1920), color = (0, 0, 0))
            d = ImageDraw.Draw(img)
            
            try:
                fnt = ImageFont.truetype(font_path, 80)
            except IOError:
                logging.error(f"Could not load font from {font_path}. Using default Pillow font.")
                fnt = ImageFont.load_default()

            text_color = "white"
            stroke_color = "black"
            stroke_width = 3

            # Calculate text size
            bbox = d.textbbox((0,0), line.strip(), font=fnt)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Center the text
            x = (img.width - text_width) / 2
            y = (img.height - text_height) / 2

            d.text((x, y), line.strip(), font=fnt, fill=text_color, stroke_width=stroke_width, stroke_fill=stroke_color, align="center")
            
            temp_path = f"/tmp/text_frame_{datetime.now().timestamp()}_{i}_{random.randint(1000, 9999)}.png"
            img.save(temp_path)
            clip = ImageClip(temp_path).set_duration(duration_per_line)
            clips.append(clip)
            
        if not clips:
            raise ValueError("No text clips to concatenate.")

        final_video_clip = concatenate_videoclips(clips, method="compose")
        output_path = f"/tmp/text_video_{datetime.now().timestamp()}_{random.randint(1000, 9999)}.mp4"
        final_video_clip.write_videofile(output_path, fps=24)
        logging.info(f"Text video created: {output_path}")
        return output_path

    async def _merge_audio_video(self, video_path: str, audio_path: str) -> str:
        """Merge generated audio with the video."""
        logging.info(f"Merging audio {audio_path} with video {video_path}")
        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)
        
        # Adjust video duration to match audio if audio is shorter, or vice-versa
        if audio_clip.duration < video_clip.duration:
            video_clip = video_clip.set_duration(audio_clip.duration)
        elif audio_clip.duration > video_clip.duration:
            # If audio is longer, loop video or extend static image at end
            # For simplicity, just set video duration to audio duration for now (will cut video if shorter)
            video_clip = video_clip.set_duration(audio_clip.duration) 

        final_clip = video_clip.set_audio(audio_clip)
        output_path = f"/tmp/merged_video_{datetime.now().timestamp()}_{random.randint(1000, 9999)}.mp4"
        final_clip.write_videofile(output_path, fps=final_clip.fps)
        logging.info(f"Audio and video merged: {output_path}")
        return output_path

    async def _add_subtitles(self, video_path: str, script: str, language: str) -> str:
        """Add dynamic subtitles to the video."""
        logging.info(f"Adding subtitles to {video_path}")
        video = VideoFileClip(video_path)
        
        font_path = self.language_configs[language]['font_path']
        if not os.path.exists(font_path):
             logging.warning(f"Font file not found at {font_path}. Using default.")
             font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf' # Fallback

        # Simple subtitle generation (each sentence appears for a calculated duration)
        sentences = [s.strip() for s in script.split('.') if s.strip()]
        
        text_clips = []
        current_time = 0
        for sentence in sentences:
            # Estimate duration based on characters or words per second
            # A more advanced approach would use actual audio timing for precise sync
            duration = max(len(sentence) * 0.1, 2) # At least 2 seconds, roughly 10 chars/sec
            
            txt_clip = TextClip(sentence, fontsize=40, color='yellow', font=font_path,
                                stroke_color='black', stroke_width=2).set_position(('center', 0.8), relative=True)
            txt_clip = txt_clip.set_start(current_time).set_duration(duration)
            text_clips.append(txt_clip)
            current_time += duration
        
        if text_clips:
            final_clip = CompositeVideoClip([video] + text_clips)
        else:
            final_clip = video

        output_path = f"/tmp/subtitled_video_{datetime.now().timestamp()}_{random.randint(1000, 9999)}.mp4"
        final_clip.write_videofile(output_path, fps=video.fps)
        logging.info(f"Subtitled video created: {output_path}")
        return output_path


    async def _optimize_for_tiktok(self, video_path: str) -> str:
        """Optimize video for TikTok (e.g., resolution, bitrate, format)."""
        logging.info(f"Optimizing video {video_path} for TikTok.")
        # TikTok recommends 720p to 1080p, 9:16 aspect ratio, H.264 codec.
        # MoviePy's default output is generally good, but we can re-encode for specific bitrate.
        clip = VideoFileClip(video_path)
        
        # Ensure correct resolution if not already set
        if clip.w != 1080 or clip.h != 1920:
             clip = clip.resize((1080, 1920))

        output_path = f"/tmp/tiktok_optimized_video_{datetime.now().timestamp()}_{random.randint(1000, 9999)}.mp4"
        clip.write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac", 
            bitrate="5000k", # Adjust bitrate as needed for quality vs. file size
            fps=24 # Common frame rate for TikTok
        )
        logging.info(f"TikTok optimized video saved to {output_path}")
        return output_path

    async def _get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds."""
        clip = VideoFileClip(video_path)
        duration = clip.duration
        clip.close()
        return duration

    async def _generate_hashtags(self, script: str, language: str) -> List[str]:
        """Generate relevant hashtags based on the script."""
        prompt = f"""
        Generate 5-10 highly relevant and trending hashtags for a TikTok video based on the following script, for {language} audience:
        
        Script: {script}
        
        Requirements:
        1. Only provide hashtags, no other text.
        2. Hashtags should be concise and popular.
        3. Include general and niche hashtags.
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            hashtags_str = response.choices[0].message.content.strip()
            # Parse hashtags (assuming they are comma-separated or space-separated)
            return [h.strip() for h in hashtags_str.replace('#', '').split() if h.strip()]
        except Exception as e:
            logging.error(f"Error generating hashtags: {e}")
            return ["#TikTokViral", "#ForYou", "#AIContent"] # Fallback

    async def _generate_title(self, script: str, language: str) -> str:
        """Generate a catchy title for the TikTok video."""
        prompt = f"""
        Generate a catchy and engaging title for a TikTok video based on the following script, for {language} audience. The title should be short and attention-grabbing.
        
        Script: {script}
        
        Requirements:
        1. Title should be under 25 characters.
        2. Make it intriguing.
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.7
            )
            title = response.choices[0].message.content.strip()
            return title[:25] # Truncate to 25 characters
        except Exception as e:
            logging.error(f"Error generating title: {e}")
            return "Watch This Now!" # Fallback

# Example usage (for testing this module independently)
if __name__ == "__main__":
    import shutil
    import os
    from dotenv import load_dotenv

    load_dotenv() # Load environment variables from .env

    async def test_video_generation():
        generator = AIVideoGenerator()

        # Create a dummy image for testing
        dummy_img_path = "/tmp/dummy_image.png"
        Image.new('RGB', (1920, 1080), color = 'red').save(dummy_img_path)
        logging.info(f"Created dummy image at {dummy_img_path}")

        config = {
            'language': 'en',
            'quality': 'high',
            'effects': ['zoom_pan']
        }

        # Test with image material
        logging.info("Testing video generation from image...")
        result_image = await generator.generate_video_from_material(dummy_img_path, config)
        logging.info(f"Image video generation result: {result_image}")
        if 'video_path' in result_image and os.path.exists(result_image['video_path']):
            logging.info(f"Generated video: {result_image['video_path']}")
        else:
            logging.error("Image video generation failed.")

        # Test with text material (no visual input)
        logging.info("Testing video generation from text (no visual material)...")
        # Ensure that _analyze_material returns 'type': 'text' if path is invalid or non-visual
        result_text = await generator.generate_video_from_material("/nonexistent/path/text_input.txt", config)
        logging.info(f"Text video generation result: {result_text}")
        if 'video_path' in result_text and os.path.exists(result_text['video_path']):
            logging.info(f"Generated text video: {result_text['video_path']}")
        else:
            logging.error("Text video generation failed.")

        # Clean up dummy files
        if os.path.exists(dummy_img_path):
            os.remove(dummy_img_path)
            logging.info(f"Cleaned up {dummy_img_path}")
        
        if 'video_path' in result_image and os.path.exists(result_image['video_path']):
            os.remove(result_image['video_path'])
            logging.info(f"Cleaned up {result_image['video_path']}")
        if 'video_path' in result_image and 'audio_path' in result_image and os.path.exists(result_image['audio_path']):
            os.remove(result_image['audio_path'])
            logging.info(f"Cleaned up {result_image['audio_path']}")

        if 'video_path' in result_text and os.path.exists(result_text['video_path']):
            os.remove(result_text['video_path'])
            logging.info(f"Cleaned up {result_text['video_path']}")
        if 'video_path' in result_text and 'audio_path' in result_text and os.path.exists(result_text['audio_path']):
            os.remove(result_text['audio_path'])
            logging.info(f"Cleaned up {result_text['audio_path']}")


    asyncio.run(test_video_generation())
